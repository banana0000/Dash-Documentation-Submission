"""Analytics dashboard built on dash_mui_charts (MUI X Charts, wrapped for
Dash), driven by dash-mantine-components query controls and cross-filtered
from the views themselves.

Shared between two entry points, the same shape as docs/model_viewer/showcase.py:

| Where                               | Notes                                   |
|-------------------------------------|-----------------------------------------|
| docs/mui_dashboard/mui_dashboard.md | The /mui-dashboard docs page, which     |
|                                     | embeds the module-level ``component``   |
|                                     | below through ``.. exec::``             |
| examples/mui_dashboard_app.py       | Fully independent standalone app, own   |
|                                     | Dash(__name__) instance, own port       |

Element ids are prefixed ``mui-dash-`` so this page's callbacks never collide
with ids on any other page of the same running multi-page app.

THE POINT OF THIS PAGE: one dataset, six views of it. ORDERS below is the
single source of truth -- 1,400 generated order rows. The dmc controls in the
sidebar narrow that list, every view is re-derived from whatever survives,
and clicking a view writes back into those same controls. No view holds its
own copy of anything, so the six cannot disagree.

THE MAP HAS NO MUI EQUIVALENT: dash_mui_charts exports BarChart, PieChart,
ScatterChart, SparklineChart, Heatmap, LineChart, CompositeChart, CandlestickChart,
TreeView and a couple of others -- nothing geographic. A choropleth needs an
actual map projection, which MUI X Charts does not provide at any tier, so the
region view stays Plotly no matter the licensing question. What it borrows from
the rest of the page instead is the LOOK of an MUI tooltip: Plotly's own hover
box is made fully transparent (hoverlabel colours all set to rgba(0,0,0,0)) and
a dark, Mantine-styled tooltip div is positioned by a clientside callback that
listens for plotly_hover/plotly_unhover on the graph's own DOM node.

LICENSING, measured rather than assumed: dmuic.LineChart, dmuic.CompositeChart
and dmuic.Heatmap each either log a "purchase a license ... or stop using the
software immediately" warning to the console without an MUI X Pro key, or (the
Heatmap) burn a plainly legible watermark straight into the rendered chart --
confirmed by screenshotting the actual output, not just checking devtools. All
three are avoided here: the trend and the heatmap are both Plotly. Everything
else (the KPI sparklines, the channel donut) is free MUI X Community.
"""
import random
from collections import defaultdict
from datetime import date, timedelta

import dash_ag_grid as dag
import dash_mantine_components as dmc
import dash_mui_charts as dmuic
import plotly.express as px
import plotly.graph_objects as go
from dash import callback, clientside_callback, dcc, Input, Output, State, no_update
from dash_iconify import DashIconify

_ID_PREFIX = "mui-dash-"

# Every dmc control under a .mui-dashboard-page ancestor is grey -- see
# assets/mui-dashboard.css -- so all of the colour on the page is data.
PAGE_CLASS = "mui-dashboard-page"

REGIONS = ["EMEA", "AMER", "APAC"]
CHANNELS = ["Direct", "Partner", "Online", "Reseller"]
PRODUCTS = ["Laptop", "Smartphone", "Tablet", "Headphones", "Smartwatch", "Monitor"]
MONTH_LABELS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# A SMALL set of categorical THEMES, not an open colour picker: a dashboard
# still adopts one theme at a time, but which one is now the visitor's call.
# Each is 4 hand-picked hues (not hues cycled from a generator), every one run
# through scripts/validate_palette.js against this page's white surface, both
# as the donut's 4 ADJACENT slots and as the map's 3 ALL-PAIRS slots (every
# region is on screen together, so every pair of the first 3 has to clear the
# same bar, not just neighbours):
#   Indigo  -- donut dE 8.9  / normal 25.1 -- map dE 10.3 / normal 28.6
#   Violet  -- donut dE 8.9  / normal 25.1 -- map dE 9.0  / normal 32.7
#   Forest  -- donut dE 21.9 / normal 27.9 -- map dE 7.0  / normal 27.9 (WARN
#              band, legal only because every slice/region also carries a
#              direct label -- the donut's arc labels, the map's own tooltip)
# All three clear the >= 8 target except Forest's deutan case, which is the
# 6-8 floor and therefore needs that direct-label relief. The warmest hue in
# every theme sits under 3:1 on white, which is why the donut carries arc
# labels rather than relying on colour alone.
#
# SLOT 0 is what actually carries a theme: it is the one hue every "shade"
# view (trend, donut, map, heatmap -- see _shade_map/_ramp below) is built
# from, so it has to be visibly different theme to theme, not just reordered
# warm/cool accents. Forest's slot 0 is green FOR THAT REASON, not orange or
# blue as an earlier pass had it -- with two blues in slot 0 (Indigo and the
# old Forest), switching themes barely changed anything a viewer could see.
PALETTES = {
    "Indigo": ["#4263eb", "#e8590c", "#0ca678", "#f08c00"],
    "Violet": ["#7048e8", "#e03131", "#0ca678", "#f08c00"],
    "Forest": ["#2f9e44", "#ae3ec9", "#e8590c", "#1971c2"],
}
CATEGORICAL = PALETTES["Indigo"]   # the default, and what the layout builds with
MUTED = "#ced4da"                  # an entity outside the current selection -- fixed, not themed

# The trend, donut and map no longer tell regions/channels apart by HUE: every
# entity is a SHADE of the one active theme colour, and only the current
# LEADER -- whichever is biggest among what's selected -- is picked out, in
# this fixed accent, regardless of which theme is active. "Colour follows the
# entity, never its rank" (the usual rule) is deliberately broken for that one
# accent slot: highlighting whoever is winning right now is the whole point.
ACCENT = "#f08c00"


def _shade_map(entities, base_hex):
    """entity -> one shade of base_hex each, fixed by position in `entities`
    so a filter never reshuffles anyone's colour -- only _lead() below (the
    ACCENT override) moves, because that is the one thing meant to move."""
    ramp = _ramp(base_hex, steps=len(entities) + 2)[1:-1]  # drop the two extremes
    return dict(zip(entities, ramp))


def _lead(totals, selected):
    """The entity with the largest total among the ones actually selected --
    that is who gets ACCENT. None (nobody highlighted) if nothing survived."""
    pool = {k: v for k, v in totals.items() if k in selected and v}
    return max(pool, key=pool.get) if pool else None


def _ramp(base_hex, steps=13, light_mix=0.88, dark_mix=0.55):
    """A light -> dark single-hue ramp for the heatmap, generated from
    whichever theme's first colour is active, so "region blue" (or violet, or
    indigo) and "heatmap blue" always read as the same hue instead of two
    unrelated ones. Plain RGB interpolation towards near-white and near-black
    versions of the same colour -- not colour-managed, but monotonic in
    lightness either way, which is all a sequential scale needs.
    """
    h = base_hex.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    light = [c + (255 - c) * light_mix for c in (r, g, b)]
    dark = [c * (1 - dark_mix) for c in (r, g, b)]
    out = []
    for i in range(steps):
        t = i / (steps - 1)
        rgb = [round(light[j] + (dark[j] - light[j]) * t) for j in range(3)]
        out.append("#{:02x}{:02x}{:02x}".format(*rgb))
    return out

# Chart chrome, shared by the two Plotly views so they read as one system
# with the MUI ones: muted axis ink, a barely-there grid, the page's own
# font. The grid is a near-invisible reference, not a ruled sheet -- low
# alpha rather than a light hex, so it reads the same on any surface colour.
_INK = "#868e96"
_GRID = "rgba(11, 11, 11, 0.06)"
_LINE = "#e9ecef"

START = date(2026, 1, 1)
DAYS = 364


def _region_of_countries():
    """ISO-3 country -> sales region, from Plotly's bundled gapminder table
    (offline, no download). Its continents map onto the three regions except
    the Middle East, which gapminder files under Asia but a sales org files
    under EMEA -- hence the override set."""
    middle_east = {"BHR", "IRN", "IRQ", "ISR", "JOR", "KWT", "LBN", "OMN",
                   "PSE", "SAU", "SYR", "TUR", "YEM"}
    to_region = {"Europe": "EMEA", "Africa": "EMEA", "Americas": "AMER",
                 "Asia": "APAC", "Oceania": "APAC"}
    table = px.data.gapminder().query("year == 2007")
    out = {r: [] for r in REGIONS}
    for iso, continent in zip(table["iso_alpha"], table["continent"]):
        out["EMEA" if iso in middle_east else to_region[continent]].append(iso)
    return out


COUNTRIES = _region_of_countries()


def build_orders(count=1400, seed=11):
    """The one dataset. Everything on the page is derived from this list."""
    rng = random.Random(seed)
    rows = []
    for i in range(count):
        when = START + timedelta(days=rng.randint(0, DAYS))
        units = rng.randint(1, 40)
        product = rng.choice(PRODUCTS)
        # Price depends on the product so Revenue and Units rank the products
        # differently -- otherwise the Metric picker would only rescale the
        # same shape and look as if it did nothing.
        base = {"Laptop": 950, "Smartphone": 650, "Tablet": 380,
                "Headphones": 120, "Smartwatch": 220, "Monitor": 310}[product]
        unit_price = round(base * rng.uniform(0.7, 1.3), 2)
        rows.append({
            "id": f"#{10_000 + i}",
            "date": when,
            "month": when.month,
            "region": rng.choice(REGIONS),
            "channel": rng.choice(CHANNELS),
            "product": product,
            "units": units,
            "revenue": round(units * unit_price, 2),
        })
    return rows


ORDERS = build_orders()

# What the Metric picker switches between. `key` is the row field to sum,
# except for "orders", which counts rows instead -- hence the None.
METRICS = {
    "revenue": {"label": "Revenue", "key": "revenue"},
    "units": {"label": "Units", "key": "units"},
    "orders": {"label": "Orders", "key": None},
}


def _id(name):
    return f"{_ID_PREFIX}{name}"


def query(regions, channels, products, months):
    """The single query function. Every view goes through here."""
    lo, hi = months
    return [r for r in ORDERS
            if r["region"] in regions
            and r["channel"] in channels
            and r["product"] in products
            and lo <= r["month"] <= hi]


def _total(rows, metric):
    key = METRICS[metric]["key"]
    return len(rows) if key is None else sum(r[key] for r in rows)


def _fmt(value, metric):
    return f"${value:,.0f}" if metric == "revenue" else f"{value:,.0f}"


def _by(rows, metric, *fields):
    """Sum (or count) the metric per distinct value of one or more fields."""
    out = defaultdict(float)
    key = METRICS[metric]["key"]
    for r in rows:
        k = r[fields[0]] if len(fields) == 1 else tuple(r[f] for f in fields)
        out[k] += 1 if key is None else r[key]
    return out


ALL = "All"   # the sentinel each MultiSelect shows when nothing is excluded


def _expand(value, everything):
    """A MultiSelect value -> the set of real entities it selects. "All" (or
    an empty value, which the normaliser turns into "All" anyway) means
    every one of them; anything else is taken literally."""
    if not value or ALL in value:
        return set(everything)
    return set(value)


def _toggle(current, value):
    """The cross-filter click rule for the selector views: clicking an entity
    narrows to it; clicking the one that is already the only one selected
    puts "All" back, so a second click always undoes the first."""
    return [ALL] if current == [value] else [value]


def _rgba(hex_color, alpha):
    h = hex_color.lstrip("#")
    return f"rgba({int(h[0:2], 16)},{int(h[2:4], 16)},{int(h[4:6], 16)},{alpha})"


def build_mui_dashboard():
    """Layout for the dashboard. Registers its callbacks on import
    (module-level @callback, same as the rest of this app's showcases) --
    import this module exactly once per running Dash app.
    """
    controls = dmc.Stack(
        children=[
            dmc.Select(
                id=_id("metric"), label="Metric",
                data=[{"label": v["label"], "value": k} for k, v in METRICS.items()],
                value="revenue", clearable=False, allowDeselect=False, w="100%",
            ),
            dmc.Stack(
                [
                    dmc.Text("Palette", size="sm", fw=500),
                    dmc.SegmentedControl(
                        id=_id("palette"),
                        data=list(PALETTES.keys()),
                        value="Indigo", size="xs", fullWidth=True,
                    ),
                ],
                gap=4,
            ),
            dmc.Stack(
                [
                    dmc.Text("Months", size="sm", fw=500),
                    dmc.RangeSlider(
                        id=_id("months"), min=1, max=12, step=1, value=[1, 12],
                        minRange=0,
                        marks=[{"value": 1, "label": "Jan"},
                               {"value": 6, "label": "Jun"},
                               {"value": 12, "label": "Dec"}],
                    ),
                    dmc.Space(h="sm"),
                ],
                gap=4,
            ),
            dmc.MultiSelect(id=_id("regions"), label="Regions",
                            data=[ALL, *REGIONS], value=[ALL], clearable=False, w="100%"),
            dmc.MultiSelect(id=_id("channels"), label="Channels",
                            data=[ALL, *CHANNELS], value=[ALL], clearable=False, w="100%"),
            dmc.MultiSelect(id=_id("products"), label="Products",
                            data=[ALL, *PRODUCTS], value=[ALL], clearable=False, w="100%"),
            dmc.Switch(id=_id("stack-toggle"), label="Stack the regions",
                       checked=False, size="sm"),
            dmc.Button(
                "Reset filters", id=_id("reset-btn"), n_clicks=0,
                leftSection=DashIconify(icon="mdi:filter-remove-outline", width=16),
                variant="outline", fullWidth=True,
            ),
            dmc.Text(id=_id("row-count"), size="xs", c="dimmed"),
        ],
        gap="md",
        w={"base": "100%", "md": 230},
        style={"flexShrink": 0},
    )

    def card(title, hint, child, extra=None):
        # `hint` is usually a plain string, wrapped in the muted caption Text
        # below -- but the heatmap passes a live component instead (its
        # click caption), so anything that already looks like a Dash
        # component is used as-is rather than re-wrapped.
        head = [dmc.Text(title, size="sm", fw=600)]
        if extra is not None:
            head.append(extra)
        head.append(hint if hasattr(hint, "_namespace") else dmc.Text(hint, size="xs", c="dimmed"))
        return dmc.Paper(
            [dmc.Group(head, justify="space-between", mb="xs", wrap="nowrap"), child],
            withBorder=True, radius="md", p="md",
        )

    def rtl(child):
        """Wraps a view so it slides in from the RIGHT and is uncovered from
        its right edge towards the left. Neither MUI X nor this page's
        Plotly views have an animation-direction setting, so each view's own
        animation is off and this CSS replaces it (assets/mui-dashboard.css).
        The `rtl-in` class that runs it is added by the clientside callback
        at the bottom of this file on every redraw, not here, so the first
        entrance plays over real data rather than the empty initial state.
        """
        return dmc.Box(child, className="mui-rtl")

    _graph_config = {"displayModeBar": False, "responsive": True}

    charts = dmc.Stack(
        [
            # Static cards, no flip: the number, its % change and the
            # sparkline all sit on the one face, permanently -- nothing to
            # click to see them.
            dmc.SimpleGrid(
                [
                    dmc.Paper(
                        [
                            dmc.Group(
                                [dmc.Text(METRICS[k]["label"], size="xs", c="dimmed"),
                                 dmc.Text(id=_id(f"kpi-change-{k}"), size="xs", fw=600)],
                                justify="space-between",
                            ),
                            dmc.Text(id=_id(f"kpi-{k}"), fw=700, size="xl"),
                            # Plotly, not dmuic.SparklineChart: MUI's sparkline
                            # only ever highlights ONE point (highlightedIndex),
                            # and this needs two (the month's low and its
                            # high) -- the same lo_i/hi_i marker trick the
                            # trend chart's line mode already uses.
                            dcc.Graph(
                                id=_id(f"spark-{k}"), config={"displayModeBar": False,
                                                              "staticPlot": True},
                                style={"height": 40, "borderRadius": "6px",
                                       "overflow": "hidden"},
                            ),
                        ],
                        withBorder=True, radius="md", p="md",
                    )
                    for i, k in enumerate(METRICS)
                ],
                cols={"base": 1, "sm": 3}, spacing="sm",
            ),
            card("Trend by month", "click a month to drill in",
                 rtl(dcc.Graph(id=_id("trend"), config=_graph_config,
                               style={"height": 290})),
                 extra=dmc.SegmentedControl(
                     id=_id("trend-type"),
                     data=[{"label": "Bar", "value": "bar"},
                           {"label": "Line", "value": "line"}],
                     value="bar", size="xs",
                 )),
            dmc.SimpleGrid(
                [
                    card("By product", "click a cell",
                         rtl(dcc.Graph(id=_id("heatmap"), config=_graph_config,
                                       style={"height": 270}))),
                    card("By channel", "click a slice",
                         rtl(dmuic.PieChart(id=_id("by-channel"), data=[], height=260,
                                            innerRadius=52, paddingAngle=2, cornerRadius=4,
                                            arcLabel="label", arcLabelMinAngle=25,
                                            highlightScope={"highlight": "item",
                                                            "fade": "global"},
                                            skipAnimation=True))),
                ],
                cols={"base": 1, "lg": 2}, spacing="sm",
            ),
            card("By region", "click a region · hover for the dmc-style tooltip",
                 rtl(dmc.Box(
                     [
                         dcc.Graph(id=_id("map"), config=_graph_config,
                                   style={"height": 320}),
                         # A Mantine-look tooltip, not Plotly's own hover box:
                         # positioned in raw pixels by the clientside callback
                         # at the bottom of this file, which listens for
                         # plotly_hover/plotly_unhover on the graph's own DOM
                         # node -- see that callback for why.
                         dmc.Paper(
                             id=_id("map-tooltip"),
                             radius="sm",
                             style={
                                 "position": "absolute", "top": 0, "left": 0,
                                 "padding": "5px 10px", "pointerEvents": "none",
                                 "background": "#1a1b1e", "color": "#f8f9fa",
                                 "fontSize": "12px", "fontWeight": 500,
                                 "whiteSpace": "nowrap", "opacity": 0, "zIndex": 5,
                                 "transition": "opacity 0.12s ease",
                                 "transform": "translate(-9999px, -9999px)",
                             },
                         ),
                     ],
                     style={"position": "relative"},
                 ))),
            card("Order details", "every order that matches the filters",
                 dmc.Box(
                     dag.AgGrid(
                         id=_id("details-grid"),
                         columnDefs=[
                             {"field": "id", "headerName": "Order", "maxWidth": 110},
                             {"field": "date", "maxWidth": 130},
                             {"field": "region", "maxWidth": 110},
                             {"field": "channel", "maxWidth": 120},
                             {"field": "product"},
                             {"field": "units", "type": "numericColumn", "maxWidth": 100},
                             {"field": "revenue", "type": "numericColumn",
                              "valueFormatter": {"function": "'$' + params.value.toLocaleString()"}},
                         ],
                         defaultColDef={"sortable": True, "filter": True, "resizable": True},
                         rowData=[],
                         dashGridOptions={"pagination": True, "paginationPageSize": 10,
                                           "animateRows": False},
                         style={"height": 360, "width": "100%"},
                         className="ag-theme-alpine",
                     ),
                     id=_id("details-wrap"), style={"width": "100%"},
                 ),
                 extra=dmc.Switch(id=_id("grid-toggle"), label="Show",
                                  checked=True, size="xs")),
        ],
        gap="sm",
        style={"flex": "1 1 auto", "minWidth": 0},
    )

    # The subtitle and badge are written by _render, so the header always
    # names what the views below are actually showing.
    header = dmc.Group(
        [
            dmc.Stack(
                [dmc.Title("Orders overview", order=3, m=0),
                 dmc.Text(id=_id("subtitle"), size="sm", c="dimmed")],
                gap=2,
            ),
            dmc.Badge(id=_id("header-count"), variant="light", color="gray",
                      size="lg", radius="sm"),
        ],
        justify="space-between", align="flex-end", mb="sm",
    )

    body = dmc.Flex(
        [controls, charts],
        direction={"base": "column", "md": "row"},
        align={"base": "stretch", "md": "flex-start"},
        gap="sm",
    )

    # The heatmap's own popup: a real dmc.Modal, not a hand-positioned
    # floating div like the map's hover tooltip -- a click needs no cursor
    # tracking, just an opened=True/False flip, so the simpler component is
    # the right one here. _heat_click fills in the title and the chart.
    heat_modal = dmc.Modal(
        id=_id("heat-modal"), opened=False, centered=True, size="sm",
        title=dmc.Text(id=_id("heat-modal-title"), fw=600, size="sm"),
        children=dcc.Graph(id=_id("heat-modal-chart"),
                           config={"displayModeBar": False}, style={"height": 220}),
    )

    return dmc.Box(
        [header, body, heat_modal, dcc.Store(id=_id("anim-signal")),
         dcc.Store(id=_id("map-tooltip-signal"))],
        id=_id("root"),
    )


_SPARK_BG = "#343a40"     # fixed dark grey tile -- not themed, unlike the rest of the page
_SPARK_LINE = "#ffffff"   # white -- the connecting line itself, against that dark tile
_SPARK_LOW = "#ff6b6b"    # red: this metric's lowest month in range (lightened for the dark tile)
_SPARK_HIGH = "#69db7c"   # green: its highest (lightened for the dark tile)


def _spark_figure(values):
    """The KPI cards' own mini chart: a white line over a fixed dark-grey
    tile, with a marker ONLY at this metric's lowest month (red) and highest
    (green) -- nothing else drawn, the same lo_i/hi_i idea the trend chart's
    line mode uses, in the usual down/up colours rather than the active
    theme, so the read ("when was this at its worst/best") never depends on
    which Palette is selected.
    """
    lo_i, hi_i = values.index(min(values)), values.index(max(values))
    sizes = [7 if i in (lo_i, hi_i) else 0 for i in range(len(values))]
    colors = [_SPARK_LOW if i == lo_i else _SPARK_HIGH if i == hi_i else _SPARK_LINE
             for i in range(len(values))]
    fig = go.Figure(go.Scatter(
        y=values, mode="lines+markers", hoverinfo="skip",
        line=dict(color=_SPARK_LINE, width=2, shape="spline", smoothing=0.6),
        marker=dict(size=sizes, color=colors, line=dict(color=_SPARK_BG, width=1.5)),
    ))
    fig.update_layout(
        margin=dict(l=2, r=2, t=4, b=4),
        paper_bgcolor=_SPARK_BG, plot_bgcolor=_SPARK_BG,
        showlegend=False,
        xaxis=dict(visible=False, fixedrange=True),
        yaxis=dict(visible=False, fixedrange=True),
    )
    return fig


def _trend_figure(rows, regions, month_idx, metric, stack, region_colors, chart_type="bar"):
    """One series per region, as grouped/stacked bars (the default) or as
    lines with an area fill -- the SegmentedControl next to this card's
    title picks which.

    Plotly, not dmuic.LineChart / CompositeChart / BarChart's own stacking
    quirks: both Pro components are ruled out on licensing, and doing both
    chart types from one Plotly figure keeps the region colours, the
    stack/group toggle and the click-to-drill-in behaviour identical
    regardless of which shape is showing -- only the trace type changes.

    `region_colors` is a plain {region: hex} map built by the caller (see
    _lead / _shade_map): every region is a fixed shade of the one active
    theme colour, except whichever region currently has the largest total,
    which gets the ACCENT colour instead -- the one deliberate exception to
    "colour follows the entity, never its rank" on this page.
    """
    labels = [MONTH_LABELS[m - 1] for m in month_idx]
    value_fmt = "$,.0f" if metric == "revenue" else ",.0f"
    fig = go.Figure()
    for region in (r for r in REGIONS if r in regions):
        per_month = _by([r for r in rows if r["region"] == region], metric, "month")
        color = region_colors[region]
        y = [round(per_month.get(m, 0), 2) for m in month_idx]
        hover = f"<b>{region}</b><br>%{{x}}: %{{y:{value_fmt}}}<extra></extra>"
        if chart_type == "bar":
            # barmode ("stack" or "group", set on the layout below) is what
            # actually arranges these -- no per-trace stack/group key needed.
            # cornerradius + a thin white outline: rounded, breathing-room
            # bar ends rather than square blocks butted against each other.
            trace = go.Bar(x=labels, y=y, name=region,
                            marker=dict(color=color, cornerradius=4,
                                        line=dict(color="#ffffff", width=1)),
                            hovertemplate=hover)
        else:
            # Markers only at each region's lowest and highest month -- the
            # two points worth a reader's eye -- not one on every month,
            # which on a 12-point spline just repeats what the line shows.
            lo_i, hi_i = y.index(min(y)), y.index(max(y))
            sizes = [8 if i in (lo_i, hi_i) else 0 for i in range(len(y))]
            kwargs = dict(
                x=labels, y=y, name=region, mode="lines+markers",
                line=dict(color=color, width=2, shape="spline", smoothing=0.6),
                marker=dict(size=sizes, color=color, line=dict(color="#ffffff", width=1.5)),
                hovertemplate=hover,
            )
            if stack:
                kwargs.update(stackgroup="total", fillcolor=_rgba(color, 0.55))
            else:
                kwargs.update(fill="tozeroy", fillcolor=_rgba(color, 0.14))
            trace = go.Scatter(**kwargs)
        fig.add_trace(trace)
    tick = "$~s" if metric == "revenue" else "~s"
    fig.update_layout(
        barmode="stack" if (chart_type == "bar" and stack) else "group",
        bargap=0.22, bargroupgap=0.08,
        margin=dict(l=48, r=12, t=8, b=32),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="system-ui, -apple-system, Segoe UI, sans-serif",
                  size=12, color=_INK),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="left", x=0,
                    bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(type="category", showgrid=False, linecolor=_LINE, fixedrange=True),
        yaxis=dict(showgrid=True, gridcolor=_GRID, gridwidth=1,
                   zeroline=False, tickformat=tick, fixedrange=True),
    )
    return fig


def _map_figure(rows_no_region, regions, metric, region_colors):
    """The region selector: every country filled with its region's colour --
    a fixed shade of the theme, except the current leader in ACCENT (see
    _lead / _shade_map) -- greyed out (MUTED) when that region is outside
    the selection.

    Built WITHOUT the region filter, the same rule as every cross-filter
    source -- a view that picks regions must keep showing all of them. One
    trace per region, so a click reports the region directly (customdata)
    rather than a country the callback would have to look up.

    Plotly's own hover box is switched off visually (every hoverlabel colour
    set transparent) rather than with hoverinfo="skip", which would also stop
    the plotly_hover DOM event the map-tooltip clientside callback listens
    for. `text` carries the caption that callback reads instead -- a dmc-look
    floating tooltip standing in for the one MUI X has no map chart to draw.
    """
    per_region = _by(rows_no_region, metric, "region")
    fig = go.Figure()
    for region in REGIONS:
        color = region_colors[region] if region in regions else MUTED
        isos = COUNTRIES[region]
        caption = f"{region} — {_fmt(per_region.get(region, 0), metric)}"
        fig.add_trace(go.Choropleth(
            locations=isos, locationmode="ISO-3", z=[1] * len(isos),
            colorscale=[[0, color], [1, color]], showscale=False,
            marker_line_color="#ffffff", marker_line_width=0.4,
            customdata=[region] * len(isos), text=[caption] * len(isos),
            name=region, hovertemplate="%{text}<extra></extra>",
            hoverlabel=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(0,0,0,0)",
                            font=dict(color="rgba(0,0,0,0)", size=1)),
        ))
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        geo=dict(projection_type="natural earth", showframe=False,
                 showcoastlines=False, showcountries=False,
                 showland=True, landcolor="#f1f3f5", bgcolor="rgba(0,0,0,0)",
                 lataxis_range=[-58, 85]),
        # Keeps a user's pan/zoom across redraws, which would otherwise reset
        # the map every time any filter changed.
        uirevision="map",
    )
    return fig


def _heat_figure(rows_no_product, selected_products, month_idx, metric, sequential):
    """The product-by-month heatmap, as a real Plotly go.Heatmap -- no
    printed numbers, no hover popup (every hoverlabel colour is transparent,
    same trick as the map). A click is what surfaces a value: it narrows the
    board to that product AND that month, the same cross-filter every other
    view here does, and the callback below echoes the clicked cell's own
    quantity into the caption next to this card's title. hoverinfo="none",
    not "skip" -- "skip" also silences the plotly_click event the cross-filter
    callback needs, not just the (already unwanted) hover box.

    Rows outside the current product selection are veiled with a translucent
    band, since a heatmap has one colour scale and cannot recolour a row on
    its own.

    Plotly, not dmuic.Heatmap: that one is MUI X Pro, and without a licence
    key it burns a large, plainly legible "MUI X Missing license key"
    watermark INTO the rendered chart -- not a console-only warning like
    LineChart/CompositeChart, but something every viewer of the page sees,
    confirmed by screenshotting the actual chart rather than just checking
    devtools.

    Rows are sorted by their total, DESCENDING, biggest first. Built
    WITHOUT the product filter, the same rule as every cross-filter
    source: a view that picks products must keep showing all of them, or
    one click would leave a single row with nothing else to pick.
    """
    cell = _by(rows_no_product, metric, "product", "month")
    totals = {p: sum(cell.get((p, m), 0) for m in month_idx) for p in PRODUCTS}
    order = sorted(PRODUCTS, key=lambda p: totals[p], reverse=True)
    labels = [MONTH_LABELS[m - 1] for m in month_idx]
    z = [[round(cell.get((p, m), 0), 2) for m in month_idx] for p in order]
    scale = [[i / (len(sequential) - 1), c] for i, c in enumerate(sequential)]

    fig = go.Figure(go.Heatmap(
        z=z, x=labels, y=order, colorscale=scale, showscale=False,
        xgap=2, ygap=2, hoverinfo="none",
        hoverlabel=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(0,0,0,0)",
                        font=dict(color="rgba(0,0,0,0)", size=1)),
    ))
    best = None   # (row, col, value) -- the single largest cell among SELECTED
    # products only, so a veiled row can never be the one that gets outlined.
    for i, product in enumerate(order):
        if product not in selected_products:
            fig.add_shape(type="rect", xref="paper", x0=0, x1=1, yref="y",
                          y0=i - 0.5, y1=i + 0.5, line_width=0,
                          fillcolor="rgba(255,255,255,0.72)", layer="above")
            continue
        for j, v in enumerate(z[i]):
            if best is None or v > best[2]:
                best = (i, j, v)
    if best is not None:
        i, j, _ = best
        # The one ACCENT touch on an otherwise single-hue chart: an outline,
        # not a fill, so the cell's own shade (its actual value) stays readable.
        fig.add_shape(type="rect", xref="x", x0=j - 0.5, x1=j + 0.5,
                      yref="y", y0=i - 0.5, y1=i + 0.5,
                      line=dict(color=ACCENT, width=3), layer="above")
    fig.update_layout(
        # l is a floor, not the real margin: `automargin` on the y-axis
        # below is what actually reserves enough room for the product
        # names. Without it Plotly draws tick labels in whatever space l
        # happened to leave, which can put them on top of the cells.
        margin=dict(l=56, r=8, t=8, b=28),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="system-ui, -apple-system, Segoe UI, sans-serif",
                  size=12, color=_INK),
        xaxis=dict(side="bottom", showgrid=False, fixedrange=True),
        # Top row = biggest total: category order as built, drawn top-down.
        yaxis=dict(autorange="reversed", showgrid=False, fixedrange=True,
                   automargin=True),
    )
    return fig


@callback(
    Output(_id("subtitle"), "children"),
    Output(_id("header-count"), "children"),
    Output(_id("row-count"), "children"),
    *[Output(_id(f"kpi-{k}"), "children") for k in METRICS],
    *[Output(_id(f"kpi-change-{k}"), "children") for k in METRICS],
    *[Output(_id(f"kpi-change-{k}"), "c") for k in METRICS],
    *[Output(_id(f"spark-{k}"), "figure") for k in METRICS],
    Output(_id("trend"), "figure"),
    Output(_id("heatmap"), "figure"),
    Output(_id("details-grid"), "rowData"),
    Output(_id("by-channel"), "data"),
    Output(_id("map"), "figure"),
    Input(_id("metric"), "value"),
    Input(_id("months"), "value"),
    Input(_id("regions"), "value"),
    Input(_id("channels"), "value"),
    Input(_id("products"), "value"),
    Input(_id("stack-toggle"), "checked"),
    Input(_id("trend-type"), "value"),
    Input(_id("palette"), "value"),
)
def _render(metric, months, regions, channels, products, stack, trend_type, palette):
    """One callback for the whole board, deliberately: every view is a
    projection of the same filtered rows, so splitting this would run the
    query once per view and allow one view to update while another has not.
    """
    months = months or [1, 12]
    regions = _expand(regions, REGIONS)
    channels = _expand(channels, CHANNELS)
    products = _expand(products, PRODUCTS)
    rows = query(regions, channels, products, months)
    lo, hi = months
    month_idx = list(range(lo, hi + 1))
    labels = [MONTH_LABELS[m - 1] for m in month_idx]

    # The active theme, and the heatmap ramp generated to match it -- every
    # view below reads `categorical`/`sequential`, never the module-level
    # CATEGORICAL/SEQUENTIAL defaults, so switching the Palette control
    # recolours everything on the page in one render.
    categorical = PALETTES.get(palette, CATEGORICAL)
    sequential = _ramp(categorical[0])

    # --- KPI cards ----------------------------------------------------------
    # The number and a % change badge (first month in range -> last), plus a
    # small white-on-grey line chart marking only that metric's lowest (red)
    # and highest (green) month in range -- nothing else on it, the same
    # "just the two points that matter" idea as the trend chart's own line
    # mode, in fixed colours so it reads the same under every Palette.
    kpis, changes, change_colors, sparks = [], [], [], []
    for key in METRICS:
        kpis.append(_fmt(_total(rows, key), key))
        per_month = _by(rows, key, "month")
        series = [round(per_month.get(m, 0), 2) for m in month_idx]
        sparks.append(_spark_figure(series))

        first_v, last_v = series[0], series[-1]
        if len(series) > 1 and first_v:
            pct = (last_v - first_v) / first_v * 100
            changes.append(f"{'▲' if pct >= 0 else '▼'} {abs(pct):.1f}%")
            change_colors.append("teal" if pct >= 0 else "red")
        else:
            changes.append("—")
            change_colors.append("dimmed")

    # --- Region shades + leader: shared by the trend chart and the map, ----
    # since both show the same three regions and must agree on who is ahead.
    region_totals = _by(query(REGIONS, channels, products, months), metric, "region")
    region_colors = _shade_map(REGIONS, categorical[0])
    lead_region = _lead(region_totals, regions)
    if lead_region:
        region_colors[lead_region] = ACCENT

    trend = _trend_figure(rows, regions, month_idx, metric, stack, region_colors, trend_type)

    # --- Heatmap: ignores the product filter (it IS that filter) -----------
    heatmap = _heat_figure(query(regions, channels, set(PRODUCTS), months),
                           products, month_idx, metric, sequential)

    # --- Details grid: every surviving row, one per order -------------------
    # AG Grid wants JSON-serialisable rows -- dates go out as ISO strings,
    # not Python date objects.
    grid_rows = [{**r, "date": r["date"].isoformat()} for r in rows]

    # --- Donut: ignores the channel filter (it IS that filter) -------------
    # Slices in DESCENDING order of value; each channel keeps its own fixed
    # shade, except the current leader, which is ACCENT regardless of slot.
    per_channel = _by(query(regions, set(CHANNELS), products, months), metric, "channel")
    channel_colors = _shade_map(CHANNELS, categorical[0])
    lead_channel = _lead(per_channel, channels)
    if lead_channel:
        channel_colors[lead_channel] = ACCENT
    channel_data = [{"id": CHANNELS.index(c), "value": round(per_channel[c], 2), "label": c,
                     "color": channel_colors[c] if c in channels else MUTED}
                    for c in sorted(per_channel, key=per_channel.get, reverse=True)
                    if per_channel[c]]

    # --- Map: ignores the region filter (it IS that filter) ----------------
    region_map = _map_figure(query(set(REGIONS), channels, products, months),
                             regions, metric, region_colors)

    span = labels[0] if len(labels) == 1 else f"{labels[0]} – {labels[-1]}"
    subtitle = f"{METRICS[metric]['label']} · {span} 2026"
    return (subtitle, f"{len(rows):,} orders",
            f"{len(rows):,} of {len(ORDERS):,} orders match",
            *kpis, *changes, *change_colors, *sparks,
            trend, heatmap, grid_rows, channel_data, region_map)


# --- Cross-filtering: every view writes back into the dmc control it owns --
# All write the SAME control a person would, so the sidebar always shows the
# true state and _render does the rest.

@callback(
    Output(_id("months"), "value", allow_duplicate=True),
    Input(_id("trend"), "clickData"),
    State(_id("months"), "value"),
    prevent_initial_call=True,
)
def _trend_click(click, months):
    """The trend is the one DRILL-DOWN rather than a selector -- clicking a
    month zooms to it and clicking it again zooms back out -- because it is
    a time axis, and "show me just May" is what a click on May means."""
    points = (click or {}).get("points") or []
    label = points[0].get("x") if points else None
    if label not in MONTH_LABELS:
        return no_update
    m = MONTH_LABELS.index(label) + 1
    return [1, 12] if months == [m, m] else [m, m]


@callback(
    Output(_id("channels"), "value", allow_duplicate=True),
    Input(_id("by-channel"), "clickData"),
    State(_id("channels"), "value"),
    prevent_initial_call=True,
)
def _pie_click(click, current):
    """`label`, not `dataIndex`: the index counts only the slices drawn, and
    they are drawn in value order, which moves; the label is the name."""
    channel = (click or {}).get("label")
    return _toggle(current, channel) if channel in CHANNELS else no_update


@callback(
    Output(_id("regions"), "value", allow_duplicate=True),
    Input(_id("map"), "clickData"),
    State(_id("regions"), "value"),
    prevent_initial_call=True,
)
def _map_click(click, current):
    points = (click or {}).get("points") or []
    region = points[0].get("customdata") if points else None
    return _toggle(current, region) if region in REGIONS else no_update


def _mini_figure(values, labels, marked_idx, shade):
    """The heatmap modal's own small chart: that product across the whole
    year, the clicked month picked out in ACCENT among bars otherwise all
    one shade of the active theme -- the same shade/ACCENT split as the rest
    of the page.
    """
    colors = [ACCENT if i == marked_idx else shade for i in range(len(values))]
    fig = go.Figure(go.Bar(x=labels, y=values,
                            marker=dict(color=colors, cornerradius=3)))
    fig.update_layout(
        margin=dict(l=36, r=8, t=8, b=26),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        font=dict(family="system-ui, -apple-system, Segoe UI, sans-serif",
                  size=11, color=_INK),
        xaxis=dict(showgrid=False, fixedrange=True),
        yaxis=dict(showgrid=True, gridcolor=_GRID, zeroline=False, fixedrange=True),
    )
    return fig


@callback(
    Output(_id("products"), "value", allow_duplicate=True),
    Output(_id("months"), "value", allow_duplicate=True),
    Output(_id("heat-modal-title"), "children"),
    Output(_id("heat-modal-chart"), "figure"),
    Output(_id("heat-modal"), "opened"),
    Input(_id("heatmap"), "clickData"),
    State(_id("products"), "value"),
    State(_id("months"), "value"),
    State(_id("regions"), "value"),
    State(_id("channels"), "value"),
    State(_id("metric"), "value"),
    State(_id("palette"), "value"),
    prevent_initial_call=True,
)
def _heat_click(click, current_products, current_months, regions, channels, metric, palette):
    """A cell picks its product AND drills into its month at once -- a full
    2-axis cross-filter, not just the row -- and opens a dmc.Modal echoing
    the clicked cell's own quantity plus a small chart of that product
    across the whole year, since the heatmap itself prints no numbers of
    its own.
    """
    points = (click or {}).get("points") or []
    if not points:
        return no_update, no_update, no_update, no_update, no_update
    product, label, value = points[0].get("y"), points[0].get("x"), points[0].get("z")
    if product not in PRODUCTS or label not in MONTH_LABELS:
        return no_update, no_update, no_update, no_update, no_update
    m = MONTH_LABELS.index(label) + 1

    new_products = _toggle(current_products, product)
    new_months = [1, 12] if current_months == [m, m] else [m, m]

    year_rows = query(_expand(regions, REGIONS), _expand(channels, CHANNELS),
                      {product}, [1, 12])
    per_month = _by(year_rows, metric, "month")
    series = [round(per_month.get(mm, 0), 2) for mm in range(1, 13)]
    shade = PALETTES.get(palette, CATEGORICAL)[0]
    chart = _mini_figure(series, MONTH_LABELS, m - 1, shade)
    caption = f"{product} · {label}: {_fmt(value or 0, metric)}"
    return new_products, new_months, caption, chart, True


@callback(
    Output(_id("regions"), "value"),
    Output(_id("channels"), "value"),
    Output(_id("products"), "value"),
    Output(_id("months"), "value"),
    Input(_id("reset-btn"), "n_clicks"),
    prevent_initial_call=True,
)
def _reset(_n_clicks):
    """Resets the four filters, not the Metric or the stack switch -- those
    are how you are looking at the data, not which data you are looking at."""
    return [ALL], [ALL], [ALL], [1, 12]


@callback(
    Output(_id("details-wrap"), "style"),
    Input(_id("grid-toggle"), "checked"),
)
def _toggle_grid(show):
    """The order-details grid is the tallest thing on the page -- collapsing
    it (not unmounting it: rowData stays put, so it's back instantly) is the
    Show switch next to its own card title."""
    return {"width": "100%", "display": "block" if show else "none"}


# Replays the right-to-left entrance on every view whenever the board
# redraws. A CSS animation only runs when its class first lands, so removing
# the class, forcing a reflow (reading offsetWidth) and re-adding it is what
# restarts it. The trend figure changes with the metric, every filter and
# the stack switch, so it is the one input that covers them all.
clientside_callback(
    """
    function(_figure) {
        const root = document.getElementById('""" + _id("root") + """');
        if (!root) { return window.dash_clientside.no_update; }
        root.querySelectorAll('.mui-rtl').forEach(function(el) {
            el.classList.remove('rtl-in');
            void el.offsetWidth;
            el.classList.add('rtl-in');
        });
        return window.dash_clientside.no_update;
    }
    """,
    Output(_id("anim-signal"), "data"),
    Input(_id("trend"), "figure"),
    prevent_initial_call=True,
)


# The map's dmc-look tooltip: Plotly's own hover box is fully transparent
# (see _map_figure), so this is what actually shows anything. Bound to
# plotly_hover/plotly_unhover on the graph's OWN DOM node -- not exposed as a
# Dash prop at all, `hoverData` carries no pixel position -- because a
# tooltip needs the real mouse position (evt.event.clientX/clientY) to
# follow the cursor, not just which point was hovered. Rebinds on every
# redraw (Input is the figure), guarded by a flag on the node so the
# listener is only ever attached once to a given DOM element.
clientside_callback(
    """
    function(_figure) {
        // dcc.Graph's own id names the WRAPPER div -- the Plotly-managed
        // element that actually has .on() is a nested .js-plotly-plot child.
        const wrap = document.getElementById('""" + _id("map") + """');
        const gd = wrap && wrap.querySelector('.js-plotly-plot');
        const tip = document.getElementById('""" + _id("map-tooltip") + """');
        if (!gd || !tip || gd._dmcTooltipBound) { return window.dash_clientside.no_update; }
        gd._dmcTooltipBound = true;
        gd.on('plotly_hover', function(evt) {
            const pt = evt.points && evt.points[0];
            if (!pt || !evt.event) { return; }
            const label = (pt.data.text && pt.data.text[pt.pointNumber]) || pt.data.name;
            tip.textContent = label;
            const rect = wrap.getBoundingClientRect();
            const x = evt.event.clientX - rect.left + 14;
            const y = evt.event.clientY - rect.top + 14;
            tip.style.transform = 'translate(' + x + 'px,' + y + 'px)';
            tip.style.opacity = '1';
        });
        gd.on('plotly_unhover', function() { tip.style.opacity = '0'; });
        return window.dash_clientside.no_update;
    }
    """,
    Output(_id("map-tooltip-signal"), "data"),
    Input(_id("map"), "figure"),
    prevent_initial_call=True,
)




# "All" normaliser, one per MultiSelect. Mantine appends each new pick to the
# end of the value, which is what tells the two cases apart without keeping
# the previous value anywhere:
#   ["Laptop", "All"] -- "All" was just picked, so it replaces everything;
#   ["All", "Laptop"] -- a product was picked while "All" was on, so it wins.
# An emptied box becomes "All" rather than a filter that matches nothing.
# Clientside, so the tidy-up costs no round trip -- and _expand() already
# reads either half-tidied state correctly, so the render in between is right.
for _name in ("regions", "channels", "products"):
    clientside_callback(
        """
        function(v) {
            if (!v || v.length === 0) { return ['All']; }
            if (v.length > 1 && v.indexOf('All') !== -1) {
                return v[v.length - 1] === 'All' ? ['All']
                                                 : v.filter(function(x) { return x !== 'All'; });
            }
            return window.dash_clientside.no_update;
        }
        """,
        Output(_id(_name), "value", allow_duplicate=True),
        Input(_id(_name), "value"),
        prevent_initial_call=True,
    )


# What `.. exec::docs.mui_dashboard.dashboard` renders on the /mui-dashboard
# docs page. The PAGE_CLASS wrapper scopes assets/mui-dashboard.css to this
# demo alone.
component = dmc.Box(build_mui_dashboard(), className=PAGE_CLASS)
