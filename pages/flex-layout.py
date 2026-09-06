from pathlib import Path

import dash_mantine_components as dmc
from dash import register_page
from dash_iconify import DashIconify

from components.flexlayout_showcase import build_flexlayout_showcase, PAGE_CLASS
from lib.constants import HEADER_HEIGHT, OG_IMAGE_URL, PAGE_TITLE_PREFIX

NAME = "FlexLayout Playground *"
DESCRIPTION = (
    "A playground for dash-flexlayout (2plot.ai / flexlayout-react) -- an IDE-style "
    "docking layout. Drag tab headers to rearrange panels, drop one on an edge to "
    "split it, and drag the splitters to resize."
)

register_page(
    __name__,
    "/flex-layout",
    name=NAME,
    title=PAGE_TITLE_PREFIX + NAME,
    description=DESCRIPTION,
    image_url=OG_IMAGE_URL,
    icon="mdi:view-dashboard-outline",
)

DOC_TEXT = (
    "The panel arrangement below is a real flexlayout-react `Model` -- a JSON tree of "
    "row/column splits bottoming out in tabsets of tabs. Dragging a tab's header (onto "
    "another tabset, or onto a panel's edge to split it) mutates that same tree, which "
    "round-trips back through the `model` prop, so \"N tabs open\" and \"Reset layout\" "
    "are reading and rewriting the exact state the UI itself is showing -- no separate "
    "client-side bookkeeping. The three switches toggle the FlexLayout element's own "
    "`realtimeResize`, `debugMode` and `supportsPopout` props directly."
)

_CODE_FILES = [
    ("pages/flex-layout.py", "python", "devicon:python"),
    ("components/flexlayout_showcase.py", "python", "devicon:python"),
]
_CODE_SOURCE = {path: Path(path).read_text(encoding="utf-8") for path, _lang, _icon in _CODE_FILES}

# dash-improve-my-llms picks this up automatically and serves it verbatim at
# /flex-layout/llms.txt -- see pages/excalidraw.py for the same pattern.
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
        id="llm-copy-button-flex-layout",
        variant="subtle",
        color="gray",
        size="compact-sm",
        className="llms-copy-button",
    ),
    label="Copy this page's /llms.txt URL — paste into ChatGPT, Claude, or any LLM",
    position="top",
    withArrow=True,
)

# Same slim single-row title bar as pages/dash-flow.py / pages/excalidraw.py.
_TITLE_ROW_HEIGHT = 40
# AppShellMain's own padding="xl" (top+bottom, from components/appshell.py)
# plus the showcase's own controls row (switches + button, mb="sm") that sits
# above the docking panel -- unlike model-viewer's sidebar, that row eats
# into the same vertical space the panel needs.
_CHROME_HEIGHT = 70 + 52

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
        build_flexlayout_showcase(
            height=f"calc(100vh - {HEADER_HEIGHT + _TITLE_ROW_HEIGHT + _CHROME_HEIGHT}px)"
        ),
    ],
    fluid=True,
    py=0,
    className=PAGE_CLASS,
)
