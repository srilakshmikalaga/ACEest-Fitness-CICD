import os
import pytest
import tkinter as tk
from unittest import mock
from app import web_app
from app.ACEest_Fitness import FitnessTrackerApp

# --------------------------------------------------------------------
# ✅ Flask App Tests (web_app.py)
# --------------------------------------------------------------------
@pytest.fixture
def client():
    """Create Flask test client."""
    web_app.fitness_app.config["TESTING"] = True
    client = web_app.fitness_app.test_client()
    yield client


def test_home_route(client):
    """Check root endpoint returns welcome message."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.get_json()
    assert "Welcome" in data["message"]


def test_add_and_view_workouts(client):
    """Add a workout and retrieve it."""
    add_response = client.post("/add", json={"exercise": "Push-ups", "duration": 15})
    assert add_response.status_code == 201
    assert add_response.get_json()["message"] == "Workout added successfully"

    view_response = client.get("/view")
    assert view_response.status_code == 200
    data = view_response.get_json()
    assert isinstance(data, list)
    assert any("exercise" in item for item in data)


def test_add_workout_with_invalid_json(client):
    """Handle bad JSON gracefully."""
    response = client.post("/add", data="invalid data")
    assert response.status_code in (400, 415, 500)


def test_add_workout_with_get_method(client):
    """Ensure GET to /add is not allowed."""
    response = client.get("/add")
    assert response.status_code in (405, 404)


# --------------------------------------------------------------------
# ✅ Tkinter App Tests (ACEest_Fitness.py)
# --------------------------------------------------------------------
@pytest.fixture
def mock_tkinter_app(monkeypatch):
    """Fully mock Tkinter for Jenkins headless environment."""

    # ---- Fake minimal Tkinter window ----
    class MockTk:
        def __init__(self):
            self.tk = True  # Tkinter widgets expect this
        def withdraw(self): pass
        def destroy(self): pass
        def title(self, *args, **kwargs): pass
        def mainloop(self): pass

    # ---- Fake basic Tkinter widgets ----
    class MockWidget:
        def __init__(self, *args, **kwargs): pass
        def grid(self, *args, **kwargs): pass
        def pack(self, *args, **kwargs): pass
        def get(self): return ""
        def insert(self, *args, **kwargs): pass
        def delete(self, *args, **kwargs): pass

    # Monkeypatch all Tkinter GUI components to mock classes
    monkeypatch.setattr(tk, "Tk", MockTk)
    monkeypatch.setattr(tk, "Label", MockWidget)
    monkeypatch.setattr(tk, "Entry", MockWidget)
    monkeypatch.setattr(tk, "Button", MockWidget)

    # Now create your mock app
    app = FitnessTrackerApp(MockTk())
    app.workout_entry = mock.Mock()
    app.duration_entry = mock.Mock()
    yield app


def test_add_workout_valid(monkeypatch, mock_tkinter_app):
    """Add workout with valid data."""
    app = mock_tkinter_app
    app.workout_entry.get.return_value = "Running"
    app.duration_entry.get.return_value = "30"

    monkeypatch.setattr("app.ACEest_Fitness.messagebox.showinfo", lambda *a, **kw: None)
    app.add_workout()

    assert len(app.workouts) == 1
    assert app.workouts[0]["workout"] == "Running"
    assert app.workouts[0]["duration"] == 30


def test_add_workout_invalid_duration(monkeypatch, mock_tkinter_app):
    """Add workout with invalid duration input."""
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
    """Add workout without required inputs."""
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
    """View workouts when none exist."""
    app = mock_tkinter_app
    app.workouts = []
    called = {}

    def fake_info(title, msg):
        called["msg"] = msg

    monkeypatch.setattr("app.ACEest_Fitness.messagebox.showinfo", fake_info)
    app.view_workouts()
    assert "No workouts" in called["msg"]


def test_view_workouts_with_entries(monkeypatch, mock_tkinter_app):
    """View workouts with example data."""
    app = mock_tkinter_app
    app.workouts = [{"workout": "Yoga", "duration": 45}]
    called = {}

    def fake_info(title, msg):
        called["msg"] = msg

    monkeypatch.setattr("app.ACEest_Fitness.messagebox.showinfo", fake_info)
    app.view_workouts()
    assert "Yoga" in called["msg"]
def test_add_multiple_workouts(monkeypatch, mock_tkinter_app):
    """Test adding multiple workouts back-to-back."""
    app = mock_tkinter_app
    app.workout_entry.get.side_effect = ["Squats", "Plank"]
    app.duration_entry.get.side_effect = ["20", "5"]

    monkeypatch.setattr("app.ACEest_Fitness.messagebox.showinfo", lambda *a, **kw: None)
    for _ in range(2):
        app.add_workout()

    assert len(app.workouts) == 2
    assert any(w["workout"] == "Squats" for w in app.workouts)

def test_clear_entries_after_add(monkeypatch, mock_tkinter_app):
    """Ensure entries are cleared after adding a workout."""
    app = mock_tkinter_app
    app.workout_entry.get.return_value = "Push-ups"
    app.duration_entry.get.return_value = "15"

    cleared = {"called": False}
    def fake_delete(*a, **kw): cleared["called"] = True
    app.workout_entry.delete = fake_delete
    app.duration_entry.delete = fake_delete

    monkeypatch.setattr("app.ACEest_Fitness.messagebox.showinfo", lambda *a, **kw: None)
    app.add_workout()

    assert cleared["called"]

def test_view_workouts_display_format(monkeypatch, mock_tkinter_app):
    """Check formatting of workout list string."""
    app = mock_tkinter_app
    app.workouts = [
        {"workout": "Yoga", "duration": 30},
        {"workout": "Cycling", "duration": 45},
    ]
    called = {}

    def fake_info(title, msg):
        called["msg"] = msg

    monkeypatch.setattr("app.ACEest_Fitness.messagebox.showinfo", fake_info)
    app.view_workouts()

    assert "Yoga" in called["msg"]
    assert "Cycling" in called["msg"]
