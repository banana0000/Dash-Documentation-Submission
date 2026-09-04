# pages/listing.py
"""Listing detail — 360 tour, gallery, map, and booking summary."""
import dash
from dash import html
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import dash_leaflet2 as dl
import dash_image_gallery as dig

from data import get_listing

dash.register_page(__name__, path_template="/listing/<listing_id>", title="Roamly - Listing")


def not_found():
    return dmc.Container(
        dmc.Stack(
            [
                dmc.Title("Listing not found", order=2),
                dmc.Anchor(dmc.Button("Back to stays"), href="/"),
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
                id="listing-gallery",
                items=gallery_items,
                showPlayButton=False,
                showFullscreenButton=True,
                showThumbnails=True,
                thumbnailPosition="bottom",
            ),
        ],
        withBorder=True,
    )

    map_panel = dmc.Card(
        [
            dmc.Text("Location", fw=600, mb="sm"),
            dmc.Text(listing["location"], size="sm", c="dimmed", mb="sm"),
            dl.Map(
                [
                    dl.TileLayer(
                        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
                        attribution="© OpenStreetMap contributors",
                    ),
                    dl.Marker(
                        position=listing["coords"],
                        popup=listing["title"],
                        iconify="tabler:map-pin-filled",
                        iconColor="#4c6ef5",
                        iconSize=32,
                    ),
                ],
                center=listing["coords"],
                zoom=12,
                style={"height": "280px", "width": "100%", "borderRadius": "var(--mantine-radius-md)"},
            ),
        ],
        withBorder=True,
    )

    booking_panel = dmc.Card(
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
            dmc.Divider(my="sm"),
            dmc.Stack(
                [
                    stat("tabler:bed", f"{listing['beds']} beds"),
                    stat("tabler:bath", f"{listing['baths']} baths"),
                    stat("tabler:users", f"{listing['guests']} guests"),
                ],
                gap="xs",
            ),
            dmc.Divider(my="sm"),
            dmc.Button("Request to book", fullWidth=True, size="md"),
            dmc.Text("You won't be charged yet", size="xs", c="dimmed", ta="center", mt="xs"),
        ],
        withBorder=True,
    )

    host_panel = dmc.Card(
        dmc.Group(
            [
                dmc.Avatar(listing["host"]["name"][0], radius="xl", color="indigo"),
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
        withBorder=True,
    )

    return dmc.Container(
        [
            dmc.Anchor(
                dmc.Group([DashIconify(icon="tabler:arrow-left", width=16), dmc.Text("Back to stays", size="sm")], gap=4),
                href="/", underline=False, c="dimmed", mb="md",
            ),
            dmc.Stack(
                [
                    dmc.Title(listing["title"], order=2),
                    dmc.Text(listing["location"], c="dimmed"),
                ],
                gap=2, mb="md",
            ),
            dmc.Grid(
                [
                    dmc.GridCol(
                        dmc.Stack([gallery_panel, dmc.Card(dmc.Text(listing["summary"]), withBorder=True), map_panel], gap="md"),
                        span={"base": 12, "md": 8},
                    ),
                    dmc.GridCol(
                        dmc.Stack([booking_panel, host_panel], gap="md"),
                        span={"base": 12, "md": 4},
                    ),
                ],
            ),
        ],
        size="lg", py="md",
    )
