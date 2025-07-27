
import gradio as gr
from app import demo as app
import os

_docs = {'PropertySheet': {'description': 'A Gradio component that renders a dynamic UI from a Python dataclass instance.\nIt allows for nested settings and automatically infers input types.', 'members': {'__init__': {'value': {'type': 'typing.Optional[typing.Any][Any, None]', 'default': 'None', 'description': 'The initial dataclass instance to render.'}, 'label': {'type': 'str | None', 'default': 'None', 'description': 'The main label for the component, displayed in the accordion header.'}, 'root_label': {'type': 'str', 'default': '"General"', 'description': 'The label for the root group of properties.'}, 'show_group_name_only_one': {'type': 'bool', 'default': 'True', 'description': 'If True, only the group name is shown when there is a single group.'}, 'disable_accordion': {'type': 'bool', 'default': 'False', 'description': 'If True, disables the accordion functionality.'}, 'visible': {'type': 'bool', 'default': 'True', 'description': 'If False, the component will be hidden.'}, 'open': {'type': 'bool', 'default': 'True', 'description': 'If False, the accordion will be collapsed by default.'}, 'elem_id': {'type': 'str | None', 'default': 'None', 'description': 'An optional string that is assigned as the id of this component in the DOM.'}, 'scale': {'type': 'int | None', 'default': 'None', 'description': 'The relative size of the component in its container.'}, 'width': {'type': 'int | str | None', 'default': 'None', 'description': 'The width of the component in pixels.'}, 'height': {'type': 'int | str | None', 'default': 'None', 'description': "The maximum height of the component's content area in pixels before scrolling."}, 'min_width': {'type': 'int | None', 'default': 'None', 'description': 'The minimum width of the component in pixels.'}, 'container': {'type': 'bool', 'default': 'True', 'description': 'If True, wraps the component in a container with a background.'}, 'elem_classes': {'type': 'list[str] | str | None', 'default': 'None', 'description': 'An optional list of strings that are assigned as the classes of this component in the DOM.'}}, 'postprocess': {'value': {'type': 'Any', 'description': 'The dataclass instance to process.'}}, 'preprocess': {'return': {'type': 'Any', 'description': 'A new, updated instance of the dataclass.'}, 'value': None}}, 'events': {'change': {'type': None, 'default': None, 'description': ''}, 'input': {'type': None, 'default': None, 'description': ''}, 'expand': {'type': None, 'default': None, 'description': ''}, 'collapse': {'type': None, 'default': None, 'description': ''}}}, '__meta__': {'additional_interfaces': {}, 'user_fn_refs': {'PropertySheet': []}}}

abs_path = os.path.join(os.path.dirname(__file__), "css.css")

with gr.Blocks(
    css=abs_path,
    theme=gr.themes.Default(
        font_mono=[
            gr.themes.GoogleFont("Inconsolata"),
            "monospace",
        ],
    ),
) as demo:
    gr.Markdown(
"""
# `gradio_propertysheet`

<div style="display: flex; gap: 7px;">
<a href="https://pypi.org/project/gradio_propertysheet/" target="_blank"><img alt="PyPI - Version" src="https://img.shields.io/pypi/v/gradio_propertysheet"></a>  
</div>

Property sheet
""", elem_classes=["md-custom"], header_links=True)
    app.render()
    gr.Markdown(
"""
## Installation

```bash
pip install gradio_propertysheet
```

## Usage

```python
import os
from pathlib import Path
import gradio as gr
from dataclasses import dataclass, field, asdict
from typing import Literal
from gradio_propertysheet import PropertySheet

# --- 1. Dataclass Definitions ---

# Dataclasses for the Original Sidebar Demo
@dataclass
class ModelSettings:
    \"\"\"Settings for loading models, VAEs, etc.\"\"\"
    model_type: Literal["SD 1.5", "SDXL", "Pony", "Custom"] = field(default="SDXL", metadata={"component": "dropdown", "label": "Base Model"})
    custom_model_path: str = field(default="/path/to/default.safetensors", metadata={"label": "Custom Model Path", "interactive_if": {"field": "model_type", "value": "Custom"}})
    vae_path: str = field(default="", metadata={"label": "VAE Path (optional)"})

@dataclass
class SamplingSettings:
    \"\"\"Settings for the image sampling process.\"\"\"
    sampler_name: Literal["Euler", "Euler a", "DPM++ 2M Karras", "UniPC"] = field(default="DPM++ 2M Karras", metadata={"component": "dropdown", "label": "Sampler"})
    steps: int = field(default=25, metadata={"component": "slider", "minimum": 1, "maximum": 150, "step": 1})
    cfg_scale: float = field(default=7.0, metadata={"component": "slider", "minimum": 1.0, "maximum": 30.0, "step": 0.5})

@dataclass
class RenderConfig:
    \"\"\"Main configuration object for rendering, grouping all settings.\"\"\"
    seed: int = field(default=-1, metadata={"component": "number_integer", "label": "Seed (-1 for random)"})
    model: ModelSettings = field(default_factory=ModelSettings)
    sampling: SamplingSettings = field(default_factory=SamplingSettings)

@dataclass
class Lighting:
    \"\"\"Lighting settings for the environment.\"\"\"
    sun_intensity: float = field(default=1.0, metadata={"component": "slider", "minimum": 0, "maximum": 5, "step": 0.1})
    color: str = field(default="#FFDDBB", metadata={"component": "colorpicker", "label": "Sun Color"})

@dataclass
class EnvironmentConfig:
    \"\"\"Main configuration for the environment.\"\"\"
    background: Literal["Sky", "Color", "Image"] = field(default="Sky", metadata={"component": "dropdown"})
    lighting: Lighting = field(default_factory=Lighting)

# Dataclasses for the Flyout Demo
@dataclass
class EulerSettings:
    \"\"\"Settings specific to the Euler sampler.\"\"\"
    s_churn: float = field(default=0.0, metadata={"component": "slider", "minimum": 0.0, "maximum": 1.0, "step": 0.01})

@dataclass
class DPM_Settings:
    \"\"\"Settings specific to DPM samplers.\"\"\"
    karras_style: bool = field(default=True, metadata={"label": "Use Karras Sigma Schedule"})

# --- 2. Data Mappings and Initial Instances ---

# Data for Original Sidebar Demo
initial_render_config = RenderConfig()
initial_env_config = EnvironmentConfig()

# Data for Flyout Demo
sampler_settings_map_py = {"Euler": EulerSettings(), "DPM++ 2M Karras": DPM_Settings(), "UniPC": None}
model_settings_map_py = {"SDXL 1.0": DPM_Settings(), "Stable Diffusion 1.5": EulerSettings(), "Pony": None}

# --- 3. CSS and JavaScript Loading ---

# Load external CSS file if it exists
script_path = Path(__file__).resolve()
script_dir = script_path.parent
css_path = script_dir / "custom.css"
flyout_css = ""
if css_path.exists():
    with open(css_path, "r", encoding="utf8") as file:
        flyout_css = file.read()

# JavaScript for positioning the flyout panel
head_script = f\"\"\"
<script>
    function position_flyout(anchorId) {{
        setTimeout(() => {{
            const anchorRow = document.getElementById(anchorId).closest('.fake-input-container');
            const flyoutElem = document.getElementById('flyout_panel');
            
            if (anchorRow && flyoutElem && flyoutElem.style.display !== 'none') {{
                const anchorRect = anchorRow.getBoundingClientRect();
                const containerRect = anchorRow.closest('.flyout-context-area').getBoundingClientRect();
                
                const flyoutWidth = flyoutElem.offsetWidth;
                const flyoutHeight = flyoutElem.offsetHeight;

                const topPosition = (anchorRect.top - containerRect.top) + (anchorRect.height / 2) - (flyoutHeight / 2);
                const leftPosition = (anchorRect.left - containerRect.left) + (anchorRect.width / 2) - (flyoutWidth / 2);

                flyoutElem.style.top = `${{topPosition}}px`;
                flyoutElem.style.left = `${{leftPosition}}px`;
            }}
        }}, 50);
    }}
</script>
\"\"\"

# --- 4. Gradio App Build ---
with gr.Blocks(css=flyout_css, head=head_script, title="PropertySheet Demos") as demo:
    gr.Markdown("# PropertySheet Component Demos")
    
    with gr.Tabs():
        with gr.TabItem("Original Sidebar Demo"):
            gr.Markdown("An example of using the `PropertySheet` component as a traditional sidebar for settings.")
            
            render_state = gr.State(value=initial_render_config)
            env_state = gr.State(value=initial_env_config)
            sidebar_visible = gr.State(False)
            
            with gr.Row():
                with gr.Column(scale=3):            
                    generate = gr.Button("Show Settings", variant="primary")
                    with gr.Row():
                        output_render_json = gr.JSON(label="Live Render State")
                        output_env_json = gr.JSON(label="Live Environment State")

                with gr.Column(scale=1):
                    render_sheet = PropertySheet(
                        value=initial_render_config,
                        label="Render Settings",
                        width=400,
                        height=550,
                        visible=False,
                        root_label="Generator"       
                    )
                    environment_sheet = PropertySheet(
                        value=initial_env_config,
                        label="Environment Settings",
                        width=400,
                        open=False,
                        visible=False,
                        root_label="General"              
                    )

            def change_visibility(is_visible, render_cfg, env_cfg):
                new_visibility = not is_visible
                button_text = "Hide Settings" if new_visibility else "Show Settings"
                return (
                    new_visibility,
                    gr.update(visible=new_visibility, value=render_cfg),
                    gr.update(visible=new_visibility, value=env_cfg),
                    gr.update(value=button_text)
                )
            
            def handle_render_change(updated_config: RenderConfig, current_state: RenderConfig):
                if updated_config is None:
                    return current_state, asdict(current_state), current_state
                if updated_config.model.model_type != "Custom":
                    updated_config.model.custom_model_path = "/path/to/default.safetensors"
                return updated_config, asdict(updated_config), updated_config

            def handle_env_change(updated_config: EnvironmentConfig, current_state: EnvironmentConfig):
                if updated_config is None:
                    return current_state, asdict(current_state), current_state
                return updated_config, asdict(updated_config), current_state

            generate.click(
                fn=change_visibility,
                inputs=[sidebar_visible, render_state, env_state],
                outputs=[sidebar_visible, render_sheet, environment_sheet, generate]
            )
            
            render_sheet.change(
                fn=handle_render_change,
                inputs=[render_sheet, render_state],
                outputs=[render_sheet, output_render_json, render_state]
            )
            
            environment_sheet.change(
                fn=handle_env_change,
                inputs=[environment_sheet, env_state],
                outputs=[environment_sheet, output_env_json, env_state]
            )
           
            demo.load(
                fn=lambda r_cfg, e_cfg: (asdict(r_cfg), asdict(e_cfg)),
                inputs=[render_state, env_state],
                outputs=[output_render_json, output_env_json]
            )

        with gr.TabItem("Flyout Popup Demo"):
            gr.Markdown("An example of attaching a `PropertySheet` as a flyout panel to other components.")
            
            flyout_visible = gr.State(False)
            active_anchor_id = gr.State(None)

            with gr.Column(elem_classes=["flyout-context-area"]):
                with gr.Row(elem_classes=["fake-input-container", "no-border-dropdown"]):
                    sampler_dd = gr.Dropdown(choices=list(sampler_settings_map_py.keys()), label="Sampler", value="Euler", elem_id="sampler_dd", scale=10)
                    sampler_ear_btn = gr.Button("⚙️", elem_id="sampler_ear_btn", scale=1, elem_classes=["integrated-ear-btn"])
                
                with gr.Row(elem_classes=["fake-input-container", "no-border-dropdown"]):
                    model_dd = gr.Dropdown(choices=list(model_settings_map_py.keys()), label="Model", value="SDXL 1.0", elem_id="model_dd", scale=10)
                    model_ear_btn = gr.Button("⚙️", elem_id="model_ear_btn", scale=1, elem_classes=["integrated-ear-btn"])

                with gr.Column(visible=False, elem_id="flyout_panel", elem_classes=["flyout-sheet"]) as flyout_panel:
                    with gr.Row(elem_classes=["close-btn-row"]):
                        close_btn = gr.Button("×", elem_classes=["flyout-close-btn"])
                    flyout_sheet = PropertySheet(visible=False, container=False, label="Settings", show_group_name_only_one=False, disable_accordion=True)

            def handle_flyout_toggle(is_vis, current_anchor, clicked_dropdown_id, settings_obj):
                if is_vis and current_anchor == clicked_dropdown_id:
                    return False, None, gr.update(visible=False), gr.update(visible=False, value=None)
                else:
                    return True, clicked_dropdown_id, gr.update(visible=True), gr.update(visible=True, value=settings_obj)

            def update_ear_visibility(selection, settings_map):
                has_settings = settings_map.get(selection) is not None
                return gr.update(visible=has_settings)

            def on_flyout_change(updated_settings, active_id, sampler_val, model_val):
                if updated_settings is None or active_id is None: return
                if active_id == sampler_dd.elem_id:
                    sampler_settings_map_py[sampler_val] = updated_settings
                elif active_id == model_dd.elem_id:
                    model_settings_map_py[model_val] = updated_settings
            
            def close_the_flyout():
                return False, None, gr.update(visible=False), gr.update(visible=False, value=None)
                
            sampler_dd.change(
                fn=lambda sel: update_ear_visibility(sel, sampler_settings_map_py),
                inputs=[sampler_dd],
                outputs=[sampler_ear_btn]
            ).then(fn=close_the_flyout, outputs=[flyout_visible, active_anchor_id, flyout_panel, flyout_sheet])
            
            sampler_ear_btn.click(
                fn=lambda is_vis, anchor, sel: handle_flyout_toggle(is_vis, anchor, sampler_dd.elem_id, sampler_settings_map_py.get(sel)),
                inputs=[flyout_visible, active_anchor_id, sampler_dd],
                outputs=[flyout_visible, active_anchor_id, flyout_panel, flyout_sheet]
            ).then(fn=None, inputs=None, outputs=None, js=f"() => position_flyout('{sampler_dd.elem_id}')")

            model_dd.change(
                fn=lambda sel: update_ear_visibility(sel, model_settings_map_py),
                inputs=[model_dd],
                outputs=[model_ear_btn]
            ).then(fn=close_the_flyout, outputs=[flyout_visible, active_anchor_id, flyout_panel, flyout_sheet])
            
            model_ear_btn.click(
                fn=lambda is_vis, anchor, sel: handle_flyout_toggle(is_vis, anchor, model_dd.elem_id, model_settings_map_py.get(sel)),
                inputs=[flyout_visible, active_anchor_id, model_dd],
                outputs=[flyout_visible, active_anchor_id, flyout_panel, flyout_sheet]
            ).then(fn=None, inputs=None, outputs=None, js=f"() => position_flyout('{model_dd.elem_id}')")
            
            flyout_sheet.change(
                fn=on_flyout_change,
                inputs=[flyout_sheet, active_anchor_id, sampler_dd, model_dd],
                outputs=None
            )

            close_btn.click(
                fn=close_the_flyout,
                inputs=None,
                outputs=[flyout_visible, active_anchor_id, flyout_panel, flyout_sheet]
            )

            def initial_flyout_setup(sampler_val, model_val):
                return {
                    sampler_ear_btn: update_ear_visibility(sampler_val, sampler_settings_map_py),
                    model_ear_btn: update_ear_visibility(model_val, model_settings_map_py)
                }
            demo.load(fn=initial_flyout_setup, inputs=[sampler_dd, model_dd], outputs=[sampler_ear_btn, model_ear_btn])

if __name__ == "__main__":
    demo.launch()
```
""", elem_classes=["md-custom"], header_links=True)


    gr.Markdown("""
## `PropertySheet`

### Initialization
""", elem_classes=["md-custom"], header_links=True)

    gr.ParamViewer(value=_docs["PropertySheet"]["members"]["__init__"], linkify=[])


    gr.Markdown("### Events")
    gr.ParamViewer(value=_docs["PropertySheet"]["events"], linkify=['Event'])




    gr.Markdown("""

### User function

The impact on the users predict function varies depending on whether the component is used as an input or output for an event (or both).

- When used as an Input, the component only impacts the input signature of the user function.
- When used as an output, the component only impacts the return signature of the user function.

The code snippet below is accurate in cases where the component is used as both an input and an output.

- **As input:** Is passed, a new, updated instance of the dataclass.
- **As output:** Should return, the dataclass instance to process.

 ```python
def predict(
    value: Any
) -> Any:
    return value
```
""", elem_classes=["md-custom", "PropertySheet-user-fn"], header_links=True)




    demo.load(None, js=r"""function() {
    const refs = {};
    const user_fn_refs = {
          PropertySheet: [], };
    requestAnimationFrame(() => {

        Object.entries(user_fn_refs).forEach(([key, refs]) => {
            if (refs.length > 0) {
                const el = document.querySelector(`.${key}-user-fn`);
                if (!el) return;
                refs.forEach(ref => {
                    el.innerHTML = el.innerHTML.replace(
                        new RegExp("\\b"+ref+"\\b", "g"),
                        `<a href="#h-${ref.toLowerCase()}">${ref}</a>`
                    );
                })
            }
        })

        Object.entries(refs).forEach(([key, refs]) => {
            if (refs.length > 0) {
                const el = document.querySelector(`.${key}`);
                if (!el) return;
                refs.forEach(ref => {
                    el.innerHTML = el.innerHTML.replace(
                        new RegExp("\\b"+ref+"\\b", "g"),
                        `<a href="#h-${ref.toLowerCase()}">${ref}</a>`
                    );
                })
            }
        })
    })
}

""")

demo.launch()
