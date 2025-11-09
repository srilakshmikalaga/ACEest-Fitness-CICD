import pytest
import tkinter as tk
from unittest import mock
import importlib.util


# --- Dynamically load the module ---
def load_v121_module():
    spec = importlib.util.spec_from_file_location(
        "ACEest_Fitness_V1_2_1", "app/ACEest_Fitness-V1.2.1.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="session")
def fitness_app_module():
    return load_v121_module()


# --- Dummy widget safe for Jenkins ---
class DummyWidget:
    """Mock Tkinter widget for headless Jenkins CI testing."""
    def __init__(self, *a, **kw):
        self.tk = self
        self._w = "mock"
        self.children = {}
        self.master = None
        self._last_child_ids = {}
        self._title = ""
        self._geometry = ""

    # Window-level methods
    def title(self, text=None):
        if text:
            self._title = text
        return self._title

    def geometry(self, size=None):
        if size:
            self._geometry = size
        return self._geometry

    def resizable(self, *a, **kw): pass

    # Widget methods
    def pack(self, *a, **kw): pass
    def grid(self, *a, **kw): pass
    def place(self, *a, **kw): pass
    def destroy(self): pass
    def config(self, *a, **kw): pass
    def bind(self, *a, **kw): pass
    def add(self, *a, **kw): pass
    def winfo_children(self): return []

    # Tkinter internals
    def call(self, *a, **kw): return None
    def createcommand(self, *a, **kw): return None


@pytest.fixture
def app_instance(monkeypatch, fitness_app_module):
    """Create a FitnessTrackerApp instance safely."""
    monkeypatch.setattr(tk, "Tk", lambda: DummyWidget())
    monkeypatch.setattr(tk, "Frame", DummyWidget)
    monkeypatch.setattr(tk, "Label", DummyWidget)
    monkeypatch.setattr(tk, "Entry", DummyWidget)
    monkeypatch.setattr(tk, "Button", DummyWidget)
    monkeypatch.setattr(tk, "Toplevel", DummyWidget)
    monkeypatch.setattr(tk, "StringVar", lambda *a, **kw: mock.Mock(get=lambda: "Workout"))
    monkeypatch.setattr(tk, "END", None)
    monkeypatch.setattr("tkinter.ttk.Combobox", DummyWidget)
    monkeypatch.setattr("tkinter.ttk.Notebook", DummyWidget)
    monkeypatch.setattr("tkinter.ttk.Style", mock.Mock())
    monkeypatch.setattr("tkinter.messagebox.showinfo", mock.Mock())
    monkeypatch.setattr("tkinter.messagebox.showerror", mock.Mock())
    monkeypatch.setattr("matplotlib.backends.backend_tkagg.FigureCanvasTkAgg", mock.Mock())

    return fitness_app_module.FitnessTrackerApp(DummyWidget())


# --- Tests ---

def test_add_workout_valid(app_instance):
    """Check valid workout addition."""
    app_instance.workout_entry = mock.Mock(get=lambda: "Push-ups", delete=lambda *a, **kw: None)
    app_instance.duration_entry = mock.Mock(get=lambda: "15", delete=lambda *a, **kw: None)
    app_instance.category_var = mock.Mock(get=lambda: "Workout")

    app_instance.add_workout()
    assert len(app_instance.workouts["Workout"]) == 1
    assert app_instance.workouts["Workout"][0]["exercise"] == "Push-ups"


def test_add_workout_invalid_duration(app_instance):
    """Invalid duration should trigger error."""
    app_instance.workout_entry = mock.Mock(get=lambda: "Sit-ups", delete=lambda *a, **kw: None)
    app_instance.duration_entry = mock.Mock(get=lambda: "abc", delete=lambda *a, **kw: None)
    app_instance.category_var = mock.Mock(get=lambda: "Workout")

    with mock.patch("tkinter.messagebox.showerror") as err:
        app_instance.add_workout()
        err.assert_called_once()


def test_view_summary_no_entries(app_instance):
    """Show info when no sessions exist."""
    app_instance.workouts = {"Warm-up": [], "Workout": [], "Cool-down": []}
    with mock.patch("tkinter.messagebox.showinfo") as info:
        app_instance.view_summary()
        info.assert_called_once()


def test_update_progress_chart_no_crash(app_instance):
    """Ensure progress chart update runs without crashing."""
    app_instance.workouts = {
        "Warm-up": [{"duration": 5}],
        "Workout": [{"duration": 10}],
        "Cool-down": [{"duration": 5}],
    }
    app_instance.update_progress_charts()  # should not raise
