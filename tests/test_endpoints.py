"""
FastAPI endpoint tests using the AAA (Arrange-Act-Assert) pattern.

Tests organized by endpoint:
- GET /activities
- POST /activities/{activity_name}/signup
- DELETE /activities/{activity_name}/unregister
- GET /
"""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_all_activities_returns_200(self, client):
        """
        Test: GET /activities returns 200 status code
        
        Arrange: No setup needed (uses fixtures)
        Act: Make GET request to /activities
        Assert: Status code is 200
        """
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200

    def test_get_activities_returns_all_activities(self, client):
        """
        Test: GET /activities returns all activities in response
        
        Arrange: Fixtures provide 3 activities
        Act: Make GET request to /activities
        Assert: Response contains all 3 activity names
        """
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities

    def test_get_activities_response_structure(self, client):
        """
        Test: GET /activities returns correct data structure for each activity
        
        Arrange: Fixtures provide activities with known structure
        Act: Make GET request to /activities
        Assert: Each activity has required fields (description, schedule, max_participants, participants)
        """
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success_adds_participant(self, client):
        """
        Test: Successful signup adds participant to activity
        
        Arrange: Get initial participant count for Chess Club
        Act: Sign up a new student
        Assert: Participant is added to the list
        """
        # Arrange
        activity_name = "Chess Club"
        new_email = "alice@mergington.edu"
        initial_response = client.get("/activities")
        initial_participants = initial_response.json()[activity_name]["participants"]
        
        # Act
        signup_response = client.post(
            f"/activities/{activity_name}/signup?email={new_email}"
        )
        
        # Assert
        assert signup_response.status_code == 200
        verify_response = client.get("/activities")
        updated_participants = verify_response.json()[activity_name]["participants"]
        assert new_email in updated_participants
        assert len(updated_participants) == len(initial_participants) + 1

    def test_signup_success_returns_message(self, client):
        """
        Test: Successful signup returns success message
        
        Arrange: Prepare valid activity and email
        Act: Make signup request
        Assert: Response contains success message
        """
        # Arrange
        activity_name = "Programming Class"
        new_email = "bob@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={new_email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert "message" in response.json()
        assert f"Signed up {new_email}" in response.json()["message"]

    def test_signup_duplicate_returns_400(self, client):
        """
        Test: Attempting to signup twice for same activity returns 400
        
        Arrange: One participant already signed up (from fixtures)
        Act: Try to signup the same person again
        Assert: Status 400 with 'already signed up' error message
        """
        # Arrange
        activity_name = "Chess Club"
        existing_email = "michael@mergington.edu"  # Already in Chess Club
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={existing_email}"
        )
        
        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student is already signed up"

    def test_signup_nonexistent_activity_returns_404(self, client):
        """
        Test: Attempting to signup for non-existent activity returns 404
        
        Arrange: Prepare signup for activity that doesn't exist
        Act: Make signup request for invalid activity
        Assert: Status 404 with 'Activity not found' error message
        """
        # Arrange
        invalid_activity = "NonExistent Club"
        email = "test@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{invalid_activity}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_participant_count_updates(self, client):
        """
        Test: After signup, GET /activities reflects updated participant count
        
        Arrange: Get initial participant count for an activity
        Act: Sign up a new participant
        Assert: GET /activities shows updated count
        """
        # Arrange
        activity_name = "Gym Class"
        new_email = "charlie@mergington.edu"
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity_name]["participants"])
        
        # Act
        client.post(f"/activities/{activity_name}/signup?email={new_email}")
        
        # Assert
        updated_response = client.get("/activities")
        updated_count = len(updated_response.json()[activity_name]["participants"])
        assert updated_count == initial_count + 1


class TestUnregisterEndpoint:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_success_removes_participant(self, client):
        """
        Test: Successful unregister removes participant from activity
        
        Arrange: Identify existing participant in activity
        Act: Unregister the participant
        Assert: Participant is removed from participants list
        """
        # Arrange
        activity_name = "Chess Club"
        email_to_remove = "michael@mergington.edu"  # Exists in Chess Club
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email_to_remove}"
        )
        
        # Assert
        assert response.status_code == 200
        verify_response = client.get("/activities")
        participants = verify_response.json()[activity_name]["participants"]
        assert email_to_remove not in participants

    def test_unregister_success_returns_message(self, client):
        """
        Test: Successful unregister returns success message
        
        Arrange: Prepare valid activity and existing participant
        Act: Make unregister request
        Assert: Response contains success message
        """
        # Arrange
        activity_name = "Programming Class"
        email = "emma@mergington.edu"  # Exists in Programming Class
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert "message" in response.json()
        assert f"Unregistered {email}" in response.json()["message"]

    def test_unregister_not_signed_up_returns_400(self, client):
        """
        Test: Attempting to unregister non-participant returns 400
        
        Arrange: Prepare email that's not signed up for activity
        Act: Try to unregister someone not in participants list
        Assert: Status 400 with 'not signed up' error message
        """
        # Arrange
        activity_name = "Chess Club"
        email_not_in_activity = "notmember@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email_not_in_activity}"
        )
        
        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student is not signed up"

    def test_unregister_nonexistent_activity_returns_404(self, client):
        """
        Test: Attempting to unregister from non-existent activity returns 404
        
        Arrange: Prepare unregister for activity that doesn't exist
        Act: Make unregister request for invalid activity
        Assert: Status 404 with 'Activity not found' error message
        """
        # Arrange
        invalid_activity = "NonExistent Club"
        email = "test@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{invalid_activity}/unregister?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_participant_count_updates(self, client):
        """
        Test: After unregister, GET /activities reflects updated participant count
        
        Arrange: Get initial participant count for an activity
        Act: Unregister an existing participant
        Assert: GET /activities shows updated count
        """
        # Arrange
        activity_name = "Chess Club"
        email = "daniel@mergington.edu"  # Exists in Chess Club
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity_name]["participants"])
        
        # Act
        client.delete(f"/activities/{activity_name}/unregister?email={email}")
        
        # Assert
        updated_response = client.get("/activities")
        updated_count = len(updated_response.json()[activity_name]["participants"])
        assert updated_count == initial_count - 1


class TestRootRedirect:
    """Tests for GET / endpoint"""

    def test_root_redirects_to_static_index(self, client):
        """
        Test: GET / redirects to static index page
        
        Arrange: Prepare request to root endpoint
        Act: Make GET request to /
        Assert: Response is a redirect (follow_redirects=False to check redirect)
        """
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307  # Temporary redirect
        assert "/static/index.html" in response.headers["location"]
