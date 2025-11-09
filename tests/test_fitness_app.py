import pytest
import tkinter as tk
from unittest import mock
from app import web_app
from app.ACEest_Fitness import FitnessTrackerApp

# --------------------------------------------------------------------
# ✅ TESTS FOR THE FLASK APP (web_app.py)
# --------------------------------------------------------------------
@pytest.fixture
def client():
    """Fixture to create a Flask test client."""
    web_app.fitness_app.config['TESTING'] = True
    client = web_app.fitness_app.test_client()
    yield client


def test_home_route(client):
    """Test root endpoint returns welcome message."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.get_json()
    assert "Welcome" in data["message"]


def test_add_and_view_workouts(client):
    """Test adding a workout and viewing it back."""
    add_response = client.post("/add", json={"exercise": "Push-ups", "duration": 15})
    assert add_response.status_code == 201
    assert add_response.get_json()["message"] == "Workout added successfully"

    view_response = client.get("/view")
    assert view_response.status_code == 200
    data = view_response.get_json()
    assert isinstance(data, list)
    assert any("exercise" in item for item in data)


def test_add_workout_with_invalid_json(client):
    """Ensure app handles invalid JSON gracefully."""
    response = client.post("/add", data="bad data")
    assert response.status_code in (400, 415, 500)


def test_add_workout_with_get_method(client):
    """Ensure GET to /add route is not allowed."""
    response = client.get("/add")
    assert response.status_code in (405, 404)  # Method Not Allowed or Not Found


# --------------------------------------------------------------------
# ✅ TESTS FOR THE TKINTER DESKTOP APP (ACEest_Fitness.py)
# --------------------------------------------------------------------
@pytest.fixture
def mock_tkinter_app(monkeypatch):
    """Create a real hidden Tkinter app for testing without visible GUI."""
    root = tk.Tk()
    root.withdraw()  # Hide window for headless CI/CD

    app = FitnessTrackerApp(root)
    app.workout_entry = mock.Mock()
    app.duration_entry = mock.Mock()

    yield app

    # Cleanup after each test
    root.destroy()


def test_add_workout_valid(monkeypatch, mock_tkinter_app):
    """Add a workout with valid inputs."""
    app = mock_tkinter_app
    app.workout_entry.get.return_value = "Running"
    app.duration_entry.get.return_value = "30"

    monkeypatch.setattr("app.ACEest_Fitness.messagebox.showinfo", lambda *a, **kw: None)
    app.add_workout()

    assert len(app.workouts) == 1
    assert app.workouts[0]["workout"] == "Running"
    assert app.workouts[0]["duration"] == 30


def test_add_workout_invalid_duration(monkeypatch, mock_tkinter_app):
    """Add workout with invalid duration should show error."""
    app = mock_tkinter_app
    app.workout_entry.get.return_value = "Cycling"
    app.duration_entry.get.return_value = "abc"

    called = {}

    def fake_error(title, msg):
        called["msg"] = msg

    monkeypatch.setattr("app.ACEest_Fitness.messagebox.showerror", fake_error)
    app.add_workout()
    assert "number" in called["msg"]


def test_add_workout_missing_inputs(monkeypatch, mock_tkinter_app):
    """Add workout without filling fields."""
    app = mock_tkinter_app
    app.workout_entry.get.return_value = ""
    app.duration_entry.get.return_value = ""

    called = {}

    def fake_error(title, msg):
        called["msg"] = msg

    monkeypatch.setattr("app.ACEest_Fitness.messagebox.showerror", fake_error)
    app.add_workout()
    assert "Please enter" in called["msg"]


def test_view_workouts_no_entries(monkeypatch, mock_tkinter_app):
    """View workouts when none are present."""
    app = mock_tkinter_app
    app.workouts = []
    called = {}

    def fake_info(title, msg):
        called["msg"] = msg

    monkeypatch.setattr("app.ACEest_Fitness.messagebox.showinfo", fake_info)
    app.view_workouts()
    assert "No workouts" in called["msg"]


def test_view_workouts_with_entries(monkeypatch, mock_tkinter_app):
    """View workouts with sample data."""
    app = mock_tkinter_app
    app.workouts = [{"workout": "Yoga", "duration": 45}]
    called = {}

    def fake_info(title, msg):
        called["msg"] = msg

    monkeypatch.setattr("app.ACEest_Fitness.messagebox.showinfo", fake_info)
    app.view_workouts()
    assert "Yoga" in called["msg"]
