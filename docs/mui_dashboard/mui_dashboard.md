---
name: MUI Charts Dashboard
description: One dataset of 1,400 orders and six cross-filtered views of it — dmc query controls narrow the rows, and clicking any chart narrows them too.
endpoint: /mui-dashboard
package: dash_mui_charts
icon: mdi:chart-box-outline
category: Showcases
order: 7
---

.. llms_copy::MUI Charts Dashboard

.. toc::

### Introduction

A playground for [dash-mui-charts](https://muicharts.2plot.dev) — 2plot.ai's Dash
wrapper around [MUI X Charts](https://mui.com/x/react-charts/) — paired with
[dash-mantine-components](https://www.dash-mantine-components.com/) as the query
layer and Plotly for the views MUI X's free tier does not cover.

The whole page is **one dataset and six views of it**: three KPI cards, a
trend-by-month chart, a by-product heatmap, a by-channel donut, a by-region
map, and an order-details grid. `ORDERS` is 1,400 generated order rows and the
single source of truth; the sidebar narrows that list, and every view is
re-derived from whatever survives. No view keeps its own copy of anything, so
the six of them cannot disagree with each other.

**It cross-filters, not just filters.** The sidebar controls are not the only
way in — clicking a slice of the donut, a region on the map, a month on the
trend chart, or a row of the heatmap narrows the same underlying selection,
because each of those clicks writes back into the very dmc control a person
would have used. A second click on the same thing undoes it.

The rows are generated from a fixed seed rather than read from a file, so the
numbers are the same on every boot.

---

### Live demo

Narrow the months, drop a region or a channel, switch the metric — every card
and chart follows in one update:

.. exec::docs.mui_dashboard.dashboard
    :code: false

---

### How it works

**One query function.** Each control writes to a normal Dash `Input`, and all of
them land in the same function. A row either survives for all five charts or for
none of them:

```python
def query(regions, channels, products, months):
    lo, hi = months
    return [r for r in ORDERS
            if r["region"] in regions
            and r["channel"] in channels
            and r["product"] in products
            and lo <= r["month"] <= hi]
```

**One callback for the whole board, deliberately.** Splitting this into six
callbacks would run `query()` six times over identical inputs — and would allow
a state where one view has updated and another has not. Instead the single
callback fans one filtered list out into the shapes each view wants:

| View | Built with | Wants | Derived by |
|---|---|---|---|
| KPI cards ×3 | `dmc.Text` + `SparklineChart` | a value, a % change and a flat list of numbers | first-to-last-month change over the metric, summed per month |
| Trend by month | `go.Bar` / `go.Scatter` | one series per region | summing the metric per month, per region |
| By product | `go.Heatmap` | a 2-D grid | summing the metric per product per month |
| By channel | `PieChart` | `[{id, value, label}]` | summing per channel |
| By region | `go.Choropleth` | one trace per region | summing per region, mapped onto ISO-3 countries |
| Order details | `dag.AgGrid` | `rowData` | the raw filtered rows, one per order |

Those are genuinely different shapes, which is the point of building each view
from the tool suited to it rather than forcing every one through the same
component.

**Licensing decided what is MUI and what is Plotly, measured rather than
assumed.** `LineChart`, `CompositeChart` and `Heatmap` are all MUI X **Pro**:
without a licence key the first two log "purchase a license ... or stop using
the software immediately" to the console on every load, and the heatmap goes
further — it burns a plainly legible watermark straight **into the rendered
chart**, confirmed by screenshotting the actual output rather than trusting
devtools. All three are avoided here, which is why the trend chart and the
heatmap are both Plotly. `SparklineChart` and `PieChart` are free MUI X
Community, so those stay MUI.

**Every cross-filter source computes itself without its own dimension.** The
heatmap is built from rows that ignore the *product* filter, the donut from
rows that ignore the *channel* filter, and the map from rows that ignore the
*region* filter — each is the view that picks that dimension, so it has to
keep showing every option, or one click would leave nothing else to pick.
Everything else in the callback (the KPI cards, the trend chart) uses the
fully filtered rows.

**Metric switching has to change the shape, not just the scale.** Unit prices
differ per product, so *Revenue* and *Units* rank the products differently. If
they did not, the Metric picker would look broken — the bars would just rescale
and nothing would move. `orders` is the odd one out: it counts rows instead of
summing a field, which is what the `None` key in `METRICS` marks.

**The categorical palette is validated, not eyeballed.** Four colours, run
through the dataviz skill's `validate_palette.js` against this page's white
surface: the worst adjacent pair (the donut) clears CVD ΔE 8.9, the worst
all-pairs comparison (the map, which shows all three regions at once) clears
ΔE 10.3 — both above the ≥ 8 target. The heatmap's sequential ramp is the same
indigo as the palette's first slot, so "region blue" and "heatmap blue" read as
the same colour rather than two unrelated ones.

A couple of smaller things worth knowing:

- **Reset filters** clears the four *filters* but leaves Metric and the
  stack switch alone: those are how you are looking at the data, not which
  data you are looking at.
- The **row counter** under the button (`"812 of 1,400 orders match"`) exists so
  an empty view is never ambiguous — you can always tell "the filter excluded
  everything" from "something broke".
- Each MultiSelect carries an **"All"** entry rather than starting pre-ticked
  with every option: a clientside callback normalises what Mantine does when
  "All" and a real pick are both present, so the sidebar and `query()` always
  agree on what "everything" means.
- `minRange=0` on the month `RangeSlider` lets both handles land on the same
  month — that is what a trend-chart click drills into — without Mantine
  refusing the drag.

---

### Source

.. source::docs/mui_dashboard/dashboard.py
    :defaultExpanded: false
    :withExpandedButton: true

---

### Standalone app

The same dashboard runs on its own, with its own `Dash(__name__)` instance and
port:

```bash
python examples/mui_dashboard_app.py
```

Serves on **http://localhost:8100**.

.. source::examples/mui_dashboard_app.py
    :defaultExpanded: false
    :withExpandedButton: true
