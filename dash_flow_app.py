"""Standalone entry point for the Dash Flow playground.

Install with: pip install dash_flows (already pinned in requirements.txt).
Run: python dash_flow_app.py, then open http://127.0.0.1:8070

Same component as the /dash-flow page on the main site (pages/dash-flow.py)
-- both import their layout from components/dash_flow_playground.py. This
file is the fully independent version: its own Dash(__name__) instance, its
own port, no imports from pages/ or run.py, the same shape as
excalidraw_app.py and color_picker_app.py.
"""
import dash_mantine_components as dmc
from dash import Dash

from components.dash_flow_playground import build_flow_playground

app = Dash(__name__)
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
