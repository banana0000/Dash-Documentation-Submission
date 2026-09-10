"""IDE-style docking layout built on dash-flexlayout (a Dash wrapper for
flexlayout-react, from 2plot.ai).

Shared between two entry points, the same shape as docs/excalidraw/kpi_mockup.py:

| Where                           | Notes                                                |
|---------------------------------|------------------------------------------------------|
| docs/flex_layout/flex_layout.md | The /flex-layout docs page, which embeds the          |
|                                 | module-level ``component`` below through ``.. exec::``|
| examples/flexlayout_app.py      | Fully independent standalone app, own Dash(__name__) |
|                                 | instance, own port                                   |

Element ids are prefixed ``flexlayout-`` so this page's callbacks never
collide with ids on any other page of the same running multi-page app.

FlexLayout's own `model` prop round-trips: every drag, resize or tab move
the user makes updates it, so a plain @callback can read the live
arrangement back (see _report_tab_count below) or overwrite it wholesale
(see _reset_layout) without any extra plumbing.

Panel content is a small sales dashboard (filters, KPI cards, two Plotly
charts, an orders table) rather than placeholder text, so dragging a tab
rearranges real widgets the way a BI tool's dockable panels would.
"""
import dash_mantine_components as dmc
import plotly.graph_objects as go
from dash import callback, dcc, Input, Output, no_update
from dash_flexlayout import FlexLayout, Tab
from dash_iconify import DashIconify

_ID_PREFIX = "flexlayout-"

# Every dmc Button/ActionIcon/Switch and FlexLayout's own selected-tab accent
# under a .flexlayout-page ancestor is cyan -- see assets/flexlayout.css.
# Both entry points (the `component` below and examples/flexlayout_app.py)
# put this class on their outermost container.
PAGE_CLASS = "flexlayout-page"

_CYAN = "#0891b2"


def _id(name):
    return f"{_ID_PREFIX}{name}"


# flexlayout-react's own JSON model format: a tree of "row" / "column" split
# containers bottoming out in "tabset" containers, each holding "tab" leaves.
# Every tab's "id" here has to match a Tab(id=...) below -- that's how
# dash-flexlayout knows which Dash children render inside which tab. Panels
# hold a small sales dashboard rather than placeholder text, so dragging a
# tab actually rearranges real widgets (charts, KPIs, a table) the way a BI
# tool's dockable panels would.
DEFAULT_MODEL = {
    "global": {"tabEnableClose": False, "tabSetEnableMaximize": True},
    "borders": [],
    "layout": {
        "type": "row",
        "weight": 100,
        "children": [
            {
                # A single full-width tabset for the KPI row, above
                # everything else -- so the stat cards actually get enough
                # horizontal room to line up in one row instead of being
                # squeezed into the narrow Filters sidebar.
                "type": "column",
                "weight": 100,
                "children": [
                    {
                        "type": "tabset",
                        "weight": 20,
                        "children": [
                            {"type": "tab", "name": "KPIs", "component": "kpis", "id": "kpis"},
                        ],
                    },
                    {
                        "type": "row",
                        "weight": 80,
                        "children": [
                            {
                                "type": "tabset",
                                "weight": 22,
                                "children": [
                                    {"type": "tab", "name": "Filters", "component": "filters", "id": "filters"},
                                ],
                            },
                            {
                                "type": "column",
                                "weight": 78,
                                "children": [
                                    {
                                        "type": "tabset",
                                        "weight": 70,
                                        "children": [
                                            {"type": "tab", "name": "Revenue", "component": "revenue", "id": "revenue"},
                                            {"type": "tab", "name": "Traffic", "component": "traffic", "id": "traffic"},
                                            {"type": "tab", "name": "Channels", "component": "channels", "id": "channels"},
                                        ],
                                    },
                                    {
                                        "type": "tabset",
                                        "weight": 30,
                                        "children": [
                                            {"type": "tab", "name": "Orders", "component": "orders", "id": "orders"},
                                        ],
                                    },
                                ],
                            },
                        ],
                    },
                ],
            },
        ],
    },
}

_MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug"]
_REVENUE = [42, 48, 45, 61, 58, 74, 69, 83]
_CHANNELS = ["Organic", "Paid", "Referral", "Social", "Email"]
_TRAFFIC = [3120, 2380, 1450, 980, 640]

_ORDERS = [
    ("#10482", "L. Andersson", "Damaged Helmet", "$129", "Shipped"),
    ("#10483", "J. Alvarez", "Barramundi Fish", "$54", "Processing"),
    ("#10484", "T. Nakamura", "Shoe", "$89", "Shipped"),
    ("#10485", "S. Müller", "Glass", "$32", "Pending"),
]

_GRAPH_CONFIG = {"displayModeBar": False, "responsive": True}
_GRAPH_LAYOUT = dict(
    margin=dict(l=36, r=12, t=12, b=32),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(size=12),
)


def _stat_card(label, value, delta, icon, color):
    return dmc.Paper(
        dmc.Group(
            [
                dmc.ThemeIcon(DashIconify(icon=icon, width=18), size=36, radius="md", variant="light", color=color),
                dmc.Stack(
                    [
                        dmc.Text(label, size="xs", c="dimmed"),
                        dmc.Group(
                            [dmc.Text(value, fw=700, size="lg"), dmc.Text(delta, size="xs", c=color)],
                            gap=6, align="baseline",
                        ),
                    ],
                    gap=0,
                ),
            ],
            gap="sm", wrap="nowrap",
        ),
        withBorder=True, radius="md", p="sm", w=200,
    )


def _filters_tab():
    return dmc.Stack(
        [
            dmc.Select(
                label="Date range", value="ytd", clearable=False, allowDeselect=False,
                data=[{"label": "Last 7 days", "value": "7d"}, {"label": "Last 30 days", "value": "30d"},
                      {"label": "Year to date", "value": "ytd"}],
            ),
            dmc.Select(
                label="Region", value="all", clearable=False, allowDeselect=False,
                data=[{"label": "All regions", "value": "all"}, {"label": "EU", "value": "eu"},
                      {"label": "US", "value": "us"}, {"label": "APAC", "value": "apac"}],
            ),
            dmc.MultiSelect(
                label="Channels", value=_CHANNELS[:3],
                data=[{"label": c, "value": c} for c in _CHANNELS],
            ),
            dmc.Switch(label="Compare to previous period", checked=True, size="sm"),
        ],
        gap="md", p="sm",
    )


def _kpis_tab():
    # A single, non-wrapping row -- if the cards don't all fit the panel's
    # width, the row scrolls horizontally instead of wrapping onto a second
    # line (which the KPI panel above the rest of the layout is too short
    # to show without clipping it).
    return dmc.ScrollArea(
        dmc.Group(
            [
                _stat_card("Revenue", "$83.4k", "+12.4%", "mdi:currency-usd", "teal"),
                _stat_card("Orders", "1,204", "+4.1%", "mdi:package-variant-closed", "indigo"),
                _stat_card("Visitors", "8,570", "-2.3%", "mdi:account-group-outline", "red"),
                _stat_card("Conversion", "3.2%", "+0.4%", "mdi:target-arrow", "teal"),
            ],
            gap="sm", align="flex-start", wrap="nowrap", p="sm",
        ),
        type="auto", scrollbarSize=8, style={"height": "100%"},
    )


def _revenue_tab():
    fig = go.Figure(
        go.Scatter(x=_MONTHS, y=_REVENUE, mode="lines+markers", fill="tozeroy",
                   line=dict(color=_CYAN, width=2), marker=dict(size=6, color=_CYAN),
                   fillcolor="rgba(8, 145, 178, 0.15)"),
    )
    fig.update_layout(**_GRAPH_LAYOUT, yaxis_title="$k")
    return dcc.Graph(figure=fig, config=_GRAPH_CONFIG, style={"height": "100%"})


def _traffic_tab():
    fig = go.Figure(go.Bar(x=_CHANNELS, y=_TRAFFIC, marker_color=_CYAN))
    fig.update_layout(**_GRAPH_LAYOUT, yaxis_title="sessions")
    return dcc.Graph(figure=fig, config=_GRAPH_CONFIG, style={"height": "100%"})


_CHANNEL_COLORS = ["#0891b2", "#f59f00", "#e64980", "#7048e8", "#40c057"]


def _channels_tab():
    fig = go.Figure(
        go.Pie(labels=_CHANNELS, values=_TRAFFIC, hole=0.55,
               marker=dict(colors=_CHANNEL_COLORS, line=dict(color="#ffffff", width=2)),
               textinfo="label+percent"),
    )
    fig.update_layout(
        margin=dict(l=12, r=12, t=12, b=12),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(size=12),
        showlegend=False,
    )
    return dcc.Graph(figure=fig, config=_GRAPH_CONFIG, style={"height": "100%"})


def _orders_tab():
    header = dmc.TableThead(dmc.TableTr([dmc.TableTh(h) for h in ("Order", "Customer", "Item", "Total", "Status")]))
    rows = [
        dmc.TableTr([dmc.TableTd(order), dmc.TableTd(customer), dmc.TableTd(item), dmc.TableTd(total),
                     dmc.TableTd(dmc.Badge(status, size="sm", variant="light", color={
                         "Shipped": "teal", "Processing": "blue", "Pending": "gray",
                     }.get(status, "gray")))])
        for order, customer, item, total, status in _ORDERS
    ]
    return dmc.Table([header, dmc.TableTbody(rows)], striped=True, highlightOnHover=True, p="xs")


def build_flexlayout_showcase(height="70vh"):
    """Layout for the FlexLayout docking playground. Registers its callbacks
    on import (module-level @callback, same as the rest of this app's pages)
    -- import this module exactly once per running Dash app.
    """
    controls = dmc.Group(
        [
            dmc.Switch(id=_id("realtime-resize-toggle"), label="Realtime resize", checked=False, size="sm"),
            dmc.Switch(id=_id("debug-toggle"), label="Debug mode", checked=False, size="sm"),
            dmc.Switch(id=_id("popout-toggle"), label="Allow popout", checked=True, size="sm"),
            dmc.Button(
                "Reset layout", id=_id("reset-btn"), n_clicks=0,
                leftSection=DashIconify(icon="mdi:view-dashboard-outline", width=16),
                variant="outline", size="compact-sm",
            ),
            dmc.Text(id=_id("tab-count"), size="sm", c="dimmed", ml="auto"),
        ],
        justify="flex-start", gap="md", wrap="wrap", mb="sm",
    )

    panel = dmc.Paper(
        FlexLayout(
            id=_id("layout"),
            model=DEFAULT_MODEL,
            realtimeResize=False,
            debugMode=False,
            supportsPopout=True,
            children=[
                Tab(id="filters", children=_filters_tab()),
                Tab(id="kpis", children=_kpis_tab()),
                Tab(id="revenue", children=_revenue_tab()),
                Tab(id="traffic", children=_traffic_tab()),
                Tab(id="channels", children=_channels_tab()),
                Tab(id="orders", children=_orders_tab()),
            ],
        ),
        withBorder=True,
        radius="md",
        style={"height": height, "overflow": "hidden", "position": "relative"},
    )

    return dmc.Stack([controls, panel], gap=0)


def _count_tabs(node):
    if not isinstance(node, dict):
        return 0
    total = 1 if node.get("type") == "tab" else 0
    for child in node.get("children", []):
        total += _count_tabs(child)
    return total


@callback(
    Output(_id("tab-count"), "children"),
    Input(_id("layout"), "model"),
)
def _report_tab_count(model):
    if not isinstance(model, dict):
        return no_update
    count = _count_tabs(model.get("layout", {}))
    return f"{count} tabs open"


@callback(
    Output(_id("layout"), "model", allow_duplicate=True),
    Input(_id("reset-btn"), "n_clicks"),
    prevent_initial_call=True,
)
def _reset_layout(_n_clicks):
    return DEFAULT_MODEL


@callback(
    Output(_id("layout"), "realtimeResize"),
    Input(_id("realtime-resize-toggle"), "checked"),
    prevent_initial_call=True,
)
def _toggle_realtime_resize(checked):
    return checked


@callback(
    Output(_id("layout"), "debugMode"),
    Input(_id("debug-toggle"), "checked"),
    prevent_initial_call=True,
)
def _toggle_debug_mode(checked):
    return checked


@callback(
    Output(_id("layout"), "supportsPopout"),
    Input(_id("popout-toggle"), "checked"),
    prevent_initial_call=True,
)
def _toggle_popout(checked):
    return checked


# What `.. exec::docs.flex_layout.showcase` renders on the /flex-layout docs
# page. The PAGE_CLASS wrapper is what scopes assets/flexlayout.css's cyan
# accent to this demo and nothing else on the page.
component = dmc.Box(build_flexlayout_showcase(height="70vh"), className=PAGE_CLASS)
