from flask import Blueprint, flash, redirect, render_template, request, url_for, abort
from flask import current_app as app
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timezone

from backend.extensions import db
from backend.models import ActivityLog, Complaint, SystemSetting, User, Ward, Notification, ComplaintUpdate
from backend.services.activity_log_service import log_activity
from backend.services.notification_service import (
    create_complaint_assigned_notification,
    create_complaint_closed_notification,
)
from backend.routes.auth_routes import admin_required
from backend.forms.admin_forms import (
    AdminActivityLogFilterForm,
    AdminComplaintAssignForm,
    AdminComplaintFilterForm,
    AdminOfficerForm,
    AdminSystemSettingsForm,
    AdminUserSearchForm,
    AdminWardForm,
)

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

USERS_PER_PAGE = 10
COMPLAINTS_PER_PAGE = 10
ACTIVITY_LOGS_PER_PAGE = 20

def get_or_404(model, object_id):
    obj = db.session.get(model, object_id)
    if obj is None:
        abort(404)
    return obj

@admin_bp.route("/dashboard")
@admin_required
def dashboard():
    total_users = User.query.count()
    total_citizens = User.query.filter_by(role=User.ROLE_CITIZEN).count()
    total_officers = User.query.filter_by(role=User.ROLE_OFFICER).count()
    
    total_complaints = Complaint.query.count()
    pending_complaints = Complaint.query.filter(Complaint.status.in_([Complaint.STATUS_SUBMITTED, Complaint.STATUS_ASSIGNED, Complaint.STATUS_IN_PROGRESS])).count()
    resolved_complaints = Complaint.query.filter_by(status=Complaint.STATUS_RESOLVED).count()
    closed_complaints = Complaint.query.filter_by(status=Complaint.STATUS_CLOSED).count()
    escalated_complaints = Complaint.query.filter(Complaint.escalation_level.in_([Complaint.ESCALATION_URGENT, Complaint.ESCALATION_CRITICAL])).count()

    recent_complaints = (
        Complaint.query.options(
            db.joinedload(Complaint.category),
            db.joinedload(Complaint.ward),
            db.joinedload(Complaint.assigned_officer),
            db.joinedload(Complaint.citizen),
        )
        .order_by(Complaint.submitted_at.desc())
        .limit(5)
        .all()
    )
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()

    return render_template(
        "admin/dashboard.html",
        total_users=total_users,
        total_citizens=total_citizens,
        total_officers=total_officers,
        total_complaints=total_complaints,
        pending_complaints=pending_complaints,
        resolved_complaints=resolved_complaints,
        closed_complaints=closed_complaints,
        escalated_complaints=escalated_complaints,
        recent_complaints=recent_complaints,
        recent_users=recent_users
    )


@admin_bp.route("/users", methods=["GET"])
@admin_required
def manage_users():
    form = AdminUserSearchForm(request.args)
    query = User.query
    
    if form.search_term.data:
        search = f"%{form.search_term.data}%"
        query = query.filter((User.full_name.ilike(search)) | (User.email.ilike(search)))
        
    if form.role.data:
        query = query.filter(User.role == form.role.data)
        
    page = request.args.get("page", 1, type=int)
    users = query.order_by(User.created_at.desc()).paginate(page=page, per_page=USERS_PER_PAGE, error_out=False)
    
    return render_template("admin/users.html", users=users, form=form)


@admin_bp.route("/users/<int:user_id>/toggle-status", methods=["POST"])
@admin_required
def toggle_user_status(user_id):
    user = get_or_404(User, user_id)
    if user.is_admin:
        flash("Cannot deactivate an admin user.", "danger")
        return redirect(url_for("admin.manage_users"))
        
    user.is_active = not user.is_active
    action = "Activated" if user.is_active else "Deactivated"
    try:
        log_activity(f"User {action}", user, details=f"User {user.email} was {action.lower()}.")
        db.session.commit()
        flash(f"User {user.full_name} has been {action.lower()}.", "success")
    except SQLAlchemyError:
        db.session.rollback()
        flash("An error occurred while updating the user status.", "danger")
        
    return redirect(url_for("admin.manage_users"))


@admin_bp.route("/officers/new", methods=["GET", "POST"])
@admin_required
def create_officer():
    form = AdminOfficerForm()
    
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data.lower()).first():
            flash("Email address already in use.", "danger")
            return render_template("admin/officer_form.html", form=form, action="Create")
            
        user = User(
            full_name=form.full_name.data,
            email=form.email.data.lower(),
            phone=form.phone.data,
            role=User.ROLE_OFFICER,
            is_active=form.is_active.data
        )
        if form.password.data:
            user.set_password(form.password.data)
        else:
            flash("Password is required for new officers.", "danger")
            return render_template("admin/officer_form.html", form=form, action="Create")
            
        try:
            db.session.add(user)
            db.session.flush()
            log_activity("Officer Created", user, details=f"Created officer {user.email}.")
            db.session.commit()
            flash("Officer created successfully.", "success")
            return redirect(url_for("admin.manage_users", role=User.ROLE_OFFICER))
        except SQLAlchemyError:
            db.session.rollback()
            flash("An error occurred while creating the officer.", "danger")
            
    return render_template("admin/officer_form.html", form=form, action="Create")


@admin_bp.route("/officers/<int:user_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_officer(user_id):
    user = get_or_404(User, user_id)
    if not user.is_officer:
        flash("Invalid officer.", "danger")
        return redirect(url_for("admin.manage_users"))
        
    form = AdminOfficerForm(obj=user)
    
    if form.validate_on_submit():
        existing_user = User.query.filter(User.email == form.email.data.lower(), User.user_id != user.user_id).first()
        if existing_user:
            flash("Email address already in use by another account.", "danger")
            return render_template("admin/officer_form.html", form=form, action="Edit")
            
        user.full_name = form.full_name.data
        user.email = form.email.data.lower()
        user.phone = form.phone.data
        user.is_active = form.is_active.data
        
        if form.password.data:
            user.set_password(form.password.data)
            
        try:
            log_activity("Officer Updated", user, details=f"Updated officer {user.email}.")
            db.session.commit()
            flash("Officer updated successfully.", "success")
            return redirect(url_for("admin.manage_users", role=User.ROLE_OFFICER))
        except SQLAlchemyError:
            db.session.rollback()
            flash("An error occurred while updating the officer.", "danger")
            
    return render_template("admin/officer_form.html", form=form, action="Edit")


@admin_bp.route("/wards", methods=["GET"])
@admin_required
def manage_wards():
    page = request.args.get("page", 1, type=int)
    wards = Ward.query.order_by(Ward.ward_name).paginate(page=page, per_page=10, error_out=False)
    return render_template("admin/wards.html", wards=wards)


@admin_bp.route("/wards/new", methods=["GET", "POST"])
@admin_required
def create_ward():
    form = AdminWardForm()
    
    if form.validate_on_submit():
        if Ward.query.filter_by(ward_code=form.ward_code.data).first():
            flash("Ward code already in use.", "danger")
            return render_template("admin/ward_form.html", form=form, action="Create")
            
        ward = Ward(
            ward_name=form.ward_name.data,
            ward_code=form.ward_code.data,
            assigned_officer_id=form.assigned_officer_id.data,
            is_active=form.is_active.data
        )
        try:
            db.session.add(ward)
            db.session.flush()
            log_activity("Ward Created", current_user, details=f"Created ward {ward.ward_code}.")
            db.session.commit()
            flash("Ward created successfully.", "success")
            return redirect(url_for("admin.manage_wards"))
        except SQLAlchemyError:
            db.session.rollback()
            flash("An error occurred while creating the ward.", "danger")
            
    return render_template("admin/ward_form.html", form=form, action="Create")


@admin_bp.route("/wards/<int:ward_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_ward(ward_id):
    ward = get_or_404(Ward, ward_id)
    form = AdminWardForm(obj=ward)
    
    if form.validate_on_submit():
        existing_ward = Ward.query.filter(Ward.ward_code == form.ward_code.data, Ward.ward_id != ward.ward_id).first()
        if existing_ward:
            flash("Ward code already in use by another ward.", "danger")
            return render_template("admin/ward_form.html", form=form, action="Edit")
            
        ward.ward_name = form.ward_name.data
        ward.ward_code = form.ward_code.data
        ward.assigned_officer_id = form.assigned_officer_id.data
        ward.is_active = form.is_active.data
        
        try:
            log_activity("Ward Updated", current_user, details=f"Updated ward {ward.ward_code}.")
            db.session.commit()
            flash("Ward updated successfully.", "success")
            return redirect(url_for("admin.manage_wards"))
        except SQLAlchemyError:
            db.session.rollback()
            flash("An error occurred while updating the ward.", "danger")
            
    return render_template("admin/ward_form.html", form=form, action="Edit")


@admin_bp.route("/wards/<int:ward_id>/toggle-status", methods=["POST"])
@admin_required
def toggle_ward_status(ward_id):
    ward = get_or_404(Ward, ward_id)
    ward.is_active = not ward.is_active
    action = "Activated" if ward.is_active else "Deactivated"
    try:
        log_activity(f"Ward {action}", current_user, details=f"Ward {ward.ward_code} was {action.lower()}.")
        db.session.commit()
        flash(f"Ward {ward.ward_name} has been {action.lower()}.", "success")
    except SQLAlchemyError:
        db.session.rollback()
        flash("An error occurred while updating the ward status.", "danger")
        
    return redirect(url_for("admin.manage_wards"))


@admin_bp.route("/complaints", methods=["GET"])
@admin_required
def manage_complaints():
    form = AdminComplaintFilterForm(request.args)
    query = Complaint.query
    
    if form.search_term.data:
        search = f"%{form.search_term.data}%"
        query = query.filter((Complaint.complaint_number.ilike(search)) | (Complaint.title.ilike(search)))
        
    if form.status.data:
        query = query.filter(Complaint.status == form.status.data)
        
    if form.priority.data:
        query = query.filter(Complaint.priority == form.priority.data)
        
    if form.category_id.data:
        query = query.filter(Complaint.category_id == form.category_id.data)
        
    if form.ward_id.data:
        query = query.filter(Complaint.ward_id == form.ward_id.data)
        
    if form.officer_id.data is not None:
        if form.officer_id.data == -1:
            query = query.filter(Complaint.assigned_officer_id.is_(None))
        else:
            query = query.filter(Complaint.assigned_officer_id == form.officer_id.data)
        
    page = request.args.get("page", 1, type=int)
    complaints = (
        query.options(
            db.joinedload(Complaint.category),
            db.joinedload(Complaint.ward),
            db.joinedload(Complaint.assigned_officer),
            db.joinedload(Complaint.citizen),
        )
        .order_by(Complaint.submitted_at.desc())
        .paginate(page=page, per_page=COMPLAINTS_PER_PAGE, error_out=False)
    )
    
    return render_template("admin/complaints.html", complaints=complaints, form=form)


@admin_bp.route("/complaints/<int:complaint_id>", methods=["GET"])
@admin_required
def view_complaint(complaint_id):
    complaint = (
        Complaint.query.filter(Complaint.complaint_id == complaint_id)
        .options(
            db.joinedload(Complaint.category),
            db.joinedload(Complaint.ward),
            db.joinedload(Complaint.assigned_officer),
            db.joinedload(Complaint.citizen),
        )
        .first_or_404()
    )
    assign_form = AdminComplaintAssignForm(obj=complaint)
    return render_template("admin/complaint_detail.html", complaint=complaint, assign_form=assign_form)


@admin_bp.route("/complaints/<int:complaint_id>/assign", methods=["POST"])
@admin_required
def assign_complaint(complaint_id):
    complaint = get_or_404(Complaint, complaint_id)
    form = AdminComplaintAssignForm()
    
    if form.validate_on_submit():
        old_officer_id = complaint.assigned_officer_id
        new_officer_id = form.assigned_officer_id.data
        
        if old_officer_id != new_officer_id:
            if new_officer_id:
                officer = db.session.get(User, new_officer_id)
                if not officer or not officer.is_officer or not officer.is_active:
                    flash("Selected officer is not available.", "danger")
                    return redirect(url_for("admin.view_complaint", complaint_id=complaint.complaint_id))
                    
            complaint.assigned_officer_id = new_officer_id
            
            if new_officer_id:
                if complaint.status == Complaint.STATUS_SUBMITTED:
                    complaint.status = Complaint.STATUS_ASSIGNED
                complaint.assigned_at = datetime.now(timezone.utc)
                
                update = ComplaintUpdate(
                    complaint_id=complaint.complaint_id,
                    status=complaint.status,
                    action="Assigned to Officer",
                    remarks=f"Complaint assigned to officer by Admin."
                )
                db.session.add(update)
                
                try:
                    create_complaint_assigned_notification(complaint, new_officer_id)
                except Exception as e:
                    app.logger.error(f"Notification creation failed during complaint assignment: {e}")
            else:
                update = ComplaintUpdate(
                    complaint_id=complaint.complaint_id,
                    status=complaint.status,
                    action="Unassigned",
                    remarks="Complaint unassigned by Admin."
                )
                db.session.add(update)
                
            try:
                log_activity("Complaint Assigned", current_user, details=f"Assigned complaint {complaint.complaint_number} to officer {new_officer_id}.")
            except Exception as e:
                app.logger.error(f"Activity logging failed during complaint assignment: {e}")
            try:
                db.session.commit()
                flash("Complaint assigned successfully.", "success")
            except SQLAlchemyError as exc:
                db.session.rollback()
                app.logger.error(f"Complaint assignment failed: {exc}")
                flash("An error occurred while assigning the complaint.", "danger")
                
    return redirect(url_for("admin.view_complaint", complaint_id=complaint.complaint_id))


@admin_bp.route("/complaints/<int:complaint_id>/close", methods=["POST"])
@admin_required
def close_complaint(complaint_id):
    complaint = get_or_404(Complaint, complaint_id)
    
    if complaint.status == Complaint.STATUS_CLOSED:
        flash("Complaint is already closed.", "info")
        return redirect(url_for("admin.view_complaint", complaint_id=complaint.complaint_id))
        
    if complaint.status != Complaint.STATUS_RESOLVED:
        flash("Only resolved complaints can be closed.", "warning")
        return redirect(url_for("admin.view_complaint", complaint_id=complaint.complaint_id))
        
    complaint.status = Complaint.STATUS_CLOSED
    complaint.closed_at = datetime.now(timezone.utc)
    
    update = ComplaintUpdate(
        complaint_id=complaint.complaint_id,
        status=Complaint.STATUS_CLOSED,
        action="Closed by Admin",
        remarks="Complaint closed administratively."
    )
    db.session.add(update)
    
    try:
        create_complaint_closed_notification(complaint, complaint.citizen_id)
    except Exception as e:
        app.logger.error(f"Notification creation failed during complaint closure: {e}")
    
    try:
        log_activity("Complaint Closed", current_user, details=f"Administratively closed complaint {complaint.complaint_number}.")
    except Exception as e:
        app.logger.error(f"Activity logging failed during complaint closure: {e}")
    
    try:
        db.session.commit()
        flash("Complaint closed successfully.", "success")
    except SQLAlchemyError as exc:
        db.session.rollback()
        app.logger.error(f"Complaint closure failed: {exc}")
        flash("An error occurred while closing the complaint.", "danger")
        
    return redirect(url_for("admin.view_complaint", complaint_id=complaint.complaint_id))


@admin_bp.route("/settings", methods=["GET", "POST"])
@admin_required
def manage_settings():
    form = AdminSystemSettingsForm()
    
    if request.method == "GET":
        urgent_days = SystemSetting.query.filter_by(setting_key="urgent_escalation_days").first()
        critical_days = SystemSetting.query.filter_by(setting_key="critical_escalation_days").first()
        max_upload = SystemSetting.query.filter_by(setting_key="max_upload_size_mb").first()
        
        if urgent_days:
            form.urgent_escalation_days.data = urgent_days.typed_value
        if critical_days:
            form.critical_escalation_days.data = critical_days.typed_value
        if max_upload:
            form.max_upload_size_mb.data = max_upload.typed_value
            
    if form.validate_on_submit():
        settings = {
            "urgent_escalation_days": str(form.urgent_escalation_days.data),
            "critical_escalation_days": str(form.critical_escalation_days.data),
            "max_upload_size_mb": str(form.max_upload_size_mb.data)
        }
        
        for key, value in settings.items():
            setting = SystemSetting.query.filter_by(setting_key=key).first()
            if setting:
                setting.setting_value = value
            else:
                setting = SystemSetting(setting_key=key, setting_value=value, setting_type=SystemSetting.TYPE_INTEGER)
                db.session.add(setting)
                
        try:
            log_activity("Settings Updated", current_user, details="System settings updated.")
            db.session.commit()
            flash("System settings updated successfully.", "success")
            return redirect(url_for("admin.manage_settings"))
        except SQLAlchemyError:
            db.session.rollback()
            flash("An error occurred while updating settings.", "danger")
            
    return render_template("admin/settings.html", form=form)


@admin_bp.route("/activity-logs", methods=["GET"])
@admin_required
def activity_logs():
    form = AdminActivityLogFilterForm(request.args)
    query = ActivityLog.query
    
    if form.user_id.data:
        query = query.filter(ActivityLog.user_id == form.user_id.data)
        
    if form.action.data:
        search = f"%{form.action.data}%"
        query = query.filter(ActivityLog.action.ilike(search))
        
    if form.date.data:
        query = query.filter(func.date(ActivityLog.created_at) == form.date.data)
        
    page = request.args.get("page", 1, type=int)
    logs = (
        query.options(db.joinedload(ActivityLog.user))
        .order_by(ActivityLog.created_at.desc())
        .paginate(page=page, per_page=ACTIVITY_LOGS_PER_PAGE, error_out=False)
    )
    
    return render_template("admin/activity_logs.html", logs=logs, form=form)
