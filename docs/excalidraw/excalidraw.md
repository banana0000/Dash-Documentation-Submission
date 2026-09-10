---
name: Excalidraw KPI Mockup
description: A KPI-dashboard mockup on a dash-excalidraw canvas — cards, donuts, charts and a flowchart in the Library, built for exporting a 1920x1080 Power BI report background.
endpoint: /excalidraw
package: dash_excalidraw
icon: mdi:draw
category: Showcases
order: 3
---

.. llms_copy::Excalidraw KPI Mockup

.. toc::

### Introduction

A canvas tool built on [dash-excalidraw](https://excalidraw.2plot.dev) —
2plot.ai's Dash wrapper around [Excalidraw](https://excalidraw.com). The
canvas opens with one worked flowchart example floating on the desk, and a
Personal Library full of hand-authored KPI templates: cards, round badges,
gradient cards, chart panels, progress bars, donuts, gradient swatches, and a
small hand-drawn scene. Drag any of them onto the canvas as many times as you
need.

The drawing is meant to end up as a **Power BI report page background**, so a
1920x1080 artboard (Full HD, the 16:9 page size) is one drag away and the
export settings are pre-set to produce a file at exactly that size.

---

### Live demo

Open the **Library** (top right) and drag a template out; the hamburger menu
(top left) holds **Reset the canvas** and **Export image**:

.. exec::docs.excalidraw.kpi_mockup
    :code: false

---

### What is on the canvas

- Opens with one worked flowchart example — faint (half-opacity) node fills,
  labels set in Excalidraw's own hand-drawn font — floating directly on the
  desk, no artboard rectangle behind it.
- KPI cards, donuts, charts and gradient swatches, plus a small hand-drawn
  scene (sun, mountains, a tree, a couple of birds), all sit in Excalidraw's
  own Library sidebar to drag out as needed.
- **Reset the canvas** and **Save to... / Export image...** are enabled in
  Excalidraw's own hamburger menu — real clear/save actions, not custom-built
  ones.
- The Help dialog's keyboard-shortcut pills are styled yellow-on-black
  (`assets/excalidraw-help-buttons.css`).
- The 1920x1080 artboard used for the Power-BI-background workflow is still
  available via `artboard_frame()` — just not placed on the canvas by default
  any more.

---

### How it works

Every element on the canvas and in the Library is a plain Excalidraw element
dict, generated in Python. Small builders (`_shape`, `_text`, `_connector`,
`_polygon`) produce the raw rectangles, ellipses, arrows and text; the
template functions (`kpi_card_template`, `donut_badge`, `sparkline_panel`,
`flowchart_sample`, ...) compose them into groups with shared `groupIds`, so a
template drags as one unit. Gradients are banded bars — Excalidraw fills a
shape with a single colour, so a ramp of thin rectangles is how a gradient
gets onto the artboard.

The component is mounted once with everything it needs in `initialData`:

```python
DashExcalidraw(
    id="excalidraw",
    width="100%",
    height="75vh",
    theme="dark",
    UIOptions={
        "canvasActions": {
            "toggleTheme": True,
            "clearCanvas": True,
            "saveAsImage": True,
            "export": {"saveFileToDisk": True},
        },
        "tools": {"image": True},
    },
    validateEmbeddable=True,
    initialData={
        "elements": elements,
        "libraryItems": build_library_items(opacity),
        "appState": {
            "viewBackgroundColor": DESK_COLOR,
            "exportPadding": 0,
            "exportWithDarkMode": False,
            "exportBackground": True,
            "currentItemRoughness": 0,
            "currentItemEndArrowhead": "triangle",
        },
    },
)
```

Two details are easy to miss:

- **The canvas stays light under a dark UI.** `theme="dark"` themes the
  toolbar and panels, but Excalidraw's dark theme also CSS-inverts the canvas
  itself. Every colour here is already hand-authored, so
  `assets/excalidraw-no-canvas-invert.css` switches that one filter off and
  leaves the rest of the dark chrome untouched.
- **The export comes out at exactly 1920x1080** when the artboard is the
  outermost element: `exportPadding` is 0 and `exportBackground` is on. In
  Power BI, set the page size to 16:9 / 1920x1080 and add the image as the
  page background at "Fit".

The site installs the GitHub build of dash-excalidraw rather than the older
PyPI release: the newer build exposes a `command` prop that updates a mounted
scene imperatively, which is what any future live-editing feature should use
instead of remounting the component.

---

### Source

.. source::docs/excalidraw/kpi_mockup.py
    :defaultExpanded: false
    :withExpandedButton: true

---

### Standalone app

The same canvas runs on its own, with its own `Dash(__name__)` instance and
port:

```bash
pip install "git+https://github.com/pip-install-python/dash-excalidraw.git"
python examples/excalidraw_app.py
```

Serves on **http://localhost:8060**.

.. source::examples/excalidraw_app.py
    :defaultExpanded: false
    :withExpandedButton: true
