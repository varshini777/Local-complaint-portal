from datetime import datetime, timezone

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask import current_app as app
from flask_login import current_user
from sqlalchemy.exc import SQLAlchemyError
from wtforms.validators import ValidationError

from backend.extensions import db
from backend.forms.auth_forms import validate_password_strength
from backend.forms.officer_forms import (
    ComplaintResolutionForm,
    ComplaintStatusForm,
    OfficerChangePasswordForm,
    OfficerProfileForm,
)
from backend.models import (
    Complaint,
    ComplaintCategory,
    ComplaintUpdate,
)
from backend.services.activity_log_service import log_activity
from backend.services.file_service import save_after_image
from backend.services.notification_service import (
    create_complaint_status_notification,
    create_complaint_resolved_notification,
)
from backend.routes.auth_routes import officer_required


officer_bp = Blueprint("officer", __name__, url_prefix="/officer")


def log_officer_activity(action, details=None):
    log_activity(action, current_user, details)


def assigned_complaints_query():
    return Complaint.query.filter(
        Complaint.assigned_officer_id == current_user.user_id,
        Complaint.is_active.is_(True),
    )


def get_assigned_complaint_or_404(complaint_id):
    return assigned_complaints_query().filter(
        Complaint.complaint_id == complaint_id
    ).first_or_404()


def active_categories():
    return (
        ComplaintCategory.query.filter_by(is_active=True)
        .order_by(ComplaintCategory.category_name.asc())
        .all()
    )


@officer_bp.route("/dashboard")
@officer_required
def dashboard():
    complaints = assigned_complaints_query()
    total_assigned = complaints.count()
    pending_complaints = complaints.filter(
        Complaint.status.in_(
            [
                Complaint.STATUS_SUBMITTED,
                Complaint.STATUS_ASSIGNED,
            ]
        )
    ).count()
    in_progress_complaints = complaints.filter(
        Complaint.status == Complaint.STATUS_IN_PROGRESS
    ).count()
    resolved_complaints = complaints.filter(
        Complaint.status == Complaint.STATUS_RESOLVED
    ).count()
    resolved_with_times = complaints.filter(
        Complaint.resolved_at.isnot(None),
        Complaint.assigned_at.isnot(None),
    ).all()
    resolution_hours = [
        (complaint.resolved_at - complaint.assigned_at).total_seconds() / 3600
        for complaint in resolved_with_times
    ]
    average_resolution_hours = (
        sum(resolution_hours) / len(resolution_hours) if resolution_hours else 0
    )
    recent_assigned_complaints = (
        complaints.options(
            db.joinedload(Complaint.category),
            db.joinedload(Complaint.ward),
            db.joinedload(Complaint.citizen),
        )
        .order_by(Complaint.submitted_at.desc())
        .limit(5)
        .all()
    )

    return render_template(
        "officer/dashboard.html",
        total_assigned=total_assigned,
        pending_complaints=pending_complaints,
        in_progress_complaints=in_progress_complaints,
        resolved_complaints=resolved_complaints,
        average_resolution_hours=round(average_resolution_hours or 0, 2),
        recent_assigned_complaints=recent_assigned_complaints,
    )


@officer_bp.route("/complaints")
@officer_required
def assigned_complaints():
    page = request.args.get("page", 1, type=int)
    status = request.args.get("status", "").strip()
    priority = request.args.get("priority", "").strip()
    category_id = request.args.get("category", "").strip()

    complaints = assigned_complaints_query()

    if status in Complaint.STATUSES:
        complaints = complaints.filter(Complaint.status == status)
    if priority in Complaint.PRIORITIES:
        complaints = complaints.filter(Complaint.priority == priority)
    if category_id.isdigit():
        complaints = complaints.filter(Complaint.category_id == int(category_id))

    pagination = (
        complaints.options(
            db.joinedload(Complaint.category),
            db.joinedload(Complaint.ward),
            db.joinedload(Complaint.citizen),
        )
        .order_by(Complaint.submitted_at.desc())
        .paginate(page=page, per_page=10, error_out=False)
    )

    return render_template(
        "officer/assigned_complaints.html",
        complaints=pagination.items,
        pagination=pagination,
        statuses=Complaint.STATUSES,
        priorities=Complaint.PRIORITIES,
        categories=active_categories(),
        filters={
            "status": status,
            "priority": priority,
            "category": category_id,
            "page": page,
        },
    )


@officer_bp.route("/complaints/<int:complaint_id>")
@officer_required
def complaint_detail(complaint_id):
    complaint = (
        assigned_complaints_query()
        .filter(Complaint.complaint_id == complaint_id)
        .options(
            db.joinedload(Complaint.category),
            db.joinedload(Complaint.ward),
            db.joinedload(Complaint.citizen),
        )
        .first_or_404()
    )

    return render_template(
        "officer/complaint_detail.html",
        complaint=complaint,
        citizen=complaint.citizen,
        timeline=complaint.timeline,
    )


@officer_bp.route("/complaints/<int:complaint_id>/status", methods=["GET", "POST"])
@officer_required
def update_status(complaint_id):
    complaint = get_assigned_complaint_or_404(complaint_id)
    form = ComplaintStatusForm(obj=complaint)

    if form.validate_on_submit():
        old_status = complaint.status
        allowed_transitions = {
            Complaint.STATUS_SUBMITTED: {Complaint.STATUS_ASSIGNED},
            Complaint.STATUS_ASSIGNED: {Complaint.STATUS_IN_PROGRESS},
            Complaint.STATUS_IN_PROGRESS: {Complaint.STATUS_RESOLVED},
            Complaint.STATUS_RESOLVED: {Complaint.STATUS_CLOSED},
        }

        if form.status.data not in allowed_transitions.get(old_status, set()):
            flash("Invalid status transition.", "danger")
            return render_template("officer/update_status.html", form=form, complaint=complaint)

        complaint.status = form.status.data
        if complaint.status == Complaint.STATUS_IN_PROGRESS and not complaint.assigned_at:
            complaint.assigned_at = datetime.now(timezone.utc)
        if complaint.status == Complaint.STATUS_RESOLVED and not complaint.resolved_at:
            complaint.resolved_at = datetime.now(timezone.utc)
        if complaint.status == Complaint.STATUS_CLOSED and not complaint.closed_at:
            complaint.closed_at = datetime.now(timezone.utc)

        db.session.add(
            ComplaintUpdate(
                complaint_id=complaint.complaint_id,
                updated_by=current_user.user_id,
                status=complaint.status,
                action="Status Updated",
                remarks=form.remarks.data.strip() if form.remarks.data else None,
            )
        )
        try:
            create_complaint_status_notification(complaint, complaint.citizen_id, old_status)
        except Exception as e:
            app.logger.error(f"Notification creation failed during status update: {e}")
        try:
            log_officer_activity(
                "Complaint Status Update",
                f"Complaint {complaint.complaint_number} changed from {old_status} to {complaint.status}.",
            )
        except Exception as e:
            app.logger.error(f"Activity logging failed during status update: {e}")

        try:
            db.session.commit()
            flash("Complaint status updated successfully.", "success")
            return redirect(
                url_for("officer.complaint_detail", complaint_id=complaint.complaint_id)
            )
        except SQLAlchemyError:
            db.session.rollback()
            flash("Status update failed.", "danger")

    return render_template("officer/update_status.html", form=form, complaint=complaint)


@officer_bp.route("/complaints/<int:complaint_id>/resolve", methods=["GET", "POST"])
@officer_required
def resolve_complaint(complaint_id):
    complaint = get_assigned_complaint_or_404(complaint_id)
    if complaint.status in {Complaint.STATUS_RESOLVED, Complaint.STATUS_CLOSED}:
        flash("Complaint is already resolved.", "warning")
        return redirect(
            url_for("officer.complaint_detail", complaint_id=complaint.complaint_id)
        )

    form = ComplaintResolutionForm(obj=complaint)

    if form.validate_on_submit():
        try:
            after_image_path = save_after_image(form.after_image.data)
            complaint.resolution_notes = form.resolution_notes.data.strip()
            complaint.work_performed = (
                form.work_performed.data.strip() if form.work_performed.data else None
            )
            complaint.materials_used = (
                form.materials_used.data.strip() if form.materials_used.data else None
            )
            complaint.additional_remarks = (
                form.additional_remarks.data.strip()
                if form.additional_remarks.data
                else None
            )
            if after_image_path:
                complaint.after_image_path = after_image_path
            complaint.status = Complaint.STATUS_RESOLVED
            complaint.resolved_at = datetime.now(timezone.utc)

            db.session.add(
                ComplaintUpdate(
                    complaint_id=complaint.complaint_id,
                    updated_by=current_user.user_id,
                    status=Complaint.STATUS_RESOLVED,
                    action="Complaint Resolved",
                    remarks=complaint.resolution_notes,
                )
            )
            try:
                create_complaint_resolved_notification(complaint, complaint.citizen_id)
            except Exception as e:
                app.logger.error(f"Notification creation failed during complaint resolution: {e}")
            try:
                log_officer_activity(
                    "Complaint Resolution",
                    f"Complaint {complaint.complaint_number} resolved.",
                )
            except Exception as e:
                app.logger.error(f"Activity logging failed during complaint resolution: {e}")
            db.session.commit()
            flash("Complaint resolved successfully.", "success")
            return redirect(
                url_for("officer.complaint_detail", complaint_id=complaint.complaint_id)
            )
        except (SQLAlchemyError, ValueError) as exc:
            db.session.rollback()
            flash(str(exc) if isinstance(exc, ValueError) else "Resolution failed.", "danger")

    return render_template("officer/update_status.html", form=form, complaint=complaint)


@officer_bp.route("/profile", methods=["GET", "POST"])
@officer_required
def profile():
    form = OfficerProfileForm(obj=current_user)

    if form.validate_on_submit():
        current_user.full_name = form.full_name.data.strip()
        current_user.phone = form.phone.data.strip()

        try:
            log_officer_activity("Profile Update", "Officer updated profile details.")
            db.session.commit()
            flash("Profile updated successfully.", "success")
            return redirect(url_for("officer.profile"))
        except SQLAlchemyError:
            db.session.rollback()
            flash("Profile update failed.", "danger")

    return render_template("officer/profile.html", form=form)


@officer_bp.route("/change-password", methods=["GET", "POST"])
@officer_required
def change_password():
    form = OfficerChangePasswordForm()

    if form.validate_on_submit():
        try:
            validate_password_strength(form, form.new_password)
        except ValidationError as exc:
            form.new_password.errors.append(str(exc))
            return render_template("officer/change_password.html", form=form)

        if not current_user.check_password(form.current_password.data):
            flash("Current password is incorrect.", "danger")
            return render_template("officer/change_password.html", form=form)

        current_user.set_password(form.new_password.data)

        try:
            log_officer_activity("Password Change", "Officer changed password.")
            db.session.commit()
            flash("Password changed successfully.", "success")
            return redirect(url_for("officer.profile"))
        except SQLAlchemyError:
            db.session.rollback()
            flash("Password change failed.", "danger")

    return render_template("officer/change_password.html", form=form)
