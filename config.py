from flask_sqlalchemy import SQLAlchemy
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

sqlite_db_path = f"sqlite:///{os.path.join(current_dir, 'database.db')}"

db = SQLAlchemy()
