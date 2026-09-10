---
name: Dash Flow Playground
description: A dash-flows playground — swap between a decision tree, a process diagram and an org chart, add and recolour nodes, and auto-layout the graph with ELK.
endpoint: /dash-flow
package: dash_flows
icon: mdi:graph-outline
category: Showcases
order: 2
---

.. llms_copy::Dash Flow Playground

.. toc::

### Introduction

A playground for [dash-flows](https://flows.2plot.dev) — 2plot.ai's Dash wrapper
around [React Flow](https://reactflow.dev). Three presets (a feature-request
decision tree, a simple linear process, and an org chart) each swap in a full
nodes/edges pair; from there you can add nodes, rename and recolour them,
toggle edge animation, auto-layout the whole graph, and export it as a PNG.

Everything on this page is a real, running `DashFlows` component. Drag nodes
around, pan and zoom, or draw a new connection between two handles.

---

### Live demo

Pick a preset in the sidebar, double-click any node to rename it, and try the
auto-layout picker:

.. exec::docs.dash_flow.playground
    :code: false

---

### How it works

Three presets — a feature-request decision tree, a simple linear process, and
an org chart — each swap in a full nodes/edges pair through the Select in the
sidebar. **Add node** appends a new node chained off the last one in the
current graph, cycling through a fixed palette. Double-clicking a node opens
its label in the text field for editing; the save icon writes it back onto
that node without touching anything else, and the palette icon opens a
`dmc.ColorPicker` modal for the node's background.

All of the diagram state — nodes, edges, the node counter, which node is being
edited — lives in the `DashFlows` component's own props and a few small
`dcc.Store` values, with one callback per direction: one reacts to
`doubleClickedNode` to start an edit, the other reacts to the preset picker,
**Add node**, **Save label**, **Reset** and **New diagram** to update the
graph:

```python
@callback(
    Output(_id("flow"), "nodes", allow_duplicate=True),
    Output(_id("flow"), "edges", allow_duplicate=True),
    Output(_id("node-counter"), "data"),
    Input(_id("preset-picker"), "value"),
    Input(_id("add-node-btn"), "n_clicks"),
    Input(_id("save-label-btn"), "n_clicks"),
    Input(_id("reset-flow-btn"), "n_clicks"),
    Input(_id("new-diagram-btn"), "n_clicks"),
    State(_id("flow"), "nodes"),
    State(_id("flow"), "edges"),
    State(_id("node-counter"), "data"),
    State(_id("node-label-input"), "value"),
    State(_id("editing-node-id"), "data"),
    prevent_initial_call=True,
)
def _update_flow(preset_key, n_clicks, save_clicks, reset_clicks, new_clicks, ...):
    triggered = dash.ctx.triggered_id
    ...
```

A few things worth knowing about the component itself, all exercised here:

- **Animated SVG edges** — every preset edge is upgraded to dash-flows'
  `animatedSvg` edge type, so a small dot travels along the connection on top
  of the dashed-line `animated` flag. The **Animated edges** switch strips
  that type back off without touching the edges' colours or labels.
- **ELK auto-layout** — the **Auto layout** picker writes an ELK options
  object into `layoutOptions` (as a JSON string, per the prop's type). With
  `animateLayout=True` the nodes glide to their new positions instead of
  snapping.
- **Undo / redo, Delete, helper lines** — `enableUndoRedo`, `deleteKeyCode`
  and `helperLines` are component props; no extra wiring needed for Ctrl+Z /
  Ctrl+Y, Delete-key removal, or snap-to-alignment guides while dragging.
- **Export PNG** — `downloadImage` is a write-only trigger: setting it starts
  the download client-side and the component resets it to `None` once done.
- **Output nodes have no source handle** — chaining a new node off an
  `output`-type node would crash React Flow (Error 008), so **Add node**
  drops that node's `type` first and lets it fall back to the default node.

One CSS note: dash-flows 1.3.0 does not forward the `style` prop to the
wrapper div it renders, so `assets/dash-flow-playground.css` sets the
canvas's width and height on `#flow-playground-flow` directly. Without it,
React Flow measures a 0px container and refuses to render.

---

### Source

The whole playground — presets, layout, callbacks — is one module. The docs
page renders its module-level `component`; the standalone app below imports
the same `build_flow_playground()`.

.. source::docs/dash_flow/playground.py
    :defaultExpanded: false
    :withExpandedButton: true

---

### Standalone app

The same playground runs on its own, with its own `Dash(__name__)` instance
and port — no imports from this site's `pages/` or `components/`:

```bash
python examples/dash_flow_app.py
```

Serves on **http://localhost:8070**.

.. source::examples/dash_flow_app.py
    :defaultExpanded: false
    :withExpandedButton: true
