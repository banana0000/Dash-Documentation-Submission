# Dash Showcases — live playgrounds for 2plot.ai components

> **Six working Dash showcases on one documentation site** — a four-shape color picker, a dash-flows diagram playground, an Excalidraw KPI mockup, a dash-flexlayout docking layout, a 3D model viewer and Roamly, a stay-booking mockup — each with a live demo, a source walkthrough and a standalone app. By [banana0000](https://github.com/banana0000), built on the [Dash Documentation Boilerplate](https://github.com/pip-install-python/Dash-Documentation-Boilerplate) template.

Every showcase on this site is a real, running Dash app embedded in its own documentation page: the demo at the top, the prose that explains how it works underneath, and the full source at the bottom. The same code also runs on its own — each showcase ships a standalone entry point in `examples/`.

---

## The showcases

| Showcase | What it is | Built on |
|---|---|---|
| [Color Picker](/color-picker) | One picker, four shapes — a continuous HSV wheel, clickable petals, a ring of swatches, and a photo you sample like an eyedropper | Dash, Plotly, `dmc.SegmentedControl` |
| [Dash Flow Playground](/dash-flow) | Decision-tree, process and org-chart presets; add and rename nodes; ELK auto-layout; PNG export | [dash-flows](https://flows.2plot.dev) (React Flow) |
| [Excalidraw KPI Mockup](/excalidraw) | A KPI-dashboard mockup on a hand-drawn canvas, with a Library of cards, donuts, charts and swatches, built to export a 1920x1080 Power BI background | [dash-excalidraw](https://excalidraw.2plot.dev) |
| [FlexLayout Playground](/flex-layout) | An IDE-style docking layout holding a small sales dashboard — drag tabs, split panels, resize with the splitters | [dash-flexlayout](https://flexlayout.2plot.dev) (flexlayout-react) |
| [3D Model Viewer](/model-viewer) | Eight glTF sample models; orbit, zoom, tone mapping, shadows, AR, and a live texture upload | [dash-model-viewer](https://modelviewer.2plot.dev) (Google model-viewer) |
| [Roamly](/roamly) | A house-only stay booking mockup — listings grid with a globe, a stay page with a gallery and a map, and a host dashboard | [dash-leaflet2](https://leaflet.2plot.dev), [dash-mui-charts](https://muicharts.2plot.dev), dash-image-gallery |

---

## How this site is organised

Each showcase follows the boilerplate's one-folder-per-page convention:

```
docs/
└── dash_flow/
    ├── dash_flow.md      # the page: frontmatter, prose, `.. exec::` and `.. source::` directives
    └── playground.py     # the demo: builders, callbacks, and a module-level `component`
```

The markdown page is discovered and registered automatically. Its `.. exec::docs.dash_flow.playground` directive imports the demo module and renders its `component`; `.. source::docs/dash_flow/playground.py` shows the same file, collapsed, further down the page. The sidebar is built from each page's frontmatter (`category` and `order`), so adding a seventh showcase is a folder, a markdown file and a Python file — no navigation code to touch.

The standalone apps live beside the site rather than inside it:

```
examples/
├── color_picker_app.py     # single-file, no imports from the repo
├── dash_flow_app.py        # imports docs/dash_flow/playground.py
├── excalidraw_app.py       # imports docs/excalidraw/kpi_mockup.py
├── flexlayout_app.py       # imports docs/flex_layout/showcase.py
├── model_viewer_app.py     # imports docs/model_viewer/showcase.py
└── roamly/                 # a complete multi-page app of its own
```

Run any of them from the repo root, for example `python examples/dash_flow_app.py`. The ports are listed on each showcase page and in [`examples/README.md`](https://github.com/pip-install-python/banana0000-Submission/blob/main/examples/README.md).

---

## Built with

- **[Dash](https://dash.plotly.com/) 4.4+** — pluggable backends (Flask / FastAPI / Quart)
- **[Dash Mantine Components](https://www.dash-mantine-components.com/) 2.8+** — the UI kit behind every control, card and code tab on the site
- **[Plotly](https://plotly.com/python/)** — the color picker's rasters, the FlexLayout charts and Roamly's globe
- The 2plot.ai component wrappers named in the table above
- **Python 3.11+**

This documentation shell — markdown-driven pages, the `.. exec::` / `.. source::` directives, theming, and the AI/LLM surfaces below — comes from the [Dash Documentation Boilerplate](https://github.com/pip-install-python/Dash-Documentation-Boilerplate) template.

---

## AI/LLM Integration

Powered by [dash-improve-my-llms](https://pypi.org/project/dash-improve-my-llms/):

- Every page serves its prose verbatim at `/<page>/llms.txt` — paste the URL into ChatGPT or Claude and they read the docs directly, source included
- `/sitemap.xml` and `/robots.txt` are generated automatically
- Training crawlers are blocked; AI search citations and browsers are not

---

## Source

- **Repository**: [pip-install-python/banana0000-Submission](https://github.com/pip-install-python/banana0000-Submission)
- **Original submission**: [banana0000/Dash-Documentation-Submission](https://github.com/banana0000/Dash-Documentation-Submission)
- **Template**: [Dash-Documentation-Boilerplate](https://github.com/pip-install-python/Dash-Documentation-Boilerplate)

---

## License

MIT — see [LICENSE](https://github.com/pip-install-python/banana0000-Submission/blob/main/LICENSE).
