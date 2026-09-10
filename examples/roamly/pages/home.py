# pages/home.py
"""Stays — browse listings."""
import dash
from dash import callback, dcc, html, Input, Output
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import plotly.graph_objects as go

from data import list_listings

dash.register_page(__name__, path="/", title="Roamly - Stays")


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
    on the per-listing page, pages/listing.py). Draggable to rotate, scroll
    to zoom, same as any other dcc.Graph. Its land/ocean colors follow this
    app's own dark mode via the callback below.
    """
    return dcc.Graph(
        id="roamly-globe",
        figure=_build_globe_figure(listings),
        config={"displayModeBar": False},
        style={"height": "380px", "marginTop": "40px", "marginBottom": "var(--mantine-spacing-lg)"},
    )


@callback(
    Output("roamly-globe", "figure"),
    Input("mantine-provider", "forceColorScheme"),
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
        href=f"/listing/{listing['id']}",
        underline=False,
    )


def layout():
    listings = list_listings()
    return dmc.Container(
        [
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
                [listing_card(listing) for listing in listings],
                cols={"base": 1, "sm": 2, "lg": 3},
                spacing="lg",
            ),
            overview_map(listings),
        ],
        size="lg", py="md",
    )
