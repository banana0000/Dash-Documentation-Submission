"""Roamly -- the Listing detail section: photo gallery, booking card and a
dash_leaflet2 map with its own draw/edit toolbar, for one stay at a time.

Embedded on the /roamly docs page through `.. exec::docs.roamly.listing`.
The standalone app (examples/roamly/pages/listing.py) reads the stay from
the URL (`/listing/<id>`); the docs page is a single route, so here a
Select picks the stay instead, and the cards in the Stays section above
(docs/roamly/stays.py) write into that same Select when clicked.

Every id carries the ``rm-listing-`` prefix so the standalone app's bare
names never collide with this site's own.
"""
import dash_mantine_components as dmc
from dash import Input, Output, callback, html
from dash_iconify import DashIconify
import dash_leaflet2 as dl
import dash_image_gallery as dig

from examples.roamly.data import get_listing, list_listings

# Esri for both modes, kept as one provider rather than mixing in CartoDB
# for dark -- Esri has no dark *street* map, so dark mode is its Dark Gray
# Canvas (still Esri's own, just more muted/abstract than the light mode's
# full street map). {z}/{y}/{x} order is Esri's own convention, the
# reverse of OSM/Carto's {z}/{x}/{y}.
_LIGHT_TILES = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}"
_DARK_TILES = "https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}"
_LIGHT_ATTRIBUTION = "Tiles © Esri — Esri, HERE, Garmin, USGS, Intermap, INCREMENT P, NRCan, Esri Japan, METI, Esri China (Hong Kong), Esri Korea, Esri (Thailand), NGCC, © OpenStreetMap contributors, GIS User Community"
_DARK_ATTRIBUTION = "Tiles © Esri — Esri, HERE, Garmin, © OpenStreetMap contributors, GIS User Community"

_ID_PREFIX = "rm-listing-"


def _id(name):
    return f"{_ID_PREFIX}{name}"


def not_found():
    return dmc.Alert("Listing not found.", color="red", variant="light")


def stat(icon, label):
    return dmc.Group(
        [DashIconify(icon=icon, width=18, color="var(--mantine-color-dimmed)"), dmc.Text(label, size="sm")],
        gap=6,
    )


def listing_detail(listing, dark=False):
    """The full detail view for one stay: summary, gallery + booking card
    side by side, then the map. `dark` picks the Esri tile set so the map
    follows the site's color scheme at render time."""
    gallery_items = [
        {"original": url, "thumbnail": url} for url in listing["gallery"]
    ]

    gallery_panel = dmc.Card(
        [
            dmc.Text("Photos", fw=600, mb="sm"),
            dig.DashImageGallery(
                id=_id("gallery"),
                items=gallery_items,
                showPlayButton=False,
                showFullscreenButton=True,
                showThumbnails=True,
                thumbnailPosition="bottom",
            ),
        ],
        withBorder=True,
        h="100%",
    )

    map_panel = dmc.Card(
        [
            dmc.Text("Location", fw=600, mb="sm"),
            dmc.Text(listing["location"], size="sm", c="dimmed", mb="sm"),
            dl.Map(
                [
                    dl.TileLayer(
                        id=_id("map-tiles"),
                        url=_DARK_TILES if dark else _LIGHT_TILES,
                        attribution=_DARK_ATTRIBUTION if dark else _LIGHT_ATTRIBUTION,
                    ),
                    dl.Marker(
                        position=listing["coords"],
                        popup=listing["title"],
                        iconify="tabler:map-pin-filled",
                        iconColor="#15aabf",
                        iconSize=32,
                    ),
                    # dash_leaflet2's own draw/edit toolbar (2plot.ai) -- a
                    # direct child of dl.Map, shapes kept in its own internal
                    # FeatureGroup, so no manual wrapping needed.
                    dl.EditControl(position="topright"),
                ],
                center=listing["coords"],
                zoom=12,
                style={"height": "280px", "width": "100%", "borderRadius": "var(--mantine-radius-md)"},
            ),
        ],
        withBorder=True,
    )

    booking_panel = dmc.Card(
        dmc.Stack(
            [
                dmc.Group(
                    [
                        dmc.Text([dmc.Text(f"${listing['price']}", span=True, fw=700, size="xl"), f" / {listing['price_unit']}"]),
                        dmc.Badge(
                            f"★ {listing['rating']} ({listing['reviews']})",
                            variant="light", color="yellow",
                        ),
                    ],
                    justify="space-between",
                ),
                dmc.Divider(),
                dmc.Stack(
                    [
                        stat("tabler:bed", f"{listing['beds']} beds"),
                        stat("tabler:bath", f"{listing['baths']} baths"),
                        stat("tabler:users", f"{listing['guests']} guests"),
                    ],
                    gap="xs",
                ),
                dmc.Divider(),
                dmc.TimePicker(
                    id=_id("checkin-time"),
                    label="Check-in time",
                    value="15:00",
                    withDropdown=True,
                ),
                dmc.Stack(
                    [
                        dmc.Button("Request to book", fullWidth=True, size="md"),
                        dmc.Text("You won't be charged yet", size="xs", c="dimmed", ta="center"),
                    ],
                    gap="xs",
                ),
                dmc.Divider(),
                dmc.Group(
                    [
                        dmc.Avatar(listing["host"]["name"][0], radius="xl", color="green"),
                        dmc.Stack(
                            [
                                dmc.Text(f"Hosted by {listing['host']['name']}", fw=600, size="sm"),
                                dmc.Text(
                                    f"Hosting since {listing['host']['since']} · {listing['host']['listings']} listings",
                                    size="xs", c="dimmed",
                                ),
                            ],
                            gap=0,
                        ),
                    ],
                ),
            ],
            justify="space-between",
            h="100%",
        ),
        withBorder=True,
        h="100%",
    )

    return dmc.Stack(
        [
            dmc.Stack(
                [
                    dmc.Title(listing["title"], order=3, style={"margin": 0}),
                    dmc.Text(listing["location"], c="dimmed"),
                ],
                gap=2,
            ),
            dmc.Card(dmc.Text(listing["summary"]), withBorder=True),
            dmc.Grid(
                [
                    dmc.GridCol(gallery_panel, span={"base": 12, "md": 8}),
                    dmc.GridCol(booking_panel, span={"base": 12, "md": 4}),
                ],
                align="stretch",
            ),
            map_panel,
        ],
        gap="md",
    )


_LISTINGS = list_listings()
_DEFAULT_ID = _LISTINGS[0]["id"]

component = dmc.Stack(
    [
        dmc.Select(
            id="rm-listing-picker",
            label="Stay",
            description="Pick a stay here, or click one of the cards in the Stays section above.",
            data=[{"label": listing["title"], "value": listing["id"]} for listing in _LISTINGS],
            value=_DEFAULT_ID,
            clearable=False,
            allowDeselect=False,
            maw=360,
        ),
        html.Div(listing_detail(get_listing(_DEFAULT_ID)), id="rm-listing-detail"),
    ],
    gap="md",
)


@callback(
    Output("rm-listing-detail", "children"),
    Input("rm-listing-picker", "value"),
    # This site's MantineProvider id (components/appshell.py): the map's
    # Esri tile set follows the docs site's dark-mode toggle. The whole
    # detail re-renders on a scheme change rather than swapping only the
    # tile URL, so a stay picked while in dark mode also comes up dark.
    Input("m2d-mantine-provider", "forceColorScheme"),
    prevent_initial_call=True,
)
def _render_detail(listing_id, scheme):
    listing = get_listing(listing_id)
    if listing is None:
        return not_found()
    return listing_detail(listing, dark=(scheme == "dark"))
