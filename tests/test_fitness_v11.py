import pytest
import tkinter as tk
from unittest import mock
import importlib.util

# Dynamically load your module
def load_v11_module():
    spec = importlib.util.spec_from_file_location(
        "ACEest_Fitness_V1_1", "app/ACEest_Fitness-V1.1.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

@pytest.fixture(scope="session")
def fitness_app_module():
    return load_v11_module()

# DummyWidget to safely replace Tkinter GUI elements
class DummyWidget:
    def __init__(self, *a, **kw):
        self.children = {}
        self._title = ""
    def title(self, val=None): self._title = val
    def geometry(self, *a, **kw): pass
    def resizable(self, *a, **kw): pass
    def pack(self, *a, **kw): pass
    def grid(self, *a, **kw): pass
    def config(self, *a, **kw): pass
    def destroy(self): pass
    def quit(self): pass
    def winfo_children(self): return []

@pytest.fixture
def app_instance(monkeypatch, fitness_app_module):
    """Creates a dummy FitnessTrackerApp instance (no real Tk window)."""
    monkeypatch.setattr(tk, "Tk", lambda: DummyWidget())
    monkeypatch.setattr(tk, "Frame", DummyWidget)
    monkeypatch.setattr(tk, "Label", DummyWidget)
    monkeypatch.setattr(tk, "Entry", DummyWidget)
    monkeypatch.setattr(tk, "Button", DummyWidget)
    monkeypatch.setattr(tk, "Toplevel", DummyWidget)
    monkeypatch.setattr(tk, "StringVar", lambda *a, **kw: mock.Mock(get=lambda: "Workout"))
    monkeypatch.setattr(tk, "END", None)
    monkeypatch.setattr("tkinter.ttk.Combobox", DummyWidget)
    monkeypatch.setattr("tkinter.messagebox.showinfo", mock.Mock())
    monkeypatch.setattr("tkinter.messagebox.showerror", mock.Mock())

    return fitness_app_module.FitnessTrackerApp(DummyWidget())

# -------------------- TESTS --------------------

def test_add_workout_valid(app_instance):
    app_instance.category_var = mock.Mock(get=lambda: "Workout")
    app_instance.workout_entry = mock.Mock(get=lambda: "Push-ups", delete=lambda *a, **kw: None)
    app_instance.duration_entry = mock.Mock(get=lambda: "15", delete=lambda *a, **kw: None)
    app_instance.add_workout()
    assert len(app_instance.workouts["Workout"]) == 1
    assert app_instance.workouts["Workout"][0]["exercise"] == "Push-ups"

def test_add_workout_invalid_input(app_instance):
    app_instance.workout_entry = mock.Mock(get=lambda: "", delete=lambda *a, **kw: None)
    app_instance.duration_entry = mock.Mock(get=lambda: "abc", delete=lambda *a, **kw: None)
    app_instance.category_var = mock.Mock(get=lambda: "Workout")
    with mock.patch("tkinter.messagebox.showerror") as err:
        app_instance.add_workout()
        err.assert_called()

def test_view_summary_no_data(app_instance):
    app_instance.workouts = {"Warm-up": [], "Workout": [], "Cool-down": []}
    with mock.patch("tkinter.messagebox.showinfo") as info:
        app_instance.view_summary()
        info.assert_called_once()

def test_view_summary_with_data(app_instance):
    app_instance.workouts["Workout"] = [
        {"exercise": "Plank", "duration": 10, "timestamp": "2025-11-09 10:00:00"}
    ]
    with mock.patch("tkinter.Toplevel", DummyWidget):
        app_instance.view_summary()
