"""加载和校验 API 配置"""
import os
from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "").strip()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()


def validate_config():
    """检查配置，返回缺失的项目列表（不抛异常，让服务先启动）"""
    errors = []
    if not DEEPSEEK_API_KEY:
        errors.append("缺少 DEEPSEEK_API_KEY，请在项目根目录创建 .env 文件并填入密钥")
    if not OPENAI_API_KEY:
        errors.append("缺少 OPENAI_API_KEY，请在项目根目录创建 .env 文件并填入密钥")
    return errors
