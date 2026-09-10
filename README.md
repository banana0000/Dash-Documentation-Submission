# Dash Showcases

<p align="center">
  <img src="https://cdn.2plot.ai/github_assets/dark_mode_2plot.png" alt="2plot" width="640">
</p>

> **Dash Showcases — live playgrounds for 2plot.ai components.** Six working Dash showcases on one documentation site — a four-shape color picker, a dash-flows diagram playground, an Excalidraw KPI mockup, a dash-flexlayout docking layout, a 3D model viewer and Roamly, a stay-booking mockup — each with a live demo, a source walkthrough and a standalone app. By [banana0000](https://github.com/banana0000), built on the [Dash Documentation Boilerplate](https://github.com/pip-install-python/Dash-Documentation-Boilerplate) template.

[![Dash](https://img.shields.io/badge/Dash-4.4.1-blue.svg)](https://dash.plotly.com/)
[![DMC](https://img.shields.io/badge/DMC-2.8.0-teal.svg)](https://www.dash-mantine-components.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## What this is

A catalogue of six Dash showcases, each one a real, running app embedded in
its own documentation page: the live demo at the top, the prose that explains
how it works underneath, and the full source at the bottom. Every showcase
also ships a standalone entry point in `examples/` that renders the same
component on its own port.

| Showcase | Docs page | Built on | Standalone app | Port |
|---|---|---|---|---|
| **Color Picker** — one picker, four shapes: a continuous HSV wheel, clickable petals, a ring of swatches, and a photo you sample like an eyedropper | [`/color-picker`](docs/color_picker/color_picker.md) | Dash, Plotly, `dmc.SegmentedControl` | `examples/color_picker_app.py` | 8560 |
| **Dash Flow Playground** — decision-tree, process and org-chart presets; add and rename nodes; ELK auto-layout; PNG export | [`/dash-flow`](docs/dash_flow/dash_flow.md) | [dash-flows](https://flows.2plot.dev) (React Flow) | `examples/dash_flow_app.py` | 8070 |
| **Excalidraw KPI Mockup** — a KPI dashboard on a hand-drawn canvas, with a Library of cards, donuts, charts and swatches, built to export a 1920x1080 Power BI background | [`/excalidraw`](docs/excalidraw/excalidraw.md) | [dash-excalidraw](https://excalidraw.2plot.dev) | `examples/excalidraw_app.py` | 8060 |
| **FlexLayout Playground** — an IDE-style docking layout holding a small sales dashboard; drag tabs, split panels, resize with the splitters | [`/flex-layout`](docs/flex_layout/flex_layout.md) | [dash-flexlayout](https://flexlayout.2plot.dev) (flexlayout-react) | `examples/flexlayout_app.py` | 8080 |
| **3D Model Viewer** — eight glTF sample models; orbit, zoom, tone mapping, shadows, AR, and a live texture upload | [`/model-viewer`](docs/model_viewer/model_viewer.md) | [dash-model-viewer](https://modelviewer.2plot.dev) (Google model-viewer) | `examples/model_viewer_app.py` | 8081 |
| **Roamly** — a house-only stay booking mockup: listings grid with a globe, a stay page with a gallery and a map, and a host dashboard | [`/roamly`](docs/roamly/roamly.md) | [dash-leaflet2](https://leaflet.2plot.dev), [dash-mui-charts](https://muicharts.2plot.dev), dash-image-gallery | `examples/roamly/app.py` | 8870 |

---

## Running it

### The documentation site

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install --no-deps markdown2dash==0.1.2   # markdown2dash pins an old gunicorn; installed without its deps

./scripts/dev.sh          # or: python run.py
```

Visit **http://localhost:8559**. The sidebar lists the six showcases under
**Showcases**; every one opens in place, like any other page of the site.

### A standalone app

Run any of them from the repo root — for example:

```bash
python examples/dash_flow_app.py     # http://localhost:8070
python examples/roamly/app.py        # http://localhost:8870
```

See [`examples/README.md`](examples/README.md) for the full list, the ports,
and how the standalone apps share their builders with the docs pages.

### Tests

```bash
pip install pytest httpx
pytest tests -q
```

The suite boots `run.py` itself and checks every registered page: it loads,
it serves real prose to crawlers, its `/<page>/llms.txt` inlines the source,
and its sidebar entry navigates in the same window.

---

## Project structure

```
.
├── docs/                            # One folder per showcase — the whole site's content
│   ├── color_picker/
│   │   ├── color_picker.md          # The page: frontmatter, prose, .. exec:: / .. source:: directives
│   │   └── picker.py                # The demo: builders, callbacks, and a module-level `component`
│   ├── dash_flow/       (dash_flow.md, playground.py)
│   ├── excalidraw/      (excalidraw.md, kpi_mockup.py)
│   ├── flex_layout/     (flex_layout.md, showcase.py)
│   ├── model_viewer/    (model_viewer.md, showcase.py)
│   └── roamly/          (roamly.md, stays.py, listing.py, host.py)
│
├── examples/                        # The same showcases as standalone apps
│   ├── README.md
│   ├── color_picker_app.py          # Single file, imports nothing from the repo
│   ├── dash_flow_app.py             # Imports docs/dash_flow/playground.py
│   ├── excalidraw_app.py            # Imports docs/excalidraw/kpi_mockup.py
│   ├── flexlayout_app.py            # Imports docs/flex_layout/showcase.py
│   ├── model_viewer_app.py          # Imports docs/model_viewer/showcase.py
│   └── roamly/                      # A complete multi-page app of its own (app.py, data.py, pages/, assets/)
│
├── assets/                          # Site CSS/JS, plus one scoped stylesheet per showcase
│   ├── color-picker.css             # .picker-responsive
│   ├── dash-flow-playground.css     # #flow-playground-flow
│   ├── excalidraw-*.css             # #excalidraw
│   ├── flexlayout.css               # .flexlayout-page
│   ├── model-viewer.css             # .model-viewer-page
│   └── roamly-embed.css             # dash-mui-charts in dark mode
│
├── pages/                           # home.md / home.py (the catalogue index) + markdown.py (the docs loader)
├── components/                      # AppShell, header, sidebar — template code, driven by lib/constants.py
├── lib/                             # Site identity, navigation contract, backends, AI/LLM + SEO plumbing
├── tests/                           # pytest suite (boots run.py; runs on Flask, FastAPI and Quart in CI)
├── scripts/                         # dev.sh, post-deploy smoke batteries
└── run.py                           # Application entry point
```

The shell — multi-page routing, theming, the pluggable Flask/FastAPI/Quart
backends, the markdown page loader and the AI/LLM surfaces — comes from the
[Dash Documentation Boilerplate](https://github.com/pip-install-python/Dash-Documentation-Boilerplate).
See that project for the template itself.

---

## How a showcase is put together

Each showcase follows the boilerplate's one-folder-per-page convention, the
same shape as every `*.2plot.dev` component site:

1. **`docs/<slug>/<slug>.md`** is the page. Its frontmatter names the page,
   its route, its icon, and where it sits in the sidebar (`category: Showcases`,
   `order: n`). The prose walks through how the demo works.
2. **`docs/<slug>/<module>.py`** is the demo. It holds the builder functions
   and the callbacks, and ends with a module-level `component` — the thing
   `.. exec::docs.<slug>.<module>` renders. `.. source::` shows the same file,
   collapsed, further down the page.
3. **`examples/<slug>_app.py`** is the standalone entry point. It imports the
   same builder, so the two can never drift apart, and serves the repo-root
   `assets/` folder so the showcase's stylesheet loads in both places.

Adding a seventh showcase is a folder, a markdown file and a Python file; the
sidebar and the search box pick it up from the frontmatter.

---

## AI/LLM integration

Powered by [dash-improve-my-llms](https://pypi.org/project/dash-improve-my-llms/):
every page serves its prose — `.. source::` files inlined — at
`/<page>/llms.txt`, and `/sitemap.xml` and `/robots.txt` are generated
automatically. Paste a page URL into ChatGPT or Claude and they read the
documentation directly.

---

## Credits

- The six showcases, their prose and their standalone apps:
  [banana0000](https://github.com/banana0000) — original submission at
  [banana0000/Dash-Documentation-Submission](https://github.com/banana0000/Dash-Documentation-Submission).
- The documentation shell:
  [Dash Documentation Boilerplate](https://github.com/pip-install-python/Dash-Documentation-Boilerplate)
  by [Pip Install Python](https://2plot.dev).

## License

MIT — see [LICENSE](LICENSE).
