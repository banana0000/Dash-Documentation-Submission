from pathlib import Path

import dash_mantine_components as dmc
from dash import html, register_page
from dash_iconify import DashIconify

from components.excalidraw_kpi import DEFAULT_OPACITY, build_excalidraw
from lib.constants import HEADER_HEIGHT, OG_IMAGE_URL, PAGE_TITLE_PREFIX

# The compact title row above the canvas is the only other thing eating
# viewport height on this page (no description/padding above the fold
# any more) -- see the layout below.
_TITLE_ROW_HEIGHT = 52
_CANVAS_HEIGHT = f"calc(100vh - {HEADER_HEIGHT + _TITLE_ROW_HEIGHT}px)"

NAME = "Excalidraw KPI Mockup *"
DESCRIPTION = (
    "A KPI-dashboard mockup on an Excalidraw canvas -- cards, donuts, charts, "
    "a flowchart -- built for exporting as a 1920x1080 Power BI report background."
)

register_page(
    __name__,
    "/excalidraw",
    name=NAME,
    title=PAGE_TITLE_PREFIX + NAME,
    description=DESCRIPTION,
    image_url=OG_IMAGE_URL,
    icon="mdi:draw",
)

DOC_TEXT = (
    "The canvas opens with a 1920x1080 artboard (Full HD, the 16:9 Power BI "
    "page size) pre-populated with a sample KPI dashboard. The same KPI "
    "cards, round badges, gradient cards, chart panels, progress bars, "
    "donuts and gradient swatches also sit in Excalidraw's own Personal "
    "Library (the Library button, top right) — drag one onto the canvas "
    "as many times as needed. To export the background: menu → Export "
    "image → PNG, scale 1x, keep the dialog's dark-mode toggle off — the UI "
    "chrome stays dark but the canvas itself is kept light (every colour "
    "here is already hand-authored dark) via "
    "`assets/excalidraw-no-canvas-invert.css`, which switches off "
    "Excalidraw's usual dark-theme canvas inversion. In Power BI, set the "
    "page size to 16:9 / 1920x1080 and add the image as page background at "
    "\"Fit\"."
)

_CODE_FILES = [
    ("pages/excalidraw.py", "python", "devicon:python"),
    ("components/excalidraw_kpi.py", "python", "devicon:python"),
]
_CODE_SOURCE = {path: Path(path).read_text(encoding="utf-8") for path, _lang, _icon in _CODE_FILES}

# dash-improve-my-llms picks this up automatically and serves it verbatim at
# /excalidraw/llms.txt — see pages/home.py and the (removed) color-picker
# live page for the same pattern. The source is embedded, not just
# described, so the crawler-facing prerender carries real content.
LLMS_DOC = (
    f"# {NAME}\n\n> {DESCRIPTION}\n\n{DOC_TEXT}\n\n"
    + "\n\n".join(
        f"## {path}\n\n```python\n{source}```" for path, source in _CODE_SOURCE.items()
    )
)

_code_tabs = dmc.CodeHighlightTabs(
    code=[
        {
            "fileName": Path(path).name,
            "code": _CODE_SOURCE[path],
            "language": language,
            "icon": DashIconify(icon=icon),
        }
        for path, language, icon in _CODE_FILES
    ],
    defaultExpanded=False,
    withExpandButton=True,
)

_copy_button = dmc.Tooltip(
    dmc.Button(
        dmc.Group(
            [DashIconify(icon="mdi:file-document-outline", width=14), "Copy llms.txt URL"],
            gap=6,
            wrap="nowrap",
        ),
        id="llm-copy-button-excalidraw",
        variant="subtle",
        color="gray",
        size="compact-sm",
        className="llms-copy-button",
    ),
    label="Copy this page's /llms.txt URL — paste into ChatGPT, Claude, or any LLM",
    position="top",
    withArrow=True,
)

# Canvas first, full-bleed, right under a slim title bar -- a drawing tool
# earns the viewport, not the page chrome around it. Everything explanatory
# (description, copy button, source) sits below the fold instead of pushing
# the canvas down.
_title_row = dmc.Group(
    justify="space-between",
    align="center",
    px="md",
    py="xs",
    style={"height": _TITLE_ROW_HEIGHT, "borderBottom": "1px solid var(--mantine-color-default-border)"},
    children=[
        dmc.Title(NAME, order=4, className="m2d-heading", style={"margin": 0}),
        _copy_button,
    ],
)

layout = dmc.Box(
    id="m2d-page-excalidraw",
    children=[
        _title_row,
        html.Div(
            build_excalidraw("excalidraw", DEFAULT_OPACITY, height=_CANVAS_HEIGHT),
            id="excalidraw-container",
        ),
        dmc.Container(
            fluid=True,
            py="xl",
            children=[
                dmc.Text(DESCRIPTION, className="m2d-paragraph"),
                dmc.Divider(my="xl"),
                dmc.Title("How it works", order=4),
                dmc.Text(DOC_TEXT, className="m2d-paragraph", mb="md"),
                _code_tabs,
            ],
        ),
    ],
)
