"""Standalone entry point for the MUI Charts Dashboard.

Install with: pip install dash_mui_charts (already pinned in requirements.txt).
Run from the repo root:

    python examples/mui_dashboard_app.py    # then open http://127.0.0.1:8100

Same component as the /mui-dashboard docs page (docs/mui_dashboard/mui_dashboard.md)
-- both build their layout from docs/mui_dashboard/dashboard.py. This file is the
fully independent version: its own Dash(__name__) instance, its own port, no
imports from pages/, components/ or run.py, the same shape as
examples/flexlayout_app.py and examples/model_viewer_app.py.

The repo root goes on sys.path so `docs.mui_dashboard` resolves from inside
examples/, and the app serves the repo-root assets/ folder, which is where
assets/mui-dashboard.css (the grey controls, scoped to PAGE_CLASS) lives.
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

import dash_mantine_components as dmc  # noqa: E402
from dash import Dash  # noqa: E402

from docs.mui_dashboard.dashboard import build_mui_dashboard, PAGE_CLASS  # noqa: E402

app = Dash(__name__, assets_folder=str(REPO_ROOT / "assets"))
app.title = "MUI Charts Dashboard"
server = app.server

app.layout = dmc.MantineProvider(
    forceColorScheme="light",
    theme={"primaryColor": "gray"},
    children=dmc.Container(
        [
            dmc.Stack(
                [
                    dmc.Title("MUI Charts Dashboard", order=1, mb=0),
                    dmc.Text(
                        "One dataset of 1,400 orders, five views of it -- the dmc controls "
                        "on the left filter the rows, and every MUI X chart is re-derived "
                        "from whatever survives.",
                        c="dimmed",
                        size="sm",
                    ),
                ],
                gap="xs",
                mb="lg",
            ),
            build_mui_dashboard(),
        ],
        size="lg",
        py="xl",
        fluid=True,
        className=PAGE_CLASS,
    ),
)


if __name__ == "__main__":
    print("MUI Charts Dashboard starting on http://localhost:8100/")
    app.run(debug=False, port=8100)
