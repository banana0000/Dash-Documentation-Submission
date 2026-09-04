# pages/home.py
"""Stays — browse listings."""
import dash
from dash import html
import dash_mantine_components as dmc
from dash_iconify import DashIconify

from data import list_listings

dash.register_page(__name__, path="/", title="Roamly - Stays")


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
                            color="indigo",
                            leftSection=DashIconify(icon="tabler:home", width=12),
                        ),
                        dmc.Text(
                            [
                                dmc.Text(f"${listing['price']}", span=True, fw=700, c="dark"),
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
                [listing_card(listing) for listing in list_listings()],
                cols={"base": 1, "sm": 2, "lg": 3},
                spacing="lg",
            ),
        ],
        size="lg", py="md",
    )
