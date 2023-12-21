from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError, EqualTo
from models.user import User
from extensions import argon2
from config import db
from sqlalchemy import text


class CourseSearch(FlaskForm):
    course = StringField(validators=[InputRequired()])

    def validate_course(self, course):
        query = text("SELECT * FROM courses WHERE course = :course")
        existing_course = db.session.execute(
            query, {"course": course.data}).fetchone()

        if existing_course is None:
            raise ValidationError("Course does not exist.")

    submit = SubmitField(render_kw={"value": "Search"})
