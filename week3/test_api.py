#!/usr/bin/env python3
"""
Simple test script for the Voice Assistant API
"""

import requests
import os
import sys
import time

API_BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check passed")
            print(f"   Status: {data.get('status')}")
            print(f"   Models loaded: {data.get('models_loaded')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_root_endpoint():
    """Test the root endpoint"""
    print("Testing root endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Root endpoint working")
            print(f"   Message: {data.get('message')}")
            return True
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Root endpoint failed: {e}")
        return False

def test_conversation_endpoints():
    """Test conversation history endpoints"""
    print("Testing conversation endpoints...")
    try:
        # Test getting history
        response = requests.get(f"{API_BASE_URL}/history", timeout=10)
        if response.status_code == 200:
            print("✅ History endpoint working")
        
        # Test clearing history
        response = requests.post(f"{API_BASE_URL}/clear_history", timeout=10)
        if response.status_code == 200:
            print("✅ Clear history endpoint working")
            return True
        else:
            print(f"❌ Clear history failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Conversation endpoints failed: {e}")
        return False

def wait_for_server(max_attempts=30):
    """Wait for the server to start"""
    print("Waiting for server to start...")
    for i in range(max_attempts):
        try:
            response = requests.get(f"{API_BASE_URL}/", timeout=2)
            if response.status_code == 200:
                print("✅ Server is ready")
                return True
        except requests.exceptions.RequestException:
            pass
        
        print(f"   Attempt {i+1}/{max_attempts}...")
        time.sleep(2)
    
    print("❌ Server failed to start within timeout")
    return False

def main():
    """Main test function"""
    print("Voice Assistant API Test Suite")
    print("=" * 40)
    
    # Check if server is running
    if not wait_for_server():
        print("\n❌ Server is not running. Please start it with:")
        print("python week_3_assignment_voice_agent_development.py")
        sys.exit(1)
    
    print()
    
    # Run tests
    tests_passed = 0
    total_tests = 3
    
    if test_root_endpoint():
        tests_passed += 1
    print()
    
    if test_health_check():
        tests_passed += 1
    print()
    
    if test_conversation_endpoints():
        tests_passed += 1
    print()
    
    # Summary
    print("=" * 40)
    print(f"Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("✅ All tests passed! API is working correctly.")
        print("\nTo test the chat endpoint, you'll need to send an audio file:")
        print("curl -X POST -F 'file=@your_audio.wav' http://localhost:8000/chat/")
    else:
        print("❌ Some tests failed. Check the output above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()