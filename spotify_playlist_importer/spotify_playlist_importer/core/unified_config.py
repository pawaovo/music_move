"""
统一配置管理模块

整合所有配置到一个地方，包括：
- Spotify API认证
- 异步API调用参数
- 日志配置
- 字符串匹配配置
- 括号内容匹配配置
"""

import os
import json
import logging
from pathlib import Path
from typing import Any, Dict, Final, List, Optional, Set, Union

from dotenv import load_dotenv

# 加载 .env 文件中的环境变量（如果存在）
load_dotenv()

# 默认配置文件路径
DEFAULT_CONFIG_PATH = "config.json"


class ConfigurationError(Exception):
    """自定义异常，用于处理缺失或无效的配置。"""
    pass


class UnifiedConfigManager:
    """
    统一配置管理器，负责管理所有配置，支持从不同来源加载配置
    """
    
    def __init__(self, config_file_path: Optional[str] = None):
        """
        初始化统一配置管理器
        
        Args:
            config_file_path: 配置文件路径，默认为当前目录下的config.json
        """
        # 配置文件路径优先级：
        # 1. 传入参数
        # 2. 环境变量CONFIG_FILE_PATH
        # 3. 默认值DEFAULT_CONFIG_PATH
        self.config_file_path = config_file_path or os.getenv("CONFIG_FILE_PATH", DEFAULT_CONFIG_PATH)
        
        # 默认配置
        self.default_config = {
            # Spotify API认证
            "SPOTIPY_CLIENT_ID": "",  # 必须提供
            "SPOTIPY_CLIENT_SECRET": "",  # 必须提供
            "SPOTIPY_REDIRECT_URI": "http://localhost:8888/callback",  # 必须提供
            
            # 日志配置
            "LOG_LEVEL": "INFO",
            "LOG_TO_FILE": False,
            "LOG_FILE_PATH": "spotify_importer.log",
            "LOG_FORMAT": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            "LOG_DATE_FORMAT": "%Y-%m-%d %H:%M:%S",
            "LOG_TO_CONSOLE": True,
            "LOG_LEVELS_PER_MODULE": "{}",
            
            # 异步API调用参数
            "CONCURRENT_LIMIT": 10,  # 并发API请求的最大数量
            "MAX_RETRIES": 5,  # 请求失败时的最大重试次数
            "BASE_RETRY_DELAY": 0.5,  # 初始重试延迟（秒）
            "MAX_RETRY_DELAY": 60.0,  # 最大重试延迟（秒）
            "USE_TOKEN_CACHE": True,  # 是否使用令牌缓存
            "TOKEN_CACHE_PATH": ".cache",  # 令牌缓存文件路径
            "CONNECT_TIMEOUT": 30,  # 连接超时（秒）
            "REQUEST_TIMEOUT": 120,  # 请求超时（秒）
            
            # 搜索配置
            "SPOTIFY_SEARCH_LIMIT": 5,  # 每次搜索返回的最大结果数量
            
            # 文本归一化配置
            "TEXT_NORMALIZATION": {
                "TRADITIONAL_TO_SIMPLIFIED": True,  # 繁体转简体
                "LOWERCASE": True,  # 转为小写
                "NORMALIZE_SPACES": True,  # 标准化空格
                "NORMALIZE_SEPARATORS": True,  # 标准化分隔符（连字符、斜杠等）
                "REMOVE_PATTERNS": [  # 要移除的正则表达式模式
                    r"\([^)]*\)",  # 小括号内容
                    r"\[[^]]*\]",  # 中括号内容
                ],
                "REPLACE_PATTERNS": {  # 要替换的正则表达式模式及其替换值
                    r"&": " and ",
                    r"\bft\b\.?": "featuring",
                    r"\bfeat\b\.?": "featuring",
                }
            },
            
            # 字符串匹配配置
            "STRING_MATCHING": {
                "TITLE_WEIGHT": 0.6,  # 标题在匹配中的权重
                "ARTIST_WEIGHT": 0.4,  # 艺术家在匹配中的权重
                "THRESHOLD": 75.0,  # 匹配阈值
                "TOP_K": 3,  # 返回的最佳匹配数量
            },
            
            # 括号内容匹配配置
            "BRACKET_MATCHING": {
                "BRACKET_WEIGHT": 0.3,  # 括号内容在匹配中的权重
                "KEYWORD_BONUS": 5.0,  # 关键词匹配的额外分数
                "THRESHOLD": 70.0,  # 括号内容匹配阈值
                "KEYWORDS": {  # 括号内常见关键词及其权重
                    "live": 6.0,
                    "acoustic": 6.0,
                    "remix": 8.0,
                    "piano": 5.0,
                    "instrumental": 7.0,
                    "karaoke": 7.0,
                    "cover": 4.0,
                    "version": 2.0,
                    "remaster": 3.0,
                    "remastered": 3.0,
                    "deluxe": 2.0,
                    "single": 3.0,
                    "album": 2.0,
                    "ep": 2.0,
                    "original": 2.0,
                    "feat": 5.0,
                    "featuring": 5.0,
                    "ft": 5.0,
                    "extended": 2.0,
                    "edit": 1.0,
                    "radio": 1.5,
                    "explicit": 1.0,
                    "clean": 1.0,
                    "bonus": 1.0,
                    "track": 1.0,
                }
            },
            
            # 增强匹配配置
            "ENHANCED_MATCHING": {
                "FIRST_STAGE_THRESHOLD": 60.0,  # 第一阶段匹配阈值
                "SECOND_STAGE_THRESHOLD": 70.0,  # 第二阶段匹配阈值
            }
        }
        
        # 加载配置
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        加载配置，优先级：环境变量 > 配置文件 > 默认值
        
        Returns:
            Dict[str, Any]: 合并后的配置字典
        """
        # 从默认配置开始
        config = self._deep_copy_dict(self.default_config)
        
        # 加载配置文件
        file_config = self._load_config_from_file()
        if file_config:
            self._deep_update_dict(config, file_config)
        
        # 从环境变量加载配置（优先级最高）
        env_config = self._load_config_from_env()
        self._deep_update_dict(config, env_config)
        
        # 验证必需的配置
        self._validate_required_config(config)
        
        return config
    
    def _deep_copy_dict(self, d: Dict) -> Dict:
        """
        深度复制字典
        
        Args:
            d: 要复制的字典
            
        Returns:
            Dict: 复制后的字典
        """
        result = {}
        for key, value in d.items():
            if isinstance(value, dict):
                result[key] = self._deep_copy_dict(value)
            else:
                result[key] = value
        return result
    
    def _deep_update_dict(self, target: Dict, source: Dict) -> None:
        """
        深度更新字典
        
        Args:
            target: 目标字典
            source: 源字典，用于更新目标字典
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_update_dict(target[key], value)
            else:
                target[key] = value
    
    def _load_config_from_file(self) -> Dict[str, Any]:
        """
        从配置文件加载配置
        
        Returns:
            Dict[str, Any]: 配置文件中的配置，如果文件不存在则返回空字典
        """
        if not os.path.exists(self.config_file_path):
            logging.info(f"配置文件 {self.config_file_path} 不存在")
            return {}
            
        try:
            with open(self.config_file_path, "r", encoding="utf-8") as f:
                file_config = json.load(f)
                logging.info(f"从 {self.config_file_path} 加载了配置")
                return file_config
        except (json.JSONDecodeError, FileNotFoundError, PermissionError) as e:
            logging.error(f"加载配置文件 {self.config_file_path} 失败: {e}")
            return {}
    
    def _load_config_from_env(self) -> Dict[str, Any]:
        """
        从环境变量加载配置，支持嵌套配置，例如：
        - 直接的配置项：SPOTIFY_CLIENT_ID
        - 嵌套的配置项：STRING_MATCHING_TITLE_WEIGHT
        
        Returns:
            Dict[str, Any]: 从环境变量加载的配置
        """
        env_config: Dict[str, Any] = {}
        
        # 处理所有环境变量
        for env_name, env_value in os.environ.items():
            # 跳过不相关的环境变量
            if not env_name.startswith(tuple(self.default_config.keys())):
                continue
                
            parts = env_name.split("_")
            current_dict = env_config
            
            # 处理直接的配置项
            if env_name in self.default_config:
                env_config[env_name] = self._convert_value(
                    env_value, 
                    self.default_config[env_name]
                )
                continue
            
            # 处理嵌套的配置项
            i = 0
            while i < len(parts):
                section = parts[i]
                
                # 尝试找到嵌套项的最深层级
                if section in self.default_config:
                    parent_key = section
                    section_keys = []
                    
                    # 收集所有可能的子键
                    for j in range(i + 1, len(parts)):
                        section_key = "_".join(parts[i+1:j+1])
                        if section_key in self.default_config[parent_key]:
                            section_keys = parts[i+1:j+1]
                            i = j
                            break
                    
                    if section_keys:
                        # 确保路径中的所有字典都存在
                        current = env_config
                        if parent_key not in current:
                            current[parent_key] = {}
                        current = current[parent_key]
                        
                        # 为嵌套配置项创建路径
                        for k in range(len(section_keys) - 1):
                            key = section_keys[k]
                            if key not in current:
                                current[key] = {}
                            current = current[key]
                        
                        # 设置最终值
                        final_key = section_keys[-1]
                        default_value = self._get_nested_value(
                            self.default_config, 
                            [parent_key] + section_keys
                        )
                        current[final_key] = self._convert_value(env_value, default_value)
                        break
                
                i += 1
        
        return env_config
    
    def _get_nested_value(self, d: Dict, keys: List[str]) -> Any:
        """
        获取嵌套字典中的值
        
        Args:
            d: 嵌套字典
            keys: 键路径
            
        Returns:
            Any: 嵌套值，如果不存在则返回None
        """
        current = d
        for key in keys:
            if key in current and isinstance(current, dict):
                current = current[key]
            else:
                return None
        return current
    
    def _convert_value(self, value: str, default_value: Any) -> Any:
        """
        根据默认值的类型转换字符串值
        
        Args:
            value: 字符串值
            default_value: 默认值，用于确定目标类型
            
        Returns:
            Any: 转换后的值
        """
        if default_value is None:
            return value
            
        if isinstance(default_value, bool):
            return value.lower() in ("true", "1", "yes", "y")
        elif isinstance(default_value, int):
            try:
                return int(value)
            except ValueError:
                return default_value
        elif isinstance(default_value, float):
            try:
                return float(value)
            except ValueError:
                return default_value
        elif isinstance(default_value, dict):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return default_value
        elif isinstance(default_value, list):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                # 尝试按逗号分隔
                return [item.strip() for item in value.split(",")]
        else:
            return value
    
    def _validate_required_config(self, config: Dict[str, Any]) -> None:
        """
        验证必需的配置项
        
        Args:
            config: 配置字典
            
        Raises:
            ConfigurationError: 如果缺少必需的配置项
        """
        # 验证必需的Spotify API凭据
        required_fields = ["SPOTIPY_CLIENT_ID", "SPOTIPY_CLIENT_SECRET", "SPOTIPY_REDIRECT_URI"]
        missing_fields = [field for field in required_fields if not config.get(field)]
        
        if missing_fields:
            raise ConfigurationError(f"缺少必需的配置项: {', '.join(missing_fields)}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值，支持使用点符号访问嵌套配置，例如：
        - 直接的配置项：SPOTIFY_CLIENT_ID
        - 嵌套的配置项：STRING_MATCHING.TITLE_WEIGHT
        
        Args:
            key: 配置键，支持点符号表示嵌套键
            default: 如果键不存在，返回的默认值
            
        Returns:
            Any: 配置值或默认值
        """
        if "." in key:
            parts = key.split(".")
            current = self.config
            for part in parts:
                if part in current and isinstance(current, dict):
                    current = current[part]
                else:
                    return default
            return current
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        设置配置值，支持使用点符号访问嵌套配置
        
        Args:
            key: 配置键，支持点符号表示嵌套键
            value: 配置值
        """
        if "." in key:
            parts = key.split(".")
            current = self.config
            for i, part in enumerate(parts[:-1]):
                if part not in current:
                    current[part] = {}
                current = current[part]
            current[parts[-1]] = value
        else:
            self.config[key] = value
    
    def get_all(self) -> Dict[str, Any]:
        """
        获取所有配置
        
        Returns:
            Dict[str, Any]: 所有配置的副本
        """
        return self._deep_copy_dict(self.config)
    
    def save_to_file(self, file_path: Optional[str] = None) -> bool:
        """
        将配置保存到文件
        
        Args:
            file_path: 配置文件路径，如果为None则使用当前的配置文件路径
            
        Returns:
            bool: 是否成功保存
        """
        path = file_path or self.config_file_path
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            logging.info(f"配置已保存到 {path}")
            return True
        except (FileNotFoundError, PermissionError) as e:
            logging.error(f"保存配置到 {path} 失败: {e}")
            return False
    
    def create_example_config(self, file_path: str = "config.example.json") -> bool:
        """
        创建示例配置文件
        
        Args:
            file_path: 示例配置文件路径
            
        Returns:
            bool: 是否成功创建
        """
        example_config = self._deep_copy_dict(self.default_config)
        
        # 移除敏感信息
        if "SPOTIPY_CLIENT_ID" in example_config:
            example_config["SPOTIPY_CLIENT_ID"] = "your_spotify_client_id"
        if "SPOTIPY_CLIENT_SECRET" in example_config:
            example_config["SPOTIPY_CLIENT_SECRET"] = "your_spotify_client_secret"
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(example_config, f, ensure_ascii=False, indent=2)
            logging.info(f"示例配置已保存到 {file_path}")
            return True
        except (FileNotFoundError, PermissionError) as e:
            logging.error(f"保存示例配置到 {file_path} 失败: {e}")
            return False


# 创建全局配置管理器实例
config_manager = UnifiedConfigManager()

# 为方便直接导入配置值，提供以下导出变量
SPOTIPY_CLIENT_ID: Final[str] = config_manager.get("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET: Final[str] = config_manager.get("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI: Final[str] = config_manager.get("SPOTIPY_REDIRECT_URI")

# 日志配置
LOG_LEVEL: Final[str] = config_manager.get("LOG_LEVEL")
LOG_TO_FILE: Final[bool] = config_manager.get("LOG_TO_FILE")
LOG_FILE_PATH: Final[Optional[str]] = config_manager.get("LOG_FILE_PATH")
LOG_FORMAT: Final[str] = config_manager.get("LOG_FORMAT")
LOG_DATE_FORMAT: Final[str] = config_manager.get("LOG_DATE_FORMAT")
LOG_TO_CONSOLE: Final[bool] = config_manager.get("LOG_TO_CONSOLE")
LOG_LEVELS_PER_MODULE: Final[str] = config_manager.get("LOG_LEVELS_PER_MODULE")

# 异步API配置
CONCURRENT_LIMIT: Final[int] = config_manager.get("CONCURRENT_LIMIT")
MAX_RETRIES: Final[int] = config_manager.get("MAX_RETRIES")
BASE_RETRY_DELAY: Final[float] = config_manager.get("BASE_RETRY_DELAY")
MAX_RETRY_DELAY: Final[float] = config_manager.get("MAX_RETRY_DELAY")
USE_TOKEN_CACHE: Final[bool] = config_manager.get("USE_TOKEN_CACHE")
TOKEN_CACHE_PATH: Final[str] = config_manager.get("TOKEN_CACHE_PATH")
CONNECT_TIMEOUT: Final[int] = config_manager.get("CONNECT_TIMEOUT")
REQUEST_TIMEOUT: Final[int] = config_manager.get("REQUEST_TIMEOUT")

# 搜索配置
SPOTIFY_SEARCH_LIMIT: Final[int] = config_manager.get("SPOTIFY_SEARCH_LIMIT", 5)  # 每次搜索返回的最大结果数量

# 字符串匹配配置
STRING_MATCHING_TITLE_WEIGHT: Final[float] = config_manager.get("STRING_MATCHING.TITLE_WEIGHT")
STRING_MATCHING_ARTIST_WEIGHT: Final[float] = config_manager.get("STRING_MATCHING.ARTIST_WEIGHT")
STRING_MATCHING_THRESHOLD: Final[float] = config_manager.get("STRING_MATCHING.THRESHOLD")
STRING_MATCHING_TOP_K: Final[int] = config_manager.get("STRING_MATCHING.TOP_K")

# 括号内容匹配配置
BRACKET_MATCHING_WEIGHT: Final[float] = config_manager.get("BRACKET_MATCHING.BRACKET_WEIGHT")
BRACKET_MATCHING_KEYWORD_BONUS: Final[float] = config_manager.get("BRACKET_MATCHING.KEYWORD_BONUS")
BRACKET_MATCHING_THRESHOLD: Final[float] = config_manager.get("BRACKET_MATCHING.THRESHOLD")
BRACKET_MATCHING_KEYWORDS: Final[Dict[str, float]] = config_manager.get("BRACKET_MATCHING.KEYWORDS", {})

# 增强匹配配置
ENHANCED_MATCHING_FIRST_STAGE_THRESHOLD: Final[float] = config_manager.get("ENHANCED_MATCHING.FIRST_STAGE_THRESHOLD")
ENHANCED_MATCHING_SECOND_STAGE_THRESHOLD: Final[float] = config_manager.get("ENHANCED_MATCHING.SECOND_STAGE_THRESHOLD")


def get_config() -> Dict[str, Any]:
    """
    获取完整配置
    
    Returns:
        Dict[str, Any]: 完整配置的副本
    """
    return config_manager.get_all()


def save_config(config: Dict[str, Any], path: Optional[str] = None) -> bool:
    """
    保存配置到文件
    
    Args:
        config: 要保存的配置字典
        path: 配置文件路径，如果为None则使用当前的配置文件路径
        
    Returns:
        bool: 是否成功保存
    """
    # 更新配置
    for key, value in config.items():
        config_manager.set(key, value)
    
    # 保存到文件
    return config_manager.save_to_file(path)


def create_example_config(file_path: str = "config.example.json") -> bool:
    """
    创建示例配置文件
    
    Args:
        file_path: 示例配置文件路径
        
    Returns:
        bool: 是否成功创建
    """
    return config_manager.create_example_config(file_path) 