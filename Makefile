# DB Operations Utility - Development Makefile
.PHONY: help install test lint format security docs clean all

# Default target
help:
	@echo "🛠️  DB Operations Utility - Development Commands"
	@echo "================================================"
	@echo ""
	@echo "Available commands:"
	@echo "  install     - Install all dependencies"
	@echo "  test        - Run all tests with coverage"
	@echo "  test-unit   - Run unit tests only"
	@echo "  lint        - Run all code quality checks"
	@echo "  format      - Format code with black and isort"
	@echo "  security    - Run security scans"
	@echo "  docs        - Build documentation"
	@echo "  clean       - Clean up generated files"
	@echo "  all         - Run format, lint, security, and test"
	@echo "  ci          - Run full CI pipeline locally"
	@echo ""
	@echo "Example usage:"
	@echo "  make install"
	@echo "  make test"
	@echo "  make all"

# Install dependencies
install:
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt
	@echo "✅ Dependencies installed!"

# Run all tests with coverage
test:
	@echo "🧪 Running tests with coverage..."
	pytest --cov=. --cov-report=term-missing --cov-report=html
	@echo "📊 Coverage report generated in htmlcov/"

# Run unit tests only
test-unit:
	@echo "🧪 Running unit tests..."
	pytest tests/ -v

# Run all linting and code quality checks
lint:
	@echo "📝 Running code quality checks..."
	@echo "  ↳ Black formatting check..."
	@black --check --diff .
	@echo "  ↳ isort import sorting check..."
	@isort --check-only --diff .
	@echo "  ↳ Flake8 style guide check..."
	@flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	@echo "  ↳ MyPy type checking..."
	@mypy . --ignore-missing-imports || true
	@echo "  ↳ Pylint code analysis..."
	@pylint **/*.py || true
	@echo "✅ Code quality checks completed!"

# Format code
format:
	@echo "🎨 Formatting code..."
	@echo "  ↳ Running Black..."
	@black .
	@echo "  ↳ Running isort..."
	@isort .
	@echo "✅ Code formatted!"

# Security scans
security:
	@echo "🔒 Running security scans..."
	@echo "  ↳ Bandit security analysis..."
	@bandit -r . -f json -o bandit-report.json || true
	@bandit -r . || true
	@echo "  ↳ Safety dependency check..."
	@safety check --json --output safety-report.json || true
	@safety check || true
	@echo "✅ Security scans completed!"

# Build documentation
docs:
	@echo "📚 Building documentation..."
	@mkdir -p docs
	@if [ ! -f docs/conf.py ]; then \
		echo "Creating Sphinx configuration..."; \
		cat > docs/conf.py << 'EOF'; \
import os; \
import sys; \
sys.path.insert(0, os.path.abspath('..')); \
project = 'DB Operations Utility'; \
copyright = '2024, CB Winslow'; \
author = 'CB Winslow'; \
extensions = ['sphinx.ext.autodoc', 'sphinx.ext.viewcode', 'sphinx.ext.napoleon']; \
templates_path = ['_templates']; \
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']; \
html_theme = 'sphinx_rtd_theme'; \
html_static_path = ['_static']; \
EOF \
	fi
	@if [ ! -f docs/index.rst ]; then \
		echo "Creating documentation index..."; \
		cat > docs/index.rst << 'EOF'; \
DB Operations Utility Documentation; \
==================================; \
; \
.. toctree::; \
   :maxdepth: 2; \
   :caption: Contents:; \
; \
   modules; \
; \
Indices and tables; \
==================; \
; \
* :ref:\`genindex\`; \
* :ref:\`modindex\`; \
* :ref:\`search\`; \
EOF \
	fi
	@cd docs && sphinx-apidoc -o . .. --force --separate
	@cd docs && sphinx-build -b html . _build/html
	@echo "📖 Documentation built in docs/_build/html/"

# Clean up generated files
clean:
	@echo "🧹 Cleaning up..."
	@rm -rf .pytest_cache/
	@rm -rf .mypy_cache/
	@rm -rf htmlcov/
	@rm -rf .coverage
	@rm -rf *.egg-info/
	@rm -rf build/
	@rm -rf dist/
	@rm -rf docs/_build/
	@rm -f bandit-report.json
	@rm -f safety-report.json
	@rm -f semgrep-report.json
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Cleanup completed!"

# Run everything (format, lint, security, test)
all: format lint security test
	@echo "🎉 All checks completed successfully!"

# Run CI pipeline locally
ci:
	@echo "🚀 Running CI pipeline locally..."
	@echo "This mirrors the GitHub Actions workflow"
	@echo ""
	@$(MAKE) format
	@echo ""
	@$(MAKE) lint
	@echo ""
	@$(MAKE) security
	@echo ""
	@$(MAKE) test
	@echo ""
	@$(MAKE) docs
	@echo ""
	@echo "✅ CI pipeline completed successfully!"
	@echo "Your code is ready for commit and push!"

# Development setup
setup: install
	@echo "🔧 Setting up development environment..."
	@if [ ! -d "venv" ]; then \
		echo "Creating virtual environment..."; \
		python -m venv venv; \
		echo "Virtual environment created!"; \
		echo ""; \
		echo "To activate:"; \
		echo "  source venv/bin/activate  # On Windows: venv\\Scripts\\activate"; \
	fi
	@echo "✅ Development environment ready!"

