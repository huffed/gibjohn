from config import db
from flask_login import UserMixin


class Courses(db.Model, UserMixin):
    __tablename__ = "courses"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15), nullable=False, unique=True)
    # FontAwesome Icon Name
    icon = db.Column(db.String(30), nullable=False, default="graduation-cap")
    # FontAwesome Icon Type (solid, regular, brands etc.)
    icon_type = db.Column(db.String(10), nullable=False, default="solid")
