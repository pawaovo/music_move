#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Spotify客户端单例模块。

此模块实现了Spotify客户端的单例模式，确保整个应用程序中只使用一个
spotipy.Spotify实例，从而减少不必要的认证开销和提高性能。

关键特性:
- 线程安全的初始化
- 懒加载（仅在首次需要时创建实例）
- 错误处理机制
- 可通过重置方法刷新实例（例如令牌无效时）
"""

import threading
import logging
from typing import Optional
import time
import os

import spotipy
from spotipy.exceptions import SpotifyException

# 从auth模块导入获取认证管理器的函数
from spotify_playlist_importer.spotify.auth import get_spotify_client

# 尝试从相对路径导入logger
try:
    from ..utils.logger import get_logger
except ImportError:
    # 如果相对导入失败，则尝试完全路径导入
    try:
        from spotify_playlist_importer.utils.logger import get_logger
    except ImportError:
        # 如果仍然失败，使用标准logging作为备用
        import logging
        get_logger = lambda name: logging.getLogger(name)

# 获取日志器
logger = get_logger(__name__)


class SpotifyClientSingleton:
    """
    Spotify客户端单例类。
    
    确保整个应用程序只使用一个spotipy.Spotify实例，
    并且该实例的创建是线程安全的。
    """
    _instance: Optional[spotipy.Spotify] = None
    _lock = threading.Lock()
    _init_in_progress = False
    _init_done = threading.Event()

    @classmethod
    def get_instance(cls) -> spotipy.Spotify:
        """
        获取Spotify客户端单例实例。
        
        如果实例尚未创建，则创建一个新实例。
        该方法是线程安全的。
        
        Returns:
            spotipy.Spotify: Spotify客户端实例
            
        Raises:
            RuntimeError: 如果初始化失败
        """
        # 检查环境变量是否有缓存指示
        cache_path_from_env = os.environ.get("SPOTIFY_CACHE_PATH", "")
        
        # 如果有缓存文件且是有效的，直接使用缓存初始化客户端
        if cache_path_from_env and os.path.exists(cache_path_from_env):
            logger.info(f"从环境变量中发现缓存文件: {cache_path_from_env}")
            # 可以在这里直接基于缓存文件初始化客户端
        
        # 如果已经有实例，直接返回
        if cls._instance is not None:
            logger.debug("返回现有的Spotify客户端实例")
            return cls._instance
        
        # 如果正在初始化中，只等待很短时间
        if cls._init_in_progress:
            logger.debug("Spotify客户端正在初始化中...")
            # 只等待短暂时间，如果超时则继续并行初始化
            # 这减少了创建过程中的等待延迟
            wait_result = cls._init_done.wait(timeout=0.5)
            if wait_result and cls._instance is not None:
                return cls._instance
        
        # 如果实例为None且未在初始化中，获取锁并初始化
        with cls._lock:
            # 双重检查锁定模式，避免多线程下的重复初始化
            if cls._instance is None and not cls._init_in_progress:
                try:
                    # 设置初始化中标记
                    cls._init_in_progress = True
                    logger.info("初始化Spotify客户端单例实例...")
                    
                    # 立即清除旧的缓存文件,确保新的认证流程
                    if os.path.exists(".spotify_cache"):
                        try:
                            os.remove(".spotify_cache")
                            logger.info("已清除旧的缓存文件以加速认证")
                        except Exception as e:
                            logger.warning(f"清除缓存文件失败: {e}")
                    
                    # 调用auth模块获取Spotify客户端
                    spotify_client = get_spotify_client()
                    
                    # 验证客户端是否有效
                    if spotify_client is None:
                        raise RuntimeError("获取Spotify客户端实例失败")
                    
                    # 设置单例实例
                    cls._instance = spotify_client
                    logger.debug("Spotify客户端单例实例成功创建")
                    
                    # 标记初始化完成
                    cls._init_done.set()
                    return cls._instance
                    
                except Exception as e:
                    logger.error(f"创建Spotify客户端单例实例时出错: {e}")
                    # 清除初始化标记
                    cls._init_in_progress = False
                    # 重置事件
                    cls._init_done.clear()
                    raise RuntimeError(f"创建Spotify客户端单例实例失败: {e}")
                finally:
                    # 清除初始化中标记
                    cls._init_in_progress = False
        
        # 如果执行到这里，说明实例已创建但在初始化过程中被其他线程设置
        if cls._instance is not None:
            return cls._instance
        else:
            # 如果仍然为None，说明初始化出现了问题
            error_msg = "Spotify客户端实例初始化后仍为None，可能存在逻辑错误"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    @classmethod
    def reset_instance(cls) -> None:
        """
        重置Spotify客户端单例实例。
        
        在令牌失效或其他需要刷新实例的情况下使用。
        
        Note:
            此方法是线程安全的。
        """
        with cls._lock:
            logger.info("重置Spotify客户端单例实例")
            cls._instance = None
            cls._init_in_progress = False
            cls._init_done.clear()
            
            # 清除缓存文件
            if os.path.exists(".spotify_cache"):
                try:
                    os.remove(".spotify_cache")
                    logger.info("已清除缓存文件")
                except Exception as e:
                    logger.warning(f"清除缓存文件失败: {e}")


# 提供一个简单的函数接口，便于使用
def get_spotify_client_instance() -> spotipy.Spotify:
    """
    获取Spotify客户端单例实例的便捷函数。
    
    Returns:
        spotipy.Spotify: Spotify客户端实例
        
    Raises:
        RuntimeError: 如果初始化失败
    """
    return SpotifyClientSingleton.get_instance() 