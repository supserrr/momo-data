#!/bin/bash

# API Testing Script for Week 3 Assignment
# Generates test cases and screenshots for REST API

echo "REST API Testing Script"
echo "======================"

# Configuration
API_BASE_URL="http://localhost:8080"
USERNAME="admin"
PASSWORD="password"
SCREENSHOTS_DIR="screenshots"

# Create screenshots directory
mkdir -p $SCREENSHOTS_DIR

echo "Testing REST API endpoints..."
echo "Base URL: $API_BASE_URL"
echo "Authentication: $USERNAME:$PASSWORD"
echo ""

# Function to test endpoint and save output
test_endpoint() {
    local method=$1
    local endpoint=$2
    local data=$3
    local description=$4
    local output_file=$5
    
    echo "Testing: $description"
    echo "Endpoint: $method $endpoint"
    
    if [ "$method" = "GET" ]; then
        curl -u $USERNAME:$PASSWORD -s "$API_BASE_URL$endpoint" | jq '.' > "$SCREENSHOTS_DIR/$output_file"
    elif [ "$method" = "POST" ]; then
        curl -u $USERNAME:$PASSWORD -X POST -H "Content-Type: application/json" -d "$data" -s "$API_BASE_URL$endpoint" | jq '.' > "$SCREENSHOTS_DIR/$output_file"
    elif [ "$method" = "PUT" ]; then
        curl -u $USERNAME:$PASSWORD -X PUT -H "Content-Type: application/json" -d "$data" -s "$API_BASE_URL$endpoint" | jq '.' > "$SCREENSHOTS_DIR/$output_file"
    elif [ "$method" = "DELETE" ]; then
        curl -u $USERNAME:$PASSWORD -X DELETE -s "$API_BASE_URL$endpoint" | jq '.' > "$SCREENSHOTS_DIR/$output_file"
    fi
    
    echo "Result saved to: $SCREENSHOTS_DIR/$output_file"
    echo ""
}

# Function to test unauthorized access
test_unauthorized() {
    local endpoint=$1
    local description=$2
    local output_file=$3
    
    echo "Testing: $description"
    echo "Endpoint: GET $endpoint (no authentication)"
    
    curl -s "$API_BASE_URL$endpoint" | jq '.' > "$SCREENSHOTS_DIR/$output_file"
    
    echo "Result saved to: $SCREENSHOTS_DIR/$output_file"
    echo ""
}

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo "Warning: jq is not installed. Installing jq for JSON formatting..."
    if command -v brew &> /dev/null; then
        brew install jq
    elif command -v apt-get &> /dev/null; then
        sudo apt-get install jq
    else
        echo "Please install jq manually for JSON formatting"
        echo "Results will be saved without formatting"
    fi
fi

# Test 1: Successful GET with authentication
test_endpoint "GET" "/transactions" "" "Successful GET with authentication" "01_successful_get_with_auth.json"

# Test 2: Unauthorized request with wrong credentials
test_unauthorized "/transactions" "Unauthorized request with wrong credentials" "02_unauthorized_request.json"

# Test 3: Get specific transaction
test_endpoint "GET" "/transactions/1" "" "Get specific transaction by ID" "03_get_specific_transaction.json"

# Test 4: Create new transaction (POST)
test_endpoint "POST" "/transactions" '{
    "amount": 5000.0,
    "currency": "RWF",
    "transaction_type": "DEPOSIT",
    "category": "DEPOSIT_AGENT",
    "direction": "credit",
    "status": "SUCCESS",
    "sender_name": "Test Agent",
    "sender_phone": "+250788999999",
    "recipient_name": "Test User",
    "recipient_phone": "+250788111111",
    "date": "2024-01-01T15:00:00",
    "original_message": "Test transaction created via API"
}' "Successful POST - Create new transaction" "04_successful_post.json"

# Test 5: Update transaction (PUT)
test_endpoint "PUT" "/transactions/1" '{
    "amount": 2500.0,
    "status": "SUCCESS"
}' "Successful PUT - Update transaction" "05_successful_put.json"

# Test 6: Delete transaction (DELETE)
test_endpoint "DELETE" "/transactions/2" "" "Successful DELETE - Delete transaction" "06_successful_delete.json"

# Test 7: DSA - Linear Search
test_endpoint "GET" "/dsa/linear-search?id=1" "" "DSA - Linear Search Demo" "07_dsa_linear_search.json"

# Test 8: DSA - Dictionary Lookup
test_endpoint "GET" "/dsa/dictionary-lookup?id=1" "" "DSA - Dictionary Lookup Demo" "08_dsa_dictionary_lookup.json"

# Test 9: DSA - Performance Comparison
test_endpoint "GET" "/dsa/comparison" "" "DSA - Performance Comparison" "09_dsa_performance_comparison.json"

# Test 10: Error handling - Invalid transaction ID
test_endpoint "GET" "/transactions/999" "" "Error handling - Invalid transaction ID" "10_error_invalid_id.json"

# Test 11: Error handling - Invalid JSON in POST
echo "Testing: Error handling - Invalid JSON in POST"
echo "Endpoint: POST /transactions (invalid JSON)"
curl -u $USERNAME:$PASSWORD -X POST -H "Content-Type: application/json" -d '{"invalid": json}' -s "$API_BASE_URL/transactions" | jq '.' > "$SCREENSHOTS_DIR/11_error_invalid_json.json"
echo "Result saved to: $SCREENSHOTS_DIR/11_error_invalid_json.json"
echo ""

# Test 12: Error handling - Missing required fields
test_endpoint "POST" "/transactions" '{
    "amount": 1000.0
}' "Error handling - Missing required fields" "12_error_missing_fields.json"

echo "All tests completed!"
echo "===================="
echo "Screenshots saved in: $SCREENSHOTS_DIR/"
echo ""
echo "Files created:"
ls -la $SCREENSHOTS_DIR/
echo ""
echo "To view the results:"
echo "  cat $SCREENSHOTS_DIR/01_successful_get_with_auth.json"
echo "  cat $SCREENSHOTS_DIR/02_unauthorized_request.json"
echo "  cat $SCREENSHOTS_DIR/04_successful_post.json"
echo "  cat $SCREENSHOTS_DIR/05_successful_put.json"
echo "  cat $SCREENSHOTS_DIR/06_successful_delete.json"
echo "  cat $SCREENSHOTS_DIR/09_dsa_performance_comparison.json"
