import json
import pytest
from app.web_app import fitness_app as app


@pytest.fixture
def client():
    app.testing = True
    return app.test_client()

def test_homepage(client):
    rv = client.get('/')
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert data.get("message") == "Welcome to ACEest Fitness Web API"

def test_add_and_view_workout(client):
    # Add a workout
    new_workout = {"workout": "Push-ups", "duration": 10}
    rv = client.post('/add', data=json.dumps(new_workout),
                     content_type='application/json')
    assert rv.status_code == 201
    data = json.loads(rv.data)
    assert data.get("message") == "Workout added successfully"

    # View all workouts
    rv2 = client.get('/view')
    assert rv2.status_code == 200
    data2 = json.loads(rv2.data)
    assert {"workout": "Push-ups", "duration": 10} in data2
