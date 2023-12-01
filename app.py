from forms.user_forms import RegisterForm, LoginForm
from models.user import User
from flask import render_template, url_for, redirect, request
from sqlalchemy import text
from flask_login import login_user, login_required, current_user, logout_user
from config import create_app
from extensions import argon2

app, db, login_manager, limiter, logger = create_app()


@login_manager.user_loader
def load_user(user_id):
    query = text(
        "SELECT uid, username, password FROM users WHERE uid = :user_id")
    result = db.session.execute(query, {"user_id": user_id}).fetchone()

    if result:
        uid, username, password = result
        return User(uid=uid, username=username, password=password)


@app.context_processor
def context_processor():
    return dict(user=current_user, active_page=request.path)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = argon2.generate_password_hash(form.password.data)
        query = text(
            "INSERT INTO users (username, password) VALUES (:username, :password)")
        try:
            db.session.execute(
                query, {"username": form.username.data, "password": hashed_password})
            db.session.commit()
            return redirect(url_for('login'))
        except Exception as error:
            db.session.rollback()
            raise error

    return render_template("register-login.html", form=form, form_type=request.path.strip("/"))


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
            return render_template("register-login.html", form=form, form_type=request.path.strip("/"))

    return render_template("register-login.html", form=form, form_type=request.path.strip("/"))


@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/courses')
@login_required
def courses():
    pass


@app.route('/tutors')
def tutors():
    pass


@app.route("/profile/<username>")
@login_required
@limiter.limit("200 per hour")
def user_profile(username):
    query = text("SELECT uid, username FROM users WHERE username = :username")
    user = db.session.execute(query, {"username": username}).fetchone()

    if user:
        return render_template("user-profile.html")
    else:
        raise Exception("User not found")


@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    return render_template("dashboard.html")


@app.errorhandler(Exception)
def handle_exception(error):
    error_message = "Looks like you found a bug."
    try:
        return render_template('error.html', error_code=error.code, error_message=error_message), error.code
    except:
        return render_template('error.html', error_code=500, error_message=error_message), "500"


@app.errorhandler(404)
def handle_exception(error):
    error_message = "Page not found."
    return render_template('error.html', error_code=error.code, error_message=error_message), error.code


@app.errorhandler(429)
def ratelimit_error(e):
    return "Rate limit exceeded. Please try again later.", 429


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
