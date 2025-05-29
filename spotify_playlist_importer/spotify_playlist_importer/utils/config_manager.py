#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
应用程序配置管理模块。

此模块提供了统一的配置管理功能，包括：
1. 从配置文件、环境变量和默认值加载配置
2. 保存配置到文件
3. 验证配置的有效性
4. 提供配置的访问和修改接口

配置优先级：环境变量 > 配置文件 > 默认值
"""

import os
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union, List, TypeVar, Generic, cast
import sys

# 设置日志
logger = logging.getLogger(__name__)

# 默认配置文件路径
DEFAULT_CONFIG_PATH = "spotify_config.json"

# 默认配置值
DEFAULT_CONFIG = {
    # API 相关配置
    "API_CONCURRENT_REQUESTS": 10,           # 并发请求数量
    "API_RATE_LIMIT_RETRIES": 5,             # API速率限制重试次数
    "API_BASE_DELAY": 0.5,                   # 重试基础延迟（秒）
    "API_MAX_DELAY": 10.0,                   # 最大重试延迟（秒）
    "API_MAX_RETRIES": 12,                   # API 请求的最大重试次数
    "API_RETRY_BASE_DELAY_SECONDS": 3.0,     # 重试的基础延迟时间（指数退避起点）
    "API_RETRY_MAX_DELAY_SECONDS": 60.0,     # 重试的最大延迟时间
    "API_TOTAL_TIMEOUT_PER_CALL_SECONDS": 100, # 单个API调用的总超时时间
    
    # 搜索相关配置
    "SPOTIFY_SEARCH_LIMIT": 3,               # 每次搜索返回的最大结果数量（影响匹配准确性和API请求数），默认值改为3
    
    # 批处理相关配置
    "BATCH_SIZE": 50,                        # 批处理大小
    "CONCURRENCY_LIMIT": 10,                 # 并发限制
    
    # 日志相关配置
    "LOG_LEVEL": "INFO",                     # 日志级别
    "LOG_TO_FILE": False,                    # 是否输出日志到文件
    "LOG_FILE_PATH": "spotify_importer.log", # 日志文件路径
    
    # 匹配相关配置
    "TITLE_WEIGHT": 0.7,                     # 标题匹配权重（调整为0.7，更重视标题匹配）
    "ARTIST_WEIGHT": 0.3,                    # 艺术家匹配权重（调整为0.3，配合标题权重）
    "MATCH_THRESHOLD": 70.0,                 # 匹配阈值
    
    # 括号内容匹配配置
    "BRACKET_WEIGHT": 0.3,                   # 括号内容匹配权重
    "KEYWORD_BONUS": 5.0,                    # 关键词匹配加分
    "BRACKET_THRESHOLD": 70.0,               # 括号内容匹配阈值
    
    # 增强匹配配置
    "FIRST_STAGE_THRESHOLD": 60.0,           # 第一阶段匹配阈值
    "SECOND_STAGE_THRESHOLD": 70.0,          # 第二阶段匹配阈值
    
    # 其他配置
    "CACHE_ENABLED": True,                   # 是否启用缓存
    "CACHE_DIR": ".cache",                   # 缓存目录
}


class ConfigValidationError(Exception):
    """配置验证错误"""
    pass


class ConfigManager:
    """配置管理器类"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径，如果为None则使用默认路径
        """
        self.config_path = config_path or DEFAULT_CONFIG_PATH
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """
        加载配置，优先级：环境变量 > 配置文件 > 默认值
        
        Returns:
            Dict[str, Any]: 合并后的配置字典
        """
        # 从默认配置开始
        config = DEFAULT_CONFIG.copy()
        
        # 从配置文件加载
        file_config = self._load_from_file()
        if file_config:
            config.update(file_config)
            
        # 从环境变量加载
        env_config = self._load_from_env()
        config.update(env_config)
        
        # 验证配置
        self._validate_config(config)
        
        return config
    
    def _load_from_file(self) -> Dict[str, Any]:
        """
        从配置文件加载配置
        
        Returns:
            Dict[str, Any]: 配置文件中的配置，如果文件不存在或无法解析则返回空字典
        """
        if not os.path.exists(self.config_path):
            logger.debug(f"配置文件 {self.config_path} 不存在")
            return {}
            
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                logger.debug(f"正在从 {self.config_path} 加载配置")
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError, PermissionError) as e:
            logger.warning(f"无法加载配置文件 {self.config_path}: {e}")
            return {}
    
    def _load_from_env(self) -> Dict[str, Any]:
        """
        从环境变量加载配置
        
        Returns:
            Dict[str, Any]: 从环境变量加载的配置
        """
        env_config = {}
        
        # 环境变量前缀
        prefix = "SPOTIFY_"
        
        for key in DEFAULT_CONFIG:
            env_key = f"{prefix}{key}"
            env_value = os.environ.get(env_key)
            
            if env_value is not None:
                # 根据默认值的类型转换环境变量值
                default_value = DEFAULT_CONFIG[key]
                
                if isinstance(default_value, bool):
                    env_config[key] = env_value.lower() in ("true", "1", "yes", "y")
                elif isinstance(default_value, int):
                    env_config[key] = int(env_value)
                elif isinstance(default_value, float):
                    env_config[key] = float(env_value)
                else:
                    env_config[key] = env_value
                    
                logger.debug(f"从环境变量 {env_key} 加载配置: {key}={env_config[key]}")
                
        return env_config
    
    def _validate_config(self, config: Dict[str, Any]) -> None:
        """
        验证配置的有效性
        
        Args:
            config: 要验证的配置字典
            
        Raises:
            ConfigValidationError: 如果配置无效
        """
        # 验证日志级别
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if config["LOG_LEVEL"] not in valid_log_levels:
            warning_msg = f"无效的日志级别: {config['LOG_LEVEL']}, 使用默认值: INFO"
            logger.warning(warning_msg)
            config["LOG_LEVEL"] = "INFO"
        
        # 验证数值配置
        for key, value in config.items():
            if key in [
                "API_CONCURRENT_REQUESTS", 
                "API_RATE_LIMIT_RETRIES", 
                "SPOTIFY_SEARCH_LIMIT", 
                "BATCH_SIZE", 
                "CONCURRENCY_LIMIT",
                "API_MAX_RETRIES",
                "API_TOTAL_TIMEOUT_PER_CALL_SECONDS"
            ]:
                if not isinstance(value, int) or value <= 0:
                    warning_msg = f"无效的配置值: {key}={value}, 使用默认值: {DEFAULT_CONFIG[key]}"
                    logger.warning(warning_msg)
                    config[key] = DEFAULT_CONFIG[key]
            
            elif key in [
                "API_BASE_DELAY", 
                "API_MAX_DELAY", 
                "TITLE_WEIGHT", 
                "ARTIST_WEIGHT", 
                "BRACKET_WEIGHT", 
                "MATCH_THRESHOLD",
                "API_RETRY_BASE_DELAY_SECONDS",
                "API_RETRY_MAX_DELAY_SECONDS"
            ]:
                if not isinstance(value, (int, float)) or value < 0:
                    warning_msg = f"无效的配置值: {key}={value}, 使用默认值: {DEFAULT_CONFIG[key]}"
                    logger.warning(warning_msg)
                    config[key] = DEFAULT_CONFIG[key]
                    
        # 验证权重和阈值
        if config["TITLE_WEIGHT"] + config["ARTIST_WEIGHT"] != 1.0:
            warning_msg = "标题权重和艺术家权重之和应该等于1.0，将自动调整"
            logger.warning(warning_msg)
            # 按比例调整
            total = config["TITLE_WEIGHT"] + config["ARTIST_WEIGHT"]
            if total > 0:
                config["TITLE_WEIGHT"] = config["TITLE_WEIGHT"] / total
                config["ARTIST_WEIGHT"] = config["ARTIST_WEIGHT"] / total
            else:
                # 如果总和为0，使用默认值
                config["TITLE_WEIGHT"] = DEFAULT_CONFIG["TITLE_WEIGHT"]
                config["ARTIST_WEIGHT"] = DEFAULT_CONFIG["ARTIST_WEIGHT"]
    
    def save_config(self) -> bool:
        """
        保存配置到文件
        
        Returns:
            bool: 是否成功保存
        """
        try:
            # 创建目录（如果不存在）
            directory = os.path.dirname(self.config_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
                
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
                
            logger.info(f"配置已保存到 {self.config_path}")
            return True
        except (FileNotFoundError, PermissionError) as e:
            logger.error(f"无法保存配置到 {self.config_path}: {e}")
            return False
    
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
    
    def reset_to_defaults(self) -> None:
        """重置所有配置为默认值"""
        self.config = DEFAULT_CONFIG.copy()
        logger.info("配置已重置为默认值")
    
    def reset_key(self, key: str) -> None:
        """
        重置特定配置键为默认值
        
        Args:
            key: 配置键
        """
        if key in DEFAULT_CONFIG:
            self.config[key] = DEFAULT_CONFIG[key]
            logger.info(f"配置 {key} 已重置为默认值: {DEFAULT_CONFIG[key]}")
        else:
            logger.warning(f"未知的配置键: {key}")


# 创建全局配置管理器实例
config_manager = ConfigManager()


def get_config(key: str, default: Any = None) -> Any:
    """
    获取配置值
    
    Args:
        key: 配置键
        default: 如果键不存在，返回的默认值
        
    Returns:
        Any: 配置值或默认值
    """
    return config_manager.get(key, default)


def set_config(key: str, value: Any) -> None:
    """
    设置配置值
    
    Args:
        key: 配置键
        value: 配置值
    """
    config_manager.set(key, value)


def save_config() -> bool:
    """
    保存配置到文件
    
    Returns:
        bool: 是否成功保存
    """
    return config_manager.save_config()


def get_all_config() -> Dict[str, Any]:
    """
    获取所有配置
    
    Returns:
        Dict[str, Any]: 所有配置的副本
    """
    return config_manager.get_all()


def reset_config() -> None:
    """重置所有配置为默认值"""
    config_manager.reset_to_defaults()


def reset_config_key(key: str) -> None:
    """
    重置特定配置键为默认值
    
    Args:
        key: 配置键
    """
    config_manager.reset_key(key)


# 常用配置的快捷访问
API_CONCURRENT_REQUESTS = config_manager.get("API_CONCURRENT_REQUESTS")
API_RATE_LIMIT_RETRIES = config_manager.get("API_RATE_LIMIT_RETRIES")
API_BASE_DELAY = config_manager.get("API_BASE_DELAY")
API_MAX_DELAY = config_manager.get("API_MAX_DELAY")
SEARCH_LIMIT = config_manager.get("SPOTIFY_SEARCH_LIMIT")
BATCH_SIZE = config_manager.get("BATCH_SIZE")
CONCURRENCY_LIMIT = config_manager.get("CONCURRENCY_LIMIT")
LOG_LEVEL = config_manager.get("LOG_LEVEL")
TITLE_WEIGHT = config_manager.get("TITLE_WEIGHT")
ARTIST_WEIGHT = config_manager.get("ARTIST_WEIGHT")
BRACKET_WEIGHT = config_manager.get("BRACKET_WEIGHT")
MATCH_THRESHOLD = config_manager.get("MATCH_THRESHOLD") 