import py_compile
from pathlib import Path


def test_dashboard_python_file_compiles():
    dashboard_path = Path("app/dashboard.py")

    assert dashboard_path.exists()

    py_compile.compile(
        str(dashboard_path),
        doraise=True,
    )


def test_dashboard_has_dynamic_ticker_section():
    dashboard_source = Path("app/dashboard.py").read_text()

    assert "def show_dynamic_ticker_section" in dashboard_source
    assert "Analyze Any SEC Ticker" in dashboard_source
    assert "Analyze ticker" in dashboard_source