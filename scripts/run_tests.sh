#!/bin/bash
# Local testing script that mirrors CI/CD pipeline

set -e

echo "🧪 Running DB Operations Utility Test Suite"
echo "==========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    print_warning "Not in a virtual environment. Consider activating one:"
    echo "  python -m venv venv"
    echo "  source venv/bin/activate  # On Windows: venv\\Scripts\\activate"
    echo ""
fi

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    print_status "Installing dependencies..."
    pip install -r requirements.txt > /dev/null 2>&1
fi

echo ""
echo "📝 Code Quality Checks"
echo "====================="

# Black formatting check
print_status "Running Black (code formatting)..."
if black --check --diff . > /dev/null 2>&1; then
    print_status "Black formatting: PASSED"
else
    print_error "Black formatting: FAILED"
    echo "Run 'black .' to fix formatting issues"
fi

# isort import sorting check
print_status "Running isort (import sorting)..."
if isort --check-only --diff . > /dev/null 2>&1; then
    print_status "Import sorting: PASSED"
else
    print_error "Import sorting: FAILED"
    echo "Run 'isort .' to fix import sorting"
fi

# Flake8 style guide
print_status "Running Flake8 (style guide)..."
if flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics > /dev/null 2>&1; then
    print_status "Flake8 style check: PASSED"
else
    print_error "Flake8 style check: FAILED"
    flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
fi

echo ""
echo "🔍 Static Analysis"
echo "=================="

# MyPy type checking
print_status "Running MyPy (type checking)..."
if mypy . --ignore-missing-imports > /dev/null 2>&1; then
    print_status "Type checking: PASSED"
else
    print_warning "Type checking: WARNINGS (non-critical)"
fi

# Pylint code analysis
print_status "Running Pylint (code analysis)..."
if pylint **/*.py > /dev/null 2>&1; then
    print_status "Code analysis: PASSED"
else
    print_warning "Code analysis: WARNINGS (non-critical)"
fi

echo ""
echo "🔒 Security Checks"
echo "=================="

# Bandit security linting
print_status "Running Bandit (security analysis)..."
if bandit -r . > /dev/null 2>&1; then
    print_status "Security analysis: PASSED"
else
    print_warning "Security analysis: WARNINGS (review recommended)"
fi

# Safety dependency checking
print_status "Running Safety (dependency vulnerabilities)..."
if safety check > /dev/null 2>&1; then
    print_status "Dependency security: PASSED"
else
    print_warning "Dependency security: WARNINGS (review recommended)"
fi

echo ""
echo "🧪 Unit Tests"
echo "============="

# Run tests with coverage
print_status "Running pytest with coverage..."
if pytest --cov=. --cov-report=term-missing --cov-report=html > /dev/null 2>&1; then
    print_status "Unit tests: PASSED"
    
    # Show coverage summary
    echo ""
    echo "📊 Coverage Report:"
    echo "=================="
    pytest --cov=. --cov-report=term-missing | tail -n 10
else
    print_error "Unit tests: FAILED"
    echo "Run 'pytest -v' for detailed test output"
fi

echo ""
echo "✅ Test suite completed!"
echo "======================="

# Check if HTML coverage report was generated
if [ -f "htmlcov/index.html" ]; then
    print_status "HTML coverage report generated: htmlcov/index.html"
fi

echo ""
echo "🚀 Next steps:"
echo "- Review any warnings or failures above"
echo "- Run 'black .' and 'isort .' to fix formatting"
echo "- Commit your changes if all tests pass"
echo "- Push to trigger the CI/CD pipeline"

