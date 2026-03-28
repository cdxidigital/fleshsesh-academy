"""
Backend API Tests for Fleshsesh Academy eCampus
Tests: Encyclopedia, Stats, Labs, Courses, Instructors endpoints
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://body-training-lab.preview.emergentagent.com')

class TestHealthAndStats:
    """Health check and stats endpoint tests"""
    
    def test_health_endpoint(self):
        """Test /api/health returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("✓ Health endpoint working")
    
    def test_stats_endpoint(self):
        """Test /api/stats returns correct counts"""
        response = requests.get(f"{BASE_URL}/api/stats")
        assert response.status_code == 200
        data = response.json()
        
        # Verify stats match expected values
        assert data["total_lessons"] == 28, f"Expected 28 lessons, got {data['total_lessons']}"
        assert data["total_levels"] == 4, f"Expected 4 levels, got {data['total_levels']}"
        assert data["total_instructors"] == 8, f"Expected 8 instructors, got {data['total_instructors']}"
        assert "total_labs" in data
        assert "total_encyclopedia_entries" in data
        print(f"✓ Stats: {data['total_lessons']} lessons, {data['total_labs']} labs, {data['total_levels']} levels, {data['total_instructors']} faculty")


class TestEncyclopediaAPI:
    """Encyclopedia endpoint tests"""
    
    def test_get_all_encyclopedia_entries(self):
        """Test /api/encyclopedia returns all entries"""
        response = requests.get(f"{BASE_URL}/api/encyclopedia")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) > 0, "Encyclopedia should have entries"
        print(f"✓ Encyclopedia has {len(data)} entries")
        
        # Verify entry structure
        entry = data[0]
        required_fields = ["id", "term", "category", "definition", "context", "depth_level"]
        for field in required_fields:
            assert field in entry, f"Entry missing required field: {field}"
        print("✓ Encyclopedia entries have correct structure")
    
    def test_encyclopedia_entry_has_faculty_insight(self):
        """Test encyclopedia entries have lecturer_note (faculty insight)"""
        response = requests.get(f"{BASE_URL}/api/encyclopedia")
        assert response.status_code == 200
        data = response.json()
        
        # Check if any entry has lecturer_note
        entries_with_notes = [e for e in data if e.get("lecturer_note")]
        assert len(entries_with_notes) > 0, "At least one entry should have faculty insight"
        print(f"✓ {len(entries_with_notes)} entries have faculty insights")
    
    def test_encyclopedia_search(self):
        """Test encyclopedia search functionality"""
        response = requests.get(f"{BASE_URL}/api/encyclopedia", params={"search": "consent"})
        assert response.status_code == 200
        data = response.json()
        
        # Should return entries matching search
        assert isinstance(data, list)
        print(f"✓ Encyclopedia search returned {len(data)} results for 'consent'")
    
    def test_encyclopedia_category_filter(self):
        """Test encyclopedia category filter"""
        response = requests.get(f"{BASE_URL}/api/encyclopedia", params={"category": "Kink and BDSM"})
        assert response.status_code == 200
        data = response.json()
        
        # All returned entries should be in the specified category
        for entry in data:
            assert entry["category"] == "Kink and BDSM"
        print(f"✓ Category filter returned {len(data)} entries for 'Kink and BDSM'")


class TestLabsAPI:
    """Labs endpoint tests"""
    
    def test_get_all_labs(self):
        """Test /api/labs returns all hedonistic labs"""
        response = requests.get(f"{BASE_URL}/api/labs")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) == 14, f"Expected 14 labs, got {len(data)}"
        print(f"✓ Labs endpoint returns {len(data)} labs")
        
        # Verify lab structure
        lab = data[0]
        required_fields = ["id", "title", "level", "description", "duration_minutes"]
        for field in required_fields:
            assert field in lab, f"Lab missing required field: {field}"
        print("✓ Labs have correct structure")
    
    def test_labs_cover_all_levels(self):
        """Test labs exist for all 4 levels"""
        response = requests.get(f"{BASE_URL}/api/labs")
        assert response.status_code == 200
        data = response.json()
        
        levels = set(lab["level"] for lab in data)
        assert levels == {1, 2, 3, 4}, f"Labs should cover levels 1-4, got {levels}"
        print("✓ Labs cover all 4 levels")


class TestCoursesAPI:
    """Courses endpoint tests"""
    
    def test_get_all_courses(self):
        """Test /api/courses returns all 4 levels"""
        response = requests.get(f"{BASE_URL}/api/courses")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) == 4, f"Expected 4 courses, got {len(data)}"
        print(f"✓ Courses endpoint returns {len(data)} courses")
        
        # Verify course structure
        course = data[0]
        required_fields = ["id", "level", "title", "theme", "description", "lessons", "lead_instructors"]
        for field in required_fields:
            assert field in course, f"Course missing required field: {field}"
        print("✓ Courses have correct structure")
    
    def test_course_lesson_counts(self):
        """Test each course has 7 lessons"""
        response = requests.get(f"{BASE_URL}/api/courses")
        assert response.status_code == 200
        data = response.json()
        
        for course in data:
            assert course["lessons"] == 7, f"Course {course['title']} should have 7 lessons, got {course['lessons']}"
        print("✓ All courses have 7 lessons each (28 total)")
    
    def test_get_course_lessons(self):
        """Test /api/courses/{course_id}/lessons returns lessons"""
        # First get a course ID
        courses_response = requests.get(f"{BASE_URL}/api/courses")
        course_id = courses_response.json()[0]["id"]
        
        response = requests.get(f"{BASE_URL}/api/courses/{course_id}/lessons")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) == 7, f"Expected 7 lessons for course, got {len(data)}"
        print(f"✓ Course lessons endpoint returns {len(data)} lessons")


class TestInstructorsAPI:
    """Instructors endpoint tests"""
    
    def test_get_all_instructors(self):
        """Test /api/instructors returns all 8 AI faculty"""
        response = requests.get(f"{BASE_URL}/api/instructors")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) == 8, f"Expected 8 instructors, got {len(data)}"
        print(f"✓ Instructors endpoint returns {len(data)} AI faculty")
        
        # Verify instructor structure
        instructor = data[0]
        required_fields = ["id", "name", "title", "specialty", "background", "voice_style", "image_url"]
        for field in required_fields:
            assert field in instructor, f"Instructor missing required field: {field}"
        print("✓ Instructors have correct structure")
    
    def test_instructor_names(self):
        """Test all expected instructors are present"""
        response = requests.get(f"{BASE_URL}/api/instructors")
        assert response.status_code == 200
        data = response.json()
        
        expected_names = [
            "Dr. Nova Vale", "Coach Mira Sol", "Prof. Arden Moss", "Dr. Elise Hart",
            "Dr. Sera Quinn", "Kai Voss", "Talia Rhine", "Prof. Jun Hart"
        ]
        actual_names = [i["name"] for i in data]
        
        for name in expected_names:
            assert name in actual_names, f"Missing instructor: {name}"
        print("✓ All 8 AI faculty members present")


class TestAuthAPI:
    """Authentication endpoint tests"""
    
    def test_register_new_user(self):
        """Test user registration"""
        import uuid
        test_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": test_email,
            "password": "TestPass123!",
            "name": "Test User"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["email"] == test_email
        print(f"✓ User registration works (created {test_email})")
    
    def test_login_with_credentials(self):
        """Test user login"""
        # First register a user
        import uuid
        test_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        
        requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": test_email,
            "password": "TestPass123!",
            "name": "Test User"
        })
        
        # Then login
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": test_email,
            "password": "TestPass123!"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        print("✓ User login works")
    
    def test_invalid_login(self):
        """Test login with invalid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401
        print("✓ Invalid login returns 401")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
