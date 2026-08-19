"""
Pytest configuration and fixtures for FastAPI tests.

Provides test client and app fixtures along with test data setup.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """
    Fixture: Create a TestClient for making requests to the FastAPI app.
    
    Returns:
        TestClient: A test client connected to the app instance
    """
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """
    Fixture: Reset activities to a known state before each test.
    
    This ensures test isolation by providing a fresh in-memory database
    for every test. The fixture automatically runs for all tests.
    
    Yields:
        None (but ensures activities dict is reset)
    """
    # Store original state
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }
    
    # Clear existing activities and reset to known state
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Cleanup after test (optional, since next test will reset anyway)
    activities.clear()
    activities.update(original_activities)
