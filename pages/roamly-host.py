import dash_mantine_components as dmc
from dash import register_page
from dash_iconify import DashIconify
import dash_mui_charts as dmuic

from lib.constants import OG_IMAGE_URL, PAGE_TITLE_PREFIX
from roamly.data import list_listings

NAME = "Roamly: Host dashboard *"
DESCRIPTION = "Roamly's host performance dashboard, embedded on the main site -- see pages/roamly.py."

register_page(
    __name__,
    "/roamly/host",
    name=NAME,
    title=PAGE_TITLE_PREFIX + NAME,
    description=DESCRIPTION,
    image_url=OG_IMAGE_URL,
    icon="tabler:map-2",
)

LLMS_DOC = f"# {NAME}\n\n> {DESCRIPTION}\n"

MONTHS = ["Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep"]
COLORS = ["#2f9e44", "#12b886", "#f59f00", "#e64980"]


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


def _build_layout():
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

    return dmc.Container(
        [
            roamly_nav("host"),
            dmc.Stack(
                [
                    dmc.Title("Host dashboard", order=2),
                    dmc.Text("Performance across all your listings.", c="dimmed"),
                ],
                gap=4, mb="lg",
            ),
            dmc.SimpleGrid(
                [
                    summary_card("tabler:home", "Active listings", str(len(listings))),
                    summary_card("tabler:eye", "Views (30d)", str(total_views), color="teal"),
                    summary_card("tabler:star-filled", "Avg rating", str(avg_rating), color="yellow"),
                    summary_card("tabler:message-circle", "Total reviews", str(total_reviews), color="grape"),
                ],
                cols={"base": 1, "sm": 2, "lg": 4},
                spacing="md", mb="lg",
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
                withBorder=True, mb="lg",
            ),
            dmc.Text("Your listings", fw=600, mb="sm"),
            dmc.SimpleGrid(
                [listing_row(listing, COLORS[i % len(COLORS)]) for i, listing in enumerate(listings)],
                cols={"base": 1, "md": 3},
                spacing="sm",
            ),
        ],
        size="lg", py="md",
    )


layout = _build_layout()
