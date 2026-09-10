"""Standalone entry point for the 3D Model Viewer.

Install with: pip install dash_model_viewer (already pinned in
requirements.txt). Run from the repo root:

    python examples/model_viewer_app.py     # then open http://127.0.0.1:8081

(8081, not the FlexLayout app's 8080, so the two can run side by side.)

Same component as the /model-viewer docs page
(docs/model_viewer/model_viewer.md) -- both import their layout from
docs/model_viewer/showcase.py. This file is the fully independent version:
its own Dash(__name__) instance, its own port, no imports from pages/,
components/ or run.py, the same shape as examples/flexlayout_app.py.

The repo root goes on sys.path so `docs.model_viewer` resolves from inside
examples/, and the app serves the repo-root assets/ folder, which is where
assets/model-viewer.css (the cyan accent, scoped to PAGE_CLASS) lives -- one
stylesheet for both entry points instead of a second copy kept in sync by
hand.
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

import dash_mantine_components as dmc  # noqa: E402
from dash import Dash  # noqa: E402

from docs.model_viewer.showcase import build_model_viewer_showcase, PAGE_CLASS  # noqa: E402

app = Dash(__name__, assets_folder=str(REPO_ROOT / "assets"))
app.title = "3D Model Viewer"
server = app.server

app.layout = dmc.MantineProvider(
    forceColorScheme="dark",
    theme={"primaryColor": "indigo"},
    children=dmc.Container(
        [
            dmc.Stack(
                [
                    dmc.Title("3D Model Viewer", order=1, mb=0),
                    dmc.Text(
                        "A small playground for dash_model_viewer (2plot.ai) -- Google's "
                        "<model-viewer> web component, wrapped for Dash.",
                        c="dimmed",
                        size="sm",
                    ),
                ],
                gap="xs",
                mb="lg",
            ),
            build_model_viewer_showcase(height="70vh"),
        ],
        size="lg",
        py="xl",
        fluid=True,
        className=PAGE_CLASS,
    ),
)


if __name__ == "__main__":
    print("3D Model Viewer starting on http://localhost:8081/")
    app.run(debug=False, port=8081)
