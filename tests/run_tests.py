#!/usr/bin/env python3
# RaidAssist Enhanced - Test Runner
# Copyright (C) 2025 Nicholas Acord <ncacord@protonmail.com>

"""
run_tests.py - Comprehensive test runner for RaidAssist Enhanced.

Runs all tests with proper configuration and generates reports.
Supports fallback testing when pytest is not available.
"""

import argparse
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# Colors for console output
class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    END = "\033[0m"


def colored_print(text, color):
    """Print colored text to console."""
    print(f"{color}{text}{Colors.END}")


def run_command(cmd, description):
    """Run a command and return success status with better reporting."""
    colored_print(f"🔍 {description}...", Colors.BLUE)
    start_time = time.time()

    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, cwd=project_root
        )
        duration = time.time() - start_time

        if result.returncode == 0:
            colored_print(f"✅ {description} - PASSED ({duration:.2f}s)", Colors.GREEN)
            if result.stdout and len(result.stdout.strip()) < 200:
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            colored_print(f"❌ {description} - FAILED ({duration:.2f}s)", Colors.RED)
            if result.stderr:
                print(f"   Error: {result.stderr.strip()}")
            if result.stdout:
                print(f"   Output: {result.stdout.strip()}")
            return False
    except Exception as e:
        colored_print(f"❌ {description} - ERROR: {e}", Colors.RED)
        return False


def check_dependencies():
    """Check if required dependencies are available."""
    print("🔍 Checking Test Dependencies...")

    dependencies = [
        ("pytest", "pytest --version"),
        ("coverage", "coverage --version"),
    ]

    all_available = True
    for name, cmd in dependencies:
        if run_command(cmd, f"Checking {name}"):
            colored_print(f"   ✅ {name} is available", Colors.GREEN)
        else:
            colored_print(
                f"   ⚠️  {name} not available - install with: pip install {name}",
                Colors.YELLOW,
            )
            all_available = False

    return all_available


def run_system_tests():
    """Run system tests."""
    print("\n🎮 Running System Tests...")
    return run_command(
        "python -m pytest tests/test_systems.py -v --tb=short",
        "Systems Tests",
    )


def run_unit_tests():
    """Run all unit tests."""
    print("\n🧪 Running Unit Tests...")
    return run_command(
        "python -m pytest tests/ -v --tb=short -m 'not slow and not integration'",
        "Unit Tests",
    )


def run_integration_tests():
    """Run integration tests."""
    print("\n🔗 Running Integration Tests...")
    return run_command(
        "python -m pytest tests/ -v --tb=short -m integration", "Integration Tests"
    )


def run_all_tests():
    """Run all tests."""
    print("\n🎯 Running All Tests...")
    return run_command("python -m pytest tests/ -v --tb=short", "All Tests")


def run_tests_with_coverage():
    """Run tests with coverage report."""
    print("\n📊 Running Tests with Coverage...")
    success = run_command(
        "python -m pytest tests/ --cov=api --cov=ui --cov=utils --cov-report=html:tests/coverage_html --cov-report=term-missing",
        "Tests with Coverage",
    )

    if success:
        coverage_path = project_root / "tests" / "coverage_html" / "index.html"
        if coverage_path.exists():
            print(f"📊 Coverage report generated: {coverage_path}")

    return success


def run_system_verification():
    """Run system verification."""
    print("\n🔧 Running System Verification...")
    return run_command("python tests/verify_enhanced.py", "System Verification")


def run_linting():
    """Run code linting if available."""
    print("\n🔍 Running Code Linting...")

    # Try different linters
    linters = [
        ("flake8", "flake8 --max-line-length=120 --ignore=E203,W503 api/ ui/ utils/"),
        ("black", "black --check --line-length=120 api/ ui/ utils/"),
        ("mypy", "mypy --ignore-missing-imports api/ ui/ utils/"),
    ]

    results = []
    for name, cmd in linters:
        print(f"  Trying {name}...")
        result = run_command(cmd, f"{name} linting")
        results.append(result)

    return any(results)  # At least one linter succeeded


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="RaidAssist Enhanced Test Runner")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument(
        "--integration", action="store_true", help="Run integration tests only"
    )
    parser.add_argument("--systems", action="store_true", help="Run system tests only")
    parser.add_argument(
        "--coverage", action="store_true", help="Run tests with coverage"
    )
    parser.add_argument(
        "--verify", action="store_true", help="Run system verification only"
    )
    parser.add_argument("--lint", action="store_true", help="Run linting only")
    parser.add_argument("--all", action="store_true", help="Run all tests and checks")
    parser.add_argument("--fast", action="store_true", help="Skip slow tests")

    args = parser.parse_args()

    print("🎮 RaidAssist Enhanced - Test Runner")
    print("Copyright (C) 2025 Nicholas Acord")
    print("=" * 60)

    # Check dependencies first
    if not check_dependencies():
        print("\n⚠️  Some dependencies missing. Install with:")
        print("pip install pytest pytest-cov flake8 black mypy")
        if not args.verify:  # Allow verification without pytest
            return 1

    # Track results
    results = []

    # Run requested tests
    if args.verify:
        results.append(run_system_verification())
    elif args.unit:
        results.append(run_unit_tests())
    elif args.integration:
        results.append(run_integration_tests())
    elif args.systems:
        results.append(run_system_tests())
    elif args.coverage:
        results.append(run_tests_with_coverage())
    elif args.lint:
        results.append(run_linting())
    elif args.all:
        results.append(run_system_verification())
        results.append(run_system_tests())
        results.append(run_unit_tests())
        results.append(run_integration_tests())
        results.append(run_linting())
        results.append(run_tests_with_coverage())
    else:
        # Default: run system tests and verification
        results.append(run_system_verification())
        results.append(run_system_tests())
        if not args.fast:
            results.append(run_unit_tests())

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)

    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"🎉 ALL TESTS PASSED ({passed}/{total})")
        print("✅ RaidAssist Enhanced is ready for use!")
        return 0
    else:
        print(f"⚠️  SOME TESTS FAILED ({passed}/{total} passed)")
        print("🔧 Please address the issues above.")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Testing cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Test runner failed: {e}")
        sys.exit(1)
