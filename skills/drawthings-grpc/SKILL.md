---
name: drawthings-grpc
description: Use local Draw Things gRPC image generation without changing the default image generation backend.
tags: [draw-things, image-generation, grpc, local, apple-silicon]
version: 0.3.0
author: Agent Hammy
---

# Draw Things gRPC

Use this plugin when the user explicitly asks for Draw Things, local/private image generation, or local model names like Qwen Image, Z Image Turbo, ERNIE, RealVisXL, Juggernaut, FLUX, LoRA, ControlNet, IP-Adapter, or FaceID.

Do not use this as the default image generator. The normal `image_generate` tool remains the default cloud image provider.

## Installed models only

The plugin never downloads all Draw Things models. It only calls Draw Things gRPC `Echo` and works with models/LoRAs/ControlNets already installed or visible in Draw Things.

## Tools

- `drawthings_list`: list available local models, LoRAs, ControlNets/IP-Adapters.
- `drawthings_generate`: generate text-to-image via Draw Things gRPC.

## Model aliases

The plugin resolves exact files/names, generated slugs, bundled aliases, and user-configured aliases from `~/.hermes/drawthings-grpc/config.json`.

Common aliases:

- `ernie-image`, `ernie-image-base`
- `qwen-image-2512`, `qwen2512`, `qwen-image`
- `z-image-turbo`, `zturbo`
- `flux2-klein`, `flux-klein`, `flux2-4b`
- `realvisxl`, `realvisxl-v4`
- `juggernaut-xl`, `juggernaut-v9`

LoRA aliases include:

- `qwen-lightning`, `qwen-image-lightning`, `lightning-4step`
- `qwen-turbo-lora`, `turbo-4step`

## Defaults strategy

Defaults are layered:

1. version defaults by model family/version
2. exact model file defaults
3. exact LoRA file defaults
4. user config overrides at `~/.hermes/drawthings-grpc/config.json`
5. explicit tool arguments

Bundled defaults include:

- Z Image Turbo: 8 steps, Euler A Trailing
- Qwen Image 2512: 35 steps, Euler A Trailing
- ERNIE Image: 50 steps, Euler A Trailing
- Qwen Image 2512 Lightning/Turbo LoRA: 4 steps
- SDXL models: 25 steps, DPM++ 2M Karras, CFG 7.0

Outputs save to `~/Pictures/Draw Things` unless `output_path` or `DRAWTHINGS_OUTPUT_DIR` is set.

## Adding user models

Install/add the model in Draw Things first. Then optionally add aliases/defaults to:

`~/.hermes/drawthings-grpc/config.json`

Example:

```json
{
  "aliases": {
    "my-anime-model": "my_anime_model_q8p.ckpt",
    "my-style-lora": "my_style_lora_f16.ckpt"
  },
  "model_defaults": {
    "my_anime_model_q8p.ckpt": {
      "steps": 28,
      "sampler": "Euler A Trailing",
      "cfg": 4.5
    }
  },
  "lora_defaults": {
    "my_style_lora_f16.ckpt": {
      "lora_weight": 0.8
    }
  }
}
```
