#!/bin/bash

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

show_help() {
    cat << EOF
Usage: ./run.sh [OPTIONS]

Options:
  --all          Run full pipeline (analysis + all methods + visualization) [DEFAULT]
  --test         Run comprehensive tests
  --method NAME  Run specific method (e.g., method_01_by_domain)
  --analyze      Run data quality analysis only
  --visualize    Run visualization generation only
  --help         Show this help message

Examples:
  ./run.sh                              Run full pipeline
  ./run.sh --test                       Run all tests
  ./run.sh --method method_01_by_domain Run specific method
  ./run.sh --analyze                    Run analysis only

EOF
}

if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    show_help
    exit 0
fi

if ! command -v python3 &> /dev/null; then
    echo "Error: python3 not found. Please install Python 3.8+"
    exit 1
fi

COMMAND="${1:---all}"

case "$COMMAND" in
    --all)
        python3 "$PROJECT_DIR/src/main.py" --full
        ;;
    --test)
        python3 "$PROJECT_DIR/tests/test_all_methods_comprehensive.py"
        ;;
    --stress-test)
        python3 "$PROJECT_DIR/tests/test_production.py"
        ;;
    --method)
        if [ -z "$2" ]; then
            echo "Error: --method requires a method name"
            echo "Example: ./run.sh --method method_01_by_domain"
            exit 1
        fi
        python3 "$PROJECT_DIR/src/main.py" --method "$2"
        ;;
    --analyze)
        python3 "$PROJECT_DIR/src/main.py" --analyze
        ;;
    --visualize)
        python3 "$PROJECT_DIR/src/main.py" --visualize
        ;;
    --list)
        python3 "$PROJECT_DIR/src/main.py" --list
        ;;
    *)
        echo "Unknown option: $COMMAND"
        echo ""
        show_help
        exit 1
        ;;
esac
