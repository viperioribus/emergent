#!/usr/bin/env python3
"""
Beach Informs Backend API Test Suite
Tests all authentication and data endpoints for the Beach Informs application.
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from frontend environment
BACKEND_URL = "https://lifeguard-mobile.preview.emergentagent.com/api"

class BeachInformsAPITester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.token = None
        self.test_results = []
        
    def log_test(self, test_name, success, message, details=None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name} - {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def test_user_registration(self):
        """Test user registration endpoint"""
        test_user = {
            "username": f"testuser_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "password": "securepassword123"
        }
        
        try:
            response = requests.post(f"{self.base_url}/auth/register", json=test_user, timeout=10)
            
            if response.status_code == 200:
                self.test_user = test_user  # Store for login test
                self.log_test("User Registration", True, "User registered successfully")
                return True
            else:
                self.log_test("User Registration", False, f"Registration failed with status {response.status_code}", response.text)
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("User Registration", False, "Network error during registration", str(e))
            return False
    
    def test_user_login(self):
        """Test user login endpoint"""
        if not hasattr(self, 'test_user'):
            self.log_test("User Login", False, "No test user available for login")
            return False
            
        try:
            response = requests.post(f"{self.base_url}/auth/login", json=self.test_user, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data and "token_type" in data:
                    self.token = data["access_token"]
                    self.log_test("User Login", True, "Login successful, JWT token received")
                    return True
                else:
                    self.log_test("User Login", False, "Login response missing token fields", data)
                    return False
            else:
                self.log_test("User Login", False, f"Login failed with status {response.status_code}", response.text)
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("User Login", False, "Network error during login", str(e))
            return False
    
    def test_get_beaches(self):
        """Test getting list of beaches"""
        if not self.token:
            self.log_test("Get Beaches", False, "No authentication token available")
            return False
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            response = requests.get(f"{self.base_url}/beaches", headers=headers, timeout=10)
            
            if response.status_code == 200:
                beaches = response.json()
                if isinstance(beaches, list) and len(beaches) >= 3:
                    # Check for expected beaches
                    beach_names = [beach.get("name", "") for beach in beaches]
                    expected_beaches = ["Santa Monica Beach", "Venice Beach", "Malibu Beach"]
                    
                    if all(name in beach_names for name in expected_beaches):
                        self.beaches = beaches  # Store for beach posts test
                        self.log_test("Get Beaches", True, f"Retrieved {len(beaches)} beaches including expected sample beaches")
                        return True
                    else:
                        self.log_test("Get Beaches", False, "Expected sample beaches not found", f"Found: {beach_names}")
                        return False
                else:
                    self.log_test("Get Beaches", False, "Invalid beaches response format or insufficient data", beaches)
                    return False
            else:
                self.log_test("Get Beaches", False, f"Get beaches failed with status {response.status_code}", response.text)
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("Get Beaches", False, "Network error getting beaches", str(e))
            return False
    
    def test_get_beach_posts(self):
        """Test getting beach posts for a specific beach"""
        if not self.token:
            self.log_test("Get Beach Posts", False, "No authentication token available")
            return False
            
        if not hasattr(self, 'beaches') or not self.beaches:
            self.log_test("Get Beach Posts", False, "No beaches available for testing")
            return False
            
        headers = {"Authorization": f"Bearer {self.token}"}
        beach_id = self.beaches[0]["id"]  # Use first beach
        
        try:
            response = requests.get(f"{self.base_url}/beach-posts/{beach_id}", headers=headers, timeout=10)
            
            if response.status_code == 200:
                posts = response.json()
                if isinstance(posts, list) and len(posts) >= 3:
                    # Check for expected posts
                    post_names = [post.get("name", "") for post in posts]
                    expected_posts = ["Post A", "Post B", "Post C"]
                    
                    if all(name in post_names for name in expected_posts):
                        self.log_test("Get Beach Posts", True, f"Retrieved {len(posts)} posts including expected sample posts")
                        return True
                    else:
                        self.log_test("Get Beach Posts", False, "Expected sample posts not found", f"Found: {post_names}")
                        return False
                else:
                    self.log_test("Get Beach Posts", False, "Invalid posts response format or insufficient data", posts)
                    return False
            else:
                self.log_test("Get Beach Posts", False, f"Get beach posts failed with status {response.status_code}", response.text)
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("Get Beach Posts", False, "Network error getting beach posts", str(e))
            return False
    
    def test_submit_inform2(self):
        """Test submitting Inform 2 data"""
        if not self.token:
            self.log_test("Submit Inform 2", False, "No authentication token available")
            return False
            
        headers = {"Authorization": f"Bearer {self.token}"}
        inform2_data = {
            "date": "2024-01-15",
            "beach_name": "Santa Monica Beach",
            "hour": 14,
            "minute": 30,
            "person_name": "John Doe",
            "age": 25,
            "postal_code": "90401",
            "incidences": ["swimming", "surfing"],
            "observations": "Clear weather, moderate waves, good visibility"
        }
        
        try:
            response = requests.post(f"{self.base_url}/inform2", json=inform2_data, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "id" in data:
                    self.log_test("Submit Inform 2", True, "Inform 2 submitted successfully")
                    return True
                else:
                    self.log_test("Submit Inform 2", False, "Invalid response format", data)
                    return False
            else:
                self.log_test("Submit Inform 2", False, f"Submit Inform 2 failed with status {response.status_code}", response.text)
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("Submit Inform 2", False, "Network error submitting Inform 2", str(e))
            return False
    
    def test_submit_inform4(self):
        """Test submitting Inform 4 data"""
        if not self.token:
            self.log_test("Submit Inform 4", False, "No authentication token available")
            return False
            
        headers = {"Authorization": f"Bearer {self.token}"}
        inform4_data = {
            "date": "2024-01-15",
            "beach_name": "Santa Monica Beach",
            "hour": 14,
            "minute": 30,
            "wind_speed": 12.5,
            "temperature": 22.3,
            "wave_height": 1.8
        }
        
        try:
            response = requests.post(f"{self.base_url}/inform4", json=inform4_data, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "id" in data:
                    self.log_test("Submit Inform 4", True, "Inform 4 submitted successfully")
                    return True
                else:
                    self.log_test("Submit Inform 4", False, "Invalid response format", data)
                    return False
            else:
                self.log_test("Submit Inform 4", False, f"Submit Inform 4 failed with status {response.status_code}", response.text)
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("Submit Inform 4", False, "Network error submitting Inform 4", str(e))
            return False
    
    def test_invalid_token(self):
        """Test API with invalid token"""
        headers = {"Authorization": "Bearer invalid_token_12345"}
        
        try:
            response = requests.get(f"{self.base_url}/beaches", headers=headers, timeout=10)
            
            if response.status_code == 401:
                self.log_test("Invalid Token Test", True, "API correctly rejected invalid token")
                return True
            else:
                self.log_test("Invalid Token Test", False, f"API should reject invalid token but returned status {response.status_code}", response.text)
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("Invalid Token Test", False, "Network error testing invalid token", str(e))
            return False
    
    def test_missing_fields_inform2(self):
        """Test Inform 2 with missing required fields"""
        if not self.token:
            self.log_test("Missing Fields Inform 2", False, "No authentication token available")
            return False
            
        headers = {"Authorization": f"Bearer {self.token}"}
        incomplete_data = {
            "date": "2024-01-15",
            "beach_name": "Santa Monica Beach"
            # Missing required fields: hour, minute, person_name, age, postal_code, incidences, observations
        }
        
        try:
            response = requests.post(f"{self.base_url}/inform2", json=incomplete_data, headers=headers, timeout=10)
            
            if response.status_code == 422:  # Validation error
                self.log_test("Missing Fields Inform 2", True, "API correctly rejected incomplete Inform 2 data")
                return True
            else:
                self.log_test("Missing Fields Inform 2", False, f"API should reject incomplete data but returned status {response.status_code}", response.text)
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("Missing Fields Inform 2", False, "Network error testing incomplete Inform 2", str(e))
            return False
    
    def test_no_auth_header(self):
        """Test protected endpoint without authentication header"""
        try:
            response = requests.get(f"{self.base_url}/beaches", timeout=10)
            
            if response.status_code == 403:  # Forbidden
                self.log_test("No Auth Header Test", True, "API correctly rejected request without auth header")
                return True
            else:
                self.log_test("No Auth Header Test", False, f"API should reject request without auth but returned status {response.status_code}", response.text)
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("No Auth Header Test", False, "Network error testing no auth header", str(e))
            return False
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print(f"🧪 Starting Beach Informs API Tests")
        print(f"🔗 Backend URL: {self.base_url}")
        print("=" * 60)
        
        # Core functionality tests
        tests = [
            self.test_user_registration,
            self.test_user_login,
            self.test_get_beaches,
            self.test_get_beach_posts,
            self.test_submit_inform2,
            self.test_submit_inform4,
            # Error case tests
            self.test_invalid_token,
            self.test_missing_fields_inform2,
            self.test_no_auth_header
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
        
        print("=" * 60)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Beach Informs API is working correctly.")
            return True
        else:
            print(f"⚠️  {total - passed} tests failed. Check the details above.")
            return False
    
    def get_summary(self):
        """Get a summary of test results"""
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        summary = {
            "total_tests": total,
            "passed": passed,
            "failed": total - passed,
            "success_rate": (passed / total * 100) if total > 0 else 0,
            "results": self.test_results
        }
        
        return summary

if __name__ == "__main__":
    tester = BeachInformsAPITester()
    success = tester.run_all_tests()
    
    # Print JSON summary for programmatic use
    print("\n" + "=" * 60)
    print("📋 JSON Summary:")
    print(json.dumps(tester.get_summary(), indent=2))
    
    sys.exit(0 if success else 1)