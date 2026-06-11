"""AI写真提示词导演 — FastAPI 入口"""
import os, sys
sys.stdout.reconfigure(encoding='utf-8')

from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from config import validate_config, DEEPSEEK_API_KEY, OPENAI_API_KEY
from models import PromptRequest, PromptResponse, ImageResponse, ErrorResponse
from models_config import PROMPT_MODELS, IMAGE_MODELS, DEFAULT_PROMPT_MODEL, DEFAULT_IMAGE_MODEL
from prompt_engine import generate_prompt
from image_generator import generate_image

# 启动警告
warnings = validate_config()
if warnings:
    print(f"\n{'='*60}")
    print("[WARN] API Key not configured:")
    for w in warnings:
        print(f"  - {w}")
    print("Please create .env file and restart the server.")
    print(f"{'='*60}\n")

app = FastAPI(title="AI写真提示词导演", version="2.1")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


@app.get("/", response_class=HTMLResponse)
async def index():
    html_path = os.path.join(BASE_DIR, "templates", "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "deepseek_key": bool(DEEPSEEK_API_KEY),
        "openai_key": bool(OPENAI_API_KEY),
    }


@app.get("/api/models")
async def list_models():
    return {
        "prompt_models": PROMPT_MODELS,
        "image_models": IMAGE_MODELS,
        "defaults": {
            "prompt": DEFAULT_PROMPT_MODEL,
            "image": DEFAULT_IMAGE_MODEL,
        }
    }


# ── 步骤1：生成提示词（支持多模型）──
@app.post("/api/generate-prompt", response_model=PromptResponse)
async def api_generate_prompt(request: PromptRequest):
    try:
        if not DEEPSEEK_API_KEY:
            return JSONResponse(
                status_code=503,
                content=ErrorResponse(
                    error="DeepSeek Key 未配置",
                    detail="缺少 DEEPSEEK_API_KEY，请在 .env 文件中填入密钥后重启服务",
                    code="API_KEY_MISSING",
                ).model_dump(),
            )

        raw = generate_prompt(
            category=request.category,
            sub_style=request.sub_style or "",
            custom_preference=request.custom_preference or "",
            model=request.model or DEFAULT_PROMPT_MODEL,
        )

        return PromptResponse(
            category=request.category,
            sub_style=raw["sub_style"],
            scene=raw.get("scene", ""),
            action=raw.get("action", ""),
            expression=raw.get("expression", ""),
            lighting=raw.get("lighting", ""),
            tone=raw.get("tone", ""),
            composition=raw.get("composition", ""),
            chinese_prompt=raw["chinese_prompt"],
            english_prompt=raw["english_prompt"],
            photography_params=raw["photography_params"],
            negative_prompt=raw.get("negative_prompt", ""),
        )

    except Exception as e:
        msg = repr(e)
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                error="提示词生成失败",
                detail=str(e)[:500],
                code="DEEPSEEK_ERROR" if "deepseek" in msg.lower() else "UNKNOWN",
            ).model_dump(),
        )


# ── 步骤2：生图（支持参考图上传 + 多模型）──
@app.post("/api/generate-image", response_model=ImageResponse)
async def api_generate_image(
    prompt: str = Form(...),
    size: str = Form("1024x1024"),
    model: str = Form(DEFAULT_IMAGE_MODEL),
    reference_image: UploadFile = File(None),
):
    try:
        if not OPENAI_API_KEY:
            return JSONResponse(
                status_code=503,
                content=ErrorResponse(
                    error="OpenAI Key 未配置",
                    detail="缺少 OPENAI_API_KEY，请在 .env 文件中填入密钥后重启服务",
                    code="API_KEY_MISSING",
                ).model_dump(),
            )

        ref_bytes = None
        if reference_image and reference_image.filename:
            ref_bytes = await reference_image.read()

        img = generate_image(prompt=prompt, size=size, reference_image_bytes=ref_bytes, model=model)

        return ImageResponse(
            image_url=img["url"],
            revised_prompt=img.get("revised_prompt", ""),
        )

    except Exception as e:
        msg = repr(e)
        detail = str(e)[:500]
        code = "UNKNOWN"

        if "content_policy_violation" in msg.lower() or "safety" in msg.lower():
            code = "SAFETY_REJECT"
            detail = "提示词被内容安全策略拒绝，请换一种描述方式重试"
        elif "timeout" in msg.lower():
            code = "TIMEOUT"
            detail = "请求超时，请检查网络后重试"
        else:
            code = "OPENAI_ERROR"

        return JSONResponse(
            status_code=500,
            content=ErrorResponse(error="图片生成失败", detail=detail, code=code).model_dump(),
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
