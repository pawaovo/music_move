#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
日志工具模块。

提供统一的日志配置和访问接口，支持：
1. 根据配置文件或环境变量设置日志级别
2. 控制台和文件双重输出
3. 丰富的日志记录格式
4. 各子模块日志的中央管理

使用方式：
```python
from spotify_playlist_importer.utils.logger import get_logger

logger = get_logger(__name__)
logger.debug("这是一条调试日志")
logger.info("这是一条信息日志")
logger.warning("这是一条警告日志")
logger.error("这是一条错误日志")
```
"""

import os
import sys
import logging
from typing import Dict, Optional, Any
from logging.handlers import RotatingFileHandler
import pathlib

from spotify_playlist_importer.utils.config_manager import get_config

# 全局日志器缓存，避免重复创建
_loggers: Dict[str, logging.Logger] = {}

# 日志级别映射
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL
}

# 日志格式
CONSOLE_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
FILE_FORMAT = "%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s"

# 日期格式
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def _create_console_handler(log_level: int) -> logging.StreamHandler:
    """
    创建控制台日志处理器
    
    Args:
        log_level: 日志级别
        
    Returns:
        logging.StreamHandler: 控制台日志处理器
    """
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    formatter = logging.Formatter(CONSOLE_FORMAT, datefmt=DATE_FORMAT)
    console_handler.setFormatter(formatter)
    return console_handler

def _create_file_handler(log_level: int, log_file: str) -> logging.Handler:
    """
    创建文件日志处理器
    
    Args:
        log_level: 日志级别
        log_file: 日志文件路径
        
    Returns:
        logging.Handler: 文件日志处理器
    """
    # 确保日志文件所在目录存在
    log_dir = os.path.dirname(log_file)
    if log_dir:
        pathlib.Path(log_dir).mkdir(parents=True, exist_ok=True)
        
    # 创建旋转文件处理器，限制单个日志文件最大5MB，最多保留5个备份
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=5*1024*1024,  # 5MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setLevel(log_level)
    formatter = logging.Formatter(FILE_FORMAT, datefmt=DATE_FORMAT)
    file_handler.setFormatter(formatter)
    return file_handler

def configure_root_logger() -> None:
    """配置根日志器"""
    # 获取日志配置
    log_level_str = get_config("LOG_LEVEL", "INFO")
    log_level = LOG_LEVELS.get(log_level_str.upper(), logging.INFO)
    
    # 配置根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # 移除已有的处理器，避免重复
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
        
    # 添加控制台处理器
    root_logger.addHandler(_create_console_handler(log_level))
    
    # 如果启用了文件日志，添加文件处理器
    log_to_file = get_config("LOG_TO_FILE", False)
    if log_to_file:
        log_file_path = get_config("LOG_FILE_PATH", "spotify_importer.log")
        root_logger.addHandler(_create_file_handler(log_level, log_file_path))
    
    # 防止日志传播到更高层级
    root_logger.propagate = False
    
    logging.info(f"已配置根日志器，级别: {log_level_str}, 文件日志: {'启用' if log_to_file else '禁用'}")

def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的日志器
    
    Args:
        name: 日志器名称，通常使用 __name__
        
    Returns:
        logging.Logger: 配置好的日志器
    """
    # 如果日志器已经存在于缓存中，直接返回
    if name in _loggers:
        return _loggers[name]
    
    # 确保根日志器已配置
    if not logging.getLogger().handlers:
        configure_root_logger()
    
    # 创建并配置模块日志器
    logger = logging.getLogger(name)
    
    # 获取日志配置
    log_level_str = get_config("LOG_LEVEL", "INFO")
    log_level = LOG_LEVELS.get(log_level_str.upper(), logging.INFO)
    
    # 设置日志级别
    logger.setLevel(log_level)
    
    # 如果需要，将所有处理器复制到此日志器
    # 通常不需要，因为默认会传播到根日志器
    # logger.handlers = logging.getLogger().handlers
    
    # 缓存日志器
    _loggers[name] = logger
    
    return logger

def set_log_level(level: str) -> None:
    """
    动态设置日志级别
    
    Args:
        level: 日志级别 ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
    """
    log_level = LOG_LEVELS.get(level.upper())
    if not log_level:
        logging.warning(f"无效的日志级别: {level}")
        return
    
    # 更新根日志器的级别
    logging.getLogger().setLevel(log_level)
    
    # 更新所有处理器的级别
    for handler in logging.getLogger().handlers:
        handler.setLevel(log_level)
    
    # 更新所有缓存的日志器的级别
    for logger in _loggers.values():
        logger.setLevel(log_level)
    
    logging.info(f"已将日志级别设置为: {level}")

def log_function_call(func):
    """
    装饰器：记录函数调用信息
    
    Args:
        func: 被装饰的函数
        
    Returns:
        装饰后的函数
    """
    logger = get_logger(func.__module__)
    
    def wrapper(*args, **kwargs):
        logger.debug(f"调用函数 {func.__name__}(args={args}, kwargs={kwargs})")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"函数 {func.__name__} 执行成功，返回: {result}")
            return result
        except Exception as e:
            logger.error(f"函数 {func.__name__} 执行失败: {e}", exc_info=True)
            raise
    
    return wrapper

def log_class_methods(cls):
    """
    装饰器：记录类的所有方法调用信息
    
    Args:
        cls: 被装饰的类
        
    Returns:
        装饰后的类
    """
    for attr_name in dir(cls):
        # 跳过特殊方法和私有方法
        if attr_name.startswith('__') or attr_name.startswith('_'):
            continue
            
        attr = getattr(cls, attr_name)
        if callable(attr):
            setattr(cls, attr_name, log_function_call(attr))
    
    return cls

# 如果直接运行此模块，进行测试
if __name__ == "__main__":
    # 配置根日志器
    configure_root_logger()
    
    # 获取当前模块的日志器
    logger = get_logger(__name__)
    
    # 测试不同级别的日志
    logger.debug("这是一条调试日志")
    logger.info("这是一条信息日志")
    logger.warning("这是一条警告日志")
    logger.error("这是一条错误日志")
    
    # 测试动态更改日志级别
    print("\n更改日志级别为DEBUG...\n")
    set_log_level("DEBUG")
    
    logger.debug("这是一条调试日志，应该可见")
    logger.info("这是一条信息日志")
    
    # 测试日志装饰器
    @log_function_call
    def test_function(arg1, arg2):
        print(f"函数执行：{arg1} + {arg2} = {arg1 + arg2}")
        return arg1 + arg2
    
    print("\n测试日志装饰器...\n")
    result = test_function(1, 2)
    print(f"函数返回值：{result}")
    
    # 测试异常记录
    print("\n测试异常记录...\n")
    try:
        test_function(1, "2")  # 将引发异常
    except TypeError:
        print("TypeErrorr已被记录")
        
    print("\n日志测试完成。") 