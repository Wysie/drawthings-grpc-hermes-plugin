"""Tool schemas for Draw Things gRPC plugin."""

DRAWTINGS_LIST = {
    "name": "drawthings_list",
    "description": (
        "List available Draw Things models, LoRAs, ControlNets/IP-Adapters, and generated aliases "
        "from the local Draw Things gRPC server. Use when the user asks what local Draw Things "
        "models/LoRAs/controls are available."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "kind": {
                "type": "string",
                "enum": ["all", "models", "loras", "controlnets", "upscalers", "textual_inversions"],
                "default": "all",
                "description": "Which inventory category to return.",
            },
            "query": {
                "type": "string",
                "description": "Optional substring/alias filter, e.g. qwen, z-image, faceid.",
            },
        },
    },
}

DRAWTINGS_GENERATE = {
    "name": "drawthings_generate",
    "description": (
        "Generate an image using the local/private Draw Things gRPC server. Use only when the user "
        "explicitly asks for Draw Things, local image generation, or a local model such as Qwen Image, "
        "Z Image, FLUX, RealVisXL, Juggernaut, or a Draw Things LoRA. This does not replace the default "
        "cloud image generation tool."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "prompt": {"type": "string", "description": "Positive prompt."},
            "negative_prompt": {"type": "string", "description": "Optional negative prompt."},
            "model": {
                "type": "string",
                "description": "Model alias, display name, or exact file. Examples: qwen-image-2512, z-image-turbo, realvisxl, juggernaut-xl.",
            },
            "lora": {
                "type": "string",
                "description": "Optional LoRA alias, display name, or exact file. Example: qwen-lightning.",
            },
            "lora_weight": {"type": "number", "default": 1.0},
            "width": {"type": "integer", "default": 1024, "description": "Width in pixels, rounded down to multiples of 64."},
            "height": {"type": "integer", "default": 1024, "description": "Height in pixels, rounded down to multiples of 64."},
            "steps": {"type": "integer", "description": "Sampling steps. If omitted, plugin picks a sensible default based on model/LoRA."},
            "sampler": {
                "type": "string",
                "description": "Sampler name. Defaults to Euler A Trailing for flow models.",
            },
            "seed": {"type": "integer", "description": "Optional deterministic seed."},
            "cfg": {"type": "number", "default": 1.0, "description": "Guidance scale/CFG."},
            "shift": {"type": "number", "description": "Flow scheduler shift multiplier for Draw Things. If a model card gives exponential_shift_mu, pass exp(mu), not mu."},
            "shift_terminal": {"type": "number", "description": "Optional terminal shift for schedulers that expose it; ignored/reported if the current Draw Things gRPC schema lacks this field."},
            "guidance_embed": {"type": "number", "description": "Guidance embed value for flow models when supported."},
            "resolution_dependent_shift": {"type": "boolean", "description": "Whether to enable resolution-dependent shift for flow models."},
            "output_path": {
                "type": "string",
                "description": "Optional absolute output file path. Defaults to ~/Pictures/Draw Things/drawthings-<model>-timestamp.png.",
            },
        },
        "required": ["prompt"],
    },
}
