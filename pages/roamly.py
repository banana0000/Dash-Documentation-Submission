import dash_mantine_components as dmc
from dash import register_page
from dash_iconify import DashIconify

from lib.constants import OG_IMAGE_URL, PAGE_TITLE_PREFIX

NAME = "Roamly *"
DESCRIPTION = (
    "A house-only stay/property booking platform mockup -- a listings grid, an "
    "individual stay page with an image gallery, and a host dashboard. Built on "
    "Dash, Dash Mantine Components and dash-leaflet."
)

register_page(
    __name__,
    "/roamly",
    name=NAME,
    title=PAGE_TITLE_PREFIX + NAME,
    description=DESCRIPTION,
    image_url=OG_IMAGE_URL,
    icon="tabler:map-2",
)

# Unlike the Dash Flow / Excalidraw apps, Roamly is not a component embedded
# into this site's own multi-page app -- it's a full standalone Dash app
# (own AppShell, own theme, own page router, own dark-mode toggle) living in
# roamly/ at the repo root. Running it inline here would collide with this
# site's own ids (e.g. both apps have a "color-scheme-toggle"), so this page
# is a link-out card rather than an embed, the same way the navbar's "Apps"
# section opens this page itself in a new tab.
ROAMLY_URL = "http://localhost:8870/"

# dash-improve-my-llms picks this up automatically and serves it verbatim at
# /roamly/llms.txt -- see pages/excalidraw.py for the same pattern. Roamly's
# own source lives outside this app (roamly/ at the repo root), so this is a
# pointer to it rather than embedded source.
LLMS_DOC = (
    f"# {NAME}\n\n> {DESCRIPTION}\n\n"
    "Roamly is a standalone Dash app, not a page embedded in this site -- "
    f"its own AppShell, theme and page router run separately at {ROAMLY_URL} "
    "(source: roamly/ at this repo's root, started with `python roamly/app.py`)."
)

layout = dmc.Container(
    id="m2d-page-roamly",
    size="sm",
    py="xl",
    children=dmc.Stack(
        [
            dmc.Group(
                [
                    dmc.ThemeIcon(
                        DashIconify(icon="tabler:map-2", width=22),
                        size=44, radius="xl", variant="filled", color="green",
                    ),
                    dmc.Title(NAME, order=3, className="m2d-heading", style={"margin": 0}),
                ],
                gap="sm",
            ),
            dmc.Text(DESCRIPTION, c="dimmed"),
            dmc.Text(
                "Roamly runs as its own standalone Dash app, so it opens in a "
                "separate tab and on its own port instead of inside this site.",
                size="sm",
            ),
            dmc.Anchor(
                dmc.Button(
                    "Open Roamly",
                    leftSection=DashIconify(icon="tabler:external-link", width=16),
                    size="md",
                ),
                href=ROAMLY_URL,
                target="_blank",
                underline=False,
            ),
            dmc.Code(f"python roamly/app.py  # serves at {ROAMLY_URL}", block=True),
        ],
        gap="md",
    ),
)
