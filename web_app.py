from flask import Flask

from app.utils.config import load_env
from app.web.routes import web_bp
from app.db.database import initialize_database


def create_app() -> Flask:
    load_env()
    initialize_database()

    app = Flask(__name__)
    app.register_blueprint(web_bp)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)