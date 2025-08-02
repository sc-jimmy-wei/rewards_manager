from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    jsonify,
    flash,
    abort,
)
from flask_login import current_user
from datetime import date

from controllers import CreditCardController, FileController, ValidationController
from utils.decorators import user_required
from utils.card_image_helper import get_card_image_from_template

# Create blueprint
credit_card_bp = Blueprint("credit_card", __name__)


@credit_card_bp.route("/")
@user_required
def index():
    """Display credit cards with optional filtering."""
    # Get filter parameters (match template parameter names)
    bank_filter = request.args.get("bank", "")
    card_type_filter = request.args.get("card_type", "")
    search_query = request.args.get("search", "")
    admin_view = request.args.get("admin_view") == "true" and current_user.is_admin()

    # Get filtered cards for current user or admin view
    cards = CreditCardController.filter_cards(
        bank_filter, card_type_filter, search_query, admin_view=admin_view
    )

    # Enrich cards with image URLs from benefit templates
    for card in cards:
        if not card.image_filename:  # Only add if no user-uploaded image
            card.template_image_url = get_card_image_from_template(card.bank, card.name)

    # Get filter options for dropdowns
    banks, card_types = CreditCardController.get_filter_options(admin_view=admin_view)

    return render_template(
        "index.html",
        cards=cards,
        banks=banks,
        card_types=card_types,
        current_filters={
            "bank": bank_filter,
            "card_type": card_type_filter,
            "search": search_query,
        },
    )


@credit_card_bp.route("/card/<int:card_id>")
@user_required
def card_detail(card_id):
    """Display card details."""
    card = CreditCardController.get_card_by_id(card_id)

    if not card:
        abort(404)
    
    # Add template image URL if no user-uploaded image
    if not card.image_filename:
        card.template_image_url = get_card_image_from_template(card.bank, card.name)
    
    credit_benefits = card.get_credit_benefits()
    reward_benefits = card.get_reward_benefits()
    usage = card.get_benefits_usage()

    # Calculate usage statistics for credit benefits only
    credit_usage_count = sum(
        1 for benefit in credit_benefits if usage.get(benefit["name"])
    )
    credit_total = len(credit_benefits)
    credit_percentage = (
        round((credit_usage_count / credit_total * 100)) if credit_total > 0 else 0
    )

    return render_template(
        "card_detail.html",
        card=card,
        credit_benefits=credit_benefits,
        reward_benefits=reward_benefits,
        usage=usage,
        credit_usage_count=credit_usage_count,
        credit_percentage=credit_percentage,
    )


@credit_card_bp.route("/add_card", methods=["GET", "POST"])
@user_required
def add_card():
    """Add a new credit card."""
    if request.method == "POST":
        # Validate form data
        errors = ValidationController.validate_card_form(request.form)

        if errors:
            # Return to form with errors and preserve form data
            for error in errors:
                flash(error, "error")
            return render_template("add_card.html", form_data=request.form)

        # Handle image upload
        image_filename = None
        if "image" in request.files:
            file = request.files["image"]
            if file.filename != "":
                image_filename = FileController.save_uploaded_file(file)

        # Create new card
        try:
            new_card = CreditCardController.create_card(request.form, image_filename)
            flash(f"Credit card '{new_card.name}' added successfully!", "success")
            return redirect(url_for("credit_card.card_detail", card_id=new_card.id))
        except Exception as e:
            flash(f"Error creating card: {str(e)}", "error")
            return render_template("add_card.html", form_data=request.form)

    # Set default opening date to today
    today = date.today().strftime("%Y-%m-%d")
    return render_template("add_card.html", default_date=today)


@credit_card_bp.route("/edit_card/<int:card_id>", methods=["GET", "POST"])
@user_required
def edit_card(card_id):
    """Edit an existing credit card."""
    card = CreditCardController.get_card_by_id(card_id)

    if not card:
        abort(404)

    if request.method == "POST":
        # Validate form data
        errors = ValidationController.validate_card_form(request.form)

        if errors:
            # Return to form with errors and preserve form data
            for error in errors:
                flash(error, "error")
            return render_template(
                "edit_card.html",
                card=card,
                benefits=card.get_benefits_list(),
                form_data=request.form,
            )

        # Handle image upload
        new_image_filename = None
        if "image" in request.files:
            file = request.files["image"]
            if file.filename != "":
                new_image_filename = FileController.save_uploaded_file(file)

        try:
            # Update card and get old image filename for cleanup
            old_image_filename = CreditCardController.update_card(
                card, request.form, new_image_filename
            )

            # Clean up old image if a new one was uploaded
            if old_image_filename and new_image_filename:
                FileController.delete_file(old_image_filename)

            flash("Credit card updated successfully!", "success")
            return redirect(url_for("credit_card.card_detail", card_id=card.id))
        except Exception as e:
            flash(f"Error updating card: {str(e)}", "error")
            return render_template(
                "edit_card.html",
                card=card,
                benefits=card.get_benefits_list(),
                form_data=request.form,
            )

    return render_template(
        "edit_card.html", card=card, benefits=card.get_benefits_list()
    )


@credit_card_bp.route("/delete_card/<int:card_id>", methods=["POST"])
@user_required
def delete_card(card_id):
    """Delete a credit card."""
    card = CreditCardController.get_card_by_id(card_id)

    if not card:
        abort(404)

    try:
        # Delete card and get image filename for cleanup
        image_filename = CreditCardController.delete_card(card)

        # Clean up associated image file
        if image_filename:
            FileController.delete_file(image_filename)

        flash("Credit card deleted successfully!", "success")
    except Exception as e:
        flash(f"Error deleting card: {str(e)}", "error")

    return redirect(url_for("credit_card.index"))


@credit_card_bp.route("/benefits_usage/<int:card_id>", methods=["GET", "POST"])
@user_required
def benefits_usage(card_id):
    """Display benefits usage page for a card or update usage."""
    card = CreditCardController.get_card_by_id(card_id)

    if not card:
        abort(404)

    if request.method == "POST":
        # Handle benefits usage update
        usage_data = {}
        for key, value in request.form.items():
            try:
                usage_data[key] = int(value)
            except ValueError:
                usage_data[key] = 0

        try:
            CreditCardController.update_benefits_usage(card, usage_data)
            flash("Benefits usage updated successfully!", "success")
        except Exception as e:
            flash(f"Error updating benefits usage: {str(e)}", "error")

        return redirect(url_for("credit_card.benefits_usage", card_id=card_id))

    # GET request - display the page
    benefits = card.get_benefits_list()
    usage = card.get_benefits_usage()
    return render_template(
        "benefits_usage.html", card=card, benefits=benefits, usage=usage
    )


@credit_card_bp.route("/update_benefits_usage/<int:card_id>", methods=["POST"])
@user_required
def update_benefits_usage(card_id):
    """Update benefits usage for a card."""
    card = CreditCardController.get_card_by_id(card_id)

    if not card:
        abort(404)
    usage_data = request.get_json()

    try:
        CreditCardController.update_benefits_usage(card, usage_data)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@credit_card_bp.route("/generate_test_data", methods=["POST"])
@user_required
def generate_test_data():
    """Generate and add test credit card data for testing purposes."""
    try:
        test_card = CreditCardController.generate_test_card()
        flash(
            f'Test card "{test_card.bank} {test_card.name}" added successfully!',
            "success",
        )
    except Exception as e:
        flash(f"Error adding test card: {str(e)}", "error")

    return redirect(url_for("credit_card.index"))


@credit_card_bp.route("/quick_add_card", methods=["POST"])
@user_required
def quick_add_card():
    """Quickly add predefined credit cards with benefits from templates."""
    selected_cards = request.form.get("selected_cards")
    
    if not selected_cards:
        flash("Please select at least one credit card to add.", "error")
        return redirect(url_for("credit_card.index"))
    
    try:
        # Parse multiple card selections (separated by |)
        card_list = [card.strip() for card in selected_cards.split('|') if card.strip()]
        
        if not card_list:
            flash("Please select at least one credit card to add.", "error")
            return redirect(url_for("credit_card.index"))
        
        added_cards = []
        errors = []
        
        for card_data in card_list:
            try:
                new_card = CreditCardController.quick_add_card(card_data)
                added_cards.append(f"{new_card.bank} {new_card.name}")
            except Exception as e:
                errors.append(f"Failed to add {card_data}: {str(e)}")
        
        # Show results
        if added_cards:
            if len(added_cards) == 1:
                flash(f"Credit card '{added_cards[0]}' added successfully! You can edit the details now.", "success")
                # Redirect to the single card detail if only one was added
                return redirect(url_for("credit_card.index"))
            else:
                flash(f"Successfully added {len(added_cards)} credit cards: {', '.join(added_cards)}. You can edit the details now.", "success")
        
        if errors:
            for error in errors:
                flash(error, "error")
        
        return redirect(url_for("credit_card.index"))
        
    except Exception as e:
        flash(f"Error adding cards: {str(e)}", "error")
        return redirect(url_for("credit_card.index"))
