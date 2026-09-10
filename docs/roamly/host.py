"""Roamly -- the Host dashboard section: summary cards, a dash_mui_charts
bar chart of views over twelve months, and a sparkline per listing.

Embedded on the /roamly docs page through `.. exec::docs.roamly.host`; the
standalone app serves the same dashboard at /host
(examples/roamly/pages/host.py). dash_mui_charts (MUI X Charts underneath)
has its own theme, separate from Mantine's, so assets/roamly-embed.css
recolors its axis and legend text when this site is in dark mode.
"""
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import dash_mui_charts as dmuic

from examples.roamly.data import list_listings

MONTHS = ["Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep"]
COLORS = ["#2f9e44", "#12b886", "#f59f00", "#e64980"]


def summary_card(icon, label, value, color="green"):
    return dmc.Card(
        dmc.Group(
            [
                dmc.ThemeIcon(DashIconify(icon=icon, width=20), size=44, radius="xl", variant="light", color=color),
                dmc.Stack(
                    [dmc.Text(label, size="xs", c="dimmed"), dmc.Text(value, fw=700, size="xl")],
                    gap=0,
                ),
            ],
        ),
        withBorder=True,
    )


def listing_row(listing, color):
    total = sum(listing["views_last_30d"])
    trend = listing["views_last_30d"][-1] - listing["views_last_30d"][0]
    return dmc.Card(
        dmc.Group(
            [
                dmc.Group(
                    [
                        dmc.Image(src=listing["cover_image"], w=64, h=64, radius="md", fit="cover"),
                        dmc.Stack(
                            [
                                dmc.Text(listing["title"], fw=600, size="sm"),
                                dmc.Text(listing["location"], size="xs", c="dimmed"),
                                dmc.Badge(
                                    f"{'+' if trend >= 0 else ''}{trend} views trend",
                                    size="xs", variant="light",
                                    color="teal" if trend >= 0 else "red",
                                ),
                            ],
                            gap=2,
                        ),
                    ],
                ),
                dmc.Stack(
                    [
                        dmuic.SparklineChart(
                            data=listing["views_last_30d"],
                            width=140, height=48,
                            color=color, area=True, curve="natural",
                            showTooltip=True, showHighlight=True,
                        ),
                        dmc.Text(f"{total} views · 30d", size="xs", c="dimmed", ta="center"),
                    ],
                    gap=4,
                ),
            ],
            justify="space-between", wrap="nowrap",
        ),
        withBorder=True,
    )


def build_dashboard():
    listings = list_listings()
    total_reviews = sum(l["reviews"] for l in listings)
    avg_rating = round(sum(l["rating"] for l in listings) / len(listings), 2)
    total_views = sum(sum(l["views_last_30d"]) for l in listings)

    trend_series = [
        {
            "id": listing["id"],
            "label": listing["title"],
            "data": listing["views_last_30d"],
            "color": COLORS[i % len(COLORS)],
        }
        for i, listing in enumerate(listings)
    ]

    peak_month_index = max(
        range(len(MONTHS)),
        key=lambda m: max(series["data"][m] for series in trend_series),
    )
    peak_value = max(series["data"][peak_month_index] for series in trend_series)

    return dmc.Stack(
        [
            dmc.Stack(
                [
                    dmc.Title("Host dashboard", order=3, style={"margin": 0}),
                    dmc.Text("Performance across all your listings.", c="dimmed"),
                ],
                gap=4,
            ),
            dmc.SimpleGrid(
                [
                    summary_card("tabler:home", "Active listings", str(len(listings))),
                    summary_card("tabler:eye", "Views (30d)", str(total_views), color="teal"),
                    summary_card("tabler:star-filled", "Avg rating", str(avg_rating), color="yellow"),
                    summary_card("tabler:message-circle", "Total reviews", str(total_reviews), color="grape"),
                ],
                cols={"base": 1, "sm": 2, "lg": 4},
                spacing="md",
            ),
            dmc.Card(
                [
                    dmc.Text("Views over the last 12 months", fw=600, mb="sm"),
                    dmuic.BarChart(
                        series=trend_series,
                        xAxis=[{"scaleType": "band", "data": MONTHS, "barGapRatio": 0}],
                        height=320,
                        colors=COLORS,
                        borderRadius=8,
                        referenceLines=[
                            {
                                "y": peak_value,
                                "label": f"Peak: {peak_value} views ({MONTHS[peak_month_index]})",
                                "labelAlign": "end",
                                "lineStyle": {"stroke": "#495057", "strokeDasharray": "4 4"},
                            },
                        ],
                    ),
                ],
                withBorder=True,
            ),
            dmc.Text("Your listings", fw=600),
            dmc.SimpleGrid(
                [listing_row(listing, COLORS[i % len(COLORS)]) for i, listing in enumerate(listings)],
                cols={"base": 1, "md": 2},
                spacing="sm",
            ),
        ],
        gap="md",
    )


component = build_dashboard()
