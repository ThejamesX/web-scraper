#!/bin/bash
# Development helper script for PriceScout

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper function to print colored messages
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if virtual environment exists
check_venv() {
    if [ ! -d "venv" ]; then
        print_warning "Virtual environment not found. Creating one..."
        python3 -m venv venv
        print_info "Virtual environment created"
    fi
}

# Activate virtual environment
activate_venv() {
    if [ -d "venv" ]; then
        print_info "Activating virtual environment..."
        source venv/bin/activate
    else
        print_error "Virtual environment not found. Run './scripts/dev.sh setup' first."
        exit 1
    fi
}

# Setup development environment
setup() {
    print_info "Setting up development environment..."
    
    # Check Python version
    python_version=$(python3 --version | awk '{print $2}')
    print_info "Python version: $python_version"
    
    # Create virtual environment
    check_venv
    
    # Activate virtual environment
    activate_venv
    
    # Install dependencies
    print_info "Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Install Playwright browsers
    print_info "Installing Playwright browsers..."
    playwright install chromium
    
    # Setup environment file
    if [ ! -f ".env" ]; then
        print_info "Creating .env file from .env.example..."
        cp .env.example .env
        print_warning "Please edit .env file with your configuration"
    else
        print_info ".env file already exists"
    fi
    
    print_info "Setup complete! 🎉"
    print_info "Run './scripts/dev.sh start' to start the development server"
}

# Start development server
start() {
    activate_venv
    print_info "Starting development server..."
    print_info "Server will be available at http://localhost:8000"
    print_info "API docs at http://localhost:8000/docs"
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
}

# Run tests
test() {
    activate_venv
    print_info "Running tests..."
    
    if [ "$1" == "coverage" ]; then
        print_info "Running tests with coverage..."
        pytest --cov=. --cov-report=html --cov-report=term
        print_info "Coverage report saved to htmlcov/index.html"
    elif [ "$1" == "slow" ]; then
        print_info "Running all tests including slow integration tests..."
        pytest -v
    elif [ "$1" == "watch" ]; then
        print_info "Running tests in watch mode..."
        pytest-watch
    else
        print_info "Running fast tests only..."
        pytest -v -m "not slow"
    fi
}

# Format code
format() {
    activate_venv
    print_info "Formatting code..."
    
    if command -v black &> /dev/null; then
        black .
        print_info "Code formatted with black"
    else
        print_warning "black not installed. Install with: pip install black"
    fi
    
    if command -v isort &> /dev/null; then
        isort .
        print_info "Imports sorted with isort"
    else
        print_warning "isort not installed. Install with: pip install isort"
    fi
}

# Lint code
lint() {
    activate_venv
    print_info "Linting code..."
    
    if command -v flake8 &> /dev/null; then
        flake8 . --max-line-length=120 --exclude=venv,__pycache__,.pytest_cache
    else
        print_warning "flake8 not installed. Install with: pip install flake8"
    fi
    
    if command -v mypy &> /dev/null; then
        mypy . --ignore-missing-imports
    else
        print_warning "mypy not installed. Install with: pip install mypy"
    fi
}

# Clean up
clean() {
    print_info "Cleaning up..."
    
    # Remove Python cache
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    find . -type f -name "*.pyo" -delete 2>/dev/null || true
    
    # Remove test cache
    rm -rf .pytest_cache htmlcov .coverage
    
    # Remove database
    rm -f *.db *.sqlite *.sqlite3
    
    print_info "Cleanup complete"
}

# Database operations
db() {
    activate_venv
    
    case "$1" in
        init)
            print_info "Initializing database..."
            python -c "from db import init_db; import asyncio; asyncio.run(init_db())"
            print_info "Database initialized"
            ;;
        reset)
            print_warning "This will delete all data. Are you sure? (y/N)"
            read -r response
            if [ "$response" == "y" ]; then
                rm -f pricescout.db
                print_info "Database deleted"
                python -c "from db import init_db; import asyncio; asyncio.run(init_db())"
                print_info "Database recreated"
            fi
            ;;
        *)
            print_error "Unknown database command. Use: init, reset"
            ;;
    esac
}

# Docker operations
docker_ops() {
    case "$1" in
        build)
            print_info "Building Docker image..."
            docker build -t pricescout:latest .
            ;;
        up)
            print_info "Starting Docker containers..."
            docker-compose up -d
            print_info "Containers started. View logs with: docker-compose logs -f"
            ;;
        down)
            print_info "Stopping Docker containers..."
            docker-compose down
            ;;
        logs)
            docker-compose logs -f web
            ;;
        shell)
            docker-compose exec web bash
            ;;
        *)
            print_error "Unknown docker command. Use: build, up, down, logs, shell"
            ;;
    esac
}

# Show help
help() {
    cat << EOF
PriceScout Development Helper Script

Usage: ./scripts/dev.sh <command> [options]

Commands:
    setup           Set up development environment
    start           Start development server
    test [option]   Run tests
                    - coverage: Run with coverage report
                    - slow: Include slow integration tests
                    - watch: Run in watch mode
    format          Format code with black and isort
    lint            Lint code with flake8 and mypy
    clean           Clean up cache and temporary files
    db <command>    Database operations
                    - init: Initialize database
                    - reset: Reset database (deletes all data)
    docker <cmd>    Docker operations
                    - build: Build Docker image
                    - up: Start containers
                    - down: Stop containers
                    - logs: View logs
                    - shell: Open shell in container
    help            Show this help message

Examples:
    ./scripts/dev.sh setup              # First time setup
    ./scripts/dev.sh start              # Start dev server
    ./scripts/dev.sh test coverage      # Run tests with coverage
    ./scripts/dev.sh docker up          # Start with Docker

EOF
}

# Main script logic
case "$1" in
    setup)
        setup
        ;;
    start)
        start
        ;;
    test)
        test "$2"
        ;;
    format)
        format
        ;;
    lint)
        lint
        ;;
    clean)
        clean
        ;;
    db)
        db "$2"
        ;;
    docker)
        docker_ops "$2"
        ;;
    help|--help|-h)
        help
        ;;
    *)
        print_error "Unknown command: $1"
        help
        exit 1
        ;;
esac
