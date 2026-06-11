"""DeepSeek 提示词生成引擎"""
import re
from openai import OpenAI
from config import DEEPSEEK_API_KEY
from system_prompt import SYSTEM_PROMPT

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
    return _client


def parse_response(text: str) -> dict:
    """解析 DeepSeek 输出，提取所有结构化字段"""
    result = {
        "scene": "", "action": "", "expression": "", "lighting": "",
        "tone": "", "composition": "",
        "chinese_prompt": "", "english_prompt": "",
        "sub_style": "", "photography_params": {}, "negative_prompt": "",
    }

    def extract_section(header):
        """提取指定 header 之后到下一个 emoji header 之间的内容"""
        # header 如 '📷 场景' — 匹配到此行末尾的冒号后提取内容
        pattern = header + r"\s*[：:]\s*(.+?)(?=\n[📷💃😊💡🎨📐🌐🌍📝⚠]|\n━━|\n🎬|\Z)"
        m = re.search(pattern, text, re.DOTALL)
        if m:
            return re.sub(r"\n{2,}", "\n", m.group(1)).strip()
        return ""

    # 提取子风格
    m = re.search(r"【子风格名】\s*[：:]\s*(.+?)(?:\n|$)", text)
    if m:
        result["sub_style"] = m.group(1).strip()

    # 提取六大结构化字段（使用精确的 emoji+标签）
    result["scene"] = extract_section(r"📷 场景")
    result["action"] = extract_section(r"💃 动作/姿态")
    result["expression"] = extract_section(r"😊 表情/情绪")
    result["lighting"] = extract_section(r"💡 光线方案")
    result["tone"] = extract_section(r"🎨 色调/影调")
    result["composition"] = extract_section(r"📐 构图建议")

    # 提取中文视觉方案
    m = re.search(r"🌐.*?中文视觉方案.*?\n(.+?)(?:\n🌍|\nEnglish|\n━━|$)", text, re.DOTALL)
    if m:
        result["chinese_prompt"] = m.group(1).strip()
    else:
        m = re.search(r"【中文视觉方案】.*?\n(.+?)(?:\n【|\n🌍|$)", text, re.DOTALL)
        if m:
            result["chinese_prompt"] = m.group(1).strip()

    # 提取英文 Prompt（兼容多种模型输出格式）
    m = re.search(r"🌍.*?English Prompt.*?\n(.+?)(?:\n━━|\n📝|\n⚠|\n\n📝|\n\n⚠|$)", text, re.DOTALL)
    if m:
        result["english_prompt"] = m.group(1).strip()
    if not result["english_prompt"]:
        m = re.search(r"【English Prompt】.*?\n(.+?)(?:\n【|\n📝|$)", text, re.DOTALL)
        if m:
            result["english_prompt"] = m.group(1).strip()
    # 如果 EN 仍然为空或包含中文（说明提取到错误的段落），用整段作为 fallback
    if not result["english_prompt"] or re.search(r'[\u4e00-\u9fff]', result["english_prompt"][:50]):
        # 尝试从整段中提取纯英文段落
        en_match = re.search(r'(?:English Prompt|英文).*?\n\s*((?:[A-Z].+?\n?)+)', text)
        if en_match:
            result["english_prompt"] = en_match.group(1).strip()[:980]

    # 提取拍摄参数
    params = {}
    for key in ["焦段", "光圈", "快门", "画幅比"]:
        m = re.search(rf"{key}\s*[：:]\s*(.+?)(?:\s{{2,}}|\n|$)", text)
        if m:
            params[key] = m.group(1).strip()
    result["photography_params"] = params

    # 提取负面提示词
    m = re.search(r"⚠️?\s*负面提示词.*?\n(.+?)(?:\n━━|\n$|$)", text, re.DOTALL)
    if m:
        result["negative_prompt"] = m.group(1).strip()

    # Fallbacks
    if not result["chinese_prompt"]:
        result["chinese_prompt"] = text.strip()
    if not result["english_prompt"]:
        result["english_prompt"] = text.strip()

    # 清理英文 prompt
    result["english_prompt"] = re.sub(r"[【】⚠].*?[：:].*?\n?", "", result["english_prompt"])
    result["english_prompt"] = result["english_prompt"].strip()
    if len(result["english_prompt"]) > 980:
        result["english_prompt"] = result["english_prompt"][:980]

    return result


def generate_prompt(category: str, sub_style: str = "", custom_preference: str = "", model: str = "deepseek-chat") -> dict:
    """调用指定模型生成写真提示词"""
    user_message = f"类别：{category}"
    if sub_style:
        user_message += f"\n子风格：{sub_style}"
    else:
        user_message += "\n子风格：随机（从该类别子风格库中挑一个最出片的）"
    if custom_preference:
        user_message += f"\n用户额外偏好：{custom_preference}"

    # DeepSeek 模型走官方 API，其他模型走代理
    if model.startswith("deepseek"):
        client = _get_client()
    else:
        client = _get_proxy_client()

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.85,
        max_tokens=3000,
        timeout=30,
    )

    raw_text = response.choices[0].message.content
    return parse_response(raw_text)


_proxy_client = None


def _get_proxy_client():
    global _proxy_client
    if _proxy_client is None:
        from config import OPENAI_API_KEY
        _proxy_client = OpenAI(api_key=OPENAI_API_KEY, base_url="https://api.geeknow.ai/v1")
    return _proxy_client
