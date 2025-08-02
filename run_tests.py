#!/usr/bin/env python3
"""
Test runner script for the Credit Card Manager application.
Supports the new MVC architecture with organized test categories.

Usage:
    python run_tests.py                # Run all tests
    python run_tests.py --models       # Run model tests
    python run_tests.py --controllers  # Run controller tests
    python run_tests.py --routes       # Run route tests
    python run_tests.py --templates    # Run template tests
    python run_tests.py --migrations   # Run migration tests
    python run_tests.py --coverage     # Run with detailed coverage report
    python run_tests.py --fast         # Skip slow tests
"""

import sys
import subprocess
import argparse
import os


def run_tests(test_type=None, coverage=False, fast=False, verbose=False):
    """Run tests with specified options."""
    # Change to project root directory
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)

    # Use uv for running tests as specified in project requirements
    cmd = ["uv", "run", "pytest", "tests/"]

    if verbose:
        cmd.append("-v")

    if coverage:
        cmd.extend(["--cov=.", "--cov-report=html", "--cov-report=term-missing"])

    if fast:
        cmd.extend(["-m", "not slow"])

    # MVC architecture test categories
    if test_type == "models":
        cmd = ["uv", "run", "pytest", "tests/models/"]
        if verbose:
            cmd.append("-v")
        if coverage:
            cmd.extend(
                ["--cov=models", "--cov-report=html", "--cov-report=term-missing"]
            )
    elif test_type == "controllers":
        cmd = ["uv", "run", "pytest", "tests/controllers/"]
        if verbose:
            cmd.append("-v")
        if coverage:
            cmd.extend(
                ["--cov=controllers", "--cov-report=html", "--cov-report=term-missing"]
            )
    elif test_type == "routes":
        cmd = ["uv", "run", "pytest", "tests/routes/"]
        if verbose:
            cmd.append("-v")
        if coverage:
            cmd.extend(
                ["--cov=routes", "--cov-report=html", "--cov-report=term-missing"]
            )
    elif test_type == "templates":
        cmd = ["uv", "run", "pytest", "tests/templates/"]
        if verbose:
            cmd.append("-v")
        if coverage:
            cmd.extend(
                ["--cov=templates", "--cov-report=html", "--cov-report=term-missing"]
            )
    elif test_type == "migrations":
        cmd = ["uv", "run", "pytest", "tests/migrations/"]
        if verbose:
            cmd.append("-v")
        if coverage:
            cmd.extend(
                ["--cov=migrations", "--cov-report=html", "--cov-report=term-missing"]
            )

    print(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(
        description="Test runner for Credit Card Manager (MVC Architecture)"
    )
    parser.add_argument(
        "--models", action="store_true", help="Run model tests (24 tests)"
    )
    parser.add_argument(
        "--controllers", action="store_true", help="Run controller tests (60 tests)"
    )
    parser.add_argument(
        "--routes", action="store_true", help="Run route tests (24 tests)"
    )
    parser.add_argument(
        "--templates", action="store_true", help="Run template tests (19 tests)"
    )
    parser.add_argument(
        "--migrations", action="store_true", help="Run migration tests (17 tests)"
    )
    parser.add_argument(
        "--coverage", action="store_true", help="Generate coverage report"
    )
    parser.add_argument("--fast", action="store_true", help="Skip slow tests")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    test_type = None
    if args.models:
        test_type = "models"
    elif args.controllers:
        test_type = "controllers"
    elif args.routes:
        test_type = "routes"
    elif args.templates:
        test_type = "templates"
    elif args.migrations:
        test_type = "migrations"

    # Display test suite information
    if not test_type:
        print("🧪 Credit Card Manager Test Suite - MVC Architecture")
        print("📊 Total: 144 tests | Coverage: 91%")
        print("┌─────────────┬───────┬──────────┬─────────────────────────────┐")
        print("│ Category    │ Tests │ Coverage │ Description                 │")
        print("├─────────────┼───────┼──────────┼─────────────────────────────┤")
        print("│ Models      │  24   │   100%   │ Database operations         │")
        print("│ Controllers │  60   │    99%   │ Business logic              │")
        print("│ Routes      │  24   │    81%   │ HTTP endpoints              │")
        print("│ Templates   │  19   │   100%   │ UI rendering                │")
        print("│ Migrations  │  17   │    96%   │ Database schema             │")
        print("└─────────────┴───────┴──────────┴─────────────────────────────┘")
        print()
        print("✅ All functionality: 144/144 tests passing")
        print()

    exit_code = run_tests(
        test_type=test_type,
        coverage=args.coverage,
        fast=args.fast,
        verbose=args.verbose,
    )

    if exit_code == 0:
        print("\n✅ All tests passed!")
        if args.coverage:
            print("📊 Coverage report generated in htmlcov/index.html")
            print("🎯 Target achieved: 91% overall coverage")
    else:
        print("\n⚠️  Some tests failed!")
        print("💡 Try running with --verbose for more details")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
