---
name: Color Picker *
description: A color picker with three switchable shapes -- a continuous HSV wheel, clickable petals, and a ring of swatches
endpoint: /examples/color-mixer
package: color-mixer
icon: mdi:palette-outline
---

.. llms_copy::Color Picker *

.. toc::

### Introduction

One color picker, three shapes. A `dmc.SegmentedControl` filters which shape
is visible — **Wheel** (a continuous HSV wheel you sample by clicking
anywhere on it, like an eyedropper), **Flower** (six clickable preset
petals), or **Ring** (twelve preset swatches arranged in a circle). All
three feed the same center swatch and hex readout.

---

### Live Demo

Switch shapes with the control at the top, then click to pick a color:

.. exec::docs.color-mixer.mixer
    :code: false
Source code:

.. source::docs/color-mixer/mixer.py

---

### How It Works

**Wheel** is a `dcc.Graph` showing a static HSV raster (hue by angle,
saturation by radius, value fixed at 1) built once at import time with
`colorsys.hsv_to_rgb`, sitting on an explicit white card (`backgroundColor:
"white"`) so it reads the same regardless of light/dark theme. It's wrapped
in a `dmc.FloatingTooltip` — a real Mantine tooltip that tracks the cursor —
whose `label` a small callback keeps in sync with `hoverData`, so hovering
shows the exact hex code under the pointer. Plotly's own hover box is
turned off (`hoverinfo="skip"`) so only the Mantine tooltip shows:

```python
@callback(
    Output("mixer-wheel-tooltip", "label"),
    Input("mixer-wheel", "hoverData"),
)
def show_hover_hex(hover_data):
    if not hover_data:
        return _DEFAULT_COLOR
    point = hover_data["points"][0]
    return _hex_from_pixel(point["x"], point["y"])
```

Clicking the wheel fires `clickData`, which carries the exact pixel the
user clicked — that pixel is run back through the same hue/saturation math
to recover the color, and a small ring marker (a `go.Scatter` point) is
drawn at that spot so the pick stays visible:

```python
@callback(
    Output("mixer-center", "style"),
    Output("mixer-hex", "children"),
    Output("mixer-wheel", "figure"),
    Input("mixer-wheel", "clickData"),
    Input({"type": "mixer-petal", "color": ALL}, "n_clicks"),
    Input({"type": "mixer-ring", "color": ALL}, "n_clicks"),
)
def pick_color(click_data, _petal_clicks, _ring_clicks):
    triggered = ctx.triggered_id
    figure = no_update
    if triggered == "mixer-wheel" and click_data:
        point = click_data["points"][0]
        x, y = point["x"], point["y"]
        hex_color = _hex_from_pixel(x, y)
        figure = _wheel_figure((x, y))
    elif isinstance(triggered, dict) and triggered.get("type") in ("mixer-petal", "mixer-ring"):
        hex_color = triggered["color"]
    else:
        hex_color = _DEFAULT_COLOR
    ...
```

**Flower** and **Ring** are plain `html.Div`s carrying a pattern-matching id
— `{"type": "mixer-petal", "color": <hex>}` or `{"type": "mixer-ring",
"color": <hex>}` — positioned with plain arithmetic (`math.sin`/`math.cos`
for the ring, CSS `rotate()` for the petals). The same callback above
listens to all three shapes' inputs at once and reads `ctx.triggered_id` to
know which one fired — no `dcc.Store` needed anywhere.

All three shapes stay mounted in the DOM at all times; a second, smaller
callback just toggles which one is `display: block` based on the
`SegmentedControl`'s value, so switching shapes never destroys or re-creates
a picker's state.

---

### The Native Page

The same widget also ships as a first-class page at `/color-mixer`
(`pages/color_mixer.py`), wired through `register_page` instead of this
markdown file. It shares its layout and callbacks with this demo via
`components/color_mixer_widget.py`, and adds its own `LLMS_DOC` — served at
`/color-mixer/llms.txt` — plus a "Copy llms.txt URL" button, matching the
pattern from **Documenting a Page for AI Assistants** on the
[Getting Started](/getting-started) page.

Source code:

.. source::pages/color_mixer.py
    :defaultExpanded: false
    :withExpandedButton: true

---

### The Standalone App

`color_mixer_app.py` is a fully independent, single-file Dash app — its own
`Dash(__name__)` instance, its own `/llms.txt` Flask route, no imports from
this repo's `pages/` or `components/`. Run it on its own with:

```bash
python color_mixer_app.py
```

It serves on port 8560, separate from the main site's 8559.

Source code:

.. source::color_mixer_app.py
    :defaultExpanded: false
    :withExpandedButton: true
