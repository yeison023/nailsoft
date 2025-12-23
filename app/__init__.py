from flask import Flask
from .config import Config
from .extensions import db, login_manager
from app.models.user import User
from app.models.enums import RoleEnum

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    from .routes import auth, public, admin, client, manicurist
    app.register_blueprint(auth.auth_bp)
    app.register_blueprint(public.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(client.bp)
    app.register_blueprint(manicurist.bp)

    @app.context_processor
    def inject_enums():
        return dict(RoleEnum=RoleEnum)
    
    @app.template_filter('currency')
    def currency(value):
        return f"${value:,.0f}".replace(",", ".")

    return app