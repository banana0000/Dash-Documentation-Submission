from pathlib import Path

import frontmatter
import dash_mantine_components as dmc
from dash import Input, Output, callback, dcc, no_update, register_page

from lib.constants import OG_IMAGE_URL, PAGE_TITLE_PREFIX, SITE_DESCRIPTION

register_page(
    __name__,
    "/",
    title=PAGE_TITLE_PREFIX + "Home",
    # Dash emits `description`, `og:description` and `twitter:description` for
    # every page from this argument, and emits them EMPTY when it is missing —
    # which is what the home page, the most-linked page on the site, was doing.
    description=SITE_DESCRIPTION,
    # The most-shared page on the site. See lib.constants.OG_IMAGE_URL for why
    # this is explicit rather than inferred from assets/.
    image_url=OG_IMAGE_URL,
)

directory = "docs"

# read the home page markdown
md_file = Path("pages") / "home.md"

post = frontmatter.loads(md_file.read_text(encoding="utf-8"))
metadata, content = post.metadata, post.content

# Module-level LLMS_DOC — dash-improve-my-llms 2.0 picks this up automatically
# and serves it verbatim at /llms.txt. No layout walking, no extraction.
LLMS_DOC = content

layout = dmc.Container(
    # Page-unique id: keeps React's keyed reconciliation of page swaps atomic
    # (see the wrapper comment in pages/markdown.py).
    id="m2d-page-home",
    size="lg",
    py="xl",
    children=[
        dcc.Markdown(
            content,
            style={
                "maxWidth": "none",  # Allow Container to control width
            }
        )
    ]
)


# A human landing on "/" gets bounced straight to the actual demo — this
# site has exactly one thing to show. Agents are unaffected: /llms.txt is a
# plain HTTP route, not part of the client-side router this callback lives
# in, so it still serves LLMS_DOC (this page's prose plus the site index)
# regardless of where a browser ends up.
#
# `prevent_initial_call=False` is required — the app sets
# `prevent_initial_callbacks=True` globally, and the very first load of "/"
# IS the case this callback exists for.
@callback(
    Output("url", "pathname"),
    Input("url", "pathname"),
    prevent_initial_call=False,
)
def _redirect_home_to_picker(pathname):
    if pathname == "/":
        return "/examples/color-picker"
    return no_update
