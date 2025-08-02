from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from controllers.airline_program_controller import AirlineProgramController
from controllers.airline_program_validation_controller import (
    AirlineProgramValidationController,
)
from utils.decorators import user_required
from datetime import date

airline_program_bp = Blueprint("airline_program", __name__)


@airline_program_bp.route("/airline_programs")
@user_required
def index():
    """Display list of airline programs with filtering."""
    # Get filter parameters
    search_query = request.args.get("search_query", "").strip()
    airline_filter = request.args.get("airline_filter", "").strip()
    program_filter = request.args.get("program_filter", "").strip()

    # Filter programs
    programs = AirlineProgramController.filter_programs(
        search_query=search_query,
        airline_filter=airline_filter,
        program_filter=program_filter,
    )

    # Get filter options
    filter_options = AirlineProgramController.get_filter_options()

    return render_template(
        "airline_programs/index.html",
        programs=programs,
        filter_options=filter_options,
        search_query=search_query,
        airline_filter=airline_filter,
        program_filter=program_filter,
        today=date.today(),
    )


@airline_program_bp.route("/airline_programs/add", methods=["GET", "POST"])
@user_required
def add_program():
    """Add a new airline program."""
    if request.method == "POST":
        # Validate form data
        errors = AirlineProgramValidationController.validate_program_form(request.form)

        if not errors:
            try:
                # Create new program
                program = AirlineProgramController.create_program(request.form)
                flash(
                    f'Airline mileage program "{program.airline_name} - {program.program_name}" created successfully!',
                    "success",
                )
                return redirect(url_for("airline_program.index"))
            except Exception as e:
                flash(f"Error creating airline mileage program: {str(e)}", "error")
        else:
            for error in errors:
                flash(error, "error")

    return render_template("airline_programs/add_program.html")


@airline_program_bp.route(
    "/airline_programs/edit/<int:program_id>", methods=["GET", "POST"]
)
@user_required
def edit_program(program_id):
    """Edit an existing airline program."""
    program = AirlineProgramController.get_program_by_id(program_id)
    if not program:
        abort(404)

    if request.method == "POST":
        # Validate form data
        errors = AirlineProgramValidationController.validate_program_form(request.form)

        if not errors:
            try:
                # Update program
                updated_program = AirlineProgramController.update_program(
                    program_id, request.form
                )
                if updated_program:
                    flash(
                        f'Airline mileage program "{updated_program.airline_name} - {updated_program.program_name}" updated successfully!',
                        "success",
                    )
                    return redirect(url_for("airline_program.index"))
                else:
                    flash("Error updating airline mileage program.", "error")
            except Exception as e:
                flash(f"Error updating airline mileage program: {str(e)}", "error")
        else:
            for error in errors:
                flash(error, "error")

    return render_template("airline_programs/edit_program.html", program=program)


@airline_program_bp.route("/airline_programs/delete/<int:program_id>", methods=["POST"])
@user_required
def delete_program(program_id):
    """Delete an airline program."""
    program = AirlineProgramController.get_program_by_id(program_id)
    if not program:
        abort(404)

    try:
        success = AirlineProgramController.delete_program(program_id)
        if success:
            flash(
                f'Airline mileage program "{program.airline_name} - {program.program_name}" deleted successfully!',
                "success",
            )
        else:
            flash("Error deleting airline mileage program.", "error")
    except Exception as e:
        flash(f"Error deleting airline mileage program: {str(e)}", "error")

    return redirect(url_for("airline_program.index"))


@airline_program_bp.route("/airline_programs/generate_test_data", methods=["POST"])
@user_required
def generate_test_data():
    """Generate test airline program data."""
    try:
        program = AirlineProgramController.generate_test_program()
        flash(
            f'Test airline mileage program "{program.airline_name} - {program.program_name}" created successfully!',
            "success",
        )
    except Exception as e:
        flash(f"Error generating test data: {str(e)}", "error")

    return redirect(url_for("airline_program.index"))
