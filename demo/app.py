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
    """Settings for loading models, VAEs, etc."""
    model_type: Literal["SD 1.5", "SDXL", "Pony", "Custom"] = field(default="SDXL", metadata={"component": "dropdown", "label": "Base Model"})
    custom_model_path: str = field(default="/path/to/default.safetensors", metadata={"label": "Custom Model Path", "interactive_if": {"field": "model_type", "value": "Custom"}})
    vae_path: str = field(default="", metadata={"label": "VAE Path (optional)"})

@dataclass
class SamplingSettings:
    """Settings for the image sampling process."""
    sampler_name: Literal["Euler", "Euler a", "DPM++ 2M Karras", "UniPC"] = field(default="DPM++ 2M Karras", metadata={"component": "dropdown", "label": "Sampler"})
    steps: int = field(default=25, metadata={"component": "slider", "minimum": 1, "maximum": 150, "step": 1})
    cfg_scale: float = field(default=7.0, metadata={"component": "slider", "minimum": 1.0, "maximum": 30.0, "step": 0.5})

@dataclass
class RenderConfig:
    """Main configuration object for rendering, grouping all settings."""
    seed: int = field(default=-1, metadata={"component": "number_integer", "label": "Seed (-1 for random)"})
    model: ModelSettings = field(default_factory=ModelSettings)
    sampling: SamplingSettings = field(default_factory=SamplingSettings)

@dataclass
class Lighting:
    """Lighting settings for the environment."""
    sun_intensity: float = field(default=1.0, metadata={"component": "slider", "minimum": 0, "maximum": 5, "step": 0.1})
    color: str = field(default="#FFDDBB", metadata={"component": "colorpicker", "label": "Sun Color"})

@dataclass
class EnvironmentConfig:
    """Main configuration for the environment."""
    background: Literal["Sky", "Color", "Image"] = field(default="Sky", metadata={"component": "dropdown"})
    lighting: Lighting = field(default_factory=Lighting)

# Dataclasses for the Flyout Demo
@dataclass
class EulerSettings:
    """Settings specific to the Euler sampler."""
    s_churn: float = field(default=0.0, metadata={"component": "slider", "minimum": 0.0, "maximum": 1.0, "step": 0.01})

@dataclass
class DPM_Settings:
    """Settings specific to DPM samplers."""
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
head_script = f"""
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
"""

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