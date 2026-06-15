from datetime import datetime, timedelta

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask import current_app as app
from flask_login import current_user
from sqlalchemy.exc import SQLAlchemyError
from wtforms.validators import ValidationError

from backend.extensions import db
from backend.forms.auth_forms import validate_password_strength
from backend.forms.citizen_forms import (
    ChangePasswordForm,
    ComplaintForm,
    FeedbackForm,
    ProfileUpdateForm,
)
from backend.models import (
    Complaint,
    ComplaintCategory,
    ComplaintUpdate,
    Feedback,
    Notification,
    Ward,
)
from backend.services.activity_log_service import log_activity
from backend.services.file_service import save_before_image
from backend.services.notification_service import (
    create_complaint_submitted_notification,
    mark_notification_read,
    mark_all_notifications_read,
)
from backend.utils.form_helpers import (
    populate_active_category_choices,
    populate_active_ward_choices,
)
from backend.routes.auth_routes import citizen_required


citizen_bp = Blueprint("citizen", __name__, url_prefix="/citizen")


def log_citizen_activity(action, details=None):
    log_activity(action, current_user, details)


def active_categories():
    return (
        ComplaintCategory.query.filter_by(is_active=True)
        .order_by(ComplaintCategory.category_name.asc())
        .all()
    )


def active_wards():
    return Ward.query.filter_by(is_active=True).order_by(Ward.ward_name.asc()).all()


def populate_complaint_form_choices(form):
    populate_active_category_choices(form)
    populate_active_ward_choices(form)


@citizen_bp.route("/dashboard")
@citizen_required
def dashboard():
    complaints_query = Complaint.query.filter(
        Complaint.citizen_id == current_user.user_id,
        Complaint.is_active.is_(True),
    )

    total_complaints = complaints_query.count()
    pending_complaints = complaints_query.filter(
        Complaint.status.in_(
            [
                Complaint.STATUS_SUBMITTED,
                Complaint.STATUS_ASSIGNED,
                Complaint.STATUS_IN_PROGRESS,
            ]
        )
    ).count()
    resolved_complaints = complaints_query.filter(
        Complaint.status == Complaint.STATUS_RESOLVED
    ).count()
    closed_complaints = complaints_query.filter(
        Complaint.status == Complaint.STATUS_CLOSED
    ).count()
    recent_complaints = (
        complaints_query.options(
            db.joinedload(Complaint.category),
            db.joinedload(Complaint.ward),
            db.joinedload(Complaint.assigned_officer),
        )
        .order_by(Complaint.submitted_at.desc())
        .limit(5)
        .all()
    )
    stale_cutoff = datetime.utcnow() - timedelta(days=Complaint.REFILE_AFTER_DAYS)
    stale_complaints = (
        complaints_query.filter(
            Complaint.status.in_(
                [Complaint.STATUS_SUBMITTED, Complaint.STATUS_ASSIGNED]
            ),
            Complaint.submitted_at <= stale_cutoff,
        )
        .order_by(Complaint.submitted_at.asc())
        .all()
    )

    return render_template(
        "citizen/dashboard.html",
        total_complaints=total_complaints,
        pending_complaints=pending_complaints,
        resolved_complaints=resolved_complaints,
        closed_complaints=closed_complaints,
        recent_complaints=recent_complaints,
        stale_complaints=stale_complaints,
    )


@citizen_bp.route("/complaints/new", methods=["GET", "POST"])
@citizen_required
def submit_complaint():
    form = ComplaintForm()
    populate_complaint_form_choices(form)

    if form.validate_on_submit():
        try:
            before_image_path = save_before_image(form.before_image.data)
            complaint = Complaint(
                title=form.title.data.strip(),
                description=form.description.data.strip(),
                category_id=form.category.data,
                priority=form.priority.data,
                status=Complaint.STATUS_SUBMITTED,
                escalation_level=Complaint.ESCALATION_NORMAL,
                location=form.location.data.strip(),
                ward_id=form.ward.data,
                citizen_id=current_user.user_id,
                before_image_path=before_image_path,
                is_active=True,
            )
            db.session.add(complaint)
            db.session.flush()

            db.session.add(
                ComplaintUpdate(
                    complaint_id=complaint.complaint_id,
                    updated_by=current_user.user_id,
                    status=Complaint.STATUS_SUBMITTED,
                    action="Complaint Submitted",
                    remarks="Complaint submitted by citizen.",
                )
            )
            try:
                create_complaint_submitted_notification(complaint, current_user.user_id)
            except Exception as e:
                app.logger.error(f"Notification creation failed during complaint submission: {e}")
            try:
                log_citizen_activity(
                    "Complaint Submission",
                    f"Complaint {complaint.complaint_number} submitted.",
                )
            except Exception as e:
                app.logger.error(f"Activity logging failed during complaint submission: {e}")
            db.session.commit()
            flash("Complaint submitted successfully.", "success")
            return redirect(
                url_for("citizen.complaint_detail", complaint_id=complaint.complaint_id)
            )
        except (SQLAlchemyError, ValueError) as exc:
            db.session.rollback()
            app.logger.error(f"Complaint submission failed: {exc}")
            flash(str(exc) if isinstance(exc, ValueError) else "Complaint submission failed.", "danger")

    return render_template(
        "citizen/submit_complaint.html",
        form=form,
        complaint_date=datetime.utcnow(),
    )


@citizen_bp.route("/complaints")
@citizen_required
def complaint_history():
    page = request.args.get("page", 1, type=int)
    complaint_number = request.args.get("complaint_number", "").strip()
    status = request.args.get("status", "").strip()
    category_id = request.args.get("category", "").strip()

    complaints = Complaint.query.filter(
        Complaint.citizen_id == current_user.user_id,
        Complaint.is_active.is_(True),
    )

    if complaint_number:
        complaints = complaints.filter(Complaint.complaint_number.ilike(f"%{complaint_number}%"))
    if status in Complaint.STATUSES:
        complaints = complaints.filter(Complaint.status == status)
    if category_id.isdigit():
        complaints = complaints.filter(Complaint.category_id == int(category_id))

    pagination = (
        complaints.options(
            db.joinedload(Complaint.category),
            db.joinedload(Complaint.ward),
            db.joinedload(Complaint.assigned_officer),
        )
        .order_by(Complaint.submitted_at.desc())
        .paginate(page=page, per_page=10, error_out=False)
    )

    return render_template(
        "citizen/complaint_history.html",
        complaints=pagination.items,
        pagination=pagination,
        categories=active_categories(),
        statuses=Complaint.STATUSES,
        filters={
            "complaint_number": complaint_number,
            "status": status,
            "category": category_id,
            "page": page,
        },
    )


@citizen_bp.route("/complaints/<int:complaint_id>")
@citizen_required
def complaint_detail(complaint_id):
    complaint = (
        Complaint.query.filter(
            Complaint.complaint_id == complaint_id,
            Complaint.citizen_id == current_user.user_id,
            Complaint.is_active.is_(True),
        )
        .options(
            db.joinedload(Complaint.category),
            db.joinedload(Complaint.ward),
            db.joinedload(Complaint.assigned_officer),
        )
        .first_or_404()
    )

    return render_template(
        "citizen/complaint_detail.html",
        complaint=complaint,
        timeline=complaint.timeline,
    )


@citizen_bp.route("/notifications")
@citizen_required
def notifications():
    citizen_notifications = (
        Notification.query.filter(
            Notification.user_id == current_user.user_id,
            Notification.is_active.is_(True),
        )
        .options(db.joinedload(Notification.complaint))
        .order_by(Notification.created_at.desc())
        .all()
    )
    return render_template(
        "citizen/notifications.html",
        notifications=citizen_notifications,
    )


@citizen_bp.route("/notifications/<int:notification_id>/read", methods=["POST"])
@citizen_required
def mark_notification_read_route(notification_id):
    from flask import abort
    notification = mark_notification_read(notification_id, current_user.user_id)
    if not notification:
        abort(404)
    flash("Notification marked as read.", "success")
    return redirect(url_for("citizen.notifications"))


@citizen_bp.route("/notifications/read-all", methods=["POST"])
@citizen_required
def mark_all_notifications_read_route():
    updated_count = mark_all_notifications_read(current_user.user_id)
    if updated_count > 0:
        log_citizen_activity(
            "Notifications Read",
            f"Citizen marked {updated_count} notifications as read.",
        )
        db.session.commit()
    flash("All notifications marked as read.", "success")
    return redirect(url_for("citizen.notifications"))


@citizen_bp.route("/profile", methods=["GET", "POST"])
@citizen_required
def profile():
    form = ProfileUpdateForm(obj=current_user)

    if form.validate_on_submit():
        current_user.full_name = form.full_name.data.strip()
        current_user.phone = form.phone.data.strip()

        try:
            log_citizen_activity("Profile Update", "Citizen updated profile details.")
            db.session.commit()
            flash("Profile updated successfully.", "success")
            return redirect(url_for("citizen.profile"))
        except SQLAlchemyError:
            db.session.rollback()
            flash("Profile update failed.", "danger")

    return render_template("citizen/profile.html", form=form)


@citizen_bp.route("/change-password", methods=["GET", "POST"])
@citizen_required
def change_password():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        try:
            validate_password_strength(form, form.new_password)
        except ValidationError as exc:
            form.new_password.errors.append(str(exc))
            return render_template("citizen/change_password.html", form=form)

        if not current_user.check_password(form.current_password.data):
            flash("Current password is incorrect.", "danger")
            return render_template("citizen/change_password.html", form=form)

        current_user.set_password(form.new_password.data)

        try:
            log_citizen_activity("Password Change", "Citizen changed password.")
            db.session.commit()
            flash("Password changed successfully.", "success")
            return redirect(url_for("citizen.profile"))
        except SQLAlchemyError:
            db.session.rollback()
            flash("Password change failed.", "danger")

    return render_template("citizen/change_password.html", form=form)


@citizen_bp.route("/complaints/<int:complaint_id>/feedback", methods=["GET", "POST"])
@citizen_required
def submit_feedback(complaint_id):
    complaint = Complaint.query.filter(
        Complaint.complaint_id == complaint_id,
        Complaint.citizen_id == current_user.user_id,
        Complaint.is_active.is_(True),
    ).first_or_404()

    if complaint.status != Complaint.STATUS_RESOLVED:
        flash("Feedback can only be submitted for resolved complaints.", "warning")
        return redirect(url_for("citizen.complaint_detail", complaint_id=complaint.complaint_id))

    existing_feedback = Feedback.query.filter_by(complaint_id=complaint.complaint_id).first()
    if existing_feedback:
        flash("You have already submitted feedback for this complaint.", "info")
        return redirect(url_for("citizen.complaint_detail", complaint_id=complaint.complaint_id))

    form = FeedbackForm()

    if form.validate_on_submit():
        feedback = Feedback(
            complaint_id=complaint.complaint_id,
            citizen_id=current_user.user_id,
            rating=form.rating.data,
            comment=form.comment.data,
            is_active=True,
        )
        try:
            db.session.add(feedback)
            log_citizen_activity("Feedback Submitted", f"Submitted feedback for complaint {complaint.complaint_number}.")
            db.session.commit()
            flash("Thank you for your feedback!", "success")
            return redirect(url_for("citizen.complaint_detail", complaint_id=complaint.complaint_id))
        except SQLAlchemyError:
            db.session.rollback()
            flash("Failed to submit feedback. Please try again.", "danger")

    return render_template("citizen/feedback.html", form=form, complaint=complaint)
