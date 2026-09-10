---
name: 3D Model Viewer
description: A dash-model-viewer playground — Google's model-viewer web component wrapped for Dash. Switch between eight glTF sample models, orbit and zoom, tweak tone mapping and shadows, and try AR on a phone.
endpoint: /model-viewer
package: dash_model_viewer
icon: mdi:cube-outline
category: Showcases
order: 5
---

.. llms_copy::3D Model Viewer

.. toc::

### Introduction

A playground for [dash-model-viewer](https://modelviewer.2plot.dev) —
2plot.ai's Dash wrapper around Google's
[model-viewer](https://modelviewer.dev) web component. Eight public glTF
sample models (Khronos's own demo assets, hosted on their CDN — no local
files, no API key) swap in through the picker on the left, each restoring its
own starting camera orbit.

---

### Live demo

Drag to orbit, scroll or use the magnifier buttons to zoom, and try the AR
button on a phone:

.. exec::docs.model_viewer.showcase
    :code: false

---

### How it works

Every control maps onto one `<model-viewer>` prop, wired straight through
with a one-line callback each — there is no client state beyond what the
component itself holds:

- **Model** swaps `src`, `alt`, `cameraOrbit` and `cameraTarget` together, so
  each model comes up framed the way it was authored.
- **Tone mapping** and **Shadow intensity** are the element's own lighting
  props (`toneMapping`, `shadowIntensity`).
- **AR button** and **Camera controls** toggle the `ar` and `cameraControls`
  props directly.
- **Zoom in / out** scale just the radius component of the `cameraOrbit`
  string, clamped so repeated clicks can never collapse it to zero.

```python
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
```

Two controls have to run **clientside**, and the reasons are worth knowing:

- **Reset camera.** Once you free-orbit the model with the mouse,
  model-viewer's live camera drifts away from the `cameraOrbit` value Dash
  last set — but that value itself has not changed, so a server callback
  returning the same string is a no-op prop diff and the click does nothing.
  The clientside callback sets the properties directly on the element and
  calls `jumpCameraToGoal()`, which forces the reset regardless of what the
  mouse has done since.
- **Upload texture (PNG).** An uploaded image needs to show up *on the
  model*, not as a poster. model-viewer's scripting API can swap a material's
  base-colour texture live, so the callback calls `viewer.createTexture()`
  and paints the upload onto every material's surface.

The cyan accent on the buttons, slider and switches comes from
`assets/model-viewer.css`, scoped to the `.model-viewer-page` wrapper.

---

### Source

.. source::docs/model_viewer/showcase.py
    :defaultExpanded: false
    :withExpandedButton: true

---

### Standalone app

The same viewer runs on its own, with its own `Dash(__name__)` instance and
port:

```bash
python examples/model_viewer_app.py
```

Serves on **http://localhost:8081**.

.. source::examples/model_viewer_app.py
    :defaultExpanded: false
    :withExpandedButton: true
