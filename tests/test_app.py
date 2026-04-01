import copy
import pytest
from fastapi.testclient import TestClient

import src.app as app_module
from src.app import app

# ---------------------------------------------------------------------------
# Snapshot of the initial activities state taken at import time.
# Used by the reset_activities fixture to restore state between tests.
# ---------------------------------------------------------------------------
INITIAL_ACTIVITIES = copy.deepcopy(app_module.activities)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def client():
    """Return a synchronous TestClient for the FastAPI app."""
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore in-memory activities to their initial state before every test."""
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(INITIAL_ACTIVITIES))
    yield


# ---------------------------------------------------------------------------
# GET /activities
# ---------------------------------------------------------------------------

def test_get_activities_returns_all(client):
    # Arrange — initial state has 9 activities (set up by reset_activities)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == len(INITIAL_ACTIVITIES)
    assert "Chess Club" in data


# ---------------------------------------------------------------------------
# POST /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

def test_signup_success(client):
    # Arrange
    activity_name = "Chess Club"
    new_email = "newstudent@mergington.edu"
    before_count = len(app_module.activities[activity_name]["participants"])

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": new_email},
    )

    # Assert
    assert response.status_code == 200
    assert new_email in response.json()["message"]
    assert len(app_module.activities[activity_name]["participants"]) == before_count + 1
    assert new_email in app_module.activities[activity_name]["participants"]


def test_signup_activity_not_found(client):
    # Arrange
    activity_name = "Nonexistent Club"
    email = "student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_duplicate_returns_400(client):
    # Arrange — use an email already in the participants list
    activity_name = "Chess Club"
    existing_email = app_module.activities[activity_name]["participants"][0]

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": existing_email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


# ---------------------------------------------------------------------------
# DELETE /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

def test_unregister_success(client):
    # Arrange
    activity_name = "Chess Club"
    target_email = app_module.activities[activity_name]["participants"][0]
    before_count = len(app_module.activities[activity_name]["participants"])

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": target_email},
    )

    # Assert
    assert response.status_code == 200
    assert "Unregistered" in response.json()["message"]
    assert len(app_module.activities[activity_name]["participants"]) == before_count - 1
    assert target_email not in app_module.activities[activity_name]["participants"]


def test_unregister_participant_not_found(client):
    # Arrange
    activity_name = "Chess Club"
    unknown_email = "ghost@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": unknown_email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_unregister_activity_not_found(client):
    # Arrange
    activity_name = "Nonexistent Club"
    email = "student@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_case_insensitive(client):
    # Arrange — stored email is lowercase; send uppercase version
    activity_name = "Chess Club"
    stored_email = app_module.activities[activity_name]["participants"][0]
    upper_email = stored_email.upper()

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": upper_email},
    )

    # Assert
    assert response.status_code == 200
    assert stored_email not in app_module.activities[activity_name]["participants"]
