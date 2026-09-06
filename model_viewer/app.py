"""Standalone entry point for the 3D Model Viewer.

Install with: pip install dash_model_viewer (already pinned in requirements.txt).
Run: python model_viewer/app.py, then open http://127.0.0.1:8080

Same component as the /model-viewer page on the main site
(pages/model-viewer.py) -- both import their layout from
model_viewer/showcase.py. This file is the fully independent version: its
own Dash(__name__) instance, its own port, no imports from pages/ or
run.py, the same shape as dash_flow_app.py and excalidraw_app.py. Lives in
its own directory the same way roamly/ does, but its CSS (model-viewer.css)
stays in the repo-level assets/ folder since the embedded page needs it
there too -- so assets_folder is pointed back at that shared folder instead
of the (nonexistent) model_viewer/assets/.
"""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

import dash_mantine_components as dmc
from dash import Dash

from model_viewer.showcase import build_model_viewer_showcase, PAGE_CLASS

app = Dash(__name__, assets_folder=str(_REPO_ROOT / "assets"))
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
    print("3D Model Viewer starting on http://localhost:8080/")
    app.run(debug=False, port=8080)
