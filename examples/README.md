# Standalone apps

Every showcase on the documentation site also runs on its own. Each entry
point here is a complete Dash app with its own `Dash(__name__)` instance and
port — nothing in this folder imports `pages/`, `components/` or `run.py`.

Run them **from the repo root**:

| App | Command | Port | Imports its layout from |
|---|---|---|---|
| Color Picker | `python examples/color_picker_app.py` | 8560 | — (single file, self-contained) |
| Dash Flow Playground | `python examples/dash_flow_app.py` | 8070 | `docs/dash_flow/playground.py` |
| Excalidraw KPI Mockup | `python examples/excalidraw_app.py` | 8060 | `docs/excalidraw/kpi_mockup.py` |
| FlexLayout Playground | `python examples/flexlayout_app.py` | 8080 | `docs/flex_layout/showcase.py` |
| 3D Model Viewer | `python examples/model_viewer_app.py` | 8081 | `docs/model_viewer/showcase.py` |
| Roamly | `python examples/roamly/app.py` | 8870 | its own `pages/` and `data.py` |

## How the sharing works

The docs page and the standalone app of a showcase render the **same
component**. The builder (`build_flow_playground()`, `build_excalidraw()`,
...) and its callbacks live in the showcase's `docs/<slug>/` folder, where
the docs page embeds the module-level `component` through `.. exec::`; the
standalone app imports the same builder. That is why importing a docs
module never instantiates a second `Dash()` app, and why the two entry
points can never drift apart.

Two lines at the top of each app make that work from inside `examples/`:

```python
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))          # so `docs.<slug>` resolves

app = Dash(__name__, assets_folder=str(REPO_ROOT / "assets"))
```

The second line serves the repo-root `assets/` folder — the per-showcase
stylesheets (`assets/flexlayout.css`, `assets/model-viewer.css`,
`assets/excalidraw-*.css`, `assets/dash-flow-playground.css`) are scoped to
each showcase's own wrapper class or id, so one copy covers both entry
points.

## Roamly

Roamly is the exception: a full multi-page app (its own `AppShell`, theme,
dark-mode toggle and page router) rather than a single component, so it is
a self-contained package with its own `requirements.txt` and can be deployed
on its own (`render.yaml` gives it a service with `rootDir: examples/roamly`).
The docs page's three Roamly sections import their listing data from
`examples/roamly/data.py`, so the site and the standalone app always show
the same stays.

```bash
pip install -r examples/roamly/requirements.txt
python examples/roamly/app.py
```
