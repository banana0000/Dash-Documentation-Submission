# Color Picker

> A Dash color picker with three switchable shapes — a continuous HSV wheel, clickable petals, and a ring of swatches — built on top of the [Dash Documentation Boilerplate](https://github.com/pip-install-python/Dash-Documentation-Boilerplate) template. By [banana0000](https://github.com/banana0000).

One color picker, three shapes. A `dmc.SegmentedControl` switches between:

- **Wheel** — a continuous HSV wheel you sample by clicking anywhere on it, like an eyedropper
- **Flower** — six clickable preset petals
- **Ring** — twelve preset swatches arranged in a circle

All three feed the same center swatch and hex readout, and stay mounted in the DOM at once — switching shapes never destroys a picker's state.

---

## Try it

The full interactive demo, with a source-code walkthrough of every shape, lives on the [Color Picker](/examples/color-picker) page.

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
- **[Plotly](https://plotly.com/python/)** — the HSV wheel's `go.Image` raster and hover readout
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
