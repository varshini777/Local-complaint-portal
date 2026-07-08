import sys

with open('d:/Local_complaint/backend/routes/citizen_routes.py', 'r', encoding='utf-8') as f:
    content = f.read()

refile_route = """
from flask import abort

@citizen_bp.route("/complaints/<int:complaint_id>/refile", methods=["GET", "POST"])
@citizen_required
def refile_complaint(complaint_id):
    original_complaint = Complaint.query.filter_by(
        complaint_id=complaint_id,
        is_active=True
    ).first_or_404()

    if original_complaint.citizen_id != current_user.user_id:
        abort(403)

    form = ComplaintForm()
    populate_complaint_form_choices(form)

    if request.method == "GET":
        form.title.data = original_complaint.title
        form.description.data = original_complaint.description
        form.category.data = original_complaint.category_id
        form.ward.data = original_complaint.ward_id
        form.priority.data = original_complaint.priority
        form.location.data = original_complaint.location

    if form.validate_on_submit():
        try:
            before_image_path = save_before_image(form.before_image.data)
            new_complaint = Complaint(
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
            db.session.add(new_complaint)
            db.session.flush()

            db.session.add(
                ComplaintUpdate(
                    complaint_id=new_complaint.complaint_id,
                    updated_by=current_user.user_id,
                    status=Complaint.STATUS_SUBMITTED,
                    action="Complaint Submitted",
                    remarks="Complaint re-submitted by citizen.",
                )
            )
            try:
                create_complaint_submitted_notification(new_complaint, current_user.user_id)
            except Exception as e:
                app.logger.error(f"Notification creation failed during complaint re-submission: {e}")
            try:
                log_citizen_activity(
                    "Complaint Re-submission",
                    f"Complaint {new_complaint.complaint_number} re-submitted.",
                )
            except Exception as e:
                app.logger.error(f"Activity logging failed during complaint re-submission: {e}")
            db.session.commit()
            flash("Complaint successfully re-submitted with a new complaint number.", "success")
            return redirect(
                url_for("citizen.complaint_detail", complaint_id=new_complaint.complaint_id)
            )
        except (SQLAlchemyError, ValueError) as exc:
            db.session.rollback()
            app.logger.error(f"Complaint re-submission failed: {exc}")
            flash(str(exc) if isinstance(exc, ValueError) else "Complaint re-submission failed.", "danger")

    return render_template(
        "citizen/submit_complaint.html",
        form=form,
        complaint_date=datetime.utcnow(),
        is_refile=True
    )
"""

if "def refile_complaint" not in content:
    target = '@citizen_bp.route("/complaints")'
    if target in content:
        content = content.replace(target, refile_route + '\n\n' + target)
        with open('d:/Local_complaint/backend/routes/citizen_routes.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print("Successfully added refile_complaint route.")
    else:
        print("Could not find target route.")
else:
    print("Route already exists.")
