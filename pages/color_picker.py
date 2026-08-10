from pathlib import Path

import dash_mantine_components as dmc
from dash import register_page
from dash_iconify import DashIconify

from components.color_picker_widget import build_layout
from lib.constants import OG_IMAGE_URL, PAGE_TITLE_PREFIX

NAME = "Color Picker *"
DESCRIPTION = "A clickable flower-shaped color picker built with plain Dash html components."

# NAV_NAME (not NAME) drives both the sidebar label and the <title> tag:
# dash-improve-my-llms's prerender injection overwrites <title> from the
# registered page's `name`, ignoring `title=` entirely. Reusing NAME here
# would make this page and the docs demo (docs/color-picker/color-picker.md,
# same NAME) render an identical sidebar entry and an identical <title> —
# indistinguishable in the nav and a duplicate-title flag to any crawler
# comparing head metadata site-wide. The on-page heading below still uses
# the clean NAME.
NAV_NAME = NAME + " — Live Page"

register_page(
    __name__,
    "/color-picker",
    name=NAV_NAME,
    title=PAGE_TITLE_PREFIX + NAV_NAME,
    description=DESCRIPTION,
    image_url=OG_IMAGE_URL,
    icon="mdi:palette-outline",
)

DOC_TEXT = (
    "Click any petal of the flower and its center blooms in that color; the "
    "hex code is shown underneath. Six `html.Div` petals, each carrying a "
    'pattern-matching id `{"type": "picker-petal", "color": <hex>}`, are '
    "absolutely positioned around a shared pivot and rotated 60° apart — no "
    "image, canvas or SVG. One callback listens to every petal's `n_clicks` "
    "at once and reads the clicked color straight off `ctx.triggered_id`."
)

_CODE_FILES = [
    ("pages/color_picker.py", "python", "devicon:python"),
    ("components/color_picker_widget.py", "python", "devicon:python"),
]
_CODE_SOURCE = {path: Path(path).read_text(encoding="utf-8") for path, _lang, _icon in _CODE_FILES}

# dash-improve-my-llms picks this up automatically and serves it verbatim at
# /color-picker/llms.txt — see pages/home.py for the same pattern. The source
# is embedded (not just described) so the crawler-facing prerender carries as
# much real content as the docs demo's expanded `.. source::` directives do.
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
        id="llm-copy-button-color-picker",
        variant="subtle",
        color="gray",
        size="compact-sm",
        className="llms-copy-button",
    ),
    label="Copy this page's /llms.txt URL — paste into ChatGPT, Claude, or any LLM",
    position="top",
    withArrow=True,
)

layout = dmc.Container(
    id="m2d-page-color-picker",
    size="lg",
    py="xl",
    children=[
        dmc.Title(NAME, order=2, className="m2d-heading"),
        dmc.Text(DESCRIPTION, className="m2d-paragraph"),
        dmc.Box(_copy_button, c="dimmed", my="sm"),
        build_layout(),
        dmc.Divider(my="xl"),
        dmc.Title("How it works", order=4),
        dmc.Text(DOC_TEXT, className="m2d-paragraph", mb="md"),
        _code_tabs,
    ],
)
