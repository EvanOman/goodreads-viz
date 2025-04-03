# List available commands
default:
    @just --list

install:
    uv venv
    uv sync

# Run tests
test:
    pytest

# Run tests with coverage
test-cov:
    pytest --cov=goodreads_viz --cov-report=term-missing

# Run type checking
typecheck:
    mypy goodreads_viz

# Run linting
lint:
    ruff check .

# Format code
fmt:
    ruff format .
    ruff check . --select I --fix # imports

# Run all checks (format, lint, typecheck, test)
check: fmt lint typecheck test

# Clean python cache files
clean:
    find . -type d -name "__pycache__" -exec rm -r {} +
    find . -type f -name "*.pyc" -delete
    find . -type f -name "*.pyo" -delete
    find . -type f -name "*.pyd" -delete
    find . -type f -name ".coverage" -delete
    find . -type d -name "*.egg-info" -exec rm -r {} +
    find . -type d -name "*.egg" -exec rm -r {} +
    find . -type d -name ".pytest_cache" -exec rm -r {} +
    find . -type d -name ".mypy_cache" -exec rm -r {} +
    find . -type d -name ".ruff_cache" -exec rm -r {} + 