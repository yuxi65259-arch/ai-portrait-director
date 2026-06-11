"""Pydantic 请求/响应模型"""
from pydantic import BaseModel, Field
from typing import Optional, Literal

CATEGORY_OPTIONS = Literal["个人写真", "婚纱写真", "旅拍写真", "创意/概念写真", "COS写真"]
SIZE_OPTIONS = Literal["1024x1024", "1792x1024", "1024x1792"]


# ── 提示词生成 ──
class PromptRequest(BaseModel):
    category: CATEGORY_OPTIONS
    sub_style: Optional[str] = Field(default=None, max_length=100)
    custom_preference: Optional[str] = Field(default=None, max_length=500)
    model: Optional[str] = Field(default=None, max_length=100)


class PromptResponse(BaseModel):
    category: str
    sub_style: str
    scene: str = ""           # 📷 场景
    action: str = ""          # 💃 动作/姿态
    expression: str = ""      # 😊 表情/情绪
    lighting: str = ""        # 💡 光线方案
    tone: str = ""            # 🎨 色调/影调
    composition: str = ""     # 📐 构图建议
    chinese_prompt: str       # 🌐 中文视觉方案
    english_prompt: str       # 🌍 English Prompt
    photography_params: dict = {}
    negative_prompt: str = ""


# ── 图片生成 ──
class ImageRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=4000)
    size: SIZE_OPTIONS = "1792x1024"


class ImageResponse(BaseModel):
    image_url: str
    revised_prompt: Optional[str] = None


# ── 通用错误 ──
class ErrorResponse(BaseModel):
    error: str
    detail: str = ""
    code: str = ""
