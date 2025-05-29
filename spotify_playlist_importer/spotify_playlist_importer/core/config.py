import os
import json
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
from typing import Final, Optional, Dict, Any

# 默认配置文件路径
DEFAULT_CONFIG_PATH = "config.json"

# 尝试查找和加载.env文件
def load_env_files():
    """
    尝试加载 .env 文件。
    主要用于本地开发。在 Render 等部署环境中，环境变量应通过平台设置。
    """
    # 尝试从当前工作目录或其父目录加载 .env 文件
    # find_dotenv 会从当前目录开始向上查找
    loaded_path = find_dotenv(usecwd=True, raise_error_if_not_found=False)
    
    if loaded_path:
        if load_dotenv(loaded_path, verbose=True): # verbose=True 会在加载时打印信息
            print(f"已加载环境变量文件: {loaded_path}")
            return True
            
    print("信息: 未找到 .env 文件或无法加载。应用将依赖于操作系统注入的环境变量。")
    return False

# 加载.env文件
load_env_files()


class ConfigurationError(Exception):
    """自定义异常，用于处理缺失或无效的配置。"""
    pass


def _load_config_from_file() -> Dict[str, Any]:
    """
    尝试从配置文件加载配置
    
    Returns:
        Dict[str, Any]: 配置字典，如果文件不存在或无法解析则返回空字典
    """
    config_path = os.getenv("CONFIG_FILE_PATH", DEFAULT_CONFIG_PATH)
    try:
        if Path(config_path).exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError, PermissionError) as e:
        print(f"无法加载配置文件 {config_path}: {e}")
    return {}


# 加载配置文件
_config = _load_config_from_file()


def get_config(key: str, default: Any = None, required: bool = False) -> Any:
    """
    获取配置值，优先从环境变量获取，然后从配置文件获取
    
    Args:
        key: 配置键名
        default: 默认值，如果未找到配置
        required: 是否为必需的配置，如果为True且未找到配置则抛出异常
        
    Returns:
        Any: 配置值
        
    Raises:
        ConfigurationError: 如果required为True但未找到配置
    """
    # 1. 从环境变量获取
    value = os.getenv(key)
    
    # 2. 如果环境变量中没有，从配置文件获取
    if value is None and key in _config:
        value = _config[key]
    
    # 3. 如果仍然没有，使用默认值
    if value is None:
        value = default
        
    # 4. 如果是必需的且未找到，抛出异常
    if value is None and required:
        raise ConfigurationError(f"缺失必需的配置项: {key}")
    
    # 5. 如果值是带引号的字符串，去除引号
    if isinstance(value, str) and value.startswith("'") and value.endswith("'"):
        value = value[1:-1]
    elif isinstance(value, str) and value.startswith('"') and value.endswith('"'):
        value = value[1:-1]
        
    return value


# 获取必需的 Spotify API 凭据
SPOTIPY_CLIENT_ID: Final[str] = get_config("SPOTIPY_CLIENT_ID", required=True)
SPOTIPY_CLIENT_SECRET: Final[str] = get_config("SPOTIPY_CLIENT_SECRET", required=True)
SPOTIPY_REDIRECT_URI: Final[str] = get_config("SPOTIPY_REDIRECT_URI", required=True)

# 日志相关配置
# 获取日志级别并设置默认值
_raw_log_level: Final[str] = get_config("LOG_LEVEL", "INFO")
VALID_LOG_LEVELS: Final[list[str]] = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

# 处理 LOG_LEVEL，确保其为有效值，默认为 "INFO"
if _raw_log_level and _raw_log_level.upper() in VALID_LOG_LEVELS:
    LOG_LEVEL: Final[str] = _raw_log_level.upper()
else:
    LOG_LEVEL: Final[str] = "INFO"  # 默认日志级别
    if _raw_log_level:  # 如果设置了但无效
        print(
            f"警告: 提供了无效的 LOG_LEVEL '{_raw_log_level}'。默认使用 'INFO'。"
            f"有效的日志级别包括 {VALID_LOG_LEVELS}"
        )

# 日志文件配置
_log_to_file_raw = get_config("LOG_TO_FILE", "false")
LOG_TO_FILE: Final[bool] = _log_to_file_raw.lower() in ("true", "1", "yes", "y") if isinstance(_log_to_file_raw, str) else bool(_log_to_file_raw)
LOG_FILE_PATH: Final[Optional[str]] = get_config("LOG_FILE_PATH")

# 日志格式配置
LOG_FORMAT: Final[str] = get_config("LOG_FORMAT", "%(asctime)s [%(levelname)s] %(name)s: %(message)s")
LOG_DATE_FORMAT: Final[str] = get_config("LOG_DATE_FORMAT", "%Y-%m-%d %H:%M:%S")

# 其他日志相关的配置
_log_to_console_raw = get_config("LOG_TO_CONSOLE", "true")
LOG_TO_CONSOLE: Final[bool] = _log_to_console_raw.lower() in ("true", "1", "yes", "y") if isinstance(_log_to_console_raw, str) else bool(_log_to_console_raw)

# 日志特定模块的级别配置
# 例如：可以为 spotify.auth 模块单独设置日志级别为 "DEBUG"
# 格式: JSON字符串 {"module_name": "LEVEL"}，例如：{"spotify.auth": "DEBUG"}
LOG_LEVELS_PER_MODULE: Final[str] = get_config("LOG_LEVELS_PER_MODULE", "{}")

# API调用相关配置
API_CONCURRENT_REQUESTS: Final[int] = int(get_config("API_CONCURRENT_REQUESTS", "10"))
API_RATE_LIMIT_RETRIES: Final[int] = int(get_config("API_RATE_LIMIT_RETRIES", "3"))
API_BASE_DELAY: Final[float] = float(get_config("API_BASE_DELAY", "0.5"))
API_MAX_DELAY: Final[float] = float(get_config("API_MAX_DELAY", "10.0"))

# 搜索相关配置
SEARCH_LIMIT: Final[int] = int(get_config("SEARCH_LIMIT", "5"))  # 默认值改为5，获取适当数量的候选歌曲

def save_config(config: Dict[str, Any], path: Optional[str] = None) -> bool:
    """
    保存配置到文件
    
    Args:
        config: 要保存的配置字典
        path: 配置文件路径，如果未指定则使用默认路径
        
    Returns:
        bool: 是否成功保存
    """
    config_path = path or os.getenv("CONFIG_FILE_PATH", DEFAULT_CONFIG_PATH)
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except (FileNotFoundError, PermissionError) as e:
        print(f"无法保存配置文件 {config_path}: {e}")
        return False
