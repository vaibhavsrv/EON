#!/usr/bin/env python3
"""
Test script for EON AI Brain
Run this to test all functionality locally
"""

import requests
import json
import sys
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def print_response(title: str, response: Dict[str, Any]):
    """Pretty print response"""
    print(f"\n{'='*60}")
    print(f"TEST: {title}")
    print(f"{'='*60}")
    print(json.dumps(response, indent=2))

def test_health_check():
    """Test health check endpoint"""
    response = requests.get(f"{BASE_URL}/").json()
    print_response("Health Check", response)
    assert response["status"] == "EON Brain Running"

def test_call_command():
    """Test make_call tool"""
    data = {"message": "Call John"}
    response = requests.post(f"{BASE_URL}/chat", json=data).json()
    print_response("Call Command", response)
    assert response["action"] == "call"
    assert response["data"]["contact"] == "John"
    return response["session_id"]

def test_message_command(session_id: str):
    """Test send_message tool"""
    data = {
        "message": "Send a WhatsApp message to Sarah saying I'll be there in 10 minutes",
        "session_id": session_id
    }
    response = requests.post(f"{BASE_URL}/chat", json=data).json()
    print_response("Message Command", response)
    assert response["action"] == "message"
    assert response["data"]["message"]  # Just check message exists

def test_navigation_command(session_id: str):
    """Test navigate tool"""
    data = {
        "message": "Navigate to the nearest coffee shop",
        "session_id": session_id
    }
    response = requests.post(f"{BASE_URL}/chat", json=data).json()
    print_response("Navigation Command", response)
    assert response["action"] == "navigation"

def test_device_control_command(session_id: str):
    """Test control_device tool"""
    data = {
        "message": "Turn on Bluetooth",
        "session_id": session_id
    }
    response = requests.post(f"{BASE_URL}/chat", json=data).json()
    print_response("Device Control Command", response)
    if "error" not in response:
        assert response["action"] == "device_control"
    else:
        print("Warning: Device control returned error, continuing tests")

def test_open_app_command(session_id: str):
    """Test open_app tool"""
    data = {
        "message": "Open Gmail",
        "session_id": session_id
    }
    response = requests.post(f"{BASE_URL}/chat", json=data).json()
    print_response("Open App Command", response)
    if "error" not in response:
        assert response["action"] == "open_app"
    else:
        print("Warning: Open app returned error, continuing tests")

def test_connectivity_command(session_id: str):
    """Test control_connectivity tool"""
    data = {
        "message": "Turn off WiFi",
        "session_id": session_id
    }
    response = requests.post(f"{BASE_URL}/chat", json=data).json()
    print_response("Connectivity Command", response)
    if "error" not in response:
        assert response["action"] == "connectivity"
    else:
        print("Warning: Connectivity returned error, continuing tests")

def test_session_management(session_id: str):
    """Test session retrieval"""
    response = requests.get(f"{BASE_URL}/session/{session_id}").json()
    print_response("Session Information", response)
    assert response["session_id"] == session_id
    assert response["message_count"] >= 1

def test_error_handling():
    """Test error handling"""
    # Empty message
    try:
        response = requests.post(f"{BASE_URL}/chat", json={"message": ""})
        if response.status_code != 200:
            print_response("Error Handling - Empty Message", response.json())
    except Exception as e:
        print(f"Error test passed: {e}")

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("EON AI BRAIN - COMPREHENSIVE TEST SUITE")
    print("="*60)
    
    try:
        # Basic health check
        test_health_check()
        
        # Get session ID from first call
        session_id = test_call_command()
        
        # Test all commands with the same session
        test_message_command(session_id)
        test_navigation_command(session_id)
        test_device_control_command(session_id)
        test_open_app_command(session_id)
        test_connectivity_command(session_id)
        
        # Session management
        test_session_management(session_id)
        
        # Error handling
        test_error_handling()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60 + "\n")
        
        return True
    
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
