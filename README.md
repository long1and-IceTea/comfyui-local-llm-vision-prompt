# LM Studio SDXL Vision Node

A ComfyUI custom node that sends an input image to LM Studio's OpenAI-compatible vision endpoint and returns a concise SDXL prompt.

## Features

- Accepts ComfyUI `IMAGE` input
- Encodes image to JPEG base64 for local API transfer
- Calls LM Studio `/v1/chat/completions`
- Filters model reasoning (`<think>...</think>` and `/think ... /endthink`) and returns only final prompt text

## Requirements

- ComfyUI
- Python packages:
  - `requests`
  - `numpy`
  - `Pillow`
  - `torch` (provided by ComfyUI environment in most setups)

Install minimal dependencies:

```bash
pip install -r requirements.txt
```

## Usage

1. Put `lm_studio_sdxl_vision.py` in your ComfyUI custom nodes path.
2. Start LM Studio local server with a vision-capable model.
3. In ComfyUI, use node **LM Studio SDXL Interrogator**.
4. Default API URL:
   - `http://127.0.0.1:1234/v1/chat/completions`

## Inputs

- `image`: ComfyUI image tensor
- `api_url`: LM Studio endpoint
- `system_prompt`: Prompt template for SDXL caption style
- `max_tokens`: Output length cap
- `temperature`: Sampling temperature

## Output

- `sdxl_prompt` (string): final cleaned prompt text for downstream SDXL workflow

## License

MIT
