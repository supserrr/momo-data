#!/bin/bash

# MoMo Frontend Server Script
# This script serves the frontend dashboard using Python's built-in HTTP server

set -e  # Exit on any error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DEFAULT_PORT=8000
DEFAULT_HOST="localhost"

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
    echo "  -p, --port PORT    Port number (default: $DEFAULT_PORT)"
    echo "  -h, --host HOST    Host address (default: $DEFAULT_HOST)"
    echo "  -a, --api          Start API server instead of static server"
    echo "  -b, --background   Run server in background"
    echo "  -k, --kill         Kill existing server on specified port"
    echo "  -s, --status       Check server status"
    echo "  --help             Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Start static server on default port"
    echo "  $0 -p 3000                           # Start on port 3000"
    echo "  $0 -a                                # Start API server"
    echo "  $0 -b -p 8000                        # Start in background on port 8000"
    echo "  $0 -k -p 8000                        # Kill server on port 8000"
}

# Default values
PORT=$DEFAULT_PORT
HOST=$DEFAULT_HOST
START_API=false
BACKGROUND=false
KILL_SERVER=false
CHECK_STATUS=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        -h|--host)
            HOST="$2"
            shift 2
            ;;
        -a|--api)
            START_API=true
            shift
            ;;
        -b|--background)
            BACKGROUND=true
            shift
            ;;
        -k|--kill)
            KILL_SERVER=true
            shift
            ;;
        -s|--status)
            CHECK_STATUS=true
            shift
            ;;
        --help)
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

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to kill server on port
kill_server() {
    local port=$1
    print_status "Checking for server on port $port..."
    
    if check_port $port; then
        print_status "Killing server on port $port..."
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
        sleep 2
        
        if check_port $port; then
            print_error "Failed to kill server on port $port"
            exit 1
        else
            print_success "Server on port $port killed successfully"
        fi
    else
        print_warning "No server found on port $port"
    fi
}

# Function to check server status
check_server_status() {
    local port=$1
    print_status "Checking server status on port $port..."
    
    if check_port $port; then
        print_success "Server is running on port $port"
        
        # Try to get server info
        local pid=$(lsof -ti:$port)
        if [[ -n "$pid" ]]; then
            print_status "Process ID: $pid"
            
            # Try to get process command
            local cmd=$(ps -p $pid -o comm= 2>/dev/null || echo "Unknown")
            print_status "Process: $cmd"
        fi
        
        # Test if server responds
        if curl -s -o /dev/null -w "%{http_code}" "http://$HOST:$port" | grep -q "200\|404"; then
            print_success "Server is responding to HTTP requests"
        else
            print_warning "Server is running but not responding to HTTP requests"
        fi
    else
        print_warning "No server found on port $port"
    fi
}

# Handle kill and status commands
if [[ "$KILL_SERVER" == true ]]; then
    kill_server $PORT
    exit 0
fi

if [[ "$CHECK_STATUS" == true ]]; then
    check_server_status $PORT
    exit 0
fi

# Validate port number
if ! [[ "$PORT" =~ ^[0-9]+$ ]] || [[ "$PORT" -lt 1 ]] || [[ "$PORT" -gt 65535 ]]; then
    print_error "Invalid port number: $PORT"
    print_status "Port must be a number between 1 and 65535"
    exit 1
fi

# Check if port is already in use
if check_port $PORT; then
    print_warning "Port $PORT is already in use"
    print_status "Use -k flag to kill existing server or choose a different port"
    exit 1
fi

# Change to project root directory
cd "$PROJECT_ROOT"

# Check if required files exist
if [[ "$START_API" == false ]]; then
    if [[ ! -f "index.html" ]]; then
        print_error "Frontend file not found: index.html"
        print_status "Please ensure you're in the correct project directory"
        exit 1
    fi
else
    if [[ ! -f "api/app.py" ]]; then
        print_error "API file not found: api/app.py"
        print_status "Please ensure you're in the correct project directory"
        exit 1
    fi
fi

# Start server
if [[ "$START_API" == true ]]; then
    print_status "Starting MoMo API server..."
    print_status "Host: $HOST"
    print_status "Port: $PORT"
    print_status "API Documentation: http://$HOST:$PORT/docs"
    
    if [[ "$BACKGROUND" == true ]]; then
        print_status "Starting server in background..."
        nohup python3 -m uvicorn api.app:app --host $HOST --port $PORT > data/logs/api_server.log 2>&1 &
        SERVER_PID=$!
        echo $SERVER_PID > data/logs/api_server.pid
        print_success "API server started in background (PID: $SERVER_PID)"
        print_status "Log file: data/logs/api_server.log"
        print_status "PID file: data/logs/api_server.pid"
    else
        print_status "Starting API server (Press Ctrl+C to stop)..."
        python3 -m uvicorn api.app:app --host $HOST --port $PORT
    fi
else
    print_status "Starting MoMo frontend server..."
    print_status "Host: $HOST"
    print_status "Port: $PORT"
    print_status "Dashboard: http://$HOST:$PORT"
    
    if [[ "$BACKGROUND" == true ]]; then
        print_status "Starting server in background..."
        nohup python3 -m http.server $PORT --bind $HOST > data/logs/frontend_server.log 2>&1 &
        SERVER_PID=$!
        echo $SERVER_PID > data/logs/frontend_server.pid
        print_success "Frontend server started in background (PID: $SERVER_PID)"
        print_status "Log file: data/logs/frontend_server.log"
        print_status "PID file: data/logs/frontend_server.pid"
    else
        print_status "Starting frontend server (Press Ctrl+C to stop)..."
        python3 -m http.server $PORT --bind $HOST
    fi
fi

if [[ "$BACKGROUND" == false ]]; then
    print_success "Server stopped"
fi
