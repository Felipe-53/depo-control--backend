from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_bcrypt import Bcrypt
from .error_handling import register_error_handlers
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

# initialize extensions
db = SQLAlchemy()
socketio = SocketIO()
bcrypt = Bcrypt()


def create_app():
    sentry_sdk.init(
        dsn="https://467f0b38ee74402a8fd88e61cb551631@o467829.ingest.sentry.io/5494810",
        integrations=[FlaskIntegration()],
        traces_sample_rate=1.0
    )

    app = Flask(__name__)
    app.config.from_object('config.ProdConfig')

    # Register extensions
    db.init_app(app)
    socketio.init_app(app)
    bcrypt.init_app(app)

    # Register Error Handlers
    register_error_handlers(app)

    # Register sockeio handlers
    from .api.connections.connections import register_socketio_handlers
    register_socketio_handlers(socketio)

    # Register blueprints
    from depo_control.api.login import login
    app.register_blueprint(login.bp)

    from depo_control.api.main import movs
    app.register_blueprint(movs.bp)

    from depo_control.api.main import main_get_endpoints
    app.register_blueprint(main_get_endpoints.bp)

    from depo_control.api.admin import admin_get_endpoints
    app.register_blueprint(admin_get_endpoints.bp)

    from depo_control.api.admin import admin_post_endpoints
    app.register_blueprint(admin_post_endpoints.bp)

    return app
