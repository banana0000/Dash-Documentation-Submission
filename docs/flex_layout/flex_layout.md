---
name: FlexLayout Playground
description: An IDE-style docking layout built on dash-flexlayout — drag tab headers to rearrange a small sales dashboard, drop one on an edge to split a panel, and drag the splitters to resize.
endpoint: /flex-layout
package: dash_flexlayout
icon: mdi:view-dashboard-outline
category: Showcases
order: 4
---

.. llms_copy::FlexLayout Playground

.. toc::

### Introduction

A playground for [dash-flexlayout](https://flexlayout.2plot.dev) — 2plot.ai's
Dash wrapper around [flexlayout-react](https://github.com/caplin/FlexLayout),
the docking-layout engine behind IDE-style panel arrangements.

The panels hold a small sales dashboard — filters, KPI cards, two Plotly
charts, a donut and an orders table — rather than placeholder text, so
dragging a tab rearranges real widgets the way a BI tool's dockable panels
would.

---

### Live demo

Drag a tab's header onto another tabset, or onto a panel's edge to split it;
drag the splitters to resize; use the ⛶ button to maximize a tabset:

.. exec::docs.flex_layout.showcase
    :code: false

---

### How it works

The panel arrangement is a real flexlayout-react `Model` — a JSON tree of
`row` / `column` splits bottoming out in `tabset` containers holding `tab`
leaves. Every tab's `id` in that model matches a `Tab(id=...)` child of the
`FlexLayout` component; that is how dash-flexlayout knows which Dash children
render inside which tab:

```python
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
)
```

Dragging a tab's header (onto another tabset, or onto a panel's edge to split
it) mutates that same tree, which round-trips back through the `model` prop.
So **N tabs open** and **Reset layout** are reading and rewriting the exact
state the UI itself is showing — no separate client-side bookkeeping:

```python
@callback(
    Output(_id("tab-count"), "children"),
    Input(_id("layout"), "model"),
)
def _report_tab_count(model):
    count = _count_tabs(model.get("layout", {}))
    return f"{count} tabs open"


@callback(
    Output(_id("layout"), "model", allow_duplicate=True),
    Input(_id("reset-btn"), "n_clicks"),
    prevent_initial_call=True,
)
def _reset_layout(_n_clicks):
    return DEFAULT_MODEL
```

The three switches toggle the FlexLayout element's own `realtimeResize`,
`debugMode` and `supportsPopout` props directly.

The cyan accent — every Button, ActionIcon and Switch in the demo, plus
flexlayout-react's own selected-tab, splitter and drag-indicator colours —
comes from `assets/flexlayout.css`, scoped to the `.flexlayout-page` wrapper
so it never leaks into the rest of the site.

---

### Source

.. source::docs/flex_layout/showcase.py
    :defaultExpanded: false
    :withExpandedButton: true

---

### Standalone app

The same docking layout runs on its own, with its own `Dash(__name__)`
instance and port:

```bash
python examples/flexlayout_app.py
```

Serves on **http://localhost:8080**.

.. source::examples/flexlayout_app.py
    :defaultExpanded: false
    :withExpandedButton: true
