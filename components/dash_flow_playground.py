"""Dash Flow playground: decision-tree / process / org-chart diagrams built with
dash-flows (2plot.ai / React Flow), editable in the browser.

Shared between two entry points, the same shape as components/excalidraw_kpi.py:

| Where               | Notes                                            |
|---------------------|---------------------------------------------------|
| pages/dash-flow.py  | Embedded page on the main site at /dash-flow       |
| dash_flow_app.py    | Fully independent standalone app, own Dash(__name__) instance, own port |

Element ids are prefixed ``flow-playground-`` so this page's callbacks never
collide with ids on any other page of the same running multi-page app.
"""
import json

import dash
from dash import dcc, callback, clientside_callback, Input, Output, State, no_update
import dash_mantine_components as dmc
from dash_flows import DashFlows
from dash_iconify import DashIconify

PRESETS = {
    "decision": {
        "label": "Feature Request Decision Tree",
        "nodes": [
            {"id": "1", "type": "input", "position": {"x": 320, "y": 0}, "data": {"label": "New feature request"},
             "style": {"background": "#4263eb", "color": "#fff", "border": "none", "borderRadius": "10px", "padding": "10px 16px", "fontWeight": 600, "width": 200}},
            {"id": "2", "position": {"x": 320, "y": 130}, "data": {"label": "Aligned with roadmap?"},
             "style": {"background": "#343a40", "color": "#fff", "border": "none", "borderRadius": "10px", "padding": "10px 16px", "fontWeight": 600, "width": 200}},
            {"id": "3", "type": "output", "position": {"x": 40, "y": 260}, "data": {"label": "Decline & log feedback"},
             "style": {"background": "#e03131", "color": "#fff", "border": "none", "borderRadius": "10px", "padding": "10px 16px", "fontWeight": 600, "width": 200}},
            {"id": "4", "position": {"x": 460, "y": 260}, "data": {"label": "Estimate effort"},
             "style": {"background": "#343a40", "color": "#fff", "border": "none", "borderRadius": "10px", "padding": "10px 16px", "fontWeight": 600, "width": 200}},
            {"id": "5", "type": "output", "position": {"x": 320, "y": 390}, "data": {"label": "Schedule for next sprint"},
             "style": {"background": "#12b886", "color": "#fff", "border": "none", "borderRadius": "10px", "padding": "10px 16px", "fontWeight": 600, "width": 200}},
            {"id": "6", "type": "output", "position": {"x": 620, "y": 390}, "data": {"label": "Add to backlog for review"},
             "style": {"background": "#f08c00", "color": "#fff", "border": "none", "borderRadius": "10px", "padding": "10px 16px", "fontWeight": 600, "width": 200}},
        ],
        "edges": [
            {"id": "e1-2", "source": "1", "target": "2", "animated": True, "style": {"stroke": "#4263eb", "strokeWidth": 2.5}},
            {"id": "e2-3", "source": "2", "target": "3", "label": "no", "animated": True, "style": {"stroke": "#e03131", "strokeWidth": 2.5}},
            {"id": "e2-4", "source": "2", "target": "4", "label": "yes", "animated": True, "style": {"stroke": "#12b886", "strokeWidth": 2.5}},
            {"id": "e4-5", "source": "4", "target": "5", "label": "low effort", "animated": True, "style": {"stroke": "#12b886", "strokeWidth": 2.5}},
            {"id": "e4-6", "source": "4", "target": "6", "label": "high effort", "animated": True, "style": {"stroke": "#f08c00", "strokeWidth": 2.5}},
        ],
    },
    "process": {
        "label": "Simple Process",
        "nodes": [
            {"id": "1", "type": "input", "position": {"x": 0, "y": 80}, "data": {"label": "1. Start"},
             "style": {"background": "#12b886", "color": "#fff", "border": "none", "borderRadius": "10px", "padding": "10px 16px", "fontWeight": 600, "width": 180}},
            {"id": "2", "position": {"x": 260, "y": 80}, "data": {"label": "2. Process"},
             "style": {"background": "#fd7e14", "color": "#fff", "border": "none", "borderRadius": "10px", "padding": "10px 16px", "fontWeight": 600, "width": 180}},
            {"id": "3", "type": "output", "position": {"x": 520, "y": 80}, "data": {"label": "3. Done"},
             "style": {"background": "#e64980", "color": "#fff", "border": "none", "borderRadius": "10px", "padding": "10px 16px", "fontWeight": 600, "width": 180}},
        ],
        "edges": [
            {"id": "e1-2", "source": "1", "target": "2", "animated": True, "style": {"stroke": "#fd7e14", "strokeWidth": 2.5}},
            {"id": "e2-3", "source": "2", "target": "3", "animated": True, "style": {"stroke": "#e64980", "strokeWidth": 2.5}},
        ],
    },
    "org": {
        "label": "Org Chart",
        "nodes": [
            {"id": "1", "type": "input", "position": {"x": 220, "y": 0}, "data": {"label": "CEO"},
             "style": {"background": "#212529", "color": "#fff", "border": "none", "borderRadius": "10px", "padding": "10px 16px", "fontWeight": 600, "width": 160}},
            {"id": "2", "type": "output", "position": {"x": 40, "y": 140}, "data": {"label": "Engineering"},
             "style": {"background": "#1971c2", "color": "#fff", "border": "none", "borderRadius": "10px", "padding": "10px 16px", "fontWeight": 600, "width": 160}},
            {"id": "3", "type": "output", "position": {"x": 260, "y": 140}, "data": {"label": "Design"},
             "style": {"background": "#f08c00", "color": "#fff", "border": "none", "borderRadius": "10px", "padding": "10px 16px", "fontWeight": 600, "width": 160}},
            {"id": "4", "type": "output", "position": {"x": 480, "y": 140}, "data": {"label": "Sales"},
             "style": {"background": "#2f9e44", "color": "#fff", "border": "none", "borderRadius": "10px", "padding": "10px 16px", "fontWeight": 600, "width": 160}},
        ],
        "edges": [
            {"id": "e1-2", "source": "1", "target": "2", "style": {"stroke": "#1971c2", "strokeWidth": 2.5}},
            {"id": "e1-3", "source": "1", "target": "3", "style": {"stroke": "#f08c00", "strokeWidth": 2.5}},
            {"id": "e1-4", "source": "1", "target": "4", "style": {"stroke": "#2f9e44", "strokeWidth": 2.5}},
        ],
    },
}

NODE_COLORS = ["#4263eb", "#12b886", "#fd7e14", "#e64980", "#7048e8", "#f08c00"]

# ELK algorithm presets for the "Layout" picker -- keys go in layoutOptions
# (sent to DashFlows as a JSON string, per its own prop type). animateLayout
# on the component makes nodes glide from their current spot to the new one
# instead of snapping.
LAYOUT_PRESETS = {
    "layered-down": {
        "label": "Layered (Down)",
        "options": {"elk.algorithm": "layered", "elk.direction": "DOWN",
                    "elk.spacing.nodeNode": "60", "elk.layered.spacing.nodeNodeBetweenLayers": "90"},
    },
    "layered-right": {
        "label": "Layered (Right)",
        "options": {"elk.algorithm": "layered", "elk.direction": "RIGHT",
                    "elk.spacing.nodeNode": "60", "elk.layered.spacing.nodeNodeBetweenLayers": "90"},
    },
    "tree": {
        "label": "Tree",
        "options": {"elk.algorithm": "mrtree", "elk.direction": "DOWN", "elk.spacing.nodeNode": "60"},
    },
    "radial": {
        "label": "Radial",
        "options": {"elk.algorithm": "radial", "elk.spacing.nodeNode": "60"},
    },
}

_ID_PREFIX = "flow-playground-"


def _id(name):
    return f"{_ID_PREFIX}{name}"


def build_flow_playground(height="70vh"):
    """Layout for the diagram playground. Registers its callbacks on import
    (module-level @callback, same as the rest of this app's pages) -- import
    this module exactly once per running Dash app.
    """
    return dmc.Stack(
        [
            # One row, every control packed together on the right
            # (justify="flex-end") -- was split (picker right, actions
            # left) via marginLeft: auto on just the picker; now the whole
            # cluster moves as one.
            dmc.Group(
                [
                    dmc.Button("Add node", id=_id("add-node-btn"), n_clicks=0, variant="filled"),
                    dmc.TextInput(
                        id=_id("node-label-input"),
                        placeholder="Double-click a node to edit its text",
                        disabled=True,
                        w=280,
                    ),
                    dmc.Tooltip(
                        dmc.ActionIcon(
                            DashIconify(icon="mdi:content-save-outline", width=18),
                            id=_id("save-label-btn"),
                            n_clicks=0,
                            variant="light",
                            size="lg",
                            disabled=True,
                        ),
                        label="Save label",
                        position="top",
                        withArrow=True,
                    ),
                    dmc.Button(
                        "Export PNG", id=_id("export-png-btn"), n_clicks=0, variant="outline", color="grape",
                    ),
                    dmc.Select(
                        id=_id("layout-picker"),
                        placeholder="Auto layout",
                        data=[{"label": v["label"], "value": k} for k, v in LAYOUT_PRESETS.items()],
                        clearable=True,
                        w=170,
                    ),
                    dmc.Select(
                        id=_id("preset-picker"),
                        data=[{"label": v["label"], "value": k} for k, v in PRESETS.items()],
                        value="decision",
                        clearable=False,
                        allowDeselect=False,
                        w=260,
                    ),
                ],
                justify="flex-end",
                gap="sm",
                wrap="wrap",
            ),
            dmc.Paper(
                DashFlows(
                    id=_id("flow"),
                    nodes=PRESETS["decision"]["nodes"],
                    edges=PRESETS["decision"]["edges"],
                    fitView=True,
                    showControls=True,
                    showMiniMap=True,
                    showBackground=True,
                    colorMode="dark",
                    themePreset="glass",
                    # The canvas backdrop itself stays colorMode="dark"'s own
                    # near-black -- this only reaches the dot-grid pattern
                    # (via --xy-background-pattern-color-props), not the
                    # backdrop, confirmed by inspecting the live DOM. Faint
                    # black rather than the pattern's own default grey, so
                    # the grid reads as a subtle texture on black instead of
                    # standing out.
                    backgroundColor="rgba(0, 0, 0, 0.4)",
                    style={"width": "100%", "height": "100%"},
                    downloadImage=None,
                    # A few extras beyond the original playground: undo/redo
                    # (Ctrl+Z / Ctrl+Y, built into the component -- no extra
                    # wiring needed), Delete-key removal of a selected node
                    # or edge, and helper lines while dragging a node so it
                    # snaps into alignment with its neighbours.
                    enableUndoRedo=True,
                    deleteKeyCode="Delete",
                    helperLines=True,
                    # Nodes glide to their new spot instead of snapping when
                    # the Layout picker below sets layoutOptions.
                    animateLayout=True,
                    animateLayoutDuration=400,
                ),
                withBorder=True,
                radius="md",
                style={"height": height, "width": "100%", "overflow": "hidden"},
            ),
            dcc.Store(id=_id("node-counter"), data=0),
            dcc.Store(id=_id("editing-node-id"), data=None),
            # sink for the focus/select-text clientside callback below
            dcc.Store(id=_id("focus-sink")),
        ],
        gap="sm",
    )


@callback(
    Output(_id("node-label-input"), "value"),
    Output(_id("node-label-input"), "disabled"),
    Output(_id("save-label-btn"), "disabled"),
    Output(_id("editing-node-id"), "data"),
    Input(_id("flow"), "doubleClickedNode"),
    prevent_initial_call=True,
)
def _start_editing_label(node):
    if not node or not node.get("id"):
        return no_update, no_update, no_update, no_update
    label = (node.get("data") or {}).get("label", "")
    return label, False, False, node["id"]


@callback(
    Output(_id("flow"), "nodes"),
    Output(_id("flow"), "edges"),
    Output(_id("node-counter"), "data"),
    Input(_id("preset-picker"), "value"),
    Input(_id("add-node-btn"), "n_clicks"),
    Input(_id("save-label-btn"), "n_clicks"),
    State(_id("flow"), "nodes"),
    State(_id("flow"), "edges"),
    State(_id("node-counter"), "data"),
    State(_id("node-label-input"), "value"),
    State(_id("editing-node-id"), "data"),
    prevent_initial_call=True,
)
def _update_flow(preset_key, n_clicks, save_clicks, current_nodes, current_edges, counter, new_label, editing_id):
    triggered = dash.ctx.triggered_id

    if triggered == _id("preset-picker"):
        preset = PRESETS[preset_key]
        return preset["nodes"], preset["edges"], 0

    if triggered == _id("save-label-btn"):
        if not editing_id or not new_label or not current_nodes:
            return no_update, no_update, no_update
        updated_nodes = [
            {**n, "data": {**n["data"], "label": new_label}} if n["id"] == editing_id else n
            for n in current_nodes
        ]
        return updated_nodes, current_edges, counter

    if triggered == _id("add-node-btn") and current_nodes:
        counter = (counter or 0) + 1
        new_id = f"extra-{counter}"
        last_node = current_nodes[-1]
        # An "output"-type node has no source handle in React Flow, so an
        # edge leaving it crashes the component (Error 008). Chaining off
        # one of those just means it's no longer the end of the graph, so
        # drop the type and let it fall back to the default node (both
        # handles).
        if last_node.get("type") == "output":
            last_node = {k: v for k, v in last_node.items() if k != "type"}
        new_node = {
            "id": new_id,
            "position": {"x": last_node["position"]["x"] + 60, "y": last_node["position"]["y"] + 120},
            "data": {"label": f"New node {counter}"},
            "style": {
                "background": NODE_COLORS[counter % len(NODE_COLORS)],
                "color": "#fff", "border": "none", "borderRadius": "10px",
                "padding": "10px 16px", "fontWeight": 600, "width": 160,
            },
        }
        new_edge = {
            "id": f"e-{last_node['id']}-{new_id}",
            "source": last_node["id"], "target": new_id,
            "animated": True,
            "style": {"stroke": new_node["style"]["background"], "strokeWidth": 2.5},
        }
        updated_nodes = current_nodes[:-1] + [last_node]
        return updated_nodes + [new_node], current_edges + [new_edge], counter

    return no_update, no_update, no_update


@callback(
    Output(_id("flow"), "layoutOptions"),
    Input(_id("layout-picker"), "value"),
    prevent_initial_call=True,
)
def _apply_layout(layout_key):
    if not layout_key:
        return no_update
    return json.dumps(LAYOUT_PRESETS[layout_key]["options"])


@callback(
    Output(_id("flow"), "downloadImage"),
    Input(_id("export-png-btn"), "n_clicks"),
    prevent_initial_call=True,
)
def _export_png(_n_clicks):
    """`downloadImage` is a write-only trigger: setting it starts the
    download client-side and the component resets it back to None once
    done, so there's nothing to read back here."""
    return {
        "format": "png",
        "filename": "dash-flow-diagram",
        "backgroundColor": "#0f172a",
        "pixelRatio": 2,
    }


# Selects the label text (not just focuses the field) the moment a
# double-click starts an edit, so typing immediately replaces it instead of
# inserting at wherever the cursor happens to land. Reads the input by id
# rather than an event target, since this fires from editing-node-id
# (set by _start_editing_label above) rather than a DOM event on the field
# itself; the id could resolve to the <input> directly or to a Mantine
# wrapper div around it, so both are handled. A short setTimeout lets the
# Python round-trip's value/disabled update commit to the DOM first.
clientside_callback(
    """
    function(editingId) {
        if (!editingId) {
            return window.dash_clientside.no_update;
        }
        setTimeout(function() {
            const el = document.getElementById('flow-playground-node-label-input');
            const input = el && (el.tagName === 'INPUT' ? el : el.querySelector('input'));
            if (input) {
                input.focus();
                input.select();
            }
        }, 50);
        return window.dash_clientside.no_update;
    }
    """,
    Output(_id("focus-sink"), "data"),
    Input(_id("editing-node-id"), "data"),
    prevent_initial_call=True,
)
