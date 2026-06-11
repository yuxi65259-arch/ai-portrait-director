"""GPT-Image-2 图片生成（支持参考图）"""
import re, base64
from openai import OpenAI
from config import OPENAI_API_KEY

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=OPENAI_API_KEY,
            base_url="https://api.geeknow.ai/v1",
            timeout=180,
        )
    return _client


def generate_image(prompt: str, size: str = "1792x1024", reference_image_bytes: bytes = None, model: str = "gpt-image-2") -> dict:
    """调用指定生图模型生成图片，可选参考图"""

    if reference_image_bytes:
        # 有参考图：走 chat completions，带图片
        b64 = base64.b64encode(reference_image_bytes).decode()
        response = _get_client().chat.completions.create(
            model=model if model != "gpt-image-2" else "gpt-image-2",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": f"Based on this reference photo, generate a similar style portrait. {prompt}. Image size: {size}."},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
                ]
            }],
            max_tokens=4000,
        )
        content = response.choices[0].message.content
        urls = re.findall(r'!\[.*?\]\((https?://[^\s\)]+)\)', content)
        if not urls:
            urls = re.findall(r'https?://[^\s\)]+\.(?:png|jpg|jpeg|webp)', content)
        return {
            "url": urls[0] if urls else "",
            "revised_prompt": "",
        }
    else:
        # 无参考图：走 images.generate
        response = _get_client().images.generate(
            model=model,
            prompt=prompt,
            size=size,
            n=1,
        )
        data = response.data[0]
        return {
            "url": data.url,
            "revised_prompt": getattr(data, "revised_prompt", None) or "",
        }
