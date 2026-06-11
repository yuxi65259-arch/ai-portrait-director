"""可选模型配置"""

PROMPT_MODELS = [
    {"id": "deepseek-chat", "name": "DeepSeek", "desc": "性价比高，中文理解好"},
    {"id": "deepseek-v4-pro", "name": "DeepSeek V4 Pro", "desc": "最新版，推理更强"},
    {"id": "gemini-3-pro-preview", "name": "Gemini 3 Pro", "desc": "Google 最新旗舰"},
    {"id": "gemini-2.5-pro", "name": "Gemini 2.5 Pro", "desc": "Google 推理模型"},
    {"id": "doubao-seed-1-6-250615", "name": "豆包 Seed 1.6", "desc": "字节跳动旗舰"},
    {"id": "doubao-pro-256k", "name": "豆包 Pro", "desc": "字节跳动，长上下文"},
    {"id": "gpt-5", "name": "GPT-5", "desc": "OpenAI 最新模型"},
    {"id": "gpt-5.4", "name": "GPT-5.4", "desc": "最新 OpenAI 模型"},
    {"id": "claude-opus-4-7", "name": "Claude Opus 4.7", "desc": "Anthropic 旗舰"},
    {"id": "claude-sonnet-4-6", "name": "Claude Sonnet 4.6", "desc": "Anthropic 高效模型"},
    {"id": "qwen3-max", "name": "通义千问 Max", "desc": "阿里最新旗舰"},
    {"id": "kimi-k2.6", "name": "Kimi K2.6", "desc": "月之暗面最新"},
]

IMAGE_MODELS = [
    {"id": "gpt-image-2", "name": "GPT-Image-2", "desc": "OpenAI 最新生图，质量最高"},
    {"id": "gpt-image-1.5", "name": "GPT-Image-1.5", "desc": "OpenAI 生图模型"},
    {"id": "gemini-2.5-flash-image", "name": "Gemini Flash Image", "desc": "速度最快，~10秒出图"},
    {"id": "gemini-3-pro-image-preview", "name": "Gemini 3 Pro Image", "desc": "Google 最新生图"},
    {"id": "doubao-seedream-4-5-251128", "name": "豆包 Seedream 4.5", "desc": "字节跳动生图"},
    {"id": "doubao-seedream-5-0-260128", "name": "豆包 Seedream 5.0", "desc": "字节跳动最新生图"},
]

DEFAULT_PROMPT_MODEL = "deepseek-chat"
DEFAULT_IMAGE_MODEL = "gpt-image-2"
