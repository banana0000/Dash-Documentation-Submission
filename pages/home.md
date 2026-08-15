# Color Picker

> A Dash color picker with four switchable shapes — a continuous HSV wheel, clickable petals, a ring of swatches, and a photo you sample like an eyedropper — built on top of the [Dash Documentation Boilerplate](https://github.com/pip-install-python/Dash-Documentation-Boilerplate) template. By [banana0000](https://github.com/banana0000).

One color picker, four shapes. A `dmc.SegmentedControl` switches between:

- **Wheel** — a continuous HSV wheel, hover to preview and click to lock a color, like an eyedropper
- **Flower** — two layered rings of six petals each, a lighter tint nested inside the full-saturation outer ring
- **Ring** — twelve preset swatches arranged in a circle
- **Photo** — a generated, photo-like image you sample pixel by pixel

All four feed the same center swatch and hex readout, and stay mounted in the DOM at once — switching shapes never destroys a picker's state.

---

## Try it

The full interactive demo, with a source-code walkthrough of every shape, lives on the [Color Picker](/examples/color-picker) page.

---

## How it works

Every shape separates **preview** (hover, entirely client-side) from **lock-in** (click, resolved server-side), so the two never fight over the same `Output`.

**Wheel** is a `dcc.Graph` showing a static HSV raster (hue by angle, saturation by radius, value fixed at 1) built once at import time with `colorsys.hsv_to_rgb`. Plotly's native hover tooltip is off (`hoverinfo="none"`) — a clientside callback reads `hoverData`, redoes the hue/saturation math in JavaScript, and paints a semi-transparent preview overlay on the center swatch. **Photo** is a generated raster with no such formula, so it ships its real per-pixel hex as `customdata` instead, and the same clientside callback reads that directly when the photo is what's being hovered:

```python
go.Image(z=_PHOTO_RGBA, customdata=_PHOTO_HEX, hoverinfo="none")
```

Clicking either graph fires `clickData` — Python re-derives the color (a formula for the wheel, a table lookup for the photo) and *locks* it into the swatch. The marker showing the last pick is moved with `Patch()` instead of rebuilding the whole figure, so a click ships ~40 bytes back instead of re-serializing the raster.

**Flower** and **Ring** are plain `html.Div`s carrying a pattern-matching id — `{"type": "picker-petal", "color": <hex>}` or `{"type": "picker-ring", "color": <hex>}` — positioned with plain arithmetic (`math.sin`/`math.cos` for the ring, CSS `rotate()` for the petals). They also carry a `data-picker-color` attribute; a second clientside callback binds native `mouseenter`/`mouseleave` listeners to preview them the same way as the wheel and photo. One server-side callback listens to all four shapes' click-style inputs at once and reads `ctx.triggered_id` to know which one fired — no `dcc.Store` needed anywhere.

---

## Where it lives in this repo

The picker ships in two places:

| Where | File | Notes |
|---|---|---|
| Docs demo | `docs/color-picker/color-picker.md` | This site, at [/examples/color-picker](/examples/color-picker), with the full source walkthrough |
| Standalone app | `color_picker_app.py` | A fully independent single-file Dash app, no imports from `pages/` or `components/` |

---

## Built With

- **[Dash](https://dash.plotly.com/) 4.4+** — pluggable backends (Flask / FastAPI / Quart)
- **[Dash Mantine Components](https://www.dash-mantine-components.com/) 2.7+** — the UI kit behind the segmented control, center swatch and code tabs
- **[Plotly](https://plotly.com/python/)** — the wheel's and photo's `go.Image` rasters and hover readout
- **Python 3.11+**

This documentation shell — markdown-driven pages, the `.. exec::` / `.. source::` directives, theming, and the AI/LLM surfaces below — comes from the [Dash Documentation Boilerplate](https://github.com/pip-install-python/Dash-Documentation-Boilerplate) template.

---

## AI/LLM Integration

Powered by [dash-improve-my-llms](https://pypi.org/project/dash-improve-my-llms/):

- Every page serves its prose verbatim at `/<page>/llms.txt` — paste the URL into ChatGPT or Claude and they read the docs directly
- `/sitemap.xml` and `/robots.txt` are generated automatically
- Training crawlers are blocked; AI search citations and browsers are not

---

## Source

- **Repository**: [banana0000/Dash-Documentation-Submission](https://github.com/banana0000/Dash-Documentation-Submission)
- **Template**: [Dash-Documentation-Boilerplate](https://github.com/pip-install-python/Dash-Documentation-Boilerplate)

---

## License

MIT — see [LICENSE](https://github.com/banana0000/Dash-Documentation-Submission/blob/main/LICENSE).
