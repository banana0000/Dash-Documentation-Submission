"""Standalone entry point for the Excalidraw KPI-dashboard mockup.

Install with: pip install "git+https://github.com/pip-install-python/dash-excalidraw.git"
(newer than the 0.0.4 release on PyPI -- see components/excalidraw_kpi.py's
module docstring for why that matters). Run: python excalidraw_app.py, then
open http://127.0.0.1:8060

Same component as the /excalidraw page on the main site (pages/excalidraw.py)
-- both import their layout from components/excalidraw_kpi.py. This file is
the fully independent version: its own Dash(__name__) instance, its own
port, no imports from pages/ or run.py, the same shape as color_picker_app.py.
See components/excalidraw_kpi.py for the templates, the artboard/export
details, and the Personal Library contents.
"""
from dash import Dash, html

from components.excalidraw_kpi import DEFAULT_OPACITY, build_excalidraw

app = Dash(__name__)

app.layout = html.Div([
    html.H3("Excalidraw mockup", style={"margin": "0 0 0.75rem 0", "color": "#f8fafc"}),
    html.Div(build_excalidraw("excalidraw", DEFAULT_OPACITY), id="excalidraw-container"),
], style={"padding": "1rem", "backgroundColor": "#0f172a", "minHeight": "100vh"})


if __name__ == "__main__":
    app.run(debug=False, port=8060)
