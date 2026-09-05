from pathlib import Path

import dash_mantine_components as dmc
from dash import callback, dcc, register_page, Input, Output
from dash_iconify import DashIconify
import plotly.graph_objects as go

from lib.constants import OG_IMAGE_URL, PAGE_TITLE_PREFIX
from roamly.data import list_listings

NAME = "Roamly *"
DESCRIPTION = (
    "A house-only stay/property booking platform mockup -- a listings grid, an "
    "individual stay page with an image gallery, and a host dashboard. Built on "
    "Dash, Dash Mantine Components and dash-leaflet2."
)

register_page(
    __name__,
    "/roamly",
    name=NAME,
    title=PAGE_TITLE_PREFIX + NAME,
    description=DESCRIPTION,
    image_url=OG_IMAGE_URL,
    icon="tabler:map-2",
)

# dash-improve-my-llms picks this up automatically and serves it verbatim at
# /roamly/llms.txt -- see pages/excalidraw.py for the same pattern.
LLMS_DOC = (
    f"# {NAME}\n\n> {DESCRIPTION}\n\n"
    "Embedded here at /roamly, /roamly/host and /roamly/listing/<id> -- the "
    "same app also runs standalone (own AppShell, theme, port) from roamly/ "
    "at this repo's root, started with `python roamly/app.py`."
)


_ACTIVE_GRADIENT = {"from": "blue", "to": "green", "deg": 45}


def roamly_logo():
    return dmc.Anchor(
        dmc.Group(
            [
                dmc.ThemeIcon(
                    DashIconify(icon="tabler:map-2", width=16),
                    size=26, radius="xl", variant="filled", color="green",
                ),
                dmc.Text(
                    "Roamly", fw=700, size="md",
                    variant="gradient", gradient=_ACTIVE_GRADIENT,
                ),
            ],
            gap=6,
        ),
        href="/roamly", underline=False,
    )


def roamly_nav(active):
    """Roamly's own logo + Stays/Host dashboard switcher, embedded inline
    in the page instead of living in a second header -- this site's own
    navbar already owns that role, so Roamly's separate AppShell/header
    (used by the standalone app in roamly/app.py) isn't part of the embed.

    Each of the three embedded pages is its own module, so unlike the
    standalone app (one shared layout, a callback watching the URL) each
    page here just hardcodes which tab is "active" -- there's no dynamic
    routing within a single layout to react to.
    """
    def tab(label, href, key):
        is_active = active == key
        return dmc.Anchor(
            dmc.Button(
                label, size="xs", radius="xl",
                variant="gradient" if is_active else "light",
                gradient=_ACTIVE_GRADIENT if is_active else None,
            ),
            href=href,
        )

    return dmc.Group(
        [
            roamly_logo(),
            dmc.Group(
                [tab("Stays", "/roamly", "stays"), tab("Host dashboard", "/roamly/host", "host")],
                gap="xs",
            ),
        ],
        justify="space-between", mb="md",
    )


def _build_globe_figure(listings, dark=False):
    center_lat = sum(l["coords"][0] for l in listings) / len(listings)
    center_lon = sum(l["coords"][1] for l in listings) / len(listings)

    fig = go.Figure(
        go.Scattergeo(
            lat=[l["coords"][0] for l in listings],
            lon=[l["coords"][1] for l in listings],
            text=[f"{l['title']} — ${l['price']}/{l['price_unit']}" for l in listings],
            mode="markers",
            marker=dict(size=12, color="#15aabf", line=dict(width=1, color="white")),
            hoverinfo="text",
        )
    )
    fig.update_geos(
        projection_type="orthographic",
        projection_rotation=dict(lon=center_lon, lat=center_lat),
        showland=True, landcolor="#343a40" if dark else "#e9ecef",
        showocean=True, oceancolor="#1a1b1e" if dark else "#d0ebff",
        showcountries=True, countrycolor="#495057" if dark else "#adb5bd",
        showlakes=False,
        bgcolor="rgba(0,0,0,0)",
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=380,
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def overview_map(listings):
    """All listings on one 3D-look globe -- Plotly's own Scattergeo with an
    orthographic projection, rather than dash_leaflet2's flat 2D Map (used
    on the per-listing page, pages/roamly-listing.py). Draggable to rotate,
    scroll to zoom, same as any other dcc.Graph. Its land/ocean colors
    follow this site's own dark mode via the callback below, since the
    figure is otherwise static (this page's `layout` is a plain module-
    level value, built once at import time, not a function).
    """
    return dcc.Graph(
        id="roamly-globe",
        figure=_build_globe_figure(listings),
        config={"displayModeBar": False},
        style={"height": "380px", "marginTop": "40px", "marginBottom": "var(--mantine-spacing-lg)"},
    )


@callback(
    Output("roamly-globe", "figure"),
    Input("m2d-mantine-provider", "forceColorScheme"),
)
def _globe_for_scheme(scheme):
    return _build_globe_figure(list_listings(), dark=(scheme == "dark"))


def listing_card(listing):
    return dmc.Anchor(
        dmc.Card(
            [
                dmc.CardSection(
                    dmc.Image(src=listing["cover_image"], h=200, fit="cover"),
                ),
                dmc.Group(
                    [
                        dmc.Stack(
                            [
                                dmc.Text(listing["title"], fw=600, size="md", truncate=True),
                                dmc.Text(listing["location"], size="sm", c="dimmed"),
                            ],
                            gap=2,
                        ),
                        dmc.Badge(
                            f"★ {listing['rating']}",
                            variant="light",
                            color="yellow",
                            leftSection=DashIconify(icon="tabler:star-filled", width=12),
                        ),
                    ],
                    justify="space-between",
                    align="flex-start",
                    mt="sm",
                ),
                dmc.Group(
                    [
                        dmc.Badge(
                            f"{listing['beds']} beds · {listing['baths']} baths",
                            variant="light",
                            color="green",
                            leftSection=DashIconify(icon="tabler:home", width=12),
                        ),
                        dmc.Text(
                            [
                                dmc.Text(f"${listing['price']}", span=True, fw=700),
                                f" / {listing['price_unit']}",
                            ],
                            size="sm",
                        ),
                    ],
                    justify="space-between",
                    mt="xs",
                ),
                dmc.Text(
                    "Click for photos and map",
                    size="xs", c="dimmed", ta="center", mt="xs",
                ),
            ],
            withBorder=True,
        ),
        href=f"/roamly/listing/{listing['id']}",
        underline=False,
    )


layout = dmc.Container(
    id="m2d-page-roamly",
    children=[
        roamly_nav("stays"),
        dmc.Stack(
            [
                dmc.Title("Find your next stay", order=1),
                dmc.Text(
                    "Browse full houses with real photos, ratings, and maps — no surprises at check-in.",
                    c="dimmed", size="lg",
                ),
            ],
            gap=4, mb="lg",
        ),
        dmc.SimpleGrid(
            [listing_card(listing) for listing in list_listings()],
            cols={"base": 1, "sm": 2, "lg": 3},
            spacing="lg",
        ),
        overview_map(list_listings()),
    ],
    size="lg", py="md",
)
