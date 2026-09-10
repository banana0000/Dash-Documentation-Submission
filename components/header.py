import dash_mantine_components as dmc
from dash import Output, Input, State, clientside_callback, html, get_asset_url
from dash_iconify import DashIconify

from components.backend_badge import create_backend_badge
from components.navbar import search_data
from lib.backend import get_backend_info
from lib.constants import (
    GITHUB_URL,
    HEADER_HEIGHT,
    LOGO_ASSET,
    LOGO_STYLE,
    WORDMARK,
    WORDMARK_COLOR,
    WORDMARK_VISIBLE_FROM,
)


def create_link(icon, href):
    """Create an external link icon button"""
    return dmc.Anchor(
        dmc.ActionIcon(
            DashIconify(icon=icon, width=22),
            variant="subtle",
            size="lg",
            color="gray",
        ),
        href=href,
        target="_blank",
    )


def create_search(data):
    """Searchable dropdown for page navigation — the sidebar's pages and
    nothing else (components/navbar.search_data decides: never Home, never a
    hidden-tier page)."""
    return dmc.Select(
        id="select-component",
        placeholder="Search pages...",
        searchable=True,
        clearable=True,
        w=240,
        size="sm",
        nothingFoundMessage="No pages found",
        leftSection=DashIconify(icon="mingcute:search-3-line", width=18),
        data=search_data(data),
        visibleFrom="sm",
        comboboxProps={"zIndex": 2000},
        styles={
            "input": {
                "borderColor": "var(--mantine-color-gray-4)",
            }
        }
    )


def _create_openapi_link():
    """Show a Swagger UI link only when the FastAPI backend is active."""
    info = get_backend_info()
    if info.name != "fastapi":
        return None
    return dmc.Tooltip(
        label="OpenAPI docs (Swagger UI) — available on the FastAPI backend",
        position="bottom",
        withArrow=True,
        children=dmc.Anchor(
            dmc.Badge(
                "OpenAPI",
                leftSection=DashIconify(icon="logos:swagger", width=14),
                variant="light",
                color="cyan",
                radius="sm",
                styles={"root": {"textTransform": "none", "fontWeight": 600}},
            ),
            href="/docs",
            target="_blank",
            underline=False,
        ),
    )


def create_header(data):
    """Create application header with logo, search, and theme toggle"""
    return dmc.AppShellHeader(
        dmc.Group(
            [
                # Left section: Hamburger (mobile) + Burger (desktop collapse) + Logo
                dmc.Group(
                    [
                        dmc.ActionIcon(
                            DashIconify(icon="radix-icons:hamburger-menu", width=22),
                            id="drawer-hamburger-button",
                            variant="subtle",
                            size="lg",
                            color="gray",
                            hiddenFrom="md",
                        ),
                        # Desktop-only burger: collapses/expands the AppShell navbar
                        # on md-xl screens. Default opened=True so users see the X
                        # state on first load (navbar visible).
                        dmc.Burger(
                            id="desktop-navbar-toggle",
                            opened=True,
                            size="sm",
                            visibleFrom="md",
                        ),
                        # Logo + wordmark, both from lib/constants.py so a
                        # rename of the site never has to touch this file.
                        dmc.Anchor(
                            dmc.Group(
                                [
                                    html.Img(
                                        src=get_asset_url(LOGO_ASSET),
                                        alt="",
                                        style=LOGO_STYLE,
                                    ),
                                    dmc.Text(
                                        WORDMARK,
                                        size="lg",
                                        fw=700,
                                        c=WORDMARK_COLOR,
                                        id="dash-docs-title",
                                        visibleFrom=WORDMARK_VISIBLE_FROM,
                                    ),
                                ],
                                gap="sm",
                            ),
                            href="/",
                            underline=False,
                            **{"aria-label": f"{WORDMARK} — home"},
                        ),
                    ],
                    gap="md",
                ),

                # Right section: Backend badge + OpenAPI (fastapi only) + Search + GitHub + Theme toggle
                dmc.Group(
                    [
                        dmc.Box(create_backend_badge(), visibleFrom="sm"),
                        dmc.Box(_create_openapi_link(), visibleFrom="md"),
                        create_search(data),
                        create_link("radix-icons:github-logo", GITHUB_URL),
                        dmc.ActionIcon(
                            [
                                DashIconify(
                                    icon="radix-icons:sun",
                                    width=22,
                                    id="light-theme-icon",
                                ),
                                DashIconify(
                                    icon="radix-icons:moon",
                                    width=22,
                                    id="dark-theme-icon",
                                ),
                            ],
                            variant="subtle",
                            color="yellow",
                            id="color-scheme-toggle",
                            size="lg",
                        ),
                    ],
                    gap="sm",
                ),
            ],
            justify="space-between",
            h=HEADER_HEIGHT,
            px="xl",
        ),
    )


clientside_callback(
    """
    function(value) {
        if (value) {
            return value
        }
    }
    """,
    Output("url", "href"),
    Input("select-component", "value"),
)

# Mobile drawer search → navigate (the header Select is hidden below `sm`).
clientside_callback(
    """
    function(value) {
        if (value) {
            return value
        }
        return window.dash_clientside.no_update
    }
    """,
    Output("url", "href", allow_duplicate=True),
    Input("mobile-select-component", "value"),
    prevent_initial_call=True,
)

# The overlay no longer covers the header, so the hamburger stays reachable
# while the drawer is open — make a second tap close it.
clientside_callback(
    """function(n_clicks, opened) { return !opened }""",
    Output("components-navbar-drawer", "opened"),
    Input("drawer-hamburger-button", "n_clicks"),
    State("components-navbar-drawer", "opened"),
    prevent_initial_call=True,
)
