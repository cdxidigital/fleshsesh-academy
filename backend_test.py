#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime
import uuid

class FleshseshAcademyAPITester:
    def __init__(self, base_url="https://body-training-lab.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        self.test_results.append({
            "test": name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if headers:
            test_headers.update(headers)
        
        if self.token and 'Authorization' not in test_headers:
            test_headers['Authorization'] = f'Bearer {self.token}'

        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=10)

            success = response.status_code == expected_status
            details = f"Status: {response.status_code}"
            
            if not success:
                try:
                    error_data = response.json()
                    details += f", Response: {error_data}"
                except:
                    details += f", Response: {response.text[:200]}"
            
            self.log_test(name, success, details)
            
            if success:
                try:
                    return response.json()
                except:
                    return {"status": "success"}
            return None

        except Exception as e:
            self.log_test(name, False, f"Exception: {str(e)}")
            return None

    def test_health_endpoints(self):
        """Test basic health endpoints"""
        print("\n🔍 Testing Health Endpoints...")
        self.run_test("API Root", "GET", "", 200)
        self.run_test("Health Check", "GET", "health", 200)

    def test_authentication(self):
        """Test user registration and login"""
        print("\n🔍 Testing Authentication...")
        
        # Generate unique test user
        test_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        test_password = "TestPass123!"
        test_name = "Test User"
        
        # Test registration
        register_data = {
            "email": test_email,
            "password": test_password,
            "name": test_name
        }
        
        result = self.run_test("User Registration", "POST", "auth/register", 200, register_data)
        if result and 'token' in result:
            self.token = result['token']
            self.user_id = result['user']['id']
            print(f"   Registered user: {test_email}")
        
        # Test login
        login_data = {
            "email": test_email,
            "password": test_password
        }
        
        result = self.run_test("User Login", "POST", "auth/login", 200, login_data)
        if result and 'token' in result:
            self.token = result['token']
            print(f"   Logged in user: {test_email}")
        
        # Test get current user
        if self.token:
            self.run_test("Get Current User", "GET", "auth/me", 200)
        
        # Test duplicate registration
        self.run_test("Duplicate Registration", "POST", "auth/register", 400, register_data)
        
        # Test invalid login
        invalid_login = {
            "email": test_email,
            "password": "wrongpassword"
        }
        self.run_test("Invalid Login", "POST", "auth/login", 401, invalid_login)

    def test_courses_endpoints(self):
        """Test courses-related endpoints"""
        print("\n🔍 Testing Courses Endpoints...")
        
        # Get all courses
        courses = self.run_test("Get All Courses", "GET", "courses", 200)
        
        if courses:
            print(f"   Found {len(courses)} courses")
            
            # Test individual course retrieval
            if len(courses) > 0:
                course_id = courses[0]['id']
                self.run_test("Get Single Course", "GET", f"courses/{course_id}", 200)
                
                # Test lessons for course
                self.run_test("Get Course Lessons", "GET", f"courses/{course_id}/lessons", 200)
        
        # Test non-existent course
        self.run_test("Get Non-existent Course", "GET", "courses/invalid-id", 404)

    def test_lessons_endpoints(self):
        """Test lesson-related endpoints"""
        print("\n🔍 Testing Lessons Endpoints...")
        
        # Test getting a specific lesson
        lesson_id = "lesson-1-1-1"  # From the sample data
        lesson = self.run_test("Get Single Lesson", "GET", f"lessons/{lesson_id}", 200)
        
        # Test lesson completion (requires authentication)
        if self.token and lesson:
            result = self.run_test("Complete Lesson", "POST", f"lessons/{lesson_id}/complete", 200)
            if result:
                print(f"   XP earned: {result.get('xp_earned', 0)}")
        
        # Test non-existent lesson
        self.run_test("Get Non-existent Lesson", "GET", "lessons/invalid-id", 404)

    def test_instructors_endpoints(self):
        """Test instructors-related endpoints"""
        print("\n🔍 Testing Instructors Endpoints...")
        
        # Get all instructors
        instructors = self.run_test("Get All Instructors", "GET", "instructors", 200)
        
        if instructors:
            print(f"   Found {len(instructors)} instructors")
            
            # Test individual instructor retrieval
            if len(instructors) > 0:
                instructor_id = instructors[0]['id']
                self.run_test("Get Single Instructor", "GET", f"instructors/{instructor_id}", 200)
        
        # Test non-existent instructor
        self.run_test("Get Non-existent Instructor", "GET", "instructors/invalid-id", 404)

    def test_unauthorized_access(self):
        """Test endpoints that require authentication without token"""
        print("\n🔍 Testing Unauthorized Access...")
        
        # Temporarily remove token
        temp_token = self.token
        self.token = None
        
        self.run_test("Unauthorized Get User", "GET", "auth/me", 401)
        self.run_test("Unauthorized Complete Lesson", "POST", "lessons/lesson-1-1-1/complete", 401)
        
        # Restore token
        self.token = temp_token

    def run_all_tests(self):
        """Run all test suites"""
        print("🚀 Starting Fleshsesh Academy API Tests")
        print(f"Testing against: {self.base_url}")
        print("=" * 60)
        
        try:
            self.test_health_endpoints()
            self.test_authentication()
            self.test_courses_endpoints()
            self.test_lessons_endpoints()
            self.test_instructors_endpoints()
            self.test_unauthorized_access()
            
        except Exception as e:
            print(f"❌ Test suite failed with exception: {e}")
        
        # Print summary
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return 0
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed")
            return 1

def main():
    tester = FleshseshAcademyAPITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())