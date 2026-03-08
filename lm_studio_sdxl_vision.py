import torch
import requests
import base64
import numpy as np
from PIL import Image
import io
import re


class LMStudioSDXLVision:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "input_text": ("STRING", {"multiline": True, "default": ""}),
                "api_url": ("STRING", {"default": "http://127.0.0.1:1234/v1/chat/completions"}),
                "system_prompt": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "You are an expert prompt and text optimizer. If an image is provided, describe it accurately and concisely. If user text is provided, improve and optimize it for downstream creative AI workflows. Return only the final optimized prompt/text.",
                    },
                ),
                "max_tokens": ("INT", {"default": 300, "min": 32, "max": 4096, "step": 32}),
                "temperature": ("FLOAT", {"default": 0.4, "min": 0.0, "max": 1.0, "step": 0.1}),
            },
            "optional": {
                "image": ("IMAGE",),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("sdxl_prompt",)
    FUNCTION = "generate_prompt"
    CATEGORY = "LMStudio/Workflow"

    def _extract_final_prompt(self, content):
        text = (content or "").strip()
        if not text:
            return ""

        # Remove common reasoning blocks returned by thinking models.
        text = re.sub(r"(?is)<think>.*?</think>", "", text).strip()
        text = re.sub(r"(?is)/think\b.*?/endthink\b", "", text).strip()

        # Fallback: if /think marker still exists, keep the last non-empty segment.
        if re.search(r"(?i)/think\b", text):
            parts = [p.strip() for p in re.split(r"(?i)/think\b", text) if p.strip()]
            if parts:
                text = parts[-1]

        text = re.sub(r"(?im)^\s*(final answer|answer|prompt)\s*:\s*", "", text).strip()
        return text

    def generate_prompt(self, input_text, api_url, system_prompt, max_tokens, temperature, image=None):
        content = [{"type": "text", "text": system_prompt}]

        if input_text and input_text.strip():
            content.append(
                {
                    "type": "text",
                    "text": (
                        "User text to optimize:\n"
                        f"{input_text.strip()}\n\n"
                        "If user text exists, prioritize rewriting/optimizing it. "
                        "Return only the final optimized text or prompt."
                    ),
                }
            )

        if image is not None:
            # IMAGE tensor -> JPEG base64
            i = 255.0 * image[0].cpu().numpy()
            img = Image.fromarray(np.uint8(i))
            buffered = io.BytesIO()
            img.save(buffered, format="JPEG", quality=85)
            img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
            content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_str}"}})

        if len(content) == 1:
            return ("Input Error: provide at least one of input_text or image.",)

        payload = {
            "model": "local-model",
            "messages": [{"role": "user", "content": content}],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        try:
            response = requests.post(api_url, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            raw_content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            prompt = self._extract_final_prompt(raw_content) or raw_content.strip()
            return (prompt,)
        except requests.exceptions.RequestException as e:
            return (f"API Connection Error: Make sure LM Studio server is running. Details: {e}",)


NODE_CLASS_MAPPINGS = {"LMStudioSDXLVision": LMStudioSDXLVision}
NODE_DISPLAY_NAME_MAPPINGS = {"LMStudioSDXLVision": "LM Studio Local LLM Vision"}
