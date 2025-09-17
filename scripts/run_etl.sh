#!/bin/bash

# MoMo ETL Pipeline Runner Script
# This script runs the complete ETL pipeline for processing MoMo XML data

set -e  # Exit on any error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ETL_SCRIPT="$PROJECT_ROOT/etl/run.py"
DEFAULT_XML_FILE="$PROJECT_ROOT/data/raw/momo.xml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -x, --xml FILE     Path to XML input file (default: $DEFAULT_XML_FILE)"
    echo "  -n, --no-export    Skip dashboard JSON export"
    echo "  -d, --dry-run      Parse and clean data without loading to database"
    echo "  -l, --log-level    Set logging level (DEBUG, INFO, WARNING, ERROR)"
    echo "  -h, --help         Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Run with default XML file"
    echo "  $0 -x data/raw/custom.xml            # Run with custom XML file"
    echo "  $0 -d                                # Dry run (no database loading)"
    echo "  $0 -n -l DEBUG                       # Skip export, debug logging"
}

# Default values
XML_FILE="$DEFAULT_XML_FILE"
EXPORT_JSON=true
DRY_RUN=false
LOG_LEVEL="INFO"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -x|--xml)
            XML_FILE="$2"
            shift 2
            ;;
        -n|--no-export)
            EXPORT_JSON=false
            shift
            ;;
        -d|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -l|--log-level)
            LOG_LEVEL="$2"
            shift 2
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Validate XML file
if [[ ! -f "$XML_FILE" ]]; then
    print_error "XML file not found: $XML_FILE"
    print_status "Please ensure the XML file exists or specify a different file with -x option"
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if required Python packages are installed
print_status "Checking Python dependencies..."
if ! python3 -c "import lxml, dateutil, sqlite3" 2>/dev/null; then
    print_warning "Some required Python packages are missing"
    print_status "Installing dependencies from requirements.txt..."
    
    if [[ -f "$PROJECT_ROOT/requirements.txt" ]]; then
        pip3 install -r "$PROJECT_ROOT/requirements.txt"
    else
        print_error "requirements.txt not found. Please install dependencies manually."
        exit 1
    fi
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p "$PROJECT_ROOT/data/raw"
mkdir -p "$PROJECT_ROOT/data/processed"
mkdir -p "$PROJECT_ROOT/logs"
mkdir -p "$PROJECT_ROOT/data/logs/dead_letter"

# Build Python command
PYTHON_CMD="python3 $ETL_SCRIPT --xml \"$XML_FILE\" --log-level $LOG_LEVEL"

if [[ "$EXPORT_JSON" == false ]]; then
    PYTHON_CMD="$PYTHON_CMD --no-export"
fi

if [[ "$DRY_RUN" == true ]]; then
    PYTHON_CMD="$PYTHON_CMD --dry-run"
fi

# Run ETL pipeline
print_status "Starting MoMo ETL Pipeline..."
print_status "XML File: $XML_FILE"
print_status "Export JSON: $EXPORT_JSON"
print_status "Dry Run: $DRY_RUN"
print_status "Log Level: $LOG_LEVEL"
echo ""

# Change to project root directory
cd "$PROJECT_ROOT"

# Execute the ETL pipeline
if eval "$PYTHON_CMD"; then
    print_success "ETL pipeline completed successfully!"
    
    if [[ "$DRY_RUN" == false ]]; then
        # Show database stats if not dry run
        if [[ -f "$PROJECT_ROOT/data/db.sqlite3" ]]; then
            print_status "Database file created: $PROJECT_ROOT/data/db.sqlite3"
            
            # Get database size
            DB_SIZE=$(du -h "$PROJECT_ROOT/data/db.sqlite3" | cut -f1)
            print_status "Database size: $DB_SIZE"
        fi
        
        # Show processed data if exported
        if [[ "$EXPORT_JSON" == true && -f "$PROJECT_ROOT/data/processed/dashboard.json" ]]; then
            print_status "Dashboard data exported: $PROJECT_ROOT/data/processed/dashboard.json"
        fi
    fi
    
    # Show log file location
    if [[ -f "$PROJECT_ROOT/data/logs/etl.log" ]]; then
        print_status "ETL log file: $PROJECT_ROOT/data/logs/etl.log"
    fi
    
else
    print_error "ETL pipeline failed!"
    print_status "Check the log file for details: $PROJECT_ROOT/data/logs/etl.log"
    exit 1
fi

print_success "Script completed successfully!"
