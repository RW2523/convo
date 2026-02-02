#!/bin/bash

# Test script for PersonaPlex API

set -e

API_URL="${API_URL:-http://localhost:8000}"

echo "=========================================="
echo "Testing PersonaPlex API"
echo "API URL: $API_URL"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test 1: Root endpoint
echo -n "Test 1: Root endpoint... "
RESPONSE=$(curl -s "$API_URL/")
if echo "$RESPONSE" | grep -q "PersonaPlex"; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    echo "Response: $RESPONSE"
fi

# Test 2: Health check
echo -n "Test 2: Health check... "
RESPONSE=$(curl -s "$API_URL/health")
if echo "$RESPONSE" | grep -q "healthy\|model_loaded"; then
    echo -e "${GREEN}✓${NC}"
    echo "  Response: $RESPONSE"
else
    echo -e "${RED}✗${NC}"
    echo "  Response: $RESPONSE"
fi

# Test 3: Model info
echo -n "Test 3: Model info... "
RESPONSE=$(curl -s "$API_URL/info")
if echo "$RESPONSE" | grep -q "model_name\|loaded"; then
    echo -e "${GREEN}✓${NC}"
    echo "  Response: $RESPONSE"
else
    echo -e "${YELLOW}⚠${NC} Model may not be loaded"
    echo "  Response: $RESPONSE"
fi

# Test 4: Text generation
echo -n "Test 4: Text generation... "
RESPONSE=$(curl -s -X POST "$API_URL/generate" \
    -H "Content-Type: application/json" \
    -d '{"text": "Hello, how are you?"}')

if echo "$RESPONSE" | grep -q "output\|success"; then
    echo -e "${GREEN}✓${NC}"
    echo "  Response: $RESPONSE"
else
    echo -e "${RED}✗${NC}"
    echo "  Response: $RESPONSE"
fi

echo ""
echo "=========================================="
echo "API testing completed"
echo "=========================================="
