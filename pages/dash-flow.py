from pathlib import Path

import dash_mantine_components as dmc
from dash import register_page
from dash_iconify import DashIconify

from components.dash_flow_playground import build_flow_playground
from lib.constants import HEADER_HEIGHT, OG_IMAGE_URL, PAGE_TITLE_PREFIX

NAME = "Dash Flow Playground *"
DESCRIPTION = (
    "A playground for dash-flows (2plot.ai / React Flow) -- switch between a decision "
    "tree, a process diagram and an org chart, add nodes, and double-click any node to "
    "rename it."
)

register_page(
    __name__,
    "/dash-flow",
    name=NAME,
    title=PAGE_TITLE_PREFIX + NAME,
    description=DESCRIPTION,
    image_url=OG_IMAGE_URL,
    icon="mdi:graph-outline",
)

DOC_TEXT = (
    "Three presets -- a feature-request decision tree, a simple linear process, and an "
    "org chart -- each swap in a full nodes/edges pair through the Select above the "
    "canvas. \"Add node\" appends a new node chained off the last one in the current "
    "graph, cycling through a fixed palette. Double-clicking a node opens its label in "
    "the text field for editing; \"Save label\" writes it back onto that node without "
    "touching anything else. All of the diagram state -- nodes, edges, the node counter, "
    "which node is being edited -- lives in the DashFlows component's own props and two "
    "small dcc.Store values, with one callback per direction: one reacts to double-click "
    "to start an edit, the other reacts to the preset picker, \"Add node\" and \"Save "
    "label\" to update the graph."
)

_CODE_FILES = [
    ("pages/dash-flow.py", "python", "devicon:python"),
    ("components/dash_flow_playground.py", "python", "devicon:python"),
]
_CODE_SOURCE = {path: Path(path).read_text(encoding="utf-8") for path, _lang, _icon in _CODE_FILES}

# dash-improve-my-llms picks this up automatically and serves it verbatim at
# /dash-flow/llms.txt -- see pages/excalidraw.py for the same pattern.
LLMS_DOC = (
    f"# {NAME}\n\n> {DESCRIPTION}\n\n{DOC_TEXT}\n\n"
    + "\n\n".join(
        f"## {path}\n\n```python\n{source}```" for path, source in _CODE_SOURCE.items()
    )
)

_copy_button = dmc.Tooltip(
    dmc.Button(
        dmc.Group(
            [DashIconify(icon="mdi:file-document-outline", width=14), "Copy llms.txt URL"],
            gap=6,
            wrap="nowrap",
        ),
        id="llm-copy-button-dash-flow",
        variant="subtle",
        color="gray",
        size="compact-sm",
        className="llms-copy-button",
    ),
    label="Copy this page's /llms.txt URL — paste into ChatGPT, Claude, or any LLM",
    position="top",
    withArrow=True,
)

# A slim single-row title bar instead of a full Title+description block --
# same treatment as pages/excalidraw.py, and it hands the canvas roughly
# 100px more height than the old layout did. fluid=True (no max-width) does
# the same for width.
_TITLE_ROW_HEIGHT = 40
# AppShellMain's own padding="xl" (top+bottom, from components/appshell.py)
# -- the controls (Add node/label editor/Save/Export/Reset/...) live in
# their own sidebar beside the canvas now, not a row above it, so this only
# has to cover that padding. Measured empirically, not derived from
# Mantine's spacing tokens; re-measure if the surrounding chrome changes.
_CHROME_HEIGHT = 70

layout = dmc.Container(
    [
        dmc.Group(
            justify="space-between",
            align="center",
            style={"height": _TITLE_ROW_HEIGHT},
            children=[
                dmc.Title(NAME, order=4, className="m2d-heading", style={"margin": 0}),
                _copy_button,
            ],
        ),
        build_flow_playground(
            # Double the previous (half-viewport) height this page used --
            # back to the plain viewport-fit height.
            height=f"calc(100vh - {HEADER_HEIGHT + _TITLE_ROW_HEIGHT + _CHROME_HEIGHT}px)",
        ),
    ],
    fluid=True,
    py=0,
)
