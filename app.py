from forms.user_forms import RegisterForm, LoginForm
from models.user import User
from flask import Flask, render_template, url_for, redirect, request
from sqlalchemy import text
from flask_login import login_user, LoginManager, login_required, current_user, logout_user
from config import db, sqlite_db_path
from extensions import argon2
from flask_limiter import Limiter

app = Flask(__name__)
argon2.init_app(app)
app.config["SQLALCHEMY_DATABASE_URI"] = sqlite_db_path
app.config["SECRET_KEY"] = "havoc3141"  # dont actually know what this does tbh

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

limiter = Limiter(
    app=app,
    key_func=lambda: request.remote_addr,
    storage_uri="memory://"
)


@login_manager.user_loader
def load_user(user_id):
    query = text(
        "SELECT uid, username, password FROM users WHERE uid = :user_id")
    result = db.session.execute(query, {"user_id": user_id}).fetchone()

    if result:
        uid, username, password = result
        return User(uid=uid, username=username, password=password)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        query = text("SELECT * FROM users WHERE username = :username")
        user = db.session.execute(
            query, {"username": form.username.data}).fetchone()

        if user and argon2.check_password_hash(user.password, form.password.data):
            login_user(User(uid=user.uid, username=user.username,
                       password=user.password))
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", form=form)

    return render_template("login.html", form=form)


@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = argon2.generate_password_hash(form.password.data)
        query = text(
            "INSERT INTO users (username, password) VALUES (:username, :password)")
        db.session.execute(
            query, {"username": form.username.data, "password": hashed_password})
        db.session.commit()
        return redirect(url_for('login'))

    return render_template("register.html", form=form)


@app.route("/@<username>")
@login_required
@limiter.limit("200 per hour")
def user_profile(username):
    query = text("SELECT uid, username FROM users WHERE username = :username")
    user = db.session.execute(query, {"username": username}).fetchone()

    if user:
        return render_template("user-profile.html", user=User(uid=user.uid, username=user.username), username=user.username, uid=user.uid)
    else:
        raise Exception("User not found")


@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    return render_template("dashboard.html", user=current_user, username=current_user.username, uid=current_user.uid)


@app.errorhandler(429)
def ratelimit_error(e):
    return "Rate limit exceeded. Please try again later.", 429


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
