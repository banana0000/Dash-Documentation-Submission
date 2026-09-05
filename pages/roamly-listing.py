import dash_mantine_components as dmc
from dash import callback, Input, Output, register_page
from dash_iconify import DashIconify
import dash_leaflet2 as dl
import dash_image_gallery as dig

from lib.constants import OG_IMAGE_URL, PAGE_TITLE_PREFIX
from roamly.data import get_listing

NAME = "Roamly: Listing *"
DESCRIPTION = "A single Roamly stay's detail page, embedded on the main site -- see pages/roamly.py."

register_page(
    __name__,
    path_template="/roamly/listing/<listing_id>",
    name=NAME,
    title=PAGE_TITLE_PREFIX + NAME,
    description=DESCRIPTION,
    image_url=OG_IMAGE_URL,
    icon="tabler:map-2",
)

LLMS_DOC = f"# {NAME}\n\n> {DESCRIPTION}\n"

# A real street map (roads, labels, buildings) rather than the blank
# Light/Dark Gray Canvas basemaps used before -- Esri's own street map for
# light mode ({z}/{y}/{x} order, its own convention, the reverse of
# OSM/Carto's {z}/{x}/{y}); Esri has no dark equivalent, so dark mode falls
# back to CartoDB's dark_all, which is a genuine dark *street* map (roads
# and labels), not the abstract dark gray canvas.
_LIGHT_TILES = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}"
_DARK_TILES = "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
_LIGHT_ATTRIBUTION = "Tiles © Esri — Esri, HERE, Garmin, USGS, Intermap, INCREMENT P, NRCan, Esri Japan, METI, Esri China (Hong Kong), Esri Korea, Esri (Thailand), NGCC, © OpenStreetMap contributors, GIS User Community"
_DARK_ATTRIBUTION = "© OpenStreetMap contributors, © CARTO"

# Every id on this page carries this prefix -- Roamly's standalone version
# (roamly/pages/listing.py) uses the bare names, which would collide with
# this site's own ids (e.g. plain "mantine-provider" isn't one here, but a
# second copy of this page's own ids would be if either page were ever
# rendered twice) and keeps the two copies' callbacks unambiguous.
_ID_PREFIX = "rm-listing-"


def _id(name):
    return f"{_ID_PREFIX}{name}"


def roamly_nav():
    return dmc.Group(
        [
            dmc.Anchor(dmc.Button("Stays", variant="light", size="xs"), href="/roamly"),
            dmc.Anchor(dmc.Button("Host dashboard", variant="light", size="xs"), href="/roamly/host"),
        ],
        gap="xs", mb="md",
    )


def not_found():
    return dmc.Container(
        dmc.Stack(
            [
                dmc.Title("Listing not found", order=2),
                dmc.Anchor(dmc.Button("Back to stays"), href="/roamly"),
            ],
            align="center", py="xl",
        ),
        size="sm",
    )


def stat(icon, label):
    return dmc.Group(
        [DashIconify(icon=icon, width=18, color="var(--mantine-color-dimmed)"), dmc.Text(label, size="sm")],
        gap=6,
    )


def layout(listing_id=None, **kwargs):
    listing = get_listing(listing_id)
    if listing is None:
        return not_found()

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
                        url=_LIGHT_TILES,
                        attribution=_LIGHT_ATTRIBUTION,
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

    return dmc.Container(
        [
            roamly_nav(),
            dmc.Anchor(
                dmc.Group([DashIconify(icon="tabler:arrow-left", width=16), dmc.Text("Back to stays", size="sm")], gap=4),
                href="/roamly", underline=False, c="dimmed", mb="md",
            ),
            dmc.Stack(
                [
                    dmc.Title(listing["title"], order=2),
                    dmc.Text(listing["location"], c="dimmed"),
                ],
                gap=2, mb="md",
            ),
            dmc.Card(dmc.Text(listing["summary"]), withBorder=True, mb="md"),
            dmc.Grid(
                [
                    dmc.GridCol(gallery_panel, span={"base": 12, "md": 8}),
                    dmc.GridCol(booking_panel, span={"base": 12, "md": 4}),
                ],
                align="stretch",
                mb="md",
            ),
            map_panel,
        ],
        size="lg", py="md",
    )


@callback(
    Output(_id("map-tiles"), "url"),
    Output(_id("map-tiles"), "attribution"),
    # This site's own MantineProvider id (components/appshell.py), not
    # Roamly's standalone "mantine-provider" -- the embed follows this
    # site's dark-mode toggle, since Roamly's own header/toggle aren't part
    # of the embed.
    Input("m2d-mantine-provider", "forceColorScheme"),
)
def _tile_layer_for_scheme(scheme):
    if scheme == "dark":
        return _DARK_TILES, _DARK_ATTRIBUTION
    return _LIGHT_TILES, _LIGHT_ATTRIBUTION
