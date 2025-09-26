#!/bin/bash

# Run MoMo API Server
# Main API server for MoMo transaction processing and analytics

echo "Starting MoMo API Server..."
echo "=========================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if the API file exists
if [ ! -f "api/momo_api_server.py" ]; then
    echo "Error: api/momo_api_server.py not found"
    echo "Please run this script from the project root directory"
    exit 1
fi

# Set default port
PORT=${1:-8000}

echo "Port: $PORT"
echo "Authentication: Basic Auth (admin:password)"
echo ""
echo "This server includes ALL functionality:"
echo "  ✅ REST API with transaction processing"
echo "  ✅ Frontend dashboard with charts and analytics"
echo "  ✅ DSA requirements (linear search, dictionary lookup)"
echo "  ✅ Static file serving"
echo "  ✅ All endpoints on a single port"
echo ""
echo "Frontend: http://localhost:$PORT/"
echo "API Base: http://localhost:$PORT/api/"
echo "DSA Demo: http://localhost:$PORT/dsa/comparison"
echo ""
echo "Example Usage:"
echo "  curl -u admin:password http://localhost:$PORT/api/transactions"
echo "  curl -u admin:password http://localhost:$PORT/api/dashboard-data"
echo "  curl -u admin:password http://localhost:$PORT/dsa/comparison"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=============================================="

# Run the MoMo API server
python3 api/momo_api_server.py --port $PORT
