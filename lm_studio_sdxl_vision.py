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
                "image": ("IMAGE",),
                "api_url": ("STRING", {"default": "http://127.0.0.1:1234/v1/chat/completions"}),
                "system_prompt": ("STRING", {
                    "multiline": True,
                    "default": "You are a Stable Diffusion XL prompt expert. Describe this image accurately in natural language. Use this structure: [Main Subject], [Action/Pose], [Environment/Background], [Lighting], [Art Style/Camera angle]. Keep it concise, under 50 words, and comma-separated."
                }),
                "max_tokens": ("INT", {"default": 150}),
                "temperature": ("FLOAT", {"default": 0.4, "min": 0.0, "max": 1.0, "step": 0.1}),
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

    def generate_prompt(self, image, api_url, system_prompt, max_tokens, temperature):
        # 杞崲寮犻噺涓哄浘鍍?
        i = 255. * image[0].cpu().numpy()
        img = Image.fromarray(np.uint8(i))

        # 鍐呭瓨涓浆涓築ase64
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=85) # 鐢↗PEG绋嶅井鍘嬬缉锛屽姞蹇湰鍦癆PI浼犺緭
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

        payload = {
            "model": "local-model",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": system_prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_str}"}}
                    ]
                }
            ],
            "max_tokens": max_tokens,
            "temperature": temperature
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
NODE_DISPLAY_NAME_MAPPINGS = {"LMStudioSDXLVision": "LM Studio SDXL Interrogator"}
