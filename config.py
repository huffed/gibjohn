from extensions import argon2
from flask_less import lessc
from flask_limiter import Limiter
from flask import Flask, request
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
import logging
from logging.handlers import RotatingFileHandler
import os
from flask_wtf.csrf import CSRFProtect

current_dir = os.path.dirname(os.path.abspath(__file__))

sqlite_db_path = f"sqlite:///{os.path.join(current_dir, 'database.db')}"

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = sqlite_db_path
    app.config["SECRET_KEY"] = "gibjohn123"
    csrf = CSRFProtect(app)

    argon2.init_app(app)
    lessc(app)
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "login"
    login_manager.login_message = "Please log in to access this page."

    limiter = Limiter(
        app=app, key_func=lambda: request.remote_addr, storage_uri="memory://")

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    app.logger.handlers.clear()
    file_handler = RotatingFileHandler(
        'error.log', maxBytes=1024 * 1024 * 10, backupCount=10)
    file_handler.setLevel(logging.ERROR)
    formatter = logging.Formatter(
        '\n%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return app, db, login_manager, limiter, logger
