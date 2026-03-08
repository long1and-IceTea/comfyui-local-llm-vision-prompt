# ComfyUI Local LLM Vision Prompt Node

A ComfyUI custom node that sends image/text input to any local LLM service with an OpenAI-compatible API (including LM Studio) and returns concise optimized prompt/caption text.

## Features

- Supports image + text optimization together
- Supports text-only optimization (image is optional)
- Encodes image to JPEG base64 for local API transfer
- Calls OpenAI-compatible `/v1/chat/completions`
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
2. Start your local LLM server (LM Studio, Ollama-compatible gateway, vLLM gateway, etc.) with a vision-capable model.
3. In ComfyUI, use node **LM Studio Local LLM Vision**.
4. Default API URL:
   - `http://127.0.0.1:1234/v1/chat/completions`

## Inputs

- `input_text`: optional text to optimize/rewrite
- `image` (optional): ComfyUI image tensor
- `api_url`: OpenAI-compatible local endpoint
- `system_prompt`: prompt template for image+text optimization behavior
- `max_tokens`: output length cap (32-4096)
- `temperature`: sampling temperature

## Output

- `sdxl_prompt` (string): final cleaned prompt text for any downstream workflow (kept for compatibility)

## Compatibility

- Class name and output slot name are kept for backward compatibility with existing ComfyUI workflows.

## License

MIT
