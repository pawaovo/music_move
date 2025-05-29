import os
import json
from typing import Final, Optional, Dict, Any, Union, List
from pathlib import Path

# 从现有的配置模块继承Spotify API凭据配置
from spotify_playlist_importer.core.config import (
    SPOTIPY_CLIENT_ID,
    SPOTIPY_CLIENT_SECRET,
    SPOTIPY_REDIRECT_URI,
    LOG_LEVEL
)

# 异步API默认配置
# 这些配置可以通过环境变量或配置文件覆盖
DEFAULT_ASYNC_CONFIG = {
    # 并发控制
    "CONCURRENT_LIMIT": 10,  # 并发API请求的最大数量
    
    # 速率限制处理和重试策略
    "MAX_RETRIES": 5,  # 请求失败时的最大重试次数
    "BASE_RETRY_DELAY": 0.5,  # 初始重试延迟（秒）
    "MAX_RETRY_DELAY": 60,  # 最大重试延迟（秒）
    
    # 缓存配置
    "USE_TOKEN_CACHE": True,  # 是否使用令牌缓存
    "TOKEN_CACHE_PATH": ".cache",  # 令牌缓存文件路径
    
    # 超时配置
    "CONNECT_TIMEOUT": 90,  # 连接超时（秒）
    "REQUEST_TIMEOUT": 300,  # 请求超时（秒）
    
    # 搜索配置
    "SPOTIFY_SEARCH_LIMIT": 3,  # 每次搜索返回的最大结果数量
    
    # 批处理配置
    "BATCH_SIZE": 50,  # 批处理大小
    "MAX_CONCURRENCY": 10,  # 最大并发数
    "CACHE_PARSED_SONGS": True,  # 是否缓存解析结果
    "PREPROCESS_ALL": True,  # 是否预处理所有歌曲
}

# 配置文件路径
CONFIG_FILE_PATH = "api_config.json"


class AsyncConfigManager:
    """
    异步API配置管理器，负责加载和管理异步API的配置
    """
    
    def __init__(self, config_file_path: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            config_file_path: 配置文件路径，默认为api_config.json
        """
        self.config_file_path = config_file_path or CONFIG_FILE_PATH
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        加载配置，优先级：环境变量 > 配置文件 > 默认值
        
        Returns:
            Dict[str, Any]: 合并后的配置字典
        """
        # 从默认配置开始
        config = DEFAULT_ASYNC_CONFIG.copy()
        
        # 加载配置文件
        file_config = self._load_config_from_file()
        if file_config:
            # 处理嵌套配置，如批处理配置
            if "BATCH_PROCESSING" in file_config:
                batch_config = file_config.pop("BATCH_PROCESSING", {})
                if "BATCH_SIZE" in batch_config:
                    config["BATCH_SIZE"] = batch_config["BATCH_SIZE"]
                if "MAX_CONCURRENCY" in batch_config:
                    config["MAX_CONCURRENCY"] = batch_config["MAX_CONCURRENCY"]
                if "CACHE_PARSED_SONGS" in batch_config:
                    config["CACHE_PARSED_SONGS"] = batch_config["CACHE_PARSED_SONGS"]
                if "PREPROCESS_ALL" in batch_config:
                    config["PREPROCESS_ALL"] = batch_config["PREPROCESS_ALL"]
            
            config.update(file_config)
        
        # 从环境变量加载配置（优先级最高）
        env_config = self._load_config_from_env()
        config.update(env_config)
        
        return config
    
    def _load_config_from_file(self) -> Dict[str, Any]:
        """
        从配置文件加载配置
        
        Returns:
            Dict[str, Any]: 配置文件中的配置，如果文件不存在则返回空字典
        """
        if not Path(self.config_file_path).exists():
            return {}
            
        try:
            with open(self.config_file_path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def _load_config_from_env(self) -> Dict[str, Any]:
        """
        从环境变量加载配置
        
        Returns:
            Dict[str, Any]: 从环境变量加载的配置
        """
        env_config = {}
        
        # 映射环境变量名到配置键
        env_mapping = {
            "SPOTIFY_CONCURRENT_LIMIT": "CONCURRENT_LIMIT",
            "SPOTIFY_MAX_RETRIES": "MAX_RETRIES",
            "SPOTIFY_BASE_RETRY_DELAY": "BASE_RETRY_DELAY",
            "SPOTIFY_MAX_RETRY_DELAY": "MAX_RETRY_DELAY",
            "SPOTIFY_USE_TOKEN_CACHE": "USE_TOKEN_CACHE",
            "SPOTIFY_TOKEN_CACHE_PATH": "TOKEN_CACHE_PATH",
            "SPOTIFY_CONNECT_TIMEOUT": "CONNECT_TIMEOUT",
            "SPOTIFY_REQUEST_TIMEOUT": "REQUEST_TIMEOUT",
            "SPOTIFY_SEARCH_LIMIT": "SPOTIFY_SEARCH_LIMIT",
            "SPOTIFY_BATCH_SIZE": "BATCH_SIZE",
            "SPOTIFY_MAX_CONCURRENCY": "MAX_CONCURRENCY",
            "SPOTIFY_CACHE_PARSED_SONGS": "CACHE_PARSED_SONGS",
            "SPOTIFY_PREPROCESS_ALL": "PREPROCESS_ALL",
        }
        
        # 从环境变量加载配置
        for env_name, config_key in env_mapping.items():
            if env_value := os.getenv(env_name):
                # 根据默认值的类型转换环境变量值
                default_value = DEFAULT_ASYNC_CONFIG.get(config_key)
                if isinstance(default_value, bool):
                    env_config[config_key] = env_value.lower() in ("true", "1", "yes")
                elif isinstance(default_value, int):
                    env_config[config_key] = int(env_value)
                elif isinstance(default_value, float):
                    env_config[config_key] = float(env_value)
                else:
                    env_config[config_key] = env_value
        
        return env_config
    
    def save_config_to_file(self) -> None:
        """
        将当前配置保存到配置文件
        """
        try:
            with open(self.config_file_path, "w") as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            import sys
            print(f"保存配置到文件失败: {e}", file=sys.stderr)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键
            default: 如果键不存在，返回的默认值
            
        Returns:
            Any: 配置值或默认值
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        设置配置值
        
        Args:
            key: 配置键
            value: 配置值
        """
        self.config[key] = value
    
    def get_all(self) -> Dict[str, Any]:
        """
        获取所有配置
        
        Returns:
            Dict[str, Any]: 所有配置的副本
        """
        return self.config.copy()


# 创建全局配置管理器实例
async_config = AsyncConfigManager()

# 导出配置值，方便其他模块直接导入使用
CONCURRENT_LIMIT: Final[int] = async_config.get("CONCURRENT_LIMIT")
MAX_RETRIES: Final[int] = async_config.get("MAX_RETRIES")
BASE_RETRY_DELAY: Final[float] = async_config.get("BASE_RETRY_DELAY")
MAX_RETRY_DELAY: Final[float] = async_config.get("MAX_RETRY_DELAY")
USE_TOKEN_CACHE: Final[bool] = async_config.get("USE_TOKEN_CACHE")
TOKEN_CACHE_PATH: Final[str] = async_config.get("TOKEN_CACHE_PATH")
CONNECT_TIMEOUT: Final[int] = async_config.get("CONNECT_TIMEOUT")
REQUEST_TIMEOUT: Final[int] = async_config.get("REQUEST_TIMEOUT")
SPOTIFY_SEARCH_LIMIT: Final[int] = async_config.get("SPOTIFY_SEARCH_LIMIT")
BATCH_SIZE: Final[int] = async_config.get("BATCH_SIZE")
MAX_CONCURRENCY: Final[int] = async_config.get("MAX_CONCURRENCY")
CACHE_PARSED_SONGS: Final[bool] = async_config.get("CACHE_PARSED_SONGS")
PREPROCESS_ALL: Final[bool] = async_config.get("PREPROCESS_ALL")


def get_async_config() -> Dict[str, Any]:
    """
    获取异步API的配置
    
    Returns:
        Dict[str, Any]: 异步API配置
    """
    return async_config.get_all()


def save_async_config(config: Dict[str, Any]) -> None:
    """
    保存异步API配置
    
    Args:
        config: 要保存的配置字典
    """
    for key, value in config.items():
        async_config.set(key, value)
    async_config.save_config_to_file() 