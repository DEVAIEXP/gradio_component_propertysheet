import gradio as gr
from dataclasses import dataclass, field, asdict
from typing import Literal
from gradio_propertysheet import PropertySheet

# --- Main Configuration Dataclasses for the "Render Settings" Sheet ---

@dataclass
class ModelSettings:
    """Settings for loading models, VAEs, etc."""
    model_type: Literal["SD 1.5", "SDXL", "Pony", "Custom"] = field(
        default="SDXL",
        metadata={"component": "dropdown", "label": "Base Model"}
    )
    custom_model_path: str = field(
        default="/path/to/default.safetensors",
        metadata={"label": "Custom Model Path", "interactive_if": {"field": "model_type", "value": "Custom"}}
    )
    vae_path: str = field(
        default="",
        metadata={"label": "VAE Path (optional)"}
    )

@dataclass
class SamplingSettings:
    """Settings for the image sampling process."""
    sampler_name: Literal["Euler", "Euler a", "DPM++ 2M Karras", "UniPC"] = field(
        default="DPM++ 2M Karras",
        metadata={"component": "dropdown", "label": "Sampler", "help": "The algorithm for the diffusion process."}
    )
    steps: int = field(
        default=25,
        metadata={"component": "slider", "minimum": 1, "maximum": 150, "step": 1, "label": "Sampling Steps", "help": "More steps can improve quality."}
    )
    cfg_scale: float = field(
        default=7.0,
        metadata={"component": "slider", "minimum": 1.0, "maximum": 30.0, "step": 0.5, "label": "CFG Scale", "help": "How strongly the prompt is adhered to."}
    )

@dataclass
class ImageSettings:
    """Settings for image dimensions."""
    width: int = field(
        default=1024,
        metadata={"component": "slider", "minimum": 512, "maximum": 2048, "step": 64, "label": "Image Width"}
    )
    height: int = field(
        default=1024,
        metadata={"component": "slider", "minimum": 512, "maximum": 2048, "step": 64, "label": "Image Height"}
    )

@dataclass
class PostprocessingSettings:
    """Settings for image post-processing effects."""
    restore_faces: bool = field(
        default=True,
        metadata={"label": "Restore Faces", "help": "Use a secondary model to fix distorted faces."}
    )
    enable_hr: bool = field(
        default=False,
        metadata={"label": "Hires. fix", "help": "Enable a second pass at a higher resolution."}
    )
    denoising_strength: float = field(
        default=0.45,
        metadata={"component": "slider", "minimum": 0.0, "maximum": 1.0, "step": 0.01, "label": "Denoising Strength", "interactive_if": {"field": "enable_hr", "value": True}}
    )

@dataclass
class AdvancedSettings:
    """Advanced and rarely changed settings."""
    clip_skip: int = field(
        default=2,
        metadata={"component": "slider", "minimum": 1, "maximum": 12, "step": 1, "label": "CLIP Skip", "help": "Skip final layers of the text encoder."}
    )
    noise_schedule: Literal["Default", "Karras", "Exponential"] = field(
        default="Karras",
        metadata={"component": "dropdown", "label": "Noise Schedule"}
    )
    do_not_scale_cond_uncond: bool = field(
        default=False,
        metadata={"label": "Do not scale cond/uncond"}
    )

@dataclass
class ScriptSettings:
    """Settings for automation scripts like X/Y/Z plots."""
    script_name: Literal["None", "Prompt matrix", "X/Y/Z plot"] = field(
        default="None",
        metadata={"component": "dropdown", "label": "Script"}
    )
    x_values: str = field(
        default="-1, 10, 20",
        metadata={"label": "X axis values", "interactive_if": {"field": "script_name", "value": "X/Y/Z plot"}}
    )
    y_values: str = field(
        default="",
        metadata={"label": "Y axis values", "interactive_if": {"field": "script_name", "value": "X/Y/Z plot"}}
    )

@dataclass
class RenderConfig:
    """Main configuration object for rendering, grouping all settings."""
    seed: int = field(
        default=-1,
        metadata={"component": "number_integer", "label": "Seed (-1 for random)", "help": "The random seed for generation."}
    )
    batch_size: int = field(
        default=1,
        metadata={"component": "slider", "minimum": 1, "maximum": 8, "step": 1, "label": "Batch Size"}
    )
    # Nested groups
    model: ModelSettings = field(default_factory=ModelSettings)
    sampling: SamplingSettings = field(default_factory=SamplingSettings)
    image: ImageSettings = field(default_factory=ImageSettings)
    postprocessing: PostprocessingSettings = field(default_factory=PostprocessingSettings)
    scripts: ScriptSettings = field(default_factory=ScriptSettings)
    advanced: AdvancedSettings = field(default_factory=AdvancedSettings)

# --- Configuration for the Secondary Property Sheet ---

@dataclass
class Lighting:
    """Lighting settings for the environment."""
    sun_intensity: float = field(default=1.0, metadata={"component": "slider", "minimum": 0, "maximum": 5, "step": 0.1})
    ambient_occlusion: bool = field(default=True, metadata={"label": "Ambient Occlusion"})
    color: str = field(default="#FFDDBB", metadata={"component": "colorpicker", "label": "Sun Color"})

@dataclass
class EnvironmentConfig:
    """Main configuration for the environment."""
    background: Literal["Sky", "Color", "Image"] = field(default="Sky", metadata={"component": "dropdown"})
    lighting: Lighting = field(default_factory=Lighting)


# --- Initial Instances ---
initial_render_config = RenderConfig()
initial_env_config = EnvironmentConfig()

# --- Gradio Application ---
with gr.Blocks(title="PropertySheet Demo") as demo:
    gr.Markdown("# PropertySheet Component Demo")
    gr.Markdown("An example of a realistic application layout using the `PropertySheet` component as a sidebar for settings.")

    with gr.Row():
        # Main content area on the left
        with gr.Column(scale=3):
            gr.Image(label="Main Viewport", height=500, value=None)
            gr.Textbox(label="AI Prompt", lines=3, placeholder="Enter your prompt here...")
            gr.Button("Generate", variant="primary")
            with gr.Row():
                output_render_json = gr.JSON(label="Live Render State")
                output_env_json = gr.JSON(label="Live Environment State")

        # Sidebar with Property Sheets on the right
        with gr.Column(scale=1):
            render_sheet = PropertySheet(
                value=initial_render_config, 
                label="Render Settings",
                width=400,
                height=550  # Set a fixed height to demonstrate internal scrolling
            )
            environment_sheet = PropertySheet(
                value=initial_env_config,
                label="Environment Settings",
                width=400,
                open=False  # Start collapsed to show the accordion feature
            )

    # --- Event Handlers ---

    def handle_render_change(updated_config: RenderConfig | None):
        """Callback to process changes from the Render Settings sheet."""
        if updated_config is None:
            return initial_render_config, asdict(initial_render_config)
        
        # Example of business logic: reset custom path if not in custom mode
        if updated_config.model.model_type != "Custom":
            updated_config.model.custom_model_path = "/path/to/default.safetensors"
            
        return updated_config, asdict(updated_config)

    def handle_env_change(updated_config: EnvironmentConfig | None):
        """Callback to process changes from the Environment Settings sheet."""
        if updated_config is None:
            return initial_env_config, asdict(initial_env_config)
        return updated_config, asdict(updated_config)

    render_sheet.change(
        fn=handle_render_change,
        inputs=[render_sheet],
        outputs=[render_sheet, output_render_json]
    )
    environment_sheet.change(
        fn=handle_env_change,
        inputs=[environment_sheet],
        outputs=[environment_sheet, output_env_json]
    )
   
    # Load initial state into JSON viewers on app load
    demo.load(
        fn=lambda: (asdict(initial_render_config), asdict(initial_env_config)),
        outputs=[output_render_json, output_env_json]
    )

if __name__ == "__main__":
    demo.launch()