"""Roamly -- the Stays section: a grid of listing cards and an orthographic
globe pinning every stay.

Embedded on the /roamly docs page through `.. exec::docs.roamly.stays`. The
listing data is the standalone app's own module (examples/roamly/data.py),
imported here so the docs page and `python examples/roamly/app.py` can never
disagree about which stays exist.

The docs page is one route, so the standalone app's /listing/<id> navigation
becomes an in-page selection instead: clicking a card picks that stay in the
Listing detail section further down the page (docs/roamly/listing.py) and
scrolls to it. Ids are prefixed ``rm-`` so nothing here collides with the
rest of the site.
"""
import dash_mantine_components as dmc
from dash import ALL, Input, Output, callback, clientside_callback, ctx, dcc, html, no_update
from dash_iconify import DashIconify
import plotly.graph_objects as go

from examples.roamly.data import list_listings

ACTIVE_GRADIENT = {"from": "blue", "to": "green", "deg": 45}


def roamly_logo():
    """The Roamly wordmark, as the standalone app's header draws it."""
    return dmc.Group(
        [
            dmc.ThemeIcon(
                DashIconify(icon="tabler:map-2", width=16),
                size=26, radius="xl", variant="filled", color="green",
            ),
            dmc.Text(
                "Roamly", fw=700, size="md",
                variant="gradient", gradient=ACTIVE_GRADIENT,
            ),
        ],
        gap=6,
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
    in the Listing detail section, docs/roamly/listing.py). Draggable to
    rotate, scroll to zoom, same as any other dcc.Graph. Its land/ocean
    colors follow this site's dark mode via the callback below, since the
    figure is otherwise static (built once at import time).
    """
    return dcc.Graph(
        id="rm-globe",
        figure=_build_globe_figure(listings),
        config={"displayModeBar": False},
        style={"height": "380px", "marginTop": "24px"},
    )


@callback(
    Output("rm-globe", "figure"),
    # This site's own MantineProvider id (components/appshell.py), not the
    # standalone app's "mantine-provider" -- the embed follows the docs
    # site's dark-mode toggle.
    Input("m2d-mantine-provider", "forceColorScheme"),
)
def _globe_for_scheme(scheme):
    return _build_globe_figure(list_listings(), dark=(scheme == "dark"))


def listing_card(listing):
    """A stay card. The wrapping Div carries a pattern-matching id so one
    callback below can tell which card was clicked."""
    return html.Div(
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
            style={"height": "100%"},
        ),
        id={"type": "rm-stay-card", "index": listing["id"]},
        n_clicks=0,
        style={"cursor": "pointer"},
    )


component = dmc.Stack(
    [
        roamly_logo(),
        dmc.Stack(
            [
                dmc.Title("Find your next stay", order=3, style={"margin": 0}),
                dmc.Text(
                    "Browse full houses with real photos, ratings, and maps — no surprises at check-in.",
                    c="dimmed",
                ),
            ],
            gap=4,
        ),
        dmc.SimpleGrid(
            [listing_card(listing) for listing in list_listings()],
            cols={"base": 1, "sm": 2, "lg": 2},
            spacing="lg",
        ),
        overview_map(list_listings()),
        # Sink for the scroll-to-detail clientside callback below.
        dcc.Store(id="rm-stay-scroll-sink"),
    ],
    gap="md",
)


@callback(
    Output("rm-listing-picker", "value"),
    Input({"type": "rm-stay-card", "index": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def _select_stay_from_card(clicks):
    """A card click selects that stay in the Listing detail section's picker
    (docs/roamly/listing.py); the picker's own callback renders the detail."""
    if not any(clicks):
        return no_update
    return ctx.triggered_id["index"]


# Scroll the Listing detail section into view on a card click. The detail
# element always exists (it renders the first stay at import time), so the
# scroll can fire immediately while the server callback above swaps its
# content.
clientside_callback(
    """
    function(clicks) {
        if (!clicks || !clicks.some(Boolean)) {
            return window.dash_clientside.no_update;
        }
        const target = document.getElementById('rm-listing-detail');
        if (target) {
            target.scrollIntoView({behavior: 'smooth', block: 'start'});
        }
        return window.dash_clientside.no_update;
    }
    """,
    Output("rm-stay-scroll-sink", "data"),
    Input({"type": "rm-stay-card", "index": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
