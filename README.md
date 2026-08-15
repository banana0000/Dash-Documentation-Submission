# Color Picker

<p align="center">
  <img src="https://cdn.2plot.ai/github_assets/dark_mode_2plot.png" alt="2plot" width="640">
</p>

> A Dash color picker with four switchable shapes — a continuous HSV wheel, clickable petals, a ring of swatches, and a photo you sample like an eyedropper — built on top of the [Dash Documentation Boilerplate](https://github.com/pip-install-python/Dash-Documentation-Boilerplate) template. By [banana0000](https://github.com/banana0000).

[![Dash](https://img.shields.io/badge/Dash-4.4.1-blue.svg)](https://dash.plotly.com/)
[![DMC](https://img.shields.io/badge/DMC-2.7.0-teal.svg)](https://www.dash-mantine-components.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## What this is

One color picker, four shapes. A `dmc.SegmentedControl` switches between:

- **Wheel** — a continuous HSV wheel, hover to preview and click to lock a color, like an eyedropper
- **Flower** — two layered rings of six petals each, a lighter tint nested inside the full-saturation outer ring
- **Ring** — twelve preset swatches arranged in a circle
- **Photo** — a generated, photo-like image you sample pixel by pixel

All four feed the same center swatch and hex readout, and stay mounted in the DOM at once — switching shapes never destroys a picker's state.

The picker ships in two places in this repo:

| Where | File | Notes |
|---|---|---|
| Docs demo | [`docs/color-picker/color-picker.md`](docs/color-picker/color-picker.md) | Registered at `/examples/color-picker`, walks through how it works |
| Standalone app | [`color_picker_app.py`](color_picker_app.py) | Fully independent single-file Dash app, no imports from `pages/` or `components/` |

---

## How it works

Every shape separates **preview** (hover, entirely client-side) from **lock-in** (click, resolved server-side), so the two never fight over the same `Output`.

**Wheel** is a `dcc.Graph` showing a static HSV raster (hue by angle, saturation by radius, value fixed at 1) built once at import time with `colorsys.hsv_to_rgb`. Plotly's native hover tooltip is off (`hoverinfo="none"`) — a clientside callback reads `hoverData`, redoes the hue/saturation math in JavaScript, and paints a semi-transparent preview overlay on the center swatch. **Photo** is a generated raster with no such formula, so it ships its real per-pixel hex as `customdata` instead, and the same clientside callback reads that directly when the photo is what's being hovered:

```python
go.Image(z=_PHOTO_RGBA, customdata=_PHOTO_HEX, hoverinfo="none")
```

Clicking either graph fires `clickData` — Python re-derives the color (a formula for the wheel, a table lookup for the photo) and *locks* it into the swatch. The marker showing the last pick is moved with `Patch()` instead of rebuilding the whole figure, so a click ships ~40 bytes back instead of re-serializing the raster.

**Flower** and **Ring** are plain `html.Div`s carrying a pattern-matching id — `{"type": "picker-petal", "color": <hex>}` or `{"type": "picker-ring", "color": <hex>}` — positioned with plain arithmetic (`math.sin`/`math.cos` for the ring, CSS `rotate()` for the petals). They also carry a `data-picker-color` attribute; a second clientside callback binds native `mouseenter`/`mouseleave` listeners to preview them the same way as the wheel and photo. One server-side callback listens to all four shapes' click-style inputs at once and reads `ctx.triggered_id` to know which one fired — no `dcc.Store` needed anywhere.

See [`docs/color-picker/color-picker.md`](docs/color-picker/color-picker.md) for the full walkthrough.

---

## Running it

### Full site (docs demo)

```bash
pip install -r requirements.txt
pip install --no-deps markdown2dash==0.1.2   # markdown2dash pins an old gunicorn; installed without its deps
npm install

./scripts/dev.sh          # or: python run.py
```

Visit **http://localhost:8559**, then go to `/examples/color-picker` (the docs demo with source walkthrough).

### Standalone

```bash
python color_picker_app.py
```

Serves on **http://localhost:8560** — a single-file app with no dependency on the rest of this repo.

---

## Project structure

```
.
├── color_picker_app.py            # Standalone single-file version
├── docs/
│   └── color-picker/
│       ├── color-picker.md        # Docs demo at /examples/color-picker
│       └── picker.py              # Example embedded in the docs demo
└── ...                            # Dash Documentation Boilerplate scaffolding
                                    # (multi-page routing, theming, backends)
```

This repo is forked from the [Dash Documentation Boilerplate](https://github.com/pip-install-python/Dash-Documentation-Boilerplate) template, which supplies the surrounding app shell — navigation, theming, pluggable Flask/FastAPI/Quart backends, and the markdown-driven page loader that registers `docs/color-picker/color-picker.md` as a page automatically. See that project for details on the template itself.

---

## License

MIT — see [LICENSE](LICENSE).
