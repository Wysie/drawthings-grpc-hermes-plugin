# Draw Things gRPC plugin for Hermes Agent

Local/private image generation through Draw Things' gRPC server. This plugin intentionally does **not** replace Hermes Agent's default cloud image generation provider. Use it only when the user explicitly asks for Draw Things, local image generation, or a local model/LoRA such as Qwen Image, Z Image, ERNIE, FLUX, RealVisXL, Juggernaut, or FaceID/IP-Adapter workflows.

## What this does

- Lists Draw Things models, LoRAs, ControlNets/IP-Adapters, upscalers, and textual inversions via gRPC `Echo`.
- Generates images via gRPC `GenerateImage`.
- Resolves friendly aliases such as `qwen-image-2512`, `z-image-turbo`, `ernie-image`, `realvisxl`, and `qwen-lightning`.
- Applies layered model defaults for steps, sampler, CFG, LoRA weight, and related settings.
- Saves output images locally.

## Important: installed models only

This plugin does **not** download every Draw Things model.

It only does this:

1. Calls Draw Things gRPC `Echo`.
2. Reads metadata for models/LoRAs/ControlNets already installed or visible in your Draw Things app/server.
3. Resolves aliases/default settings for those installed items.
4. Calls `GenerateImage` using the selected installed model.

It will not install Hugging Face files, mutate your Draw Things model library, or fill your disk.

## Requirements

- Hermes Agent with plugin support.
- Draw Things with the gRPC server enabled.
- Python dependencies available in the Hermes environment:
  - `grpcio`
  - `flatbuffers`
  - `fpzip`
  - `numpy`
  - `Pillow`

Install missing dependencies into Hermes' venv, for example:

```bash
~/.hermes/hermes-agent/venv/bin/python3 -m pip install grpcio flatbuffers fpzip numpy Pillow
```

## Install

Clone/copy this plugin into your Hermes plugins directory:

```bash
mkdir -p ~/.hermes/plugins
git clone https://github.com/Wysie/drawthings-grpc-hermes-plugin.git ~/.hermes/plugins/drawthings-grpc
hermes plugins enable drawthings-grpc
hermes gateway restart   # if using Telegram/WhatsApp/etc.
```

Then start a new Hermes session so the new toolset is loaded.

## Tools

- `drawthings_list`: list installed models, LoRAs, ControlNets/IP-Adapters, upscalers, textual inversions from Draw Things gRPC `Echo` metadata.
- `drawthings_generate`: text-to-image generation via Draw Things gRPC `GenerateImage`.

Toolset name:

```text
drawthings
```

## Endpoint configuration

Defaults:

- Host: `localhost`
- Port: `7859`
- TLS: enabled

Override with environment variables:

- `DRAWTHINGS_GRPC_HOST`
- `DRAWTHINGS_GRPC_PORT`
- `DRAWTHINGS_GRPC_TLS`
- `DRAWTHINGS_GRPC_TLS_NAME` (default `localhost`; useful because Draw Things cert CN is usually localhost)
- `DRAWTHINGS_OUTPUT_DIR` (default `~/Pictures/Draw Things`)

Example LAN server:

```bash
export DRAWTHINGS_GRPC_HOST=drawthings.local
export DRAWTHINGS_GRPC_PORT=7859
export DRAWTHINGS_GRPC_TLS=true
export DRAWTHINGS_GRPC_TLS_NAME=localhost
```

## Example usage

Generate with Qwen Image quality defaults:

```json
{
  "prompt": "Hammy, a fluffy golden-and-white hamster...",
  "model": "qwen-image-2512"
}
```

Generate with Qwen Lightning LoRA:

```json
{
  "prompt": "Hammy, a fluffy golden-and-white hamster...",
  "model": "qwen-image-2512",
  "lora": "qwen-lightning"
}
```

Generate with Z Image Turbo:

```json
{
  "prompt": "Hammy, a fluffy golden-and-white hamster...",
  "model": "z-image-turbo"
}
```

Generate with ERNIE:

```json
{
  "prompt": "Hammy, a fluffy golden-and-white hamster...",
  "model": "ernie-image"
}
```

## Aliases

The plugin accepts exact Draw Things filenames, exact display names, generated slugs, and configured aliases. Examples:

- `ernie-image`, `ernie-image-base` → `ernie_image_q8p.ckpt`
- `qwen-image-2512`, `qwen2512`, `qwen-image` → `qwen_image_2512_q8p.ckpt`
- `z-image-turbo`, `zturbo` → `z_image_turbo_1.0_q8p.ckpt`
- `realvisxl`, `realvisxl-v4` → RealVisXL
- `juggernaut-xl`, `juggernaut-v9` → Juggernaut XL v9
- `qwen-lightning`, `lightning-4step` → Qwen Lightning LoRA

## Default settings strategy

Draw Things has many models. The plugin should not maintain a giant download catalog. Instead it uses layered defaults:

1. `version_defaults`: defaults by Draw Things model family/version, e.g. `qwen_image`, `z_image`, `ernie_image`, `sdxl_base_v0.9`.
2. `model_defaults`: overrides for known installed model files.
3. `lora_defaults`: overrides for known LoRA files.
4. user config overrides in `~/.hermes/drawthings-grpc/config.json`.
5. explicit tool arguments always win.

Bundled defaults live in:

```text
~/.hermes/plugins/drawthings-grpc/defaults.json
```

User overrides live in:

```text
~/.hermes/drawthings-grpc/config.json
```

Current bundled examples:

- `z_image` / Z Image Turbo: 8 steps, Euler A Trailing, CFG 1.0
- `qwen_image`: 35 steps, Euler A Trailing, CFG 1.0
- `ernie_image`: 50 steps, Euler A Trailing, CFG 1.0
- `flux1`: 4 steps, Euler A Trailing, CFG 1.0
- `sdxl_base_v0.9`: 25 steps, DPM++ 2M Karras, CFG 7.0
- Qwen Lightning/Turbo LoRAs: 4 steps, LoRA weight 1.0

## Adding your own models or LoRAs

First install/add the model inside Draw Things itself. Once Draw Things can see it, the plugin can see it via `drawthings_list`.

Then optionally add friendly aliases and defaults:

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
      "cfg": 4.5,
      "shift": 1.0,
      "guidance_embed": 3.5,
      "resolution_dependent_shift": true
    }
  },
  "lora_defaults": {
    "my_style_lora_f16.ckpt": {
      "lora_weight": 0.8
    }
  }
}
```

Save that as:

```text
~/.hermes/drawthings-grpc/config.json
```

Then use:

```json
{
  "prompt": "...",
  "model": "my-anime-model",
  "lora": "my-style-lora"
}
```

If an alias is ambiguous, use the exact Draw Things file name from `drawthings_list`.

## Why gRPC instead of HTTP API?

Draw Things' HTTP API can be convenient, but gRPC exposes model browsing metadata, LoRA/ControlNet metadata, and deterministic FlatBuffer generation configuration. This makes it better for agent automation.

## Current scope

Implemented:

- model/LoRA listing
- alias resolution
- text-to-image generation
- output decoding/saving
- layered defaults and user overrides

Planned / future work:

- img2img
- inpainting
- ControlNet/IP-Adapter image hints
- FaceID workflows
- batch generation
- richer CLI wrapper

## License

MIT
