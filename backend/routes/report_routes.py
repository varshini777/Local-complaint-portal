from flask import Blueprint, render_template, Response
from backend.routes.auth_routes import admin_required
from backend.services.report_service import (
    get_dashboard_metrics,
    get_category_analytics,
    get_ward_analytics,
    get_officer_performance,
    get_escalation_analytics,
    get_monthly_trends,
    get_feedback_analytics,
    get_complaint_aging_analytics,
    export_complaints_csv,
    export_officer_performance_csv,
    export_feedback_csv
)

report_bp = Blueprint("reports", __name__, url_prefix="/admin/reports")

@report_bp.route("/")
@admin_required
def reports_dashboard():
    dashboard_metrics = get_dashboard_metrics()
    category_analytics = get_category_analytics()
    ward_analytics = get_ward_analytics()
    officer_performance = get_officer_performance()
    escalation_analytics = get_escalation_analytics()
    monthly_trends = get_monthly_trends()
    feedback_analytics = get_feedback_analytics()
    complaint_aging = get_complaint_aging_analytics()
    
    return render_template(
        "admin/reports/dashboard.html",
        dashboard_metrics=dashboard_metrics,
        category_analytics=category_analytics,
        ward_analytics=ward_analytics,
        officer_performance=officer_performance,
        escalation_analytics=escalation_analytics,
        monthly_trends=monthly_trends,
        feedback_analytics=feedback_analytics,
        complaint_aging=complaint_aging
    )

@report_bp.route("/export/complaints")
@admin_required
def export_complaints():
    generator = export_complaints_csv()
    return Response(
        generator,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=complaints_report.csv"}
    )

@report_bp.route("/export/officers")
@admin_required
def export_officers():
    generator = export_officer_performance_csv()
    return Response(
        generator,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=officer_performance.csv"}
    )

@report_bp.route("/export/feedback")
@admin_required
def export_feedback():
    generator = export_feedback_csv()
    return Response(
        generator,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=feedback_report.csv"}
    )
