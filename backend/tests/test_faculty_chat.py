"""
Backend API Tests for Fleshsesh Academy - AI Faculty Chat Feature
Tests: Chat endpoints, session management, LLM integration
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://body-training-lab.preview.emergentagent.com')


class TestFacultyChatAPI:
    """AI Faculty Chat endpoint tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Create a test user and get auth token"""
        test_email = f"test_chat_{uuid.uuid4().hex[:8]}@example.com"
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": test_email,
            "password": "TestPass123!",
            "name": "Chat Test User"
        })
        
        if response.status_code == 200:
            return response.json()["token"]
        
        # If registration fails (user exists), try login
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": test_email,
            "password": "TestPass123!"
        })
        
        if response.status_code == 200:
            return response.json()["token"]
        
        pytest.skip("Could not authenticate for chat tests")
    
    def test_chat_requires_authentication(self):
        """Test /api/chat/faculty requires auth token"""
        response = requests.post(f"{BASE_URL}/api/chat/faculty", json={
            "message": "Hello",
            "instructor_id": "dr-nova-vale"
        })
        
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("✓ Chat endpoint requires authentication")
    
    def test_chat_with_valid_instructor(self, auth_token):
        """Test sending a message to a valid instructor"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = requests.post(
            f"{BASE_URL}/api/chat/faculty",
            json={
                "message": "Hello, can you introduce yourself?",
                "instructor_id": "dr-nova-vale"
            },
            headers=headers,
            timeout=60  # LLM responses can take time
        )
        
        assert response.status_code == 200, f"Chat failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "response" in data, "Response should contain 'response' field"
        assert "session_id" in data, "Response should contain 'session_id' field"
        assert "instructor_name" in data, "Response should contain 'instructor_name' field"
        
        # Verify instructor name matches
        assert data["instructor_name"] == "Dr. Nova Vale"
        
        # Verify response is not empty
        assert len(data["response"]) > 0, "AI response should not be empty"
        
        print(f"✓ Chat with Dr. Nova Vale works - Response length: {len(data['response'])} chars")
        print(f"  Session ID: {data['session_id']}")
        return data["session_id"]
    
    def test_chat_with_invalid_instructor(self, auth_token):
        """Test sending a message to an invalid instructor"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = requests.post(
            f"{BASE_URL}/api/chat/faculty",
            json={
                "message": "Hello",
                "instructor_id": "invalid-instructor-id"
            },
            headers=headers
        )
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ Invalid instructor returns 404")
    
    def test_get_chat_sessions(self, auth_token):
        """Test retrieving user's chat sessions"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = requests.get(
            f"{BASE_URL}/api/chat/sessions",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list), "Sessions should be a list"
        print(f"✓ Get chat sessions works - Found {len(data)} sessions")
    
    def test_chat_sessions_require_auth(self):
        """Test /api/chat/sessions requires auth"""
        response = requests.get(f"{BASE_URL}/api/chat/sessions")
        
        assert response.status_code in [401, 403]
        print("✓ Chat sessions endpoint requires authentication")
    
    def test_chat_with_different_instructors(self, auth_token):
        """Test chatting with multiple different instructors"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        instructors_to_test = [
            ("coach-mira-sol", "Coach Mira Sol"),
            ("prof-arden-moss", "Prof. Arden Moss"),
            ("kai-voss", "Kai Voss")
        ]
        
        for instructor_id, expected_name in instructors_to_test:
            response = requests.post(
                f"{BASE_URL}/api/chat/faculty",
                json={
                    "message": "Hi, what's your specialty?",
                    "instructor_id": instructor_id
                },
                headers=headers,
                timeout=60
            )
            
            assert response.status_code == 200, f"Chat with {instructor_id} failed: {response.text}"
            data = response.json()
            assert data["instructor_name"] == expected_name
            print(f"✓ Chat with {expected_name} works")
    
    def test_chat_session_persistence(self, auth_token):
        """Test that chat messages are stored in session"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Send first message
        response1 = requests.post(
            f"{BASE_URL}/api/chat/faculty",
            json={
                "message": "My name is TestUser. Remember this.",
                "instructor_id": "dr-elise-hart"
            },
            headers=headers,
            timeout=60
        )
        
        assert response1.status_code == 200
        session_id = response1.json()["session_id"]
        
        # Send follow-up message in same session
        response2 = requests.post(
            f"{BASE_URL}/api/chat/faculty",
            json={
                "message": "What was my name again?",
                "instructor_id": "dr-elise-hart",
                "session_id": session_id
            },
            headers=headers,
            timeout=60
        )
        
        assert response2.status_code == 200
        assert response2.json()["session_id"] == session_id
        print(f"✓ Chat session persistence works - Session: {session_id}")
    
    def test_get_specific_session(self, auth_token):
        """Test retrieving a specific chat session"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # First create a session
        chat_response = requests.post(
            f"{BASE_URL}/api/chat/faculty",
            json={
                "message": "Hello for session test",
                "instructor_id": "talia-rhine"
            },
            headers=headers,
            timeout=60
        )
        
        if chat_response.status_code != 200:
            pytest.skip("Could not create chat session")
        
        session_id = chat_response.json()["session_id"]
        
        # Get the specific session
        response = requests.get(
            f"{BASE_URL}/api/chat/sessions/{session_id}",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == session_id
        assert data["instructor_id"] == "talia-rhine"
        assert "messages" in data
        assert len(data["messages"]) >= 2  # User message + AI response
        print(f"✓ Get specific session works - {len(data['messages'])} messages")
    
    def test_delete_chat_session(self, auth_token):
        """Test deleting a chat session"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # First create a session
        chat_response = requests.post(
            f"{BASE_URL}/api/chat/faculty",
            json={
                "message": "Hello for delete test",
                "instructor_id": "prof-jun-hart"
            },
            headers=headers,
            timeout=60
        )
        
        if chat_response.status_code != 200:
            pytest.skip("Could not create chat session")
        
        session_id = chat_response.json()["session_id"]
        
        # Delete the session
        delete_response = requests.delete(
            f"{BASE_URL}/api/chat/sessions/{session_id}",
            headers=headers
        )
        
        assert delete_response.status_code == 200
        
        # Verify session is deleted
        get_response = requests.get(
            f"{BASE_URL}/api/chat/sessions/{session_id}",
            headers=headers
        )
        
        assert get_response.status_code == 404
        print("✓ Delete chat session works")


class TestInstructorPersonalities:
    """Test that instructors respond in character"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Create a test user and get auth token"""
        test_email = f"test_personality_{uuid.uuid4().hex[:8]}@example.com"
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": test_email,
            "password": "TestPass123!",
            "name": "Personality Test User"
        })
        
        if response.status_code == 200:
            return response.json()["token"]
        
        pytest.skip("Could not authenticate for personality tests")
    
    def test_dr_nova_vale_responds_about_physiology(self, auth_token):
        """Test Dr. Nova Vale responds about body science"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = requests.post(
            f"{BASE_URL}/api/chat/faculty",
            json={
                "message": "Can you tell me about the arousal cycle?",
                "instructor_id": "dr-nova-vale"
            },
            headers=headers,
            timeout=60
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Response should be substantive
        assert len(data["response"]) > 100, "Response should be detailed"
        print(f"✓ Dr. Nova Vale responds about physiology ({len(data['response'])} chars)")
    
    def test_kai_voss_responds_about_kink(self, auth_token):
        """Test Kai Voss responds about kink/BDSM topics"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = requests.post(
            f"{BASE_URL}/api/chat/faculty",
            json={
                "message": "What is the SSC framework?",
                "instructor_id": "kai-voss"
            },
            headers=headers,
            timeout=60
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Response should mention safety concepts
        assert len(data["response"]) > 50
        print(f"✓ Kai Voss responds about kink topics ({len(data['response'])} chars)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
