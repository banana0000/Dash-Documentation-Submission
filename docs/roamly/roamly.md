---
name: Roamly
description: Roamly is a house-only stay booking mockup built on Dash Mantine Components — a listings grid with a globe, a stay page with a photo gallery and a dash-leaflet2 map, and a host dashboard of dash-mui-charts.
endpoint: /roamly
package: dash_leaflet2
icon: tabler:map-2
category: Showcases
order: 6
---

.. llms_copy::Roamly

.. toc::

### Introduction

**Roamly** is a house-only stay/property booking platform mockup. It is not a
single component demo like the other showcases — it is a small product built
from several 2plot.ai packages at once:

- [dash-leaflet2](https://leaflet.2plot.dev) for the per-stay map, with its
  own draw/edit toolbar
- [dash-image-gallery](https://github.com/pip-install-python/dash-image-gallery)
  for the photo carousel
- [dash-mui-charts](https://muicharts.2plot.dev) for the host dashboard's bar
  chart and sparklines
- [Dash Mantine Components](https://www.dash-mantine-components.com/) for
  everything else, plus Plotly's `Scattergeo` for the globe

The three sections below are the three pages of the standalone app, embedded
on one route. The standalone app (its own `AppShell`, theme, dark-mode toggle
and page router) lives in `examples/roamly/` and is documented at the bottom.

---

### Stays

A grid of demo stays, and a wide orthographic globe pinning all of them.
Click a card to open that stay in the **Listing detail** section:

.. exec::docs.roamly.stays
    :code: false

---

### Listing detail

The full stay page: a description, a photo gallery beside a booking card with
a `dmc.TimePicker` check-in field and host info, and a full-width
dash-leaflet2 map with its own draw/edit toolbar. The standalone app reads the
stay from the URL (`/listing/<id>`); here a Select picks it:

.. exec::docs.roamly.listing
    :code: false

---

### Host dashboard

A host's listings with dash-mui-charts view-count charts, styled to stay
readable in dark mode (the chart library does not follow Mantine's colour
scheme on its own — see `assets/roamly-embed.css`):

.. exec::docs.roamly.host
    :code: false

---

### How it works

All three sections read the same listing data — three demo stays in
`examples/roamly/data.py`, imported by both the docs demos and the standalone
app, so the two can never show different stays.

**The globe** is Plotly's own `Scattergeo` with an orthographic projection,
rather than a flat 2D map: draggable to rotate, scroll to zoom, same as any
other `dcc.Graph`. Its land and ocean colours follow this site's dark mode
through one callback on the MantineProvider's `forceColorScheme`.

**The listing map** is a `dl.Map` with an Esri tile layer, a Marker carrying
an Iconify icon, and a `dl.EditControl` — dash-leaflet2's draw/edit toolbar,
which keeps its shapes in its own internal FeatureGroup, so no manual
wrapping is needed. Esri is kept as the one tile provider for both colour
schemes (its Dark Gray Canvas in dark mode), and the whole detail view is
rebuilt when either the selected stay or the colour scheme changes:

```python
@callback(
    Output("rm-listing-detail", "children"),
    Input("rm-listing-picker", "value"),
    Input("m2d-mantine-provider", "forceColorScheme"),
    prevent_initial_call=True,
)
def _render_detail(listing_id, scheme):
    listing = get_listing(listing_id)
    if listing is None:
        return not_found()
    return listing_detail(listing, dark=(scheme == "dark"))
```

**The cards** in the Stays section carry a pattern-matching id. One callback
reads `ctx.triggered_id["index"]` to learn which card was clicked and writes
that stay's id into the Listing detail picker; a clientside callback scrolls
the detail into view at the same time.

**The host dashboard** is static data rendered once at import: four summary
cards, a `dmuic.BarChart` of twelve months of views with a reference line at
the peak month, and a `dmuic.SparklineChart` per listing.

---

### Source

The three docs sections, one file each:

.. source::docs/roamly/stays.py
    :defaultExpanded: false
    :withExpandedButton: true

.. source::docs/roamly/listing.py
    :defaultExpanded: false
    :withExpandedButton: true

.. source::docs/roamly/host.py
    :defaultExpanded: false
    :withExpandedButton: true

---

### Standalone app

Unlike the other showcases, Roamly is a full multi-page Dash app of its own —
its own `AppShell`, theme, dark-mode toggle and page router — so it does not
import anything from this site. It lives in `examples/roamly/`:

| Page | Route | Notes |
|---|---|---|
| Listings | `/` | Grid of three demo stays, plus the globe |
| Listing detail | `/listing/<id>` | Gallery, booking card, dash-leaflet2 map |
| Host dashboard | `/host` | dash-mui-charts view-count charts |

```bash
pip install -r examples/roamly/requirements.txt   # dash_leaflet2, dash_image_gallery, dash_mui_charts
python examples/roamly/app.py
```

Serves on **http://localhost:8870**.

.. source::examples/roamly/app.py
    :defaultExpanded: false
    :withExpandedButton: true

.. source::examples/roamly/data.py
    :defaultExpanded: false
    :withExpandedButton: true
