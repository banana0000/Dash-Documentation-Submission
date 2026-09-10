"""Shared Excalidraw KPI-dashboard-mockup builder.

Used by two entry points: `examples/excalidraw_app.py` (a fully standalone
`Dash(__name__)` app on its own port) and `docs/excalidraw/excalidraw.md`
(the /excalidraw docs page, which embeds the module-level `component` at
the bottom of this file through `.. exec::`). Split out so importing one
entry point never instantiates the other's `Dash()` app as a side effect -- the same shape as `components/color_picker_widget.py` used to
sit relative to the color picker's page and docs demo.

The drawing is meant to end up as a Power BI report page background image, so
the canvas opens with a 1920x1080 artboard (Full HD, the 16:9 page size) and
nothing else -- a clean background to work on.

The KPI templates -- cards, round badges, gradient cards, charts, progress
bars, donuts, gradient ramp swatches -- sit in Excalidraw's Personal Library
(the sidebar behind the Library button, top right); drag one onto the
artboard as many times as needed. The "Browse libraries" link at the bottom
of that sidebar is hidden (assets/excalidraw-hide-browse-libraries.css) --
it points at libraries.excalidraw.com, not used here.

To export the background: menu -> Export image -> PNG, scale 1x. The artboard
is the outermost element and appState sets exportPadding to 0, so the file
comes out at exactly 1920x1080. Keep the dialog's dark-mode toggle OFF (it
defaults off here via exportWithDarkMode): the UI is themed "dark" for its
chrome, but assets/excalidraw-no-canvas-invert.css switches off the canvas
invert Excalidraw layers on top of that -- every colour in this file is
already hand-authored dark, so the invert (on screen or, via this toggle,
in the exported file) would flip it back to light. In Power BI, set the
page size to 16:9 / 1920x1080 and add the image as page background at
"Fit".

Corner radius and opacity of the templates are fixed in code below
(DEFAULT_BORDER_RADIUS / DEFAULT_OPACITY). Excalidraw's own UI has no numeric
field for either radius (only an Edges Sharp/Round toggle); opacity has a
built-in slider in the left panel.

On the package: pip's PyPI release 0.0.4 only reads `initialData` once at
mount and has no way to push further changes into a live scene, and its
`appState` output back to Python is stripped down to just gridSize/
viewBackgroundColor. The 0.1.0 build from GitHub instead exposes a `command`
prop (`{"id": ..., "type": "updateScene", "payload": {...}}`) that updates
the mounted scene imperatively without remounting or losing what's on the
canvas -- so a future live-editing feature (an "apply to selection" tool,
for instance) should use that, not the old approach. Both entry points need
the GitHub build:

    pip install "git+https://github.com/pip-install-python/dash-excalidraw.git"
"""
import math

from dash_excalidraw import DashExcalidraw

DEFAULT_BORDER_RADIUS = 10
DEFAULT_OPACITY = 100


def _lerp_color(start_hex, end_hex, t):
    """Linear RGB interpolation between two #rrggbb colours."""
    start = [int(start_hex[i:i + 2], 16) for i in (1, 3, 5)]
    end = [int(end_hex[i:i + 2], 16) for i in (1, 3, 5)]
    mixed = [round(s + (e - s) * t) for s, e in zip(start, end)]
    return "#{:02x}{:02x}{:02x}".format(*mixed)


GRADIENT_PALETTE = [
    ("Ocean", "#0ea5e9", "#2563eb"),
    ("Violet", "#6366f1", "#a855f7"),
    ("Sunset", "#f97316", "#ec4899"),
    ("Mint", "#10b981", "#84cc16"),
    ("Ember", "#ef4444", "#f59e0b"),
    ("Slate", "#334155", "#94a3b8"),
]


def gradient_swatch(swatch_id, seed_base, color_from, color_to, name, opacity, width=160, height=60):
    """A gradient sample bar with its name underneath -- a palette to pick
    from: copy a bar, resize it, and it keeps its colour ramp."""
    group_id = f"{swatch_id}-group"
    bands_count = 16
    band_width = width / bands_count

    elements = []
    for i in range(bands_count):
        color = _lerp_color(color_from, color_to, i / (bands_count - 1))
        elements.append({
            "id": f"{swatch_id}-band-{i}",
            "type": "rectangle",
            "x": i * band_width,
            "y": 0,
            "width": band_width + 1,
            "height": height,
            "strokeColor": color,
            "backgroundColor": color,
            "fillStyle": "solid",
            "strokeWidth": 1,
            "roughness": 0,
            "roundness": None,
            "opacity": opacity,
            "seed": seed_base + i,
            "version": 1,
            "versionNonce": seed_base + i,
            "isDeleted": False,
            "boundElements": None,
            "updated": 1,
            "link": None,
            "locked": False,
            "groupIds": [group_id],
        })

    elements.append({
        "id": f"{swatch_id}-caption",
        "type": "text",
        "x": 0,
        "y": height + 8,
        "width": width,
        "height": 20,
        "strokeColor": "#f8fafc",
        "backgroundColor": "transparent",
        "fillStyle": "hachure",
        "strokeWidth": 1,
        "roughness": 1,
        "opacity": opacity,
        "seed": seed_base + 30,
        "version": 1,
        "versionNonce": seed_base + 30,
        "fontSize": 16,
        "fontFamily": 2,
        "text": name,
        "baseline": 0,
        "lineHeight": 1.2,
        "textAlign": "center",
        "verticalAlign": "top",
        "isDeleted": False,
        "boundElements": None,
        "updated": 1,
        "link": None,
        "locked": False,
        "groupIds": [group_id],
    })

    return {"id": swatch_id, "elements": elements}


def _shape(shape_id, group_id, shape_type, x, y, width, height, stroke, background, opacity, seed,
           fill_style="solid", roughness=1, stroke_width=2, roundness=None, extra=None):
    """One drawable element with the fields Excalidraw expects on every shape."""
    element = {
        "id": shape_id,
        "type": shape_type,
        "x": x,
        "y": y,
        "width": width,
        "height": height,
        "strokeColor": stroke,
        "backgroundColor": background,
        "fillStyle": fill_style,
        "strokeWidth": stroke_width,
        "roughness": roughness,
        "roundness": roundness,
        "opacity": opacity,
        "seed": seed,
        "version": 1,
        "versionNonce": seed,
        "isDeleted": False,
        "boundElements": None,
        "updated": 1,
        "link": None,
        "locked": False,
        "groupIds": [group_id],
    }
    if extra:
        element.update(extra)
    return element


def _text(text_id, group_id, x, y, width, height, font_size, color, content, opacity, seed, align="left",
          font_family=2):
    # fontFamily: 1 = hand-drawn (Virgil/Excalifont), 2 = normal (Helvetica),
    # 3 = code (Cascadia). 2 stays the default for the KPI templates' clean
    # dashboard-card look; the flowchart's _node passes 1 for "kézzel írott".
    return _shape(text_id, group_id, "text", x, y, width, height, color, "transparent", opacity, seed,
                  fill_style="hachure", stroke_width=1, extra={
                      "fontSize": font_size,
                      "fontFamily": font_family,
                      "text": content,
                      "baseline": 0,
                      "lineHeight": 1.2,
                      "textAlign": align,
                      "verticalAlign": "top",
                  })


CANVAS_WIDTH, CANVAS_HEIGHT = 1920, 1080


ARTBOARD_COLOR = "#ffffff"
DESK_COLOR = "#e2e8f0"


def artboard_frame(opacity):
    """The Full HD design area, meant to be exported as a Power BI report page
    background: a plain filled rectangle. It is the outermost element, so
    with exportPadding 0 the exported image is exactly CANVAS_WIDTH x
    CANVAS_HEIGHT."""
    return [
        _shape("artboard", "artboard-group", "rectangle", 0, 0, CANVAS_WIDTH, CANVAS_HEIGHT,
               ARTBOARD_COLOR, ARTBOARD_COLOR, opacity, 5000, roughness=0, stroke_width=1),
    ]


def placed(template, dx, dy):
    """Shift a template's elements to (dx, dy) on the canvas."""
    return [
        dict(element, x=element["x"] + dx, y=element["y"] + dy)
        for element in template["elements"]
    ]


CIRCLE_SIZE = 180
GRADIENT_BANDS = 24


def kpi_card_template(tid, seed, accent, label, value, trend, opacity):
    group_id = f"{tid}-group"
    return {"id": tid, "elements": [
        _shape(f"{tid}-card", group_id, "rectangle", 0, 0, 240, 150, "#000000", accent, opacity, seed,
               fill_style="solid", roundness={"type": 3, "value": DEFAULT_BORDER_RADIUS}),
        _text(f"{tid}-label", group_id, 20, 20, 200, 24, 20, "#f8fafc", label, opacity, seed + 1),
        _text(f"{tid}-value", group_id, 20, 60, 200, 30, 32, "#ffffff", value, opacity, seed + 2),
        _text(f"{tid}-trend", group_id, 20, 105, 200, 24, 18, "#dbeafe", trend, opacity, seed + 3),
    ]}


def kpi_circle_template(tid, seed, accent, label, value, trend, opacity):
    """Round KPI badge. The texts span the circle's width and are centred, so
    the block stays centred whatever the text length."""
    group_id = f"{tid}-group"
    size = CIRCLE_SIZE
    return {"id": tid, "elements": [
        _shape(f"{tid}-circle", group_id, "ellipse", 0, 0, size, size, "#000000", accent, opacity, seed,
               fill_style="hachure"),
        _text(f"{tid}-label", group_id, 10, 47, size - 20, 20, 16, "#f8fafc", label, opacity, seed + 1, align="center"),
        _text(f"{tid}-value", group_id, 10, 71, size - 20, 40, 32, "#ffffff", value, opacity, seed + 2, align="center"),
        _text(f"{tid}-trend", group_id, 10, 117, size - 20, 18, 14, "#e2e8f0", trend, opacity, seed + 3, align="center"),
    ]}


def kpi_gradient_template(tid, seed, color_from, color_to, label, value, trend, opacity):
    """KPI card with a faked left-to-right gradient. Excalidraw has no gradient
    fill (an element carries a single backgroundColor), so the background is
    GRADIENT_BANDS solid strips stepping from color_from to color_to. Strips
    use roughness 0 and are 1px wider than their slot so no seams show.
    Corners stay sharp: a rounded outline over square strips would show them
    poking out at the corners."""
    group_id = f"{tid}-group"
    width, height = 240, 150
    band_width = width / GRADIENT_BANDS

    bands = []
    for i in range(GRADIENT_BANDS):
        color = _lerp_color(color_from, color_to, i / (GRADIENT_BANDS - 1))
        bands.append(_shape(f"{tid}-band-{i}", group_id, "rectangle", i * band_width, 0,
                            band_width + 1, height, color, color, opacity, seed + i,
                            roughness=0, stroke_width=1))

    return {"id": tid, "elements": bands + [
        _shape(f"{tid}-outline", group_id, "rectangle", 0, 0, width, height,
               "#000000", "transparent", opacity, seed + 90),
        _text(f"{tid}-label", group_id, 20, 20, width - 40, 24, 20, "#f8fafc", label, opacity, seed + 91),
        _text(f"{tid}-value", group_id, 20, 60, width - 40, 30, 32, "#ffffff", value, opacity, seed + 92),
        _text(f"{tid}-trend", group_id, 20, 105, width - 40, 24, 18, "#e2e8f0", trend, opacity, seed + 93),
    ]}


def bar_chart_panel(panel_id, seed, accent, title, bar_ratios, opacity):
    """Panel with a title and a row of vertical bars -- a chart placeholder."""
    group_id = f"{panel_id}-group"
    width, height = 260, 170
    plot_top, plot_bottom = 60, height - 20
    plot_height = plot_bottom - plot_top
    bar_width = 26
    gap = (width - 40 - len(bar_ratios) * bar_width) / max(len(bar_ratios) - 1, 1)

    elements = [
        _shape(f"{panel_id}-panel", group_id, "rectangle", 0, 0, width, height,
               "#000000", "#0f172a", opacity, seed, roundness={"type": 3, "value": 10}),
        _text(f"{panel_id}-title", group_id, 20, 20, width - 40, 24, 18, "#f8fafc", title, opacity, seed + 1),
    ]
    for i, ratio in enumerate(bar_ratios):
        bar_height = round(plot_height * ratio)
        elements.append(_shape(
            f"{panel_id}-bar-{i}", group_id, "rectangle",
            20 + i * (bar_width + gap), plot_bottom - bar_height, bar_width, bar_height,
            accent, accent, opacity, seed + 10 + i, roughness=0, stroke_width=1))
    return {"id": panel_id, "elements": elements}


def sparkline_panel(panel_id, seed, accent, title, points, opacity):
    """Panel with a title and a trend line drawn from relative points."""
    group_id = f"{panel_id}-group"
    width, height = 260, 150
    return {"id": panel_id, "elements": [
        _shape(f"{panel_id}-panel", group_id, "rectangle", 0, 0, width, height,
               "#000000", "#0f172a", opacity, seed, roundness={"type": 3, "value": 10}),
        _text(f"{panel_id}-title", group_id, 20, 18, width - 40, 24, 18, "#f8fafc", title, opacity, seed + 1),
        _shape(f"{panel_id}-line", group_id, "line", 20, 100, points[-1][0], 40,
               accent, "transparent", opacity, seed + 2, fill_style="hachure", stroke_width=3, extra={
                   "points": points,
                   "startArrowhead": None,
                   "endArrowhead": None,
               }),
    ]}


def progress_card(card_id, seed, accent, label, percent, opacity):
    """Card with a label and a horizontal progress bar filled to `percent`."""
    group_id = f"{card_id}-group"
    width, height = 260, 110
    track_width = width - 40

    return {"id": card_id, "elements": [
        _shape(f"{card_id}-panel", group_id, "rectangle", 0, 0, width, height,
               "#000000", "#0f172a", opacity, seed, roundness={"type": 3, "value": 10}),
        _text(f"{card_id}-label", group_id, 20, 20, track_width, 24, 18, "#f8fafc", label, opacity, seed + 1),
        _text(f"{card_id}-value", group_id, 20, 20, track_width, 24, 18, "#cbd5e1", f"{percent}%", opacity,
              seed + 2, align="right"),
        _shape(f"{card_id}-track", group_id, "rectangle", 20, 62, track_width, 14,
               "#334155", "#334155", opacity, seed + 3, roughness=0, stroke_width=1),
        _shape(f"{card_id}-fill", group_id, "rectangle", 20, 62, round(track_width * percent / 100), 14,
               accent, accent, opacity, seed + 4, roughness=0, stroke_width=1),
    ]}


def donut_badge(badge_id, seed, accent, value, caption, opacity):
    """Ring chart: an accent disc with a background-coloured disc punched in."""
    group_id = f"{badge_id}-group"
    outer, ring = 150, 26
    inner = outer - 2 * ring

    return {"id": badge_id, "elements": [
        _shape(f"{badge_id}-outer", group_id, "ellipse", 0, 0, outer, outer,
               accent, accent, opacity, seed, roughness=0, stroke_width=1),
        _shape(f"{badge_id}-inner", group_id, "ellipse", ring, ring, inner, inner,
               ARTBOARD_COLOR, ARTBOARD_COLOR, opacity, seed + 1, roughness=0, stroke_width=1),
        # dark text: it sits in the punched-out centre, which matches
        # ARTBOARD_COLOR -- i.e. whatever the artboard itself is, not accent
        _text(f"{badge_id}-value", group_id, 10, outer / 2 - 22, outer - 20, 30, 26, "#0f172a", value,
              opacity, seed + 2, align="center"),
        _text(f"{badge_id}-caption", group_id, 10, outer / 2 + 8, outer - 20, 20, 14, "#475569", caption,
              opacity, seed + 3, align="center"),
    ]}


def _node(node_id, shape_type, x, y, w, h, fill, label, opacity, seed):
    """A flowchart node: a filled shape (rectangle/diamond/ellipse) with its
    label centred on top. Its own group, separate from every other node --
    so a single click in the app selects just this box, not the whole
    diagram. The fill is faint (half the requested opacity) and the label
    uses Excalidraw's hand-drawn font -- "kézzel írott": the box reads as
    pencilled in, not printed."""
    group_id = f"{node_id}-group"
    faint = max(1, round(opacity * 0.5))
    return [
        _shape(node_id, group_id, shape_type, x, y, w, h, "#000000", fill, faint, seed,
               roughness=0, stroke_width=1.5,
               roundness={"type": 3, "value": 12} if shape_type == "rectangle" else None),
        _text(f"{node_id}-label", group_id, x, y + h / 2 - 12, w, 24, 17, "#1e293b", label,
              opacity, seed + 1, align="center", font_family=1),
    ]


def _connector(arrow_id, points, color, opacity, seed, label=None, label_pos=None,
               start_id=None, end_id=None):
    """An arrow between two flowchart nodes, optionally captioned (e.g. a
    'Yes'/'No' branch label) at an explicit (x, y). Its own group, separate
    from the nodes it connects. When start_id/end_id name a node's shape id,
    the arrow is bound to it (Excalidraw's real connector binding) so
    dragging that node in the app drags the arrow's endpoint along with it
    -- bind_flowchart_arrows() below wires the matching boundElements entry
    onto the node shape itself."""
    group_id = f"{arrow_id}-group"
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    x0, y0 = points[0]
    extra = {
        "points": [[px - x0, py - y0] for px, py in points],
        "startArrowhead": None,
        "endArrowhead": "triangle",
        "roundness": {"type": 2},
    }
    if start_id:
        extra["startBinding"] = {"elementId": start_id, "focus": 0, "gap": 4}
    if end_id:
        extra["endBinding"] = {"elementId": end_id, "focus": 0, "gap": 4}
    elements = [
        # roughness=0: a clean line, not the sketchy hand-drawn default --
        # matches the node shapes, which are already roughness=0
        _shape(arrow_id, group_id, "arrow", x0, y0, max(xs) - min(xs) or 1, max(ys) - min(ys) or 1,
               color, "transparent", opacity, seed, roughness=0, stroke_width=2.5, extra=extra),
    ]
    if label:
        lx, ly = label_pos
        elements.append(_text(
            f"{arrow_id}-label", group_id, lx, ly, 60, 20, 14, "#475569", label, opacity, seed + 1,
            font_family=1,
        ))
    return elements


def bind_flowchart_arrows(elements):
    """Give each bound node shape a boundElements entry pointing back at its
    arrow, matching what Excalidraw itself writes when you draw a connector
    by hand between two shapes. Mutates elements in place."""
    by_id = {e["id"]: e for e in elements}
    for element in elements:
        if element["type"] != "arrow":
            continue
        for binding_key in ("startBinding", "endBinding"):
            binding = element.get(binding_key)
            if not binding:
                continue
            target = by_id.get(binding["elementId"])
            if target is None:
                continue
            if target["boundElements"] is None:
                target["boundElements"] = []
            target["boundElements"].append({"id": element["id"], "type": "arrow"})
    return elements


def flowchart_sample(origin_x, origin_y, opacity, scale=0.7):
    """A small branching flowchart drawn directly on the canvas: start, a
    process step, a decision, a Yes branch ending in a success node, and a
    No branch ending in an error node -- built from the same _shape/_text
    primitives as the KPI templates, connected with arrows.

    Every position/size below is one set of numbers times `scale`, so a
    smaller flowchart is one argument, not twenty re-tuned coordinates --
    the connectors stay correctly attached regardless, since they're all
    computed from the node tuples via cx_of(), never hardcoded separately."""
    seed = 15000
    elements = []

    def s(n):
        return round(n * scale)

    cx = origin_x + s(380)  # trunk column (start / step 1 / decision / No branch)
    bx = cx + s(220)         # Yes-branch column

    start = (cx - s(80), origin_y, s(160), s(64))
    step1 = (cx - s(110), origin_y + s(130), s(220), s(72))
    decision = (cx - s(100), origin_y + s(270), s(200), s(120))
    step_yes = (bx, origin_y + s(294), s(200), s(72))
    done = (bx + s(60), origin_y + s(390), s(160), s(64))
    step_no = (cx - s(110), origin_y + s(430), s(220), s(72))
    error = (cx - s(80), origin_y + s(542), s(160), s(64))

    def cx_of(node):
        x, y, w, h = node
        return x + w / 2, y, y + h  # (center-x, top-y, bottom-y)

    elements += _node("flow-start", "ellipse", *start, "#334155", "Start", opacity, seed)
    elements += _node("flow-step1", "rectangle", *step1, "#1d4ed8", "Collect data", opacity, seed + 10)
    elements += _node("flow-decision", "diamond", *decision, "#7c3aed", "Valid?", opacity, seed + 20)
    elements += _node("flow-step-yes", "rectangle", *step_yes, "#1d4ed8", "Process", opacity, seed + 30)
    elements += _node("flow-done", "ellipse", *done, "#047857", "Done", opacity, seed + 40)
    elements += _node("flow-step-no", "rectangle", *step_no, "#b45309", "Flag error", opacity, seed + 50)
    elements += _node("flow-error", "ellipse", *error, "#dc2626", "Error", opacity, seed + 60)

    sx, _, s_bot = cx_of(start)
    _, s1_top, s1_bot = cx_of(step1)
    _, d_top, d_bot = cx_of(decision)
    d_right_x, d_right_y = decision[0] + decision[2], decision[1] + decision[3] / 2
    yx, _, y_bot = cx_of(step_yes)
    y_left_x, y_left_y = step_yes[0], step_yes[1] + step_yes[3] / 2
    dnx, dn_top, _ = cx_of(done)
    nx, n_top, n_bot = cx_of(step_no)
    ex, e_top, _ = cx_of(error)

    elements += _connector(
        "flow-arrow-start", [(sx, s_bot), (sx, s1_top)], "#475569", opacity, seed + 100,
        start_id="flow-start", end_id="flow-step1",
    )
    elements += _connector(
        "flow-arrow-step1", [(sx, s1_bot), (sx, d_top)], "#475569", opacity, seed + 110,
        start_id="flow-step1", end_id="flow-decision",
    )
    elements += _connector(
        "flow-arrow-yes", [(d_right_x, d_right_y), (y_left_x, y_left_y)],
        "#10b981", opacity, seed + 120, "Yes", (d_right_x + s(20), d_right_y - s(22)),
        start_id="flow-decision", end_id="flow-step-yes",
    )
    elements += _connector(
        "flow-arrow-done", [(yx, y_bot), (dnx, dn_top)], "#475569", opacity, seed + 130,
        start_id="flow-step-yes", end_id="flow-done",
    )
    elements += _connector(
        "flow-arrow-no", [(sx, d_bot), (nx, n_top)], "#ef4444", opacity, seed + 140,
        "No", (sx + s(12), d_bot + s(10)), start_id="flow-decision", end_id="flow-step-no",
    )
    elements += _connector(
        "flow-arrow-error", [(nx, n_bot), (ex, e_top)], "#475569", opacity, seed + 150,
        start_id="flow-step-no", end_id="flow-error",
    )

    return bind_flowchart_arrows(elements)


def _polygon(shape_id, group_id, points, stroke, background, opacity, seed,
             roughness=1, stroke_width=2, fill_style="solid"):
    """A closed, filled shape from arbitrary points -- Excalidraw's `line`
    type doubles as a polygon once its point list loops back to the start.
    Used for the hand-drawn scene's mountains, where a plain rectangle/
    ellipse/diamond can't give a triangular peak."""
    x0, y0 = points[0]
    closed = points + [points[0]]
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return _shape(
        shape_id, group_id, "line", x0, y0, max(xs) - min(xs) or 1, max(ys) - min(ys) or 1,
        stroke, background, opacity, seed, fill_style=fill_style, roughness=roughness, stroke_width=stroke_width,
        extra={
            "points": [[px - x0, py - y0] for px, py in closed],
            "startArrowhead": None,
            "endArrowhead": None,
        },
    )


def _bird(bird_id, group_id, x, y, span, stroke, opacity, seed, roughness=1):
    """A single open two-stroke "v" (well, "w") -- the shorthand every kid's
    drawing of a distant bird uses. Unfilled, roughness left at its sketchy
    default so it reads as a quick pen mark rather than a drawn shape."""
    half = span / 2
    return _shape(
        bird_id, group_id, "line", x - half, y, span, span * 0.4,
        stroke, "transparent", opacity, seed, fill_style="solid", roughness=roughness, stroke_width=2,
        extra={
            "points": [[0, span * 0.4], [half * 0.5, 0], [half, span * 0.4],
                       [half * 1.5, 0], [span, span * 0.4]],
            "startArrowhead": None,
            "endArrowhead": None,
            "roundness": {"type": 2},
        },
    )


def hand_drawn_scene(origin_x, origin_y, opacity):
    """A small landscape, drawn by hand rather than composed from the KPI
    templates: sun, two mountains, a tree and a couple of distant birds.
    Faint (half the requested opacity) and roughness=2 -- Excalidraw's
    "Cartoonist" setting, wobblier than the flowchart's clean roughness=0 or
    even `_shape`'s own roughness=1 default -- so it reads as a light pencil
    sketch left on the desk, not a drawn diagram."""
    seed = 40000
    elements = []
    roughness = 2
    faint = max(1, round(opacity * 0.5))

    ground_y = origin_y + 320

    # Sun: a disc plus radiating rays (each ray its own short line, so they
    # come out as loose pen strokes instead of a single perfect starburst).
    sun_cx, sun_cy, sun_r = origin_x + 90, origin_y + 70, 34
    elements.append(_shape(
        "scene-sun", "scene-sun-group", "ellipse",
        sun_cx - sun_r, sun_cy - sun_r, sun_r * 2, sun_r * 2,
        "#f59e0b", "#fbbf24", faint, seed, fill_style="solid", roughness=roughness,
    ))
    for i in range(8):
        angle = math.radians(i * 45)
        inner = sun_r + 8
        outer = sun_r + 20
        x1, y1 = sun_cx + inner * math.cos(angle), sun_cy + inner * math.sin(angle)
        x2, y2 = sun_cx + outer * math.cos(angle), sun_cy + outer * math.sin(angle)
        elements.append(_shape(
            f"scene-sun-ray-{i}", "scene-sun-group", "line", x1, y1, abs(x2 - x1) or 1, abs(y2 - y1) or 1,
            "#f59e0b", "transparent", faint, seed + 1 + i, stroke_width=2, roughness=roughness,
            extra={"points": [[0, 0], [x2 - x1, y2 - y1]], "startArrowhead": None, "endArrowhead": None},
        ))

    # Two mountains, the near one overlapping the far one so they read as
    # a range rather than two isolated triangles.
    elements.append(_polygon(
        "scene-mountain-far", "scene-mountains-group",
        [(origin_x + 160, ground_y), (origin_x + 280, origin_y + 90), (origin_x + 400, ground_y)],
        "#475569", "#94a3b8", faint, seed + 20, roughness=roughness,
    ))
    elements.append(_polygon(
        "scene-mountain-near", "scene-mountains-group",
        [(origin_x + 40, ground_y), (origin_x + 190, origin_y + 130), (origin_x + 340, ground_y)],
        "#334155", "#64748b", faint, seed + 21, roughness=roughness,
    ))

    # Ground
    elements.append(_shape(
        "scene-ground", "scene-ground-group", "rectangle",
        origin_x, ground_y, 520, 40, "#15803d", "#4ade80", faint, seed + 30,
        fill_style="hachure", roughness=roughness,
    ))

    # A tree: trunk plus two overlapping foliage blobs, standing on the
    # ground to the right of the mountains.
    trunk_x, trunk_w, trunk_h = origin_x + 430, 16, 60
    elements.append(_shape(
        "scene-tree-trunk", "scene-tree-group", "rectangle",
        trunk_x, ground_y - trunk_h, trunk_w, trunk_h + 8, "#78350f", "#92400e", faint, seed + 40,
        roughness=roughness,
    ))
    for i, (dx, dy, r) in enumerate([(-18, -18, 34), (18, -14, 30), (0, -44, 32)]):
        cx, cy = trunk_x + trunk_w / 2 + dx, ground_y - trunk_h + dy
        elements.append(_shape(
            f"scene-tree-foliage-{i}", "scene-tree-group", "ellipse",
            cx - r, cy - r, r * 2, r * 2, "#166534", "#22c55e", faint, seed + 41 + i,
            fill_style="solid", roughness=roughness,
        ))

    # A couple of birds, distant and small, in the empty sky between the
    # sun and the tree.
    elements.append(_bird(
        "scene-bird-0", "scene-birds-group", origin_x + 280, origin_y + 40, 26, "#334155", faint, seed + 50,
        roughness=roughness,
    ))
    elements.append(_bird(
        "scene-bird-1", "scene-birds-group", origin_x + 320, origin_y + 60, 20, "#334155", faint, seed + 51,
        roughness=roughness,
    ))

    return elements


def dashboard_sample(origin_x, origin_y, opacity):
    """A small, polished KPI dashboard -- a title, three KPI cards, a
    chart/sparkline/progress row, and two donut badges -- built from the
    same templates the Library offers. The panel templates (bar_chart_panel,
    sparkline_panel, progress_card) keep their own dark backgrounds, which
    reads as a deliberate dark-card-on-light-page look against the white
    artboard."""
    elements = [
        _text("dashboard-title", "dashboard-title-group", origin_x, origin_y, 400, 32,
              24, "#0f172a", "Q3 Performance", opacity, 30000),
    ]

    row1_y = origin_y + 46
    cards = [
        kpi_card_template("sample-kpi-revenue", 30100, "#1d4ed8", "Net revenue", "$2.4M", "▲ 18.2% vs last month", opacity),
        kpi_card_template("sample-kpi-users", 30200, "#047857", "Active users", "18.2k", "▲ 9.1% this week", opacity),
        kpi_card_template("sample-kpi-retention", 30300, "#b45309", "Retention", "87%", "▲ 3.4% above target", opacity),
    ]
    for i, card in enumerate(cards):
        elements += placed(card, origin_x + i * 280, row1_y)

    row2_y = row1_y + 180
    row2 = [
        bar_chart_panel("sample-chart-traffic", 30400, "#38bdf8", "Weekly traffic",
                        [0.45, 0.7, 0.55, 0.9, 0.65, 1.0], opacity),
        sparkline_panel("sample-chart-trend", 30500, "#22c55e", "Performance trend",
                        [[0, 0], [60, -18], [120, -6], [180, -34], [220, -22]], opacity),
        progress_card("sample-progress-goal", 30600, "#7c3aed", "Quarter goal", 78, opacity),
    ]
    for i, panel in enumerate(row2):
        elements += placed(panel, origin_x + i * 300, row2_y)

    row3_y = row2_y + 200
    donuts = [
        donut_badge("sample-donut-uptime", 30700, "#38bdf8", "99.9%", "Uptime", opacity),
        donut_badge("sample-donut-nps", 30800, "#a855f7", "62", "NPS", opacity),
    ]
    for i, badge in enumerate(donuts):
        elements += placed(badge, origin_x + i * 200, row3_y)

    return elements


def build_library_items(opacity):
    """The templates offered in Excalidraw's Personal Library (right sidebar);
    drag one onto the canvas as many times as you like."""
    templates = [
        kpi_card_template("kpi-revenue", 101, "#1d4ed8", "Net revenue", "$2.4M", "▲ 18.2% vs last month", opacity),
        kpi_card_template("kpi-users", 201, "#047857", "Active users", "18.2k", "▲ 9.1% this week", opacity),
        kpi_card_template("kpi-retention", 301, "#b45309", "Retention", "87%", "▲ 3.4% above target", opacity),
        kpi_circle_template("kpi-circle-revenue", 401, "#1d4ed8", "Revenue", "$2.4M", "▲ 18.2%", opacity),
        kpi_circle_template("kpi-circle-users", 501, "#047857", "Users", "18.2k", "▲ 9.1%", opacity),
        kpi_circle_template("kpi-circle-retention", 601, "#b45309", "Retention", "87%", "▲ 3.4%", opacity),
        kpi_gradient_template("kpi-grad-revenue", 1000, "#1d4ed8", "#7c3aed", "Net revenue", "$2.4M", "▲ 18.2% QoQ", opacity),
        kpi_gradient_template("kpi-grad-users", 1200, "#047857", "#0d9488", "Active users", "18.2k", "▲ 9.1% WoW", opacity),
        kpi_gradient_template("kpi-grad-retention", 1400, "#b45309", "#dc2626", "Retention", "87%", "▲ 3.4% MoM", opacity),
        bar_chart_panel("chart-traffic", 3000, "#38bdf8", "Weekly traffic", [0.45, 0.7, 0.55, 0.9, 0.65, 1.0], opacity),
        sparkline_panel("chart-trend", 3100, "#22c55e", "Performance trend",
                        [[0, 0], [60, -18], [120, -6], [180, -34], [220, -22]], opacity),
        progress_card("progress-goal", 3200, "#22c55e", "Quarter goal", 78, opacity),
        progress_card("progress-budget", 3300, "#f59e0b", "Budget used", 46, opacity),
        donut_badge("donut-uptime", 3400, "#38bdf8", "99.9%", "Uptime", opacity),
        donut_badge("donut-nps", 3500, "#a855f7", "62", "NPS", opacity),
        donut_badge("donut-churn", 3600, "#ef4444", "2.1%", "Churn", opacity),
        # The hand-drawn landscape: not on the canvas by default any more
        # (the flowchart is), but still one drag away for whoever wants it.
        # Origin (0, 0), not the canvas's usual (100, 100) -- Library items
        # are dropped wherever the cursor is, so they're authored relative
        # to their own top-left corner.
        {"id": "scene-landscape", "elements": hand_drawn_scene(0, 0, opacity)},
    ]
    # the navbar chips only copy hex codes, and Excalidraw fills a shape with a
    # single colour -- these banded bars are how a gradient actually gets onto
    # the artboard
    templates += [
        gradient_swatch(f"ramp-{index}", 2000 + index * 40, start, end, name, opacity)
        for index, (name, start, end) in enumerate(GRADIENT_PALETTE)
    ]
    return [
        {"id": t["id"], "status": "unpublished", "created": 1700000000000, "elements": t["elements"]}
        for t in templates
    ]


def build_canvas_elements(opacity):
    """Just the flowchart sample -- one small worked example, floating on the
    desk with no artboard rectangle behind it. The canvas pans freely, so a
    fixed background isn't earning its keep here the way it does for the
    Power-BI-export use case (artboard_frame is still there to compose in by
    hand, e.g. from the Library, whenever that's actually needed).
    hand_drawn_scene and the KPI templates are just as available, they're
    just not what greets a first-time visitor. The KPI templates themselves
    live in the Personal Library instead of being pre-placed on the canvas;
    drag one out when it's actually wanted."""
    return flowchart_sample(100, 100, opacity)


def build_excalidraw_with_elements(component_id, elements, opacity, height="85vh"):
    """Same mount as build_excalidraw, but with an already-built element list.
    Split out from build_excalidraw so a future live-editing feature can pass
    its own elements without going through build_canvas_elements -- see the
    module docstring's note on the `command`/updateScene prop; there's no
    longer any need to remount the component to change what's on the canvas.

    `height` defaults to the standalone app's own figure (it has nothing but
    a slim H3 above the canvas); the embedded /excalidraw page passes a
    taller value to fill more of the viewport under the site's header."""
    return DashExcalidraw(
        id=component_id,
        width="100%",
        height=height,
        # "dark" for the UI chrome (toolbar/panels/buttons) -- the canvas
        # itself stays light (ARTBOARD_COLOR/DESK_COLOR are near-white)
        # regardless, because assets/excalidraw-no-canvas-invert.css kills
        # the CSS invert Excalidraw's dark theme normally layers on top of
        # the canvas (--theme-filter: invert(93%) hue-rotate(180deg)) -- left
        # on, it would flip every hand-authored colour here to its opposite.
        # toggleTheme below still puts a sun/moon toggle in the app's own
        # menu, for whoever wants the light chrome back.
        theme="dark",
        gridModeEnabled=False,
        # the dash-excalidraw wrapper defaults tools.image to disabled --
        # the toolbar button renders either way, but does nothing until this
        # is set, so the image tool otherwise looks broken (no file picker
        # opens, no error either). clearCanvas surfaces Excalidraw's own
        # "Reset the canvas" action (confirmation dialog included) in the
        # hamburger menu, top left -- a real "clear everything" button
        # rather than a custom one built against the command prop. Same
        # idea for saving: saveAsImage puts "Export image" in that menu
        # (PNG/SVG/clipboard, the flow the module docstring's export steps
        # already assume), and export.saveFileToDisk adds a one-click
        # "Save to disk" alongside it that skips the dialog.
        UIOptions={
            "canvasActions": {
                "toggleTheme": True,
                "clearCanvas": True,
                "saveAsImage": True,
                "export": {"saveFileToDisk": True},
            },
            "tools": {"image": True},
        },
        # lets the "Web Embed" tool (More tools menu) embed any http(s) URL,
        # not just Excalidraw's default-recognised providers (YouTube, Figma,
        # ...). Live only in the editor -- PNG export shows a blank
        # placeholder where an embed sits, since export doesn't run iframes.
        validateEmbeddable=True,
        initialData={
            "elements": elements,
            "libraryItems": build_library_items(opacity),
            "appState": {
                # Pinned rather than left to Excalidraw's implicit default:
                # that default is computed from the mounting container's
                # size, and inside the embedded /excalidraw page's nested
                # AppShell/Mantine layout the container can still be mid-
                # layout (e.g. height 0) at the moment Excalidraw reads it --
                # the standalone app (a plain html.Div, sized immediately)
                # never hit this, which is what made it look content-specific
                # at first. Scrolled/zoomed so the artboard's top-left corner
                # sits just inside the viewport instead of literal (0, 0),
                # which the toolbar and hint text would otherwise cover.
                "scrollX": 60,
                "scrollY": 60,
                "zoom": {"value": 1},
                # the desk around the artboard; the exported image never shows
                # it, since the artboard rectangle bounds the export
                "viewBackgroundColor": DESK_COLOR,
                # 0 so the PNG comes out at exactly 1920x1080 (default is 10)
                "exportPadding": 0,
                # no dark-mode inversion to compensate: the canvas invert is
                # already killed in CSS (see the theme= comment above), so
                # colours already render true to what's stored
                "exportWithDarkMode": False,
                "exportBackground": True,
                # matches the flowchart connectors' own styling, so an arrow
                # drawn by hand with the toolbar starts out looking the same:
                # a clean line (not the sketchy hand-drawn default) with a
                # solid triangular head instead of the default open "v"
                "currentItemRoughness": 0,
                "currentItemEndArrowhead": "triangle",
            },
        },
    )


def build_excalidraw(component_id, opacity, height="85vh"):
    return build_excalidraw_with_elements(component_id, build_canvas_elements(opacity), opacity, height=height)


# What `.. exec::docs.excalidraw.kpi_mockup` renders on the /excalidraw docs
# page. The component id stays "excalidraw": assets/excalidraw-*.css scope
# their rules to #excalidraw, for both this page and the standalone app.
component = build_excalidraw("excalidraw", DEFAULT_OPACITY, height="75vh")
