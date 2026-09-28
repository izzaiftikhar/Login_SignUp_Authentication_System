from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.utils.security import hash_password, verify_password

from app.extensions import db
from app.models.user import User


auth_bp = Blueprint("auth", __name__)

# Home
@auth_bp.route("/")
def home():
    return redirect(url_for("auth.signup"))

# Signup
@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        # Check if all fields are filled
        if not username or not email or not password:
            flash("All fields are required.")
            return redirect(url_for("auth.signup"))

        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("Email already registered.")
            return redirect(url_for("auth.signup"))

        # Hash password
        password_hash = hash_password(password)

        # Create user
        new_user = User(
            username=username,
            email=email,
            password_hash=password_hash
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Account created successfully. Please log in.")
        return redirect(url_for("auth.login"))

    return render_template("signup.html")


# Login
@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        # Check if fields are filled
        if not email or not password:
            flash("Email and password are required.")
            return redirect(url_for("auth.login"))

        # Find user by email
        user = User.query.filter_by(email=email).first()

        # Check user and password
        if user and verify_password(password, user.password_hash):

            session["user_id"] = user.id
            session["username"] = user.username

            flash("Login successful.")
            return redirect(url_for("auth.dashboard"))

        flash("Invalid email or password.")
        return redirect(url_for("auth.login"))

    return render_template("login.html")


# Dashboard
@auth_bp.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        flash("Please log in first.")
        return redirect(url_for("auth.login"))

    return render_template(
        "dashboard.html",
        username=session.get("username")
    )


# Logout
@auth_bp.route("/logout")
def logout():

    session.clear()

    flash("You have been logged out.")
    return redirect(url_for("auth.login"))

