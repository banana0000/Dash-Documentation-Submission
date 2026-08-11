# Color Picker

<p align="center">
  <img src="https://cdn.2plot.ai/github_assets/dark_mode_2plot.png" alt="2plot" width="640">
</p>

> A Dash color picker with three switchable shapes — a continuous HSV wheel, clickable petals, and a ring of swatches — built on top of the [Dash Documentation Boilerplate](https://github.com/pip-install-python/Dash-Documentation-Boilerplate) template.

[![Dash](https://img.shields.io/badge/Dash-4.4.1-blue.svg)](https://dash.plotly.com/)
[![DMC](https://img.shields.io/badge/DMC-2.7.0-teal.svg)](https://www.dash-mantine-components.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## What this is

One color picker, three shapes. A `dmc.SegmentedControl` switches between:

- **Wheel** — a continuous HSV wheel you sample by clicking anywhere on it, like an eyedropper
- **Flower** — six clickable preset petals
- **Ring** — twelve preset swatches arranged in a circle

All three feed the same center swatch and hex readout, and stay mounted in the DOM at once — switching shapes never destroys a picker's state.

The picker ships in three places in this repo:

| Where | File | Notes |
|---|---|---|
| Live page | [`pages/color_picker.py`](pages/color_picker.py) | Registered at `/color-picker`, with its own `llms.txt` |
| Docs demo | [`docs/color-picker/color-picker.md`](docs/color-picker/color-picker.md) | Registered at `/examples/color-picker`, walks through how it works |
| Standalone app | [`color_picker_app.py`](color_picker_app.py) | Fully independent single-file Dash app, no imports from `pages/` or `components/` |

The page and docs demo share their layout/callbacks via [`components/color_picker_widget.py`](components/color_picker_widget.py).

---

## How it works

**Wheel** is a `dcc.Graph` showing a static HSV raster (hue by angle, saturation by radius, value fixed at 1) built once at import time with `colorsys.hsv_to_rgb`. Each pixel carries its hex string as `customdata`, so Plotly's native hover box shows the exact color under the pointer:

```python
go.Image(
    z=_WHEEL_RGBA,
    customdata=_WHEEL_HEX,
    hovertemplate="%{customdata}<extra></extra>",
)
```

Clicking the wheel fires `clickData`, which carries the exact pixel clicked — that pixel is run back through the same hue/saturation math to recover the color, and a small ring marker is drawn at that spot so the pick stays visible.

**Flower** and **Ring** are plain `html.Div`s carrying a pattern-matching id — `{"type": "picker-petal", "color": <hex>}` or `{"type": "picker-ring", "color": <hex>}` — positioned with plain arithmetic (`math.sin`/`math.cos` for the ring, CSS `rotate()` for the petals). One callback listens to all three shapes' inputs at once and reads `ctx.triggered_id` to know which one fired — no `dcc.Store` needed anywhere.

See [`docs/color-picker/color-picker.md`](docs/color-picker/color-picker.md) for the full walkthrough.

---

## Running it

### Full site (docs demo + live page)

```bash
pip install -r requirements.txt
pip install --no-deps markdown2dash==0.1.2   # markdown2dash pins an old gunicorn; installed without its deps
npm install

./scripts/dev.sh          # or: python run.py
```

Visit **http://localhost:8559**, then go to `/color-picker` (the live page) or `/examples/color-picker` (the docs demo with source walkthrough).

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
├── components/
│   └── color_picker_widget.py     # Shared layout + callbacks (wheel/flower/ring)
├── pages/
│   └── color_picker.py            # Live page at /color-picker
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
