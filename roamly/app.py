# app.py
"""
Roamly — a house-only stay/property platform.
Built on Dash, Dash Mantine Components, and dash-leaflet2 (2plot.dev).
"""
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import dash
from dash import Dash, callback, Input, Output, State
import dash_mantine_components as dmc
from dash_iconify import DashIconify

theme = {
    "primaryColor": "indigo",
    "fontFamily": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
    "defaultRadius": "md",
    "components": {
        "Card": {"defaultProps": {"shadow": "sm", "radius": "lg", "withBorder": False}},
        "Button": {"defaultProps": {"radius": "xl"}},
    },
}

app = Dash(
    __name__,
    use_pages=True,
    pages_folder="pages",
    suppress_callback_exceptions=True,
    external_stylesheets=[dmc.styles.ALL],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
app.title = "Roamly - Find your next stay"
server = app.server

navbar = dmc.AppShellHeader(
    dmc.Container(
        dmc.Group(
            [
                dmc.Anchor(
                    dmc.Group(
                        [
                            dmc.ThemeIcon(
                                DashIconify(icon="tabler:map-2", width=22),
                                size=38, radius="xl", variant="filled", color="indigo",
                            ),
                            dmc.Text("Roamly", fw=700, size="lg"),
                        ],
                        gap="xs",
                    ),
                    href="/", underline=False,
                ),
                dmc.Group(
                    [
                        dmc.Anchor(dmc.Button("Stays", variant="subtle", color="gray"), href="/"),
                        dmc.Anchor(dmc.Button("Host dashboard", variant="subtle", color="gray"), href="/host"),
                        dmc.ActionIcon(
                            DashIconify(icon="tabler:moon", width=18, id="color-scheme-icon"),
                            id="color-scheme-toggle",
                            variant="subtle", color="gray", size="lg",
                        ),
                    ],
                    gap="xs",
                ),
            ],
            justify="space-between", h="100%",
        ),
        h="100%", size="lg",
    ),
    h=64, withBorder=True, className="rm-header",
)

footer = dmc.AppShellFooter(
    dmc.Container(
        dmc.Group(
            [
                dmc.Text("© 2026 Roamly — find your next stay.", size="sm", c="dimmed", truncate=True),
                dmc.Text("Built with Dash", size="xs", c="dimmed", visibleFrom="sm"),
            ],
            justify="space-between", wrap="nowrap", gap="sm", h="100%",
        ),
        size="lg", h="100%",
    ),
    h=48, withBorder=True,
)

app.layout = dmc.MantineProvider(
    id="mantine-provider",
    theme=theme,
    forceColorScheme="light",
    children=dmc.AppShell(
        [
            navbar,
            dmc.AppShellMain(dash.page_container, pt=64, pb=48),
            footer,
        ],
        header={"height": 64},
        footer={"height": 48},
        padding="md",
    ),
)


@callback(
    Output("mantine-provider", "forceColorScheme"),
    Output("color-scheme-icon", "icon"),
    Input("color-scheme-toggle", "n_clicks"),
    State("mantine-provider", "forceColorScheme"),
    prevent_initial_call=True,
)
def toggle_color_scheme(n_clicks, current):
    new_scheme = "dark" if current != "dark" else "light"
    icon = "tabler:sun" if new_scheme == "dark" else "tabler:moon"
    return new_scheme, icon


if __name__ == "__main__":
    print("Roamly starting on http://localhost:8870/")
    app.run(debug=True, port=8870, host="0.0.0.0", use_reloader=False)
