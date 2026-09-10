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
from dash import Dash, callback, dcc, Input, Output, State
import dash_mantine_components as dmc
from dash_iconify import DashIconify

theme = {
    "primaryColor": "green",
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
    external_stylesheets=[
        dmc.styles.ALL,
        # Baloo 2 -- a rounded, friendly display face for the "Roamly"
        # wordmark only (applied via `ff=` on that one dmc.Text below), not
        # the whole app's body font.
        "https://fonts.googleapis.com/css2?family=Baloo+2:wght@700&display=swap",
    ],
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
                                size=38, radius="xl", variant="filled", color="green",
                            ),
                            dmc.Text(
                                "Roamly", fw=700, size="xl",
                                ff="'Baloo 2', cursive",
                                variant="gradient",
                                gradient={"from": "blue", "to": "green", "deg": 45},
                            ),
                        ],
                        gap="xs",
                    ),
                    href="/", underline=False,
                ),
                dmc.Group(
                    [
                        dmc.Anchor(
                            dmc.Button("Stays", id="nav-stays-btn", variant="subtle", color="gray"), href="/",
                        ),
                        dmc.Anchor(
                            dmc.Button("Host dashboard", id="nav-host-btn", variant="subtle", color="gray"),
                            href="/host",
                        ),
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
    children=[
        # A dedicated Location just for the nav-highlight callback below --
        # independent from whatever dcc.Location use_pages=True wires up
        # internally for the actual routing, so it can't collide with it.
        dcc.Location(id="roamly-url", refresh=False),
        dmc.AppShell(
            [
                navbar,
                dmc.AppShellMain(dash.page_container, pt=64, pb=48),
                footer,
            ],
            header={"height": 64},
            footer={"height": 48},
            padding="md",
        ),
    ],
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


_ACTIVE_GRADIENT = {"from": "blue", "to": "green", "deg": 45}


@callback(
    Output("nav-stays-btn", "variant"),
    Output("nav-stays-btn", "gradient"),
    Output("nav-host-btn", "variant"),
    Output("nav-host-btn", "gradient"),
    Input("roamly-url", "pathname"),
)
def _highlight_active_nav(pathname):
    # /listing/<id> counts as "Stays" too -- it's reached by browsing from
    # there, not a section of its own.
    stays_active = pathname == "/" or (pathname or "").startswith("/listing/")
    host_active = pathname == "/host"
    return (
        "gradient" if stays_active else "subtle", _ACTIVE_GRADIENT,
        "gradient" if host_active else "subtle", _ACTIVE_GRADIENT,
    )


if __name__ == "__main__":
    print("Roamly starting on http://localhost:8870/")
    app.run(debug=True, port=8870, host="0.0.0.0", use_reloader=False)
