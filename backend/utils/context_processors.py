from flask import url_for
from flask_login import current_user


def register_context_processors(app):
    @app.context_processor
    def inject_navigation_context():
        dashboard_url = None
        if current_user.is_authenticated:
            role_dashboard_routes = {
                "Citizen": "citizen.dashboard",
                "Officer": "officer.dashboard",
                "Admin": "admin.dashboard",
            }
            route_name = role_dashboard_routes.get(current_user.role)
            if route_name:
                dashboard_url = url_for(route_name)

        return {"role_dashboard_url": dashboard_url}
