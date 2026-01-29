import copy
import os
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from app import activities, app

client = TestClient(app)
_original_activities = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(copy.deepcopy(_original_activities))
    yield
    activities.clear()
    activities.update(copy.deepcopy(_original_activities))


def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data


def test_signup_adds_participant():
    email = "test_student@mergington.edu"
    response = client.post(
        f"/activities/{'Chess%20Club'}/signup?email={email}"
    )
    assert response.status_code == 200

    updated = client.get("/activities").json()
    assert email in updated["Chess Club"]["participants"]


def test_signup_duplicate_returns_400():
    email = "duplicate@mergington.edu"
    client.post(f"/activities/{'Chess%20Club'}/signup?email={email}")
    response = client.post(
        f"/activities/{'Chess%20Club'}/signup?email={email}"
    )
    assert response.status_code == 400


def test_unregister_removes_participant():
    email = "remove_me@mergington.edu"
    client.post(f"/activities/{'Chess%20Club'}/signup?email={email}")

    response = client.delete(
        f"/activities/{'Chess%20Club'}/participants?email={email}"
    )
    assert response.status_code == 200

    updated = client.get("/activities").json()
    assert email not in updated["Chess Club"]["participants"]


def test_unregister_missing_participant_returns_404():
    response = client.delete(
        "/activities/Chess%20Club/participants?email=missing@mergington.edu"
    )
    assert response.status_code == 404
