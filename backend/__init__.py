from pathlib import Path

from flask import Flask, render_template

from backend.config import Config
from backend.extensions import csrf, db, limiter, login_manager, migrate


def create_app(config_name=None):
    app = Flask(
        __name__,
        static_folder="static",
        template_folder="templates",
    )
    load_config(app, config_name)

    init_extensions(app)
    register_blueprints(app)
    register_context_processors(app)
    register_jinja_filters(app)
    register_cli_commands(app)
    register_error_handlers(app)
    configure_session_security(app)
    ensure_upload_directories(app)
    register_temporary_routes(app)

    @app.after_request
    def add_header(response):
        # Prevent browser back-button form data retention (bfcache/history)
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "-1"
        return response

    return app


def load_config(app, config_name=None):
    if config_name is None:
        app.config.from_object(Config)
        return

    if isinstance(config_name, str):
        app.config.from_object(Config)
        app.config["ENV"] = config_name
        return

    app.config.from_object(config_name)


def init_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)


def register_context_processors(app):
    from backend.utils.context_processors import register_context_processors as register_processors

    register_processors(app)


def register_jinja_filters(app):
    from backend.utils.datetime_utils import register_datetime_filters
    
    register_datetime_filters(app)


def register_blueprints(app):
    import importlib
    import logging

    blueprint_specs = (
        ("auth_routes", "auth_bp"),
        ("citizen_routes", "citizen_bp"),
        ("officer_routes", "officer_bp"),
        ("admin_routes", "admin_bp"),
        ("report_routes", "report_bp"),
    )

    for module_name, blueprint_name in blueprint_specs:
        try:
            module = importlib.import_module(f"backend.routes.{module_name}")
            blueprint = getattr(module, blueprint_name)
        except ImportError:
            logging.warning(
                "Blueprint %s not found, skipping registration.",
                module_name,
            )
            continue

        app.register_blueprint(blueprint)


def register_cli_commands(app):
    from backend.cli import register_cli_commands as register_commands

    register_commands(app)


def register_error_handlers(app):
    @app.errorhandler(403)
    def forbidden(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(error):
        return render_template("errors/500.html"), 500

    @app.errorhandler(400)
    def bad_request(error):
        return render_template("errors/400.html"), 400


def configure_session_security(app):
    app.config.setdefault("SESSION_COOKIE_HTTPONLY", True)
    app.config.setdefault("SESSION_COOKIE_SAMESITE", "Lax")

    if not app.config.get("DEBUG"):
        app.config.setdefault("SESSION_COOKIE_SECURE", True)


def ensure_upload_directories(app):
    upload_paths = (
        app.config["UPLOAD_FOLDER"],
        Path(app.config["UPLOAD_FOLDER"]) / "complaints",
        app.config["COMPLAINT_BEFORE_UPLOAD_FOLDER"],
        app.config["COMPLAINT_AFTER_UPLOAD_FOLDER"],
    )

    for upload_path in upload_paths:
        Path(upload_path).mkdir(parents=True, exist_ok=True)


def register_temporary_routes(app):
    if "index" in app.view_functions:
        return

    @app.get("/")
    def index():
        return render_template("index.html")
