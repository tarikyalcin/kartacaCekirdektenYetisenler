#!/bin/bash

# Test API endpoints with simple curl commands
echo "=== Testing API endpoints ==="

# Base URL
API_URL="http://localhost:8000/api"

# Get air quality data
echo -e "\n1. Testing /air-quality endpoint:"
curl -s "${API_URL}/air-quality/39.9334/32.8597?radius=50" | jq '.'

# Get anomalies
echo -e "\n2. Testing /anomalies endpoint:"
curl -s "${API_URL}/anomalies" | jq '.'

# Get pollution density
echo -e "\n3. Testing /pollution-density endpoint:"
curl -s "${API_URL}/pollution-density?parameter=pm25" | jq '.'

echo -e "\nTests completed!" 