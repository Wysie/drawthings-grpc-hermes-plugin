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

For a durable setup, put the endpoint in the plugin's user config:

```json
{
  "endpoint": {
    "host": "drawthings.local",
    "port": 7859,
    "tls": true,
    "tls_name": "localhost"
  }
}
```

User config path:

```text
~/.hermes/drawthings-grpc/config.json
```

This is preferred for Hermes gateway / WhatsApp / Telegram sessions because shell environment variables are not always inherited by long-running gateway tool processes. `tls_name` is the hostname used for TLS certificate verification; keep it as `localhost` when connecting to Draw Things by LAN IP because Draw Things' generated certificate is usually issued for `localhost`.

Environment variables are still supported as overrides, and are useful for one-off CLI runs, tests, or temporary endpoint switching:

- `DRAWTHINGS_GRPC_HOST`
- `DRAWTHINGS_GRPC_PORT`
- `DRAWTHINGS_GRPC_TLS`
- `DRAWTHINGS_GRPC_TLS_NAME` (default `localhost`; useful because Draw Things cert CN is usually localhost)
- `DRAWTHINGS_OUTPUT_DIR` (default `~/Pictures/Draw Things`)

Example temporary override:

```bash
export DRAWTHINGS_GRPC_HOST=drawthings.local
export DRAWTHINGS_GRPC_PORT=7859
export DRAWTHINGS_GRPC_TLS=true
export DRAWTHINGS_GRPC_TLS_NAME=localhost
```

## Setting Up gRPCServerCLI

If you do not want to manually enable the Draw Things app gRPC server after every launch, run the standalone `gRPCServerCLI-macOS` binary as a macOS LaunchAgent.

### 1. Download the prebuilt server

```bash
cd /tmp

curl -L -o gRPCServerCLI-macOS \
  https://github.com/drawthingsai/draw-things-community/releases/download/v1.20260418.1/gRPCServerCLI-macOS

chmod +x gRPCServerCLI-macOS
sudo mkdir -p /usr/local/bin
sudo mv gRPCServerCLI-macOS /usr/local/bin/gRPCServerCLI-macOS
sudo xattr -dr com.apple.quarantine /usr/local/bin/gRPCServerCLI-macOS
```

### 2. Find your Draw Things models directory

Common macOS sandbox path:

```text
~/Library/Containers/com.liuliu.draw-things/Data/Documents/Models
```

If unsure, search for it:

```bash
find "$HOME/Library/Containers" "$HOME/Documents" "$HOME/Library/Application Support" \
  -type d -name Models 2>/dev/null | grep -i "draw\\|liuliu"
```

### 3. Test the server manually

Replace the models path if yours is different:

```bash
/usr/local/bin/gRPCServerCLI-macOS \
  "$HOME/Library/Containers/com.liuliu.draw-things/Data/Documents/Models" \
  --name "Draw Things gRPC Server" \
  --address 0.0.0.0 \
  --port 7859 \
  --model-browser
```

Notes:

- TLS is enabled by default. Do **not** pass `--no-tls` unless you also configure the plugin with `DRAWTHINGS_GRPC_TLS=false`.
- `--address 0.0.0.0` allows other machines on your LAN to connect.
- `--port 7859` matches the plugin default.
- `--model-browser` enables model/LoRA metadata discovery through `Echo`.

From another machine, verify with `grpcurl` and the Draw Things `imageService.proto`:

```bash
grpcurl -insecure \
  -import-path /path/to/draw-things-comfyui/resources \
  -proto imageService.proto \
  -d '{"name":"test"}' \
  drawthings.local:7859 \
  ImageGenerationService/Echo
```

If you use an IP address instead of `drawthings.local`, replace the host accordingly.

### 4. Create a LaunchAgent for auto-start

```bash
mkdir -p ~/Library/LaunchAgents ~/Library/Logs

cat > ~/Library/LaunchAgents/io.example.drawthings-grpc.plist <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
 "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>io.example.drawthings-grpc</string>

  <key>ProgramArguments</key>
  <array>
    <string>/usr/local/bin/gRPCServerCLI-macOS</string>
    <string>/Users/YOUR_USERNAME/Library/Containers/com.liuliu.draw-things/Data/Documents/Models</string>
    <string>--name</string>
    <string>Draw Things gRPC Server</string>
    <string>--address</string>
    <string>0.0.0.0</string>
    <string>--port</string>
    <string>7859</string>
    <string>--model-browser</string>
  </array>

  <key>RunAtLoad</key>
  <true/>

  <key>KeepAlive</key>
  <true/>

  <key>StandardOutPath</key>
  <string>/Users/YOUR_USERNAME/Library/Logs/drawthings-grpc.out.log</string>

  <key>StandardErrorPath</key>
  <string>/Users/YOUR_USERNAME/Library/Logs/drawthings-grpc.err.log</string>
</dict>
</plist>
PLIST
```

Edit the plist and replace `YOUR_USERNAME` with your macOS username. Then load it:

```bash
launchctl unload ~/Library/LaunchAgents/io.example.drawthings-grpc.plist 2>/dev/null || true
launchctl load ~/Library/LaunchAgents/io.example.drawthings-grpc.plist
launchctl start io.example.drawthings-grpc
```

Verify:

```bash
launchctl list | grep drawthings
lsof -nP -iTCP:7859 -sTCP:LISTEN
tail -50 ~/Library/Logs/drawthings-grpc.out.log
tail -50 ~/Library/Logs/drawthings-grpc.err.log
```

Once `Echo` works, configure this plugin to point at that server using `~/.hermes/drawthings-grpc/config.json`:

```json
{
  "endpoint": {
    "host": "drawthings.local",
    "port": 7859,
    "tls": true,
    "tls_name": "localhost"
  }
}
```

Use `DRAWTHINGS_GRPC_HOST`, `DRAWTHINGS_GRPC_PORT`, and `DRAWTHINGS_GRPC_TLS` only when you need a temporary override.

## Example usage

Generate with Qwen Image quality defaults (also the bundled default model if `model` is omitted):

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
- `ernie-image-turbo`, `ernie-turbo` → `ernie_image_turbo_q8p.ckpt`
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
4. `default_model`: model alias/name/file used when the caller omits `model`.
5. user config overrides in `~/.hermes/drawthings-grpc/config.json`.
6. explicit tool arguments always win.

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
- `qwen_image` / Qwen Image 2512: 50 steps, Euler A Trailing, CFG 4.0
- `ernie_image_q8p.ckpt` / ERNIE Image Base: 50 steps, Euler A Trailing, CFG 4.0
- `ernie_image_turbo_q8p.ckpt` / ERNIE Image Turbo: 8 steps, Euler A Trailing, CFG 1.0
- `flux1`: 4 steps, Euler A Trailing, CFG 1.0
- `sdxl_base_v0.9`: 25 steps, DPM++ 2M Karras, CFG 7.0
- Qwen Lightning/Turbo LoRAs: 4 steps, Euler A Trailing, CFG 1.0, LoRA weight 1.0

## Adding your own models or LoRAs

First install/add the model inside Draw Things itself. Once Draw Things can see it, the plugin can see it via `drawthings_list`.

Then optionally add friendly aliases and defaults:

```json
{
  "default_model": "qwen-image-2512",
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
