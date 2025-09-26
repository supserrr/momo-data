#!/bin/bash

# MoMo Dashboard JSON Export Script
# Export dashboard JSON data

set -e  # Exit on any error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ETL_SCRIPT="$PROJECT_ROOT/etl/run.py"
DASHBOARD_JSON="$PROJECT_ROOT/data/processed/dashboard.json"
DATABASE_FILE="$PROJECT_ROOT/data/db.sqlite3"

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
    echo "  -o, --output FILE  Output JSON file path (default: $DASHBOARD_JSON)"
    echo "  -f, --force        Force export even if database is empty"
    echo "  -h, --help         Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Export to default location"
    echo "  $0 -o custom_dashboard.json          # Export to custom file"
    echo "  $0 -f                                # Force export"
}

# Default values
OUTPUT_FILE="$DASHBOARD_JSON"
FORCE_EXPORT=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -o|--output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        -f|--force)
            FORCE_EXPORT=true
            shift
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

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if database exists
if [[ ! -f "$DATABASE_FILE" ]]; then
    print_error "Database file not found: $DATABASE_FILE"
    print_status "Please run the ETL pipeline first using: ./scripts/run_etl.sh"
    exit 1
fi

# Check if database has data (unless force export)
if [[ "$FORCE_EXPORT" == false ]]; then
    print_status "Checking database for data..."
    
    # Use Python to check if database has transactions
    TRANSACTION_COUNT=$(python3 -c "
import sqlite3
try:
    conn = sqlite3.connect('$DATABASE_FILE')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM transactions')
    count = cursor.fetchone()[0]
    conn.close()
    print(count)
except Exception as e:
    print(0)
")
    
    if [[ "$TRANSACTION_COUNT" -eq 0 ]]; then
        print_warning "Database appears to be empty (0 transactions)"
        print_status "Use -f flag to force export or run ETL pipeline first"
        exit 1
    else
        print_status "Found $TRANSACTION_COUNT transactions in database"
    fi
fi

# Create output directory if it doesn't exist
OUTPUT_DIR="$(dirname "$OUTPUT_FILE")"
mkdir -p "$OUTPUT_DIR"

# Change to project root directory
cd "$PROJECT_ROOT"

# Export dashboard data using Python
print_status "Exporting dashboard data to: $OUTPUT_FILE"

python3 -c "
import sys
sys.path.append('.')

from etl.loader import DatabaseLoader
import json
from datetime import datetime

try:
    with DatabaseLoader() as db_loader:
        dashboard_data = db_loader.export_dashboard_json()
    
    # Save to specified output file
    with open('$OUTPUT_FILE', 'w') as f:
        json.dump(dashboard_data, f, indent=2, default=str)
    
    print('Dashboard data exported successfully!')
    print(f'Output file: $OUTPUT_FILE')
    
    # Show summary
    summary = dashboard_data.get('summary', {})
    print(f'Total transactions: {summary.get(\"total_transactions\", 0)}')
    print(f'Total amount: {summary.get(\"total_amount\", 0)}')
    print(f'Success rate: {summary.get(\"success_rate\", 0):.1f}%')
    
except Exception as e:
    print(f'Error exporting dashboard data: {e}')
    sys.exit(1)
"

if [[ $? -eq 0 ]]; then
    print_success "Dashboard JSON exported successfully!"
    
    # Show file information
    if [[ -f "$OUTPUT_FILE" ]]; then
        FILE_SIZE=$(du -h "$OUTPUT_FILE" | cut -f1)
        print_status "Output file: $OUTPUT_FILE"
        print_status "File size: $FILE_SIZE"
        
        # Show last modified time
        LAST_MODIFIED=$(stat -f "%Sm" "$OUTPUT_FILE" 2>/dev/null || stat -c "%y" "$OUTPUT_FILE" 2>/dev/null)
        print_status "Last modified: $LAST_MODIFIED"
    fi
    
    # Show usage instructions
    echo ""
    print_status "You can now:"
    print_status "  1. View the dashboard by opening: $PROJECT_ROOT/index.html"
    print_status "  2. Start the API server: python3 -m api.app"
    print_status "  3. Use the JSON data in your applications"
    
else
    print_error "Failed to export dashboard JSON!"
    exit 1
fi

print_success "Script completed successfully!"
