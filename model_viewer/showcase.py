"""3D model viewer built on dash_model_viewer (Google's <model-viewer> web
component, wrapped for Dash by 2plot.ai).

Shared between two entry points, the same shape as components/excalidraw_kpi.py.
Lives in its own model_viewer/ directory (like roamly/), not components/:

| Where                 | Notes                                            |
|-----------------------|---------------------------------------------------|
| pages/model-viewer.py | Embedded page on the main site at /model-viewer    |
| model_viewer/app.py   | Fully independent standalone app, own Dash(__name__) instance, own port |

model_viewer/app.py imports this module bare (``from showcase import ...``)
so the whole model_viewer/ directory stays deployable on its own; the
embedded page imports it as ``model_viewer.showcase`` instead, since it
runs from the repo root where model_viewer/ is a package (see
model_viewer/__init__.py).

Element ids are prefixed ``model-viewer-`` so this page's callbacks never
collide with ids on any other page of the same running multi-page app.

Model files are Khronos/Google's own public glTF samples, hosted on
raw.githubusercontent.com / modelviewer.dev's shared-assets CDN -- free, no
API key, no local files to ship in this repo. Every control's color (cyan)
comes from model-viewer.css -- the repo-root assets/ copy for the embedded
page, model_viewer/assets/ for the standalone app -- scoped to the
``PAGE_CLASS`` wrapper below, not a dmc `color` prop.
"""
import json
import re

import dash_mantine_components as dmc
from dash import callback, clientside_callback, ctx, dcc, Input, Output, State, no_update
from dash_iconify import DashIconify
from dash_model_viewer import DashModelViewer

_UPLOAD_HINT = "Applies this PNG as the model's surface texture."

_SKULL_SRC = "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Assets/main/Models/ScatteringSkull/glTF-Binary/ScatteringSkull.glb"

MODELS = {
    "damaged-helmet": {
        "label": "Damaged Helmet",
        # Khronos's own flagship PBR showcase model -- full metal/roughness,
        # normal, emissive and ambient-occlusion maps, rather than the flat
        # cartoon shading of the other samples, so it reads as an actual
        # rendered object under real lighting instead of a toy. First in
        # the picker and the default, for the same reason. Orbit is pulled
        # back further than a tight helmet-filling closeup so the ground
        # plane -- and the shadowIntensity slider's actual effect -- stays
        # in frame instead of being cropped out.
        "src": "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Assets/main/Models/DamagedHelmet/glTF-Binary/DamagedHelmet.glb",
        "alt": "A 3D model of a battle-damaged sci-fi helmet with realistic PBR materials",
        "orbit": "10deg 65deg 9m",
    },
    "scattering-skull": {
        "label": "Skull",
        # Khronos's subsurface-scattering demo model -- a medically-shaped
        # subject rendered with light actually passing through thin bone,
        # rather than a plain opaque material.
        "src": _SKULL_SRC,
        "alt": "A 3D model of a human skull, rendered with subsurface scattering",
        "orbit": "0deg 70deg 0.8m",
    },
    "mosquito-in-amber": {
        "label": "Mosquito in Amber",
        # A real preserved-specimen subject rendered with actual PBR
        # materials (amber's translucency, the insect's chitin) -- unlike
        # Fox (a flat-shaded low-poly toy), this one reads as a real object.
        "src": "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Assets/main/Models/MosquitoInAmber/glTF-Binary/MosquitoInAmber.glb",
        "alt": "A 3D model of a mosquito preserved in a block of amber, with realistic PBR materials",
        "orbit": "20deg 80deg 0.14m",
    },
    "virtual-city": {
        "label": "Houses (Virtual City)",
        "src": "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Assets/main/Models/VirtualCity/glTF-Binary/VirtualCity.glb",
        "alt": "A 3D model of a small block of low-poly houses and buildings",
        "orbit": "20deg 55deg 25m",
    },
    "barramundi-fish": {
        "label": "Barramundi Fish",
        "src": "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Assets/main/Models/BarramundiFish/glTF-Binary/BarramundiFish.glb",
        "alt": "A 3D model of a barramundi fish with realistic PBR scale textures",
        "orbit": "10deg 80deg 1.3m",
    },
    "shoe": {
        "label": "Shoe",
        "src": "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Assets/main/Models/MaterialsVariantsShoe/glTF-Binary/MaterialsVariantsShoe.glb",
        "alt": "A 3D model of a sneaker with realistic PBR materials",
        "orbit": "-30deg 75deg 0.4m",
    },
    "glass": {
        "label": "Glass",
        "src": "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Assets/main/Models/GlassHurricaneCandleHolder/glTF-Binary/GlassHurricaneCandleHolder.glb",
        "alt": "A 3D model of a real glass object with physically-based transparency and refraction",
        "orbit": "0deg 75deg 0.5m",
    },
    "car-concept": {
        "label": "Modern Car",
        # Khronos's own concept-car showcase model -- full PBR paint,
        # glass and chrome materials, same free/no-key CDN as the rest.
        "src": "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Assets/main/Models/CarConcept/glTF-Binary/CarConcept.glb",
        "alt": "A 3D model of a modern concept car with realistic PBR paint, glass and chrome materials",
        "orbit": "35deg 75deg 6m",
    },
}

TONE_MAPPINGS = ["neutral", "aces", "agx", "reinhard", "cineon", "linear", "none"]

# Show dimensions: 6 "dot" hotspots tracing a zigzag along 3 orthogonal
# edges through one shared corner (+X-Y+Z -> +X-Y-Z -> +X+Y-Z -> -X+Y-Z ->
# -X-Y-Z -> -X-Y+Z), each pair one edge apart, plus a "dim" label hotspot
# at each edge's midpoint. Positions start empty ("" -- not a real 3D
# coordinate) because _update_dimensions below repositions every one of
# them with model-viewer's own updateHotspot() once the actual model's
# bounding box is known; only their slot names, and which axis each edge
# runs along, are fixed ahead of time. children_classname drives the
# cyan-dot / label-pill look in model-viewer.css.
DIMENSION_HOTSPOTS = [
    {"slot": "hotspot-dot+X-Y+Z", "position": "0 0 0", "children_classname": "dot"},
    {"slot": "hotspot-dot+X-Y-Z", "position": "0 0 0", "children_classname": "dot"},
    {"slot": "hotspot-dot+X+Y-Z", "position": "0 0 0", "children_classname": "dot"},
    {"slot": "hotspot-dot-X+Y-Z", "position": "0 0 0", "children_classname": "dot"},
    {"slot": "hotspot-dot-X-Y-Z", "position": "0 0 0", "children_classname": "dot"},
    {"slot": "hotspot-dot-X-Y+Z", "position": "0 0 0", "children_classname": "dot"},
    {"slot": "hotspot-dim+X-Y", "position": "0 0 0", "children_classname": "dim"},
    {"slot": "hotspot-dim+X-Z", "position": "0 0 0", "children_classname": "dim"},
    {"slot": "hotspot-dim+Y-Z", "position": "0 0 0", "children_classname": "dim"},
    {"slot": "hotspot-dim-X-Z", "position": "0 0 0", "children_classname": "dim"},
    {"slot": "hotspot-dim-X-Y", "position": "0 0 0", "children_classname": "dim"},
]

DIMENSION_UNITS = [
    {"label": "cm", "value": "cm"},
    {"label": "mm", "value": "mm"},
    {"label": "m", "value": "m"},
    {"label": "in", "value": "in"},
    {"label": "ft", "value": "ft"},
]

_ID_PREFIX = "model-viewer-"

# Every dmc Button/ActionIcon under a .model-viewer-page ancestor is cyan
# -- see assets/model-viewer.css. Both entry points
# (pages/model-viewer.py and model_viewer/app.py) put this class on their
# outermost container, so it's page-wide rather than per-button here.
PAGE_CLASS = "model-viewer-page"

_RADIUS_RE = re.compile(r"^([\d.]+)(.*)$")


def _id(name):
    return f"{_ID_PREFIX}{name}"


def _default_target(model):
    return model.get("target", "auto auto auto")


def _scale_orbit_radius(orbit, factor):
    """Dolly in/out: scale just the radius (3rd) component of a cameraOrbit
    string, clamped so repeated zoom-in clicks can't collapse it to zero.
    """
    theta, phi, radius = orbit.split()
    match = _RADIUS_RE.match(radius)
    if not match:
        return orbit
    value, unit = match.groups()
    value = max(float(value) * factor, 0.05)
    return f"{theta} {phi} {value:.3g}{unit or 'm'}"


def build_model_viewer_showcase(height="70vh"):
    """Layout for the 3D model viewer playground. Registers its callbacks on
    import (module-level @callback, same as the rest of this app's pages) --
    import this module exactly once per running Dash app.
    """
    default_key = "damaged-helmet"
    default_model = MODELS[default_key]

    controls = dmc.Stack(
        [
            dmc.Select(
                id=_id("model-picker"),
                label="Model",
                data=[{"label": v["label"], "value": k} for k, v in MODELS.items()],
                value=default_key,
                clearable=False,
                allowDeselect=False,
                w="100%",
            ),
            dmc.Select(
                id=_id("tone-picker"),
                label="Tone mapping",
                data=[{"label": t, "value": t} for t in TONE_MAPPINGS],
                value="neutral",
                clearable=False,
                allowDeselect=False,
                w="100%",
            ),
            dmc.Stack(
                [
                    dmc.Text("Shadow intensity", size="sm", fw=500),
                    dmc.Slider(
                        id=_id("shadow-slider"),
                        min=0, max=2, step=0.1, value=1,
                        marks=[{"value": 0, "label": "0"}, {"value": 1, "label": "1"}, {"value": 2, "label": "2"}],
                    ),
                    # A little breathing room before the switches below --
                    # the "2" mark and the next row used to sit almost flush.
                    dmc.Space(h="sm"),
                ],
                gap=4,
            ),
            dmc.Switch(id=_id("ar-toggle"), label="AR button", checked=True, size="sm"),
            dmc.Switch(id=_id("controls-toggle"), label="Camera controls", checked=True, size="sm"),
            dmc.Group(
                [
                    dmc.Switch(id=_id("dims-toggle"), label="Show dimensions", checked=False, size="sm"),
                    dmc.Select(
                        id=_id("dims-units"),
                        data=DIMENSION_UNITS,
                        value="cm",
                        clearable=False,
                        allowDeselect=False,
                        w=70,
                        size="xs",
                    ),
                ],
                justify="space-between", gap="xs", wrap="nowrap",
            ),
            dmc.Button(
                "Reset camera", id=_id("reset-camera-btn"), n_clicks=0,
                leftSection=DashIconify(icon="mdi:camera-retake-outline", width=16),
                variant="filled", fullWidth=True,
            ),
            dmc.Tooltip(
                dcc.Upload(
                    id=_id("upload-texture"),
                    accept="image/png",
                    multiple=False,
                    children=dmc.Button(
                        "Upload texture (PNG)",
                        leftSection=DashIconify(icon="mdi:tray-arrow-up", width=16),
                        variant="filled", fullWidth=True,
                    ),
                    style={"width": "100%"},
                ),
                label=_UPLOAD_HINT,
                position="bottom",
                withArrow=True,
            ),
        ],
        gap="md",
        w=220,
        style={"flexShrink": 0},
    )

    viewer = dmc.Paper(
        id=_id("viewer-container"),
        children=[
            DashModelViewer(
                id=_id("viewer"),
                src=default_model["src"],
                alt=default_model["alt"],
                cameraControls=True,
                cameraOrbit=default_model["orbit"],
                cameraTarget=_default_target(default_model),
                ar=True,
                toneMapping="neutral",
                shadowIntensity=1,
                hotspots=[],
                style={"width": "100%", "height": "100%", "--poster-color": "transparent"},
            ),
            # Zoom in/out overlay -- cameraControls already lets you
            # scroll/pinch to zoom, but that gesture isn't obvious at a
            # glance, so this gives it an explicit, discoverable control too.
            dmc.Stack(
                [
                    dmc.ActionIcon(
                        DashIconify(icon="mdi:magnify-plus-outline", width=18),
                        id=_id("zoom-in-btn"), n_clicks=0,
                        variant="filled", size="lg", radius="xl",
                    ),
                    dmc.ActionIcon(
                        DashIconify(icon="mdi:magnify-minus-outline", width=18),
                        id=_id("zoom-out-btn"), n_clicks=0,
                        variant="filled", size="lg", radius="xl",
                    ),
                ],
                gap="xs",
                style={"position": "absolute", "right": 12, "bottom": 12, "zIndex": 5},
            ),
        ],
        withBorder=True,
        radius="md",
        style={
            "height": height, "flex": 1, "minWidth": 0, "overflow": "hidden",
            # Mid-gray, not near-black -- shadowIntensity renders a dark
            # contact shadow under the model, which has no visible contrast
            # against a near-black background.
            "background": "#5c5f66", "position": "relative",
        },
    )

    return dmc.Group(
        [
            controls, viewer,
            dcc.Store(id=_id("reset-camera-signal")),
            dcc.Store(id=_id("texture-signal")),
            dcc.Store(id=_id("dims-signal")),
        ],
        align="flex-start", gap="sm", wrap="nowrap",
    )


@callback(
    Output(_id("viewer"), "src"),
    Output(_id("viewer"), "alt"),
    Output(_id("viewer"), "cameraOrbit"),
    Output(_id("viewer"), "cameraTarget"),
    Input(_id("model-picker"), "value"),
    prevent_initial_call=True,
)
def _switch_model(model_key):
    model = MODELS[model_key]
    return model["src"], model["alt"], model["orbit"], _default_target(model)


@callback(
    Output(_id("viewer"), "cameraOrbit", allow_duplicate=True),
    Input(_id("zoom-in-btn"), "n_clicks"),
    Input(_id("zoom-out-btn"), "n_clicks"),
    State(_id("viewer"), "cameraOrbit"),
    State(_id("model-picker"), "value"),
    prevent_initial_call=True,
)
def _zoom(_n_in, _n_out, current_orbit, model_key):
    factor = 0.8 if ctx.triggered_id == _id("zoom-in-btn") else 1.25
    orbit = current_orbit or MODELS[model_key]["orbit"]
    return _scale_orbit_radius(orbit, factor)


@callback(
    Output(_id("viewer"), "toneMapping"),
    Input(_id("tone-picker"), "value"),
    prevent_initial_call=True,
)
def _set_tone_mapping(tone):
    return tone or no_update


@callback(
    Output(_id("viewer"), "shadowIntensity"),
    Input(_id("shadow-slider"), "value"),
    prevent_initial_call=True,
)
def _set_shadow_intensity(value):
    return value


@callback(
    Output(_id("viewer"), "ar"),
    Input(_id("ar-toggle"), "checked"),
    prevent_initial_call=True,
)
def _toggle_ar(checked):
    return checked


@callback(
    Output(_id("viewer"), "cameraControls"),
    Input(_id("controls-toggle"), "checked"),
    prevent_initial_call=True,
)
def _toggle_camera_controls(checked):
    return checked


# Reset needs to run clientside rather than as a normal @callback: once the
# user free-orbits the model with the mouse, model-viewer's live camera
# drifts away from the cameraOrbit *value* Dash last set, but that value
# itself hasn't changed -- so a server callback returning the same string
# is a no-op prop diff and the click does nothing. Setting the properties
# directly on the element and calling jumpCameraToGoal() forces the reset
# regardless of what the live (mouse-driven) camera has done since.
_RESET_MODELS_JSON = json.dumps(
    {key: {"orbit": model["orbit"], "target": _default_target(model)} for key, model in MODELS.items()}
)

clientside_callback(
    """
    function(n_clicks, model_key) {
        if (!n_clicks) { return window.dash_clientside.no_update; }
        const viewer = document.getElementById('""" + _id("viewer") + """');
        const models = """ + _RESET_MODELS_JSON + """;
        const model = models[model_key];
        if (!viewer || !model) { return window.dash_clientside.no_update; }
        viewer.cameraOrbit = model.orbit;
        viewer.cameraTarget = model.target;
        if (typeof viewer.jumpCameraToGoal === 'function') {
            viewer.jumpCameraToGoal();
        }
        return n_clicks;
    }
    """,
    Output(_id("reset-camera-signal"), "data"),
    Input(_id("reset-camera-btn"), "n_clicks"),
    State(_id("model-picker"), "value"),
    prevent_initial_call=True,
)


# An uploaded PNG needs to show up *on the model itself*, not as a poster
# (which model-viewer only ever displays before the model has loaded --
# useless once you're already looking at a loaded model) or as a flat 2D
# preview beside it. model-viewer's scripting API lets you swap a material's
# base-color texture live, so this paints the upload directly onto every
# material's surface -- genuinely "in the 3D", not a flat overlay.
clientside_callback(
    """
    async function(contents) {
        if (!contents) { return window.dash_clientside.no_update; }
        const viewer = document.getElementById('""" + _id("viewer") + """');
        if (!viewer || !viewer.model) { return window.dash_clientside.no_update; }
        try {
            const texture = await viewer.createTexture(contents);
            const materials = viewer.model.materials || [];
            materials.forEach(function(material) {
                const slot = material.pbrMetallicRoughness.baseColorTexture;
                if (slot) { slot.setTexture(texture); }
            });
        } catch (err) {
            console.error('model-viewer texture upload failed', err);
        }
        return contents;
    }
    """,
    Output(_id("texture-signal"), "data"),
    Input(_id("upload-texture"), "contents"),
    prevent_initial_call=True,
)


@callback(
    Output(_id("viewer"), "hotspots"),
    Input(_id("dims-toggle"), "checked"),
    prevent_initial_call=True,
)
def _toggle_dimension_hotspots(checked):
    """Only controls hotspot *presence* -- their actual 3D positions, edge
    labels and connecting lines are computed and drawn client-side, by
    _update_dimensions below, since that needs the live model's real
    bounding box (model-viewer's getDimensions()/getBoundingBoxCenter()),
    which Python has no access to.
    """
    return DIMENSION_HOTSPOTS if checked else []


_DOT_SLOTS_JSON = json.dumps([h["slot"] for h in DIMENSION_HOTSPOTS if h["children_classname"] == "dot"])
# Each edge connects two consecutive dots (indices into _DOT_SLOTS_JSON) --
# together the 5 edges trace the zigzag comment on DIMENSION_HOTSPOTS
# above -- and names which axis (and so which of the model's real x/y/z
# dimensions) that edge's length comes from.
_DIM_EDGES_JSON = json.dumps([
    {"slot": "hotspot-dim+X-Y", "from": 0, "to": 1, "axis": "z"},
    {"slot": "hotspot-dim+X-Z", "from": 1, "to": 2, "axis": "y"},
    {"slot": "hotspot-dim+Y-Z", "from": 2, "to": 3, "axis": "x"},
    {"slot": "hotspot-dim-X-Z", "from": 3, "to": 4, "axis": "y"},
    {"slot": "hotspot-dim-X-Y", "from": 4, "to": 5, "axis": "z"},
])
_UNIT_FACTORS_JSON = json.dumps({"m": 1, "cm": 100, "mm": 1000, "in": 39.3701, "ft": 3.28084})

# "Show dimensions" -- real measurements, not guessed ones: positions every
# DIMENSION_HOTSPOTS dot at an actual bounding-box corner via model-viewer's
# updateHotspot() (getDimensions()/getBoundingBoxCenter(), both in meters),
# writes each edge's length into its "dim" hotspot as text, and draws an
# SVG line through the 6 dots on top of the model -- queryHotspot() gives
# each dot's live on-screen (canvas) position, which a 'camera-change'
# listener keeps re-reading so the line tracks the model while the user
# orbits. Runs on model switch too (awaiting model-viewer's own `load`
# event if the new model isn't ready yet, same pattern as the texture
# upload and reset-camera callbacks above) and re-fires whenever Python
# updates the hotspots prop, so newly-added dots have something to attach
# the line to. Only one 'camera-change' listener is ever live on the
# element -- each run replaces the previous one via the viewer's own
# _dimsRedraw property rather than piling listeners up.
clientside_callback(
    """
    function(checked, unit, _hotspots, _modelKey) {
        const viewer = document.getElementById('""" + _id("viewer") + """');
        const container = document.getElementById('""" + _id("viewer-container") + """');
        if (!viewer || !container) { return window.dash_clientside.no_update; }

        if (viewer._dimsRedraw) {
            viewer.removeEventListener('camera-change', viewer._dimsRedraw);
            viewer._dimsRedraw = null;
        }
        let svg = container.querySelector('svg.model-viewer-dims-overlay');
        if (!checked) {
            if (svg) { svg.remove(); }
            return window.dash_clientside.no_update;
        }

        const DOTS = """ + _DOT_SLOTS_JSON + """;
        const EDGES = """ + _DIM_EDGES_JSON + """;
        const UNIT_FACTORS = """ + _UNIT_FACTORS_JSON + """;

        function drawLines() {
            if (!svg) {
                svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
                svg.setAttribute('class', 'model-viewer-dims-overlay');
                container.appendChild(svg);
            }
            let d = '';
            DOTS.forEach(function(slot, i) {
                const q = typeof viewer.queryHotspot === 'function' ? viewer.queryHotspot(slot) : null;
                if (!q || !q.canvasPosition) { return; }
                d += (i === 0 ? 'M ' : 'L ') + q.canvasPosition.x + ' ' + q.canvasPosition.y + ' ';
            });
            svg.innerHTML = '<path d="' + d + '" />';
        }

        function place() {
            if (!viewer.model || typeof viewer.getDimensions !== 'function') { return; }
            const dim = viewer.getDimensions();
            const c = viewer.getBoundingBoxCenter();
            const hx = dim.x / 2, hy = dim.y / 2, hz = dim.z / 2;
            const corners = [
                {x: c.x + hx, y: c.y - hy, z: c.z + hz},
                {x: c.x + hx, y: c.y - hy, z: c.z - hz},
                {x: c.x + hx, y: c.y + hy, z: c.z - hz},
                {x: c.x - hx, y: c.y + hy, z: c.z - hz},
                {x: c.x - hx, y: c.y - hy, z: c.z - hz},
                {x: c.x - hx, y: c.y - hy, z: c.z + hz},
            ];
            DOTS.forEach(function(slot, i) {
                const p = corners[i];
                viewer.updateHotspot({name: slot, position: p.x + ' ' + p.y + ' ' + p.z});
            });
            const factor = UNIT_FACTORS[unit] || UNIT_FACTORS.cm;
            const axisLength = {x: dim.x, y: dim.y, z: dim.z};
            EDGES.forEach(function(edge) {
                const a = corners[edge.from], b = corners[edge.to];
                const mid = {x: (a.x + b.x) / 2, y: (a.y + b.y) / 2, z: (a.z + b.z) / 2};
                viewer.updateHotspot({name: edge.slot, position: mid.x + ' ' + mid.y + ' ' + mid.z});
                const el = viewer.querySelector('[slot="' + edge.slot + '"]');
                if (el) { el.textContent = (axisLength[edge.axis] * factor).toFixed(1) + ' ' + unit; }
            });
            drawLines();
        }

        viewer._dimsRedraw = drawLines;
        viewer.addEventListener('camera-change', viewer._dimsRedraw);
        viewer.addEventListener('load', place, {once: true});
        if (viewer.model) { place(); }

        return window.dash_clientside.no_update;
    }
    """,
    Output(_id("dims-signal"), "data"),
    Input(_id("dims-toggle"), "checked"),
    Input(_id("dims-units"), "value"),
    Input(_id("viewer"), "hotspots"),
    Input(_id("model-picker"), "value"),
    prevent_initial_call=True,
)
