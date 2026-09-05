from pathlib import Path

import dash_mantine_components as dmc
from dash import register_page
from dash_iconify import DashIconify
import dash_leaflet2 as dl

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


def roamly_nav():
    """Roamly's own Stays/Host dashboard switcher, embedded inline in the
    page instead of living in a second header -- this site's own navbar
    already owns that role, so Roamly's separate AppShell/header (used by
    the standalone app in roamly/app.py) isn't part of the embed."""
    return dmc.Group(
        [
            dmc.Anchor(dmc.Button("Stays", variant="light", size="xs"), href="/roamly"),
            dmc.Anchor(dmc.Button("Host dashboard", variant="light", size="xs"), href="/roamly/host"),
        ],
        gap="xs", mb="md",
    )


def overview_map(listings):
    """All listings on one dash_leaflet2 map -- same tile source as the
    per-listing page (pages/roamly-listing.py), just one marker per
    listing instead of one. Unlike a Plotly geo Scattergeo (tried first),
    a tile map always fills its container's full width regardless of how
    the listings are spread out geographically -- no aspect-ratio math
    needed, it just pans/zooms.
    """
    lats = [l["coords"][0] for l in listings]
    lons = [l["coords"][1] for l in listings]
    center = [sum(lats) / len(lats), sum(lons) / len(lons)]

    return dl.Map(
        [
            dl.TileLayer(
                url="https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}",
                attribution="Tiles © Esri — Esri, HERE, Garmin, © OpenStreetMap contributors, GIS User Community",
            ),
            *[
                dl.Marker(
                    position=listing["coords"],
                    popup=f"{listing['title']} — ${listing['price']}/{listing['price_unit']}",
                    iconify="tabler:map-pin-filled",
                    iconColor="#15aabf",
                    iconSize=32,
                )
                for listing in listings
            ],
        ],
        center=center,
        zoom=3,
        style={
            "height": "380px", "width": "100%", "borderRadius": "var(--mantine-radius-md)",
            "marginTop": "40px", "marginBottom": "var(--mantine-spacing-lg)",
        },
    )


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
        roamly_nav(),
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
