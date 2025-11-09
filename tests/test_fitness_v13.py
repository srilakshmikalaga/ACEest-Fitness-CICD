import pytest
import tkinter as tk
from unittest import mock
import importlib.util


# --- Dynamically load ACEest_Fitness-V1.3 ---
def load_v13_module():
    spec = importlib.util.spec_from_file_location(
        "ACEest_Fitness_V1_3", "app/ACEest_Fitness-V1.3.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="session")
def fitness_app_module():
    return load_v13_module()


# --- DummyWidget for safe Tk mocking ---
class DummyWidget:
    def __init__(self, *a, **kw):
        self.tk = self
        self._w = "mock"
        self.children = {}
        self.master = None
        self._title = ""
        self._geometry = ""
        self._config = {}
        self._last_child_ids = {}

    def title(self, text=None):
        if text:
            self._title = text
        return self._title

    def geometry(self, size=None):
        if size:
            self._geometry = size
        return self._geometry

    def config(self, *a, **kw): self._config.update(kw)
    def resizable(self, *a, **kw): pass
    def pack(self, *a, **kw): pass
    def grid(self, *a, **kw): pass
    def place(self, *a, **kw): pass
    def destroy(self): pass
    def add(self, *a, **kw): pass
    def bind(self, *a, **kw): pass
    def winfo_children(self): return []
    def insert(self, *a, **kw): pass
    def tag_config(self, *a, **kw): pass
    def delete(self, *a, **kw): pass
    def call(self, *a, **kw): return None
    def createcommand(self, *a, **kw): return None


# --- Dummy Axes to fix spines issue ---
class DummyAxes:
    def __init__(self):
        self.spines = {"right": mock.Mock(), "top": mock.Mock()}
    def bar(self, *a, **kw): pass
    def pie(self, *a, **kw): pass
    def set_title(self, *a, **kw): pass
    def set_ylabel(self, *a, **kw): pass
    def tick_params(self, *a, **kw): pass
    def grid(self, *a, **kw): pass
    def set_facecolor(self, *a, **kw): pass
    def axis(self, *a, **kw): pass


class DummyFigure:
    def __init__(self, *a, **kw): pass
    def add_subplot(self, *a, **kw): return DummyAxes()
    def tight_layout(self, *a, **kw): pass


@pytest.fixture
def app_instance(monkeypatch, fitness_app_module):
    """Create a FitnessTrackerApp instance safely for CI."""
    monkeypatch.setattr(tk, "Tk", lambda: DummyWidget())
    monkeypatch.setattr(tk, "Frame", DummyWidget)
    monkeypatch.setattr(tk, "Label", DummyWidget)
    monkeypatch.setattr(tk, "Entry", DummyWidget)
    monkeypatch.setattr(tk, "Button", DummyWidget)
    monkeypatch.setattr(tk, "Toplevel", DummyWidget)
    monkeypatch.setattr(tk, "Text", DummyWidget)
    monkeypatch.setattr(tk, "Scrollbar", DummyWidget)
    monkeypatch.setattr(tk, "StringVar", lambda *a, **kw: mock.Mock(get=lambda: "Workout"))
    monkeypatch.setattr(tk, "END", None)

    # ttk + messagebox mocks
    monkeypatch.setattr("tkinter.ttk.Combobox", DummyWidget)
    monkeypatch.setattr("tkinter.ttk.Notebook", DummyWidget)
    monkeypatch.setattr(
        "tkinter.ttk.Style",
        mock.Mock(theme_use=lambda *a, **kw: None, configure=lambda *a, **kw: None, map=lambda *a, **kw: None),
    )
    monkeypatch.setattr("tkinter.ttk.Button", DummyWidget)
    monkeypatch.setattr("tkinter.messagebox.showinfo", mock.Mock())
    monkeypatch.setattr("tkinter.messagebox.showerror", mock.Mock())

    # Matplotlib + PDF mocks (with real Figure)
    monkeypatch.setattr("matplotlib.figure.Figure", DummyFigure)
    monkeypatch.setattr("matplotlib.backends.backend_tkagg.FigureCanvasTkAgg", mock.Mock())
    monkeypatch.setattr("reportlab.pdfgen.canvas.Canvas", mock.Mock())

    return fitness_app_module.FitnessTrackerApp(DummyWidget())


# -------------------- TESTS --------------------

def test_save_user_info_valid(app_instance):
    app_instance.name_entry = mock.Mock(get=lambda: "John Doe")
    app_instance.regn_entry = mock.Mock(get=lambda: "REG123")
    app_instance.age_entry = mock.Mock(get=lambda: "25")
    app_instance.gender_entry = mock.Mock(get=lambda: "M")
    app_instance.height_entry = mock.Mock(get=lambda: "175")
    app_instance.weight_entry = mock.Mock(get=lambda: "70")

    app_instance.save_user_info()
    assert "bmi" in app_instance.user_info
    assert app_instance.user_info["bmr"] > 1000




def test_add_workout_invalid(app_instance):
    app_instance.workout_entry = mock.Mock(get=lambda: "", delete=lambda *a, **kw: None)
    app_instance.duration_entry = mock.Mock(get=lambda: "abc", delete=lambda *a, **kw: None)
    app_instance.category_var = mock.Mock(get=lambda: "Workout")

    with mock.patch("tkinter.messagebox.showerror") as err:
        app_instance.add_workout()
        err.assert_called()


def test_view_summary_no_entries(app_instance):
    app_instance.workouts = {"Warm-up": [], "Workout": [], "Cool-down": []}
    with mock.patch("tkinter.messagebox.showinfo") as info:
        app_instance.view_summary()
        info.assert_called_once()


def test_export_weekly_report_safe(app_instance):
    app_instance.user_info = {
        "name": "John Doe", "regn_id": "R123", "age": 25, "gender": "M",
        "height": 175, "weight": 70, "bmi": 22.9, "bmr": 1650
    }
    app_instance.workouts = {"Warm-up": [], "Workout": [], "Cool-down": []}

    with mock.patch("reportlab.pdfgen.canvas.Canvas") as pdf_mock:
        app_instance.export_weekly_report()
        pdf_mock.assert_called_once()
