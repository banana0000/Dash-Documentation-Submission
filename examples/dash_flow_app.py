"""Standalone entry point for the Dash Flow playground.

Run from the repo root:

    python examples/dash_flow_app.py        # then open http://127.0.0.1:8070

Same component as the /dash-flow docs page (docs/dash_flow/dash_flow.md) --
both import their layout from docs/dash_flow/playground.py. This file is the
fully independent version: its own Dash(__name__) instance, its own port, no
imports from pages/, components/ or run.py, the same shape as
examples/excalidraw_app.py and examples/flexlayout_app.py.

The two lines below the imports are what make that work from inside
examples/: the repo root goes on sys.path so `docs.dash_flow` resolves, and
the app serves the repo-root assets/ folder (assets/dash-flow-playground.css
is required -- see that file for why) instead of a non-existent
examples/assets/.
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

import dash_mantine_components as dmc  # noqa: E402
from dash import Dash  # noqa: E402

from docs.dash_flow.playground import build_flow_playground  # noqa: E402

app = Dash(__name__, assets_folder=str(REPO_ROOT / "assets"))
app.title = "Dash Flow Playground"
server = app.server

app.layout = dmc.MantineProvider(
    forceColorScheme="dark",
    theme={"primaryColor": "indigo"},
    children=dmc.Container(
        [
            dmc.Stack(
                [
                    dmc.Title("Dash Flow Playground", order=1, mb=0),
                    dmc.Text(
                        "A small playground for the dash-flows (2plot.ai) node/edge diagram component.",
                        c="dimmed",
                        size="sm",
                    ),
                ],
                gap="xs",
                mb="lg",
            ),
            build_flow_playground(height="70vh"),
        ],
        size="lg",
        py="xl",
    ),
)


if __name__ == "__main__":
    print("Dash Flow Playground starting on http://localhost:8070/")
    app.run(debug=False, port=8070)
