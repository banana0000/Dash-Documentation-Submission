"""Standalone entry point for the FlexLayout docking playground.

Install with: pip install dash-flexlayout (already pinned in requirements.txt).
Run: python flexlayout_app.py, then open http://127.0.0.1:8080

Same component as the /flex-layout page on the main site
(pages/flex-layout.py) -- both import their layout from
components/flexlayout_showcase.py. This file is the fully independent
version: its own Dash(__name__) instance, its own port, no imports from
pages/ or run.py, the same shape as dash_flow_app.py and model_viewer/app.py.
"""
import dash_mantine_components as dmc
from dash import Dash

from components.flexlayout_showcase import build_flexlayout_showcase, PAGE_CLASS

app = Dash(__name__)
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
