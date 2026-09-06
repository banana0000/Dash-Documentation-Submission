"""Standalone entry point for the 3D Model Viewer.

Install with: pip install -r model_viewer/requirements.txt (or, running
inside the main repo's own env, its deps are already pinned in the
repo-root requirements.txt too).
Run: python model_viewer/app.py, then open http://127.0.0.1:8080

Same component as the /model-viewer page on the main site
(pages/model-viewer.py, which imports it as model_viewer.showcase) -- this
file imports the sibling module bare (`from showcase import ...`) instead,
same as roamly/pages/*.py importing roamly/data.py as bare `data`. That
bare import is what lets this whole model_viewer/ directory be deployed on
its own (e.g. Render with rootDir: model_viewer) without the rest of this
repo present: no imports from pages/, components/ or run.py, its own
Dash(__name__) instance (own assets/ subfolder, own port), the same shape
as roamly/app.py.
"""
import dash_mantine_components as dmc
from dash import Dash

from showcase import build_model_viewer_showcase, PAGE_CLASS

app = Dash(__name__)
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
