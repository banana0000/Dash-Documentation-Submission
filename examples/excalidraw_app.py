"""Standalone entry point for the Excalidraw KPI-dashboard mockup.

Install with: pip install "git+https://github.com/pip-install-python/dash-excalidraw.git"
(newer than the 0.0.4 release on PyPI -- see docs/excalidraw/kpi_mockup.py's
module docstring for why that matters). Run from the repo root:

    python examples/excalidraw_app.py       # then open http://127.0.0.1:8060

Same component as the /excalidraw docs page (docs/excalidraw/excalidraw.md)
-- both import their layout from docs/excalidraw/kpi_mockup.py. This file is
the fully independent version: its own Dash(__name__) instance, its own
port, no imports from pages/, components/ or run.py. See the builder module
for the templates, the artboard/export details, and the Personal Library
contents.

The repo root goes on sys.path so `docs.excalidraw` resolves from inside
examples/, and the app serves the repo-root assets/ folder: the three
assets/excalidraw-*.css files are scoped to #excalidraw and this canvas
depends on them (the no-canvas-invert rule in particular).
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from dash import Dash, html  # noqa: E402

from docs.excalidraw.kpi_mockup import DEFAULT_OPACITY, build_excalidraw  # noqa: E402

app = Dash(__name__, assets_folder=str(REPO_ROOT / "assets"))
app.title = "Excalidraw KPI Mockup"
server = app.server

app.layout = html.Div([
    html.H3("Excalidraw mockup", style={"margin": "0 0 0.75rem 0", "color": "#f8fafc"}),
    html.Div(build_excalidraw("excalidraw", DEFAULT_OPACITY), id="excalidraw-container"),
], style={"padding": "1rem", "backgroundColor": "#0f172a", "minHeight": "100vh"})


if __name__ == "__main__":
    print("Excalidraw KPI Mockup starting on http://localhost:8060/")
    app.run(debug=False, port=8060)
