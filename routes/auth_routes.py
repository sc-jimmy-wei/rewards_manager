from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from controllers.auth_controller import AuthController

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Login page and authentication."""
    # Redirect if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for("credit_card.index"))

    if request.method == "POST":
        # Validate form data
        errors = AuthController.validate_login_form(request.form)

        if not errors:
            # Attempt login
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")
            remember = bool(request.form.get("remember"))

            success, user, message = AuthController.login_user_by_credentials(
                username, password, remember
            )

            if success:
                flash(message, "success")
                # Redirect to next page or default to home
                next_page = request.args.get("next")
                if next_page and next_page.startswith("/"):
                    return redirect(next_page)
                return redirect(url_for("credit_card.index"))
            else:
                flash(message, "error")
        else:
            for error in errors:
                flash(error, "error")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    """Logout current user."""
    message = AuthController.logout_current_user()
    flash(message, "success")
    return redirect(url_for("auth.login"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Registration page for new users."""
    # Redirect if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for("credit_card.index"))

    if request.method == "POST":
        # Validate form data
        errors = AuthController.validate_registration_form(request.form)

        if not errors:
            # Attempt registration
            username = request.form.get("username", "").strip()
            email = request.form.get("email", "").strip()
            password = request.form.get("password", "")
            first_name = request.form.get("first_name", "").strip() or None
            last_name = request.form.get("last_name", "").strip() or None

            success, user, message = AuthController.register_user(
                username, email, password, first_name, last_name
            )

            if success:
                flash(message, "success")
                return redirect(url_for("auth.login"))
            else:
                flash(message, "error")
        else:
            for error in errors:
                flash(error, "error")

    return render_template("auth/register.html")


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    """Forgot password page to request reset."""
    # Redirect if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for("credit_card.index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()

        if not email:
            flash("Email address is required", "error")
        else:
            success, message = AuthController.generate_password_reset_token(email)

            if success:
                flash(message, "success")
                # In a real app, we'd redirect to a "check your email" page
                # For demo purposes, we show the token directly
            else:
                flash(message, "error")

    return render_template("auth/forgot_password.html")


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    """Reset password with valid token."""
    # Redirect if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for("credit_card.index"))

    if request.method == "POST":
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # Validate passwords
        if not password:
            flash("Password is required", "error")
        elif len(password) < 6:
            flash("Password must be at least 6 characters long", "error")
        elif password != confirm_password:
            flash("Passwords do not match", "error")
        else:
            success, message = AuthController.reset_password_with_token(token, password)

            if success:
                flash(message, "success")
                return redirect(url_for("auth.login"))
            else:
                flash(message, "error")

    return render_template("auth/reset_password.html", token=token)


@auth_bp.route("/profile")
@login_required
def profile():
    """User profile page."""
    from controllers.credit_card_controller import CreditCardController
    from controllers.airline_program_controller import AirlineProgramController
    from datetime import date

    # Get user statistics
    credit_cards = CreditCardController.get_all_cards(user_id=current_user.id)
    airline_programs = AirlineProgramController.get_all_programs(
        user_id=current_user.id
    )

    # Calculate days since joined
    days_since_joined = 0
    if current_user.created_at:
        days_since_joined = (date.today() - current_user.created_at.date()).days

    return render_template(
        "auth/profile.html",
        user=current_user,
        credit_card_count=len(credit_cards),
        airline_program_count=len(airline_programs),
        days_since_joined=days_since_joined,
    )
