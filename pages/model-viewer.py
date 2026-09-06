from pathlib import Path

import dash_mantine_components as dmc
from dash import register_page
from dash_iconify import DashIconify

from components.model_viewer_showcase import build_model_viewer_showcase, PAGE_CLASS
from lib.constants import HEADER_HEIGHT, OG_IMAGE_URL, PAGE_TITLE_PREFIX

NAME = "3D Model Viewer *"
DESCRIPTION = (
    "A playground for dash_model_viewer (2plot.ai) -- Google's <model-viewer> web "
    "component wrapped for Dash. Switch between four sample glTF models, rotate/zoom "
    "with the mouse, tweak tone mapping and shadow intensity, and try the AR button "
    "on a phone."
)

register_page(
    __name__,
    "/model-viewer",
    name=NAME,
    title=PAGE_TITLE_PREFIX + NAME,
    description=DESCRIPTION,
    image_url=OG_IMAGE_URL,
    icon="mdi:cube-outline",
)

DOC_TEXT = (
    "Four public glTF sample models (Khronos/Google's own demo assets, hosted on "
    "modelviewer.dev's CDN -- no local files, no API key) swap in through the Select "
    "on the left, each restoring its own starting camera orbit. \"Reset camera\" "
    "returns to that same orbit without changing the model. Tone mapping and shadow "
    "intensity are the `<model-viewer>` element's own lighting props, wired straight "
    "through; the AR and camera-controls switches toggle the element's `ar` and "
    "`cameraControls` props directly -- there is no client state beyond what the "
    "component itself holds."
)

_CODE_FILES = [
    ("pages/model-viewer.py", "python", "devicon:python"),
    ("components/model_viewer_showcase.py", "python", "devicon:python"),
]
_CODE_SOURCE = {path: Path(path).read_text(encoding="utf-8") for path, _lang, _icon in _CODE_FILES}

# dash-improve-my-llms picks this up automatically and serves it verbatim at
# /model-viewer/llms.txt -- see pages/excalidraw.py for the same pattern.
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
        id="llm-copy-button-model-viewer",
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
# AppShellMain's own padding="xl" (top+bottom, from components/appshell.py) --
# the controls live in their own sidebar beside the viewer, not a row above
# it, so this only has to cover that padding.
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
        build_model_viewer_showcase(
            height=f"calc(100vh - {HEADER_HEIGHT + _TITLE_ROW_HEIGHT + _CHROME_HEIGHT}px)"
        ),
    ],
    fluid=True,
    py=0,
    className=PAGE_CLASS,
)
