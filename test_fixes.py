#!/usr/bin/env python3
"""
Test script to verify CORS and account deletion fixes
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"
FRONTEND_ORIGIN = "http://localhost:8090"

def test_cors_headers():
    """Test that CORS headers are properly set"""
    print("Testing CORS headers...")
    
    # Test GET request
    response = requests.get(
        f"{BASE_URL}/accounts",
        headers={"Origin": FRONTEND_ORIGIN}
    )
    print(f"GET /accounts - Status: {response.status_code}")
    print(f"CORS headers: {response.headers.get('Access-Control-Allow-Origin')}")
    
    # Test OPTIONS request (preflight)
    response = requests.options(
        f"{BASE_URL}/accounts/1",
        headers={
            "Origin": FRONTEND_ORIGIN,
            "Access-Control-Request-Method": "DELETE"
        }
    )
    print(f"\nOPTIONS /accounts/1 - Status: {response.status_code}")
    print(f"CORS headers: {response.headers.get('Access-Control-Allow-Origin')}")
    print(f"Allowed methods: {response.headers.get('Access-Control-Allow-Methods')}")

def test_account_deletion():
    """Test account deletion with proper error handling"""
    print("\n\nTesting account deletion...")
    
    # First create a test account
    response = requests.post(
        f"{BASE_URL}/accounts",
        json={"username": "test_delete_account"},
        headers={"Origin": FRONTEND_ORIGIN}
    )
    
    if response.status_code == 200:
        account = response.json()
        account_id = account["id"]
        print(f"Created test account ID: {account_id}")
        
        # Now try to delete it
        response = requests.delete(
            f"{BASE_URL}/accounts/{account_id}",
            headers={"Origin": FRONTEND_ORIGIN}
        )
        print(f"DELETE /accounts/{account_id} - Status: {response.status_code}")
        print(f"CORS headers: {response.headers.get('Access-Control-Allow-Origin')}")
        
        if response.status_code == 204:
            print("Account deleted successfully (204 No Content)")
        else:
            print(f"Status: {response.status_code}, Body: {response.text}")
    else:
        print(f"Failed to create test account: {response.text}")

def test_rate_limiting():
    """Test rate limiting behavior"""
    print("\n\nTesting rate limiting...")
    
    # Make multiple requests to trigger rate limit
    for i in range(10):
        response = requests.post(
            f"{BASE_URL}/scrapes",
            json={
                "account_id": 1,
                "scrape_type": "both"
            },
            headers={"Origin": FRONTEND_ORIGIN}
        )
        print(f"Request {i+1} - Status: {response.status_code}")
        
        if response.status_code == 429:
            print(f"Rate limited! Retry-After: {response.headers.get('Retry-After')}")
            print(f"CORS headers: {response.headers.get('Access-Control-Allow-Origin')}")
            break

if __name__ == "__main__":
    print("Testing CORS and account deletion fixes...\n")
    test_cors_headers()
    test_account_deletion()
    test_rate_limiting()
    print("\nAll tests completed!")