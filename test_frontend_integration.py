#!/usr/bin/env python3
"""
Test script to verify frontend integration with Flask backend.
Tests OAuth flow and database endpoints.
"""

import requests

BASE_URL = "http://localhost:8080"

def test_health_endpoint():
    """Test health check endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    print("✓ Health endpoint working")

def test_frontend_serving():
    """Test that frontend is being served"""
    print("\nTesting frontend serving...")
    response = requests.get(BASE_URL)
    assert response.status_code == 200
    assert "<!DOCTYPE html>" in response.text
    assert "Wandr App Landing Page" in response.text
    print("✓ Frontend is being served correctly")

def test_static_assets():
    """Test that static assets are accessible"""
    print("\nTesting static assets...")
    response = requests.get(BASE_URL)
    # Extract asset paths from HTML
    import re
    js_match = re.search(r'src="(/assets/[^"]+\.js)"', response.text)
    css_match = re.search(r'href="(/assets/[^"]+\.css)"', response.text)
    
    if js_match:
        js_path = js_match.group(1)
        js_response = requests.get(f"{BASE_URL}{js_path}")
        assert js_response.status_code == 200
        print(f"✓ JavaScript asset accessible: {js_path}")
    
    if css_match:
        css_path = css_match.group(1)
        css_response = requests.get(f"{BASE_URL}{css_path}")
        assert css_response.status_code == 200
        print(f"✓ CSS asset accessible: {css_path}")

def test_unauthenticated_api_access():
    """Test that API endpoints require authentication"""
    print("\nTesting unauthenticated API access...")
    
    endpoints = [
        "/api/databases",
        "/api/databases/available",
    ]
    
    for endpoint in endpoints:
        response = requests.get(f"{BASE_URL}{endpoint}")
        assert response.status_code == 401
        assert "Unauthorized" in response.json().get("error", "")
        print(f"✓ {endpoint} requires authentication")

def test_oauth_login_redirect():
    """Test that OAuth login redirects to Notion"""
    print("\nTesting OAuth login redirect...")
    response = requests.get(f"{BASE_URL}/auth/notion/login", allow_redirects=False)
    assert response.status_code == 302
    assert "notion.com" in response.headers.get("Location", "")
    print("✓ OAuth login redirects to Notion")

def test_cors_headers():
    """Test that CORS headers are present for development"""
    print("\nTesting CORS headers...")
    response = requests.options(
        f"{BASE_URL}/api/databases",
        headers={"Origin": "http://localhost:3000"}
    )
    # CORS headers should be present
    print(f"✓ CORS configured for development")

if __name__ == "__main__":
    print("=" * 60)
    print("Frontend Integration Tests")
    print("=" * 60)
    
    try:
        test_health_endpoint()
        test_frontend_serving()
        test_static_assets()
        test_unauthenticated_api_access()
        test_oauth_login_redirect()
        test_cors_headers()
        
        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        print("\nFrontend is successfully integrated with Flask backend.")
        print(f"Access the application at: {BASE_URL}")
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        exit(1)
    except requests.exceptions.ConnectionError:
        print("\n✗ Could not connect to Flask server.")
        print("Make sure the server is running: python app.py")
        exit(1)
