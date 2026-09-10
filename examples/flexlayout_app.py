"""Standalone entry point for the FlexLayout docking playground.

Install with: pip install dash-flexlayout (already pinned in requirements.txt).
Run from the repo root:

    python examples/flexlayout_app.py       # then open http://127.0.0.1:8080

Same component as the /flex-layout docs page (docs/flex_layout/flex_layout.md)
-- both import their layout from docs/flex_layout/showcase.py. This file is
the fully independent version: its own Dash(__name__) instance, its own
port, no imports from pages/, components/ or run.py, the same shape as
examples/dash_flow_app.py and examples/model_viewer_app.py.

The repo root goes on sys.path so `docs.flex_layout` resolves from inside
examples/, and the app serves the repo-root assets/ folder, which is where
assets/flexlayout.css (the cyan accent, scoped to PAGE_CLASS) lives.
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

import dash_mantine_components as dmc  # noqa: E402
from dash import Dash  # noqa: E402

from docs.flex_layout.showcase import build_flexlayout_showcase, PAGE_CLASS  # noqa: E402

app = Dash(__name__, assets_folder=str(REPO_ROOT / "assets"))
app.title = "FlexLayout Playground"
server = app.server

app.layout = dmc.MantineProvider(
    forceColorScheme="dark",
    theme={"primaryColor": "cyan"},
    children=dmc.Container(
        [
            dmc.Stack(
                [
                    dmc.Title("FlexLayout Playground", order=1, mb=0),
                    dmc.Text(
                        "An IDE-style docking layout built on dash-flexlayout (2plot.ai) -- "
                        "drag tab headers to rearrange panels, drop one on an edge to split it.",
                        c="dimmed",
                        size="sm",
                    ),
                ],
                gap="xs",
                mb="lg",
            ),
            build_flexlayout_showcase(height="70vh"),
        ],
        size="lg",
        py="xl",
        fluid=True,
        className=PAGE_CLASS,
    ),
)


if __name__ == "__main__":
    print("FlexLayout Playground starting on http://localhost:8080/")
    app.run(debug=False, port=8080)
