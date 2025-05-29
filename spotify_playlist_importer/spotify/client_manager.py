"""
Spotify客户端管理模块

负责管理Spotify客户端实例，包括项目级别客户端和用户级别客户端。
项目级别客户端使用Client Credentials Flow获取访问令牌，用于不需要用户授权的操作（如搜索歌曲）。
用户级别客户端使用Authorization Code Flow获取和刷新访问令牌，用于需要用户授权的操作（如创建播放列表）。
"""

import logging
import os
import json
import time
import uuid
import threading
from typing import Dict, Optional, Any, Tuple, Union
from pathlib import Path
from datetime import datetime, timedelta

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from spotipy.exceptions import SpotifyException

from spotify_playlist_importer.core import config

# 配置日志
logger = logging.getLogger("spotify-client-manager")

# 项目级别客户端的缓存文件
PROJECT_TOKEN_CACHE_PATH = os.environ.get("PROJECT_TOKEN_CACHE_PATH", ".spotify_project_cache")

# 用户级别客户端的缓存文件
USER_TOKEN_CACHE_PATH = os.environ.get("USER_TOKEN_CACHE_PATH", ".spotify_cache")

# 用户令牌缓存目录
USER_TOKEN_CACHE_DIR = os.environ.get("USER_TOKEN_CACHE_DIR", ".spotify_user_tokens")

# Spotify授权范围
SPOTIFY_SCOPES = "user-read-private playlist-modify-public playlist-modify-private"

# 令牌刷新阈值（秒）- 当令牌剩余有效期小于此值时触发刷新
TOKEN_REFRESH_THRESHOLD = 300  # 5分钟

# 客户端单例和锁
_project_client: Optional[spotipy.Spotify] = None
_project_token_info: Dict[str, Any] = {}
_client_lock = threading.Lock()
_project_token_last_refresh = 0
_project_token_refresh_attempts = 0
_project_token_status = "uninitialized"  # uninitialized, valid, expired, refreshing, error

# 用户令牌缓存和锁
_user_tokens_lock = threading.Lock()
_user_tokens_cache: Dict[str, Dict[str, Any]] = {}

def _ensure_cache_dir():
    """确保用户令牌缓存目录存在"""
    if not os.path.exists(USER_TOKEN_CACHE_DIR):
        try:
            os.makedirs(USER_TOKEN_CACHE_DIR, exist_ok=True)
            logger.info(f"已创建用户令牌缓存目录: {USER_TOKEN_CACHE_DIR}")
        except Exception as e:
            logger.error(f"创建用户令牌缓存目录失败: {e}")

def _load_project_token_info() -> Dict[str, Any]:
    """
    加载项目级别令牌缓存
    
    Returns:
        Dict[str, Any]: 令牌信息
    """
    try:
        if os.path.exists(PROJECT_TOKEN_CACHE_PATH):
            with open(PROJECT_TOKEN_CACHE_PATH, "r") as f:
                token_info = json.load(f)
                # 验证令牌信息格式
                if not isinstance(token_info, dict) or not token_info.get('access_token'):
                    logger.warning("项目令牌缓存格式无效，将重新获取令牌")
                    return {}
                return token_info
    except Exception as e:
        logger.warning(f"无法加载项目令牌缓存: {e}")
    return {}

def _save_project_token_info(token_info: Dict[str, Any]) -> None:
    """
    保存项目级别令牌缓存
    
    Args:
        token_info: 令牌信息
    """
    global _project_token_status
    try:
        # 确保token_info包含必要的字段
        if not token_info.get('access_token'):
            logger.error("尝试保存无效的项目令牌信息")
            _project_token_status = "error"
            return
            
        with open(PROJECT_TOKEN_CACHE_PATH, "w") as f:
            json.dump(token_info, f)
        _project_token_status = "valid"
        logger.info("项目令牌信息已保存到缓存文件")
    except Exception as e:
        logger.warning(f"无法保存项目令牌缓存: {e}")
        _project_token_status = "error"

def get_project_spotify_client() -> spotipy.Spotify:
    """
    获取项目级别Spotify客户端（使用Client Credentials Flow）
    
    该客户端用于不需要用户授权的操作，如搜索歌曲。
    使用单例模式，确保在整个应用中只有一个客户端实例。
    实现了令牌自动刷新和错误重试机制。
    
    Returns:
        spotipy.Spotify: Spotify客户端实例
        
    Raises:
        RuntimeError: 如果多次尝试获取令牌都失败
    """
    global _project_client, _project_token_info, _project_token_last_refresh, _project_token_refresh_attempts, _project_token_status
    
    with _client_lock:
        now = int(time.time())
        
        # 检查是否需要刷新令牌
        needs_refresh = False
        
        # 如果已有客户端实例，检查令牌是否即将过期
        if _project_client is not None:
            token_expires_at = _project_token_info.get('expires_at', 0)
            is_token_expiring = token_expires_at - now < TOKEN_REFRESH_THRESHOLD
            
            if not is_token_expiring:
                # 令牌有效且未接近过期，返回现有客户端
                return _project_client
            
            # 令牌即将过期，记录并准备刷新
            logger.info(f"项目客户端令牌即将过期，剩余 {token_expires_at - now} 秒，准备刷新")
            needs_refresh = True
            _project_token_status = "refreshing"
        else:
            # 没有客户端实例，尝试从缓存加载令牌
            _project_token_info = _load_project_token_info()
            
            if _project_token_info and 'access_token' in _project_token_info:
                token_expires_at = _project_token_info.get('expires_at', 0)
                is_token_expired = token_expires_at - now < 60
                
                if not is_token_expired:
                    # 缓存中的令牌有效，创建客户端实例
                    try:
                        client_credentials_manager = SpotifyClientCredentials(
                            client_id=config.SPOTIPY_CLIENT_ID,
                            client_secret=config.SPOTIPY_CLIENT_SECRET
                        )
                        
                        # 修复：使用客户端凭证管理器创建 Spotify 客户端
                        _project_client = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
                        
                        # 获取访问令牌
                        token_info = client_credentials_manager.get_access_token(as_dict=True)
                        access_token = token_info.get('access_token')
                        expires_in = token_info.get('expires_in', 3600)  # 默认1小时
                        
                        # 保存令牌信息
                        _project_token_info = {
                            'access_token': access_token,
                            'expires_at': int(time.time()) + expires_in,
                            'token_type': 'Bearer',
                            'refresh_time': datetime.now().isoformat(),
                        }
                        
                        # 重置刷新计数
                        _project_token_refresh_attempts = 0
                        
                        # 保存到缓存文件
                        _save_project_token_info(_project_token_info)
                        
                        logger.info(f"已创建新的项目级别Spotify客户端，令牌有效期: {expires_in} 秒")
                        
                        return _project_client
                    except Exception as e:
                        logger.error(f"使用缓存令牌创建项目级别Spotify客户端失败: {e}")
                        needs_refresh = True
                else:
                    logger.info("缓存中的项目令牌已过期，将获取新令牌")
                    needs_refresh = True
            else:
                logger.info("未找到有效的项目令牌缓存，将获取新令牌")
                needs_refresh = True
        
        # 如果需要刷新或获取新令牌
        if needs_refresh:
            # 防止短时间内多次刷新
            if now - _project_token_last_refresh < 60 and _project_token_refresh_attempts > 3:
                logger.error(f"项目令牌刷新过于频繁，已尝试 {_project_token_refresh_attempts} 次")
                raise RuntimeError("项目令牌刷新过于频繁，请稍后再试")
            
            _project_token_last_refresh = now
            _project_token_refresh_attempts += 1
            
            # 创建新的客户端凭证管理器
            try:
                client_credentials_manager = SpotifyClientCredentials(
                    client_id=config.SPOTIPY_CLIENT_ID,
                    client_secret=config.SPOTIPY_CLIENT_SECRET
                )
                
                # 修复：使用客户端凭证管理器创建 Spotify 客户端
                _project_client = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
                
                # 获取访问令牌
                token_info = client_credentials_manager.get_access_token(as_dict=True)
                access_token = token_info.get('access_token')
                expires_in = token_info.get('expires_in', 3600)  # 默认1小时
                
                # 保存令牌信息
                _project_token_info = {
                    'access_token': access_token,
                    'expires_at': int(time.time()) + expires_in,
                    'token_type': 'Bearer',
                    'refresh_time': datetime.now().isoformat(),
                }
                
                # 重置刷新计数
                _project_token_refresh_attempts = 0
                
                # 保存到缓存文件
                _save_project_token_info(_project_token_info)
                
                logger.info(f"已创建新的项目级别Spotify客户端，令牌有效期: {expires_in} 秒")
                
                return _project_client
            except Exception as e:
                _project_token_status = "error"
                logger.error(f"创建项目级别Spotify客户端失败: {e}")
                # 如果这是第一次尝试，记录详细信息
                if _project_token_refresh_attempts <= 1:
                    logger.error(f"项目令牌获取失败详情: Client ID: {config.SPOTIPY_CLIENT_ID[:5]}***, 尝试次数: {_project_token_refresh_attempts}")
                raise RuntimeError(f"无法获取Spotify项目令牌: {str(e)}")

def get_auth_manager(session_id: Optional[str] = None) -> SpotifyOAuth:
    """
    创建并返回SpotifyOAuth认证管理器实例
    
    该管理器用于用户授权流程（Authorization Code Flow）。
    如果提供了session_id，则使用特定于该会话的缓存路径。
    
    Args:
        session_id: 可选的会话ID，用于多用户环境下的令牌隔离
        
    Returns:
        SpotifyOAuth: 认证管理器实例
    """
    # 从环境变量获取重定向URI，否则使用默认值
    redirect_uri = os.environ.get("SPOTIFY_REDIRECT_URI", "http://127.0.0.1:8888/callback")
    
    # 确定缓存路径
    cache_path = USER_TOKEN_CACHE_PATH
    if session_id:
        _ensure_cache_dir()
        cache_path = os.path.join(USER_TOKEN_CACHE_DIR, f"spotify_token_{session_id}")
    
    # 记录当前使用的重定向URI和缓存路径
    logger.info(f"使用Spotify重定向URI: {redirect_uri}, 缓存路径: {cache_path}")
    
    return SpotifyOAuth(
        client_id=config.SPOTIPY_CLIENT_ID,
        client_secret=config.SPOTIPY_CLIENT_SECRET,
        redirect_uri=redirect_uri,
        scope=SPOTIFY_SCOPES,
        open_browser=False,  # API服务器模式下不自动打开浏览器
        cache_path=cache_path  # 用户令牌缓存路径
    )

def get_user_spotify_client(access_token: Optional[str] = None, session_id: Optional[str] = None) -> Optional[spotipy.Spotify]:
    """
    获取用户级别Spotify客户端（使用Authorization Code Flow）
    
    该客户端用于需要用户授权的操作，如创建播放列表。
    从缓存中获取令牌，如果令牌过期则尝试刷新。
    
    Args:
        access_token: 可选的访问令牌，如果提供则直接使用
        session_id: 可选的会话ID，用于多用户环境下的令牌隔离
        
    Returns:
        Optional[spotipy.Spotify]: Spotify客户端实例或None（如果无法获取有效令牌）
    """
    try:
        # 如果直接提供了访问令牌，直接使用它
        if access_token:
            client = spotipy.Spotify(auth=access_token)
            logger.info("已使用提供的访问令牌创建用户级别Spotify客户端")
            return client
        
        # 使用全局锁防止并发问题
        with _user_tokens_lock:
            # 缓存键
            cache_key = session_id or "default"
            
            # 检查是否有缓存的令牌信息
            if cache_key in _user_tokens_cache:
                token_info = _user_tokens_cache[cache_key]
                now = int(time.time())
                
                # 检查令牌是否即将过期
                if token_info.get('expires_at', 0) - now < TOKEN_REFRESH_THRESHOLD:
                    logger.info(f"用户令牌即将过期，剩余 {token_info.get('expires_at', 0) - now} 秒，尝试刷新")
                    
                    # 尝试刷新令牌
                    if token_info.get('refresh_token'):
                        try:
                            auth_manager = get_auth_manager(session_id)
                            token_info = auth_manager.refresh_access_token(token_info['refresh_token'])
                            _user_tokens_cache[cache_key] = token_info
                            
                            # 保存到缓存文件
                            auth_manager.cache_token_info(token_info)
                            logger.info("用户令牌刷新成功")
                        except Exception as e:
                            logger.error(f"刷新用户令牌失败: {e}")
                            del _user_tokens_cache[cache_key]
                            return None
                    else:
                        logger.warning("用户令牌即将过期但没有刷新令牌")
                        del _user_tokens_cache[cache_key]
                        return None
                
                # 使用缓存的令牌创建客户端
                client = spotipy.Spotify(auth=token_info['access_token'])
                logger.info("已使用缓存令牌创建用户级别Spotify客户端")
                return client
        
        # 没有缓存的令牌，尝试从磁盘加载
        auth_manager = get_auth_manager(session_id)
        
        # 确定缓存文件路径
        cache_path = auth_manager.cache_path
        if not os.path.exists(cache_path):
            logger.warning(f"用户令牌缓存不存在: {cache_path}")
            return None
        
        # 检查是否有有效令牌
        token_info = auth_manager.get_cached_token()
        if not token_info:
            logger.warning("缓存中没有有效的用户令牌")
            return None
        
        # 检查令牌是否过期，如果过期则刷新
        if auth_manager.is_token_expired(token_info):
            logger.info("用户令牌已过期，尝试刷新")
            if not token_info.get('refresh_token'):
                logger.warning("没有刷新令牌，无法刷新用户令牌")
                return None
                
            try:
                token_info = auth_manager.refresh_access_token(token_info['refresh_token'])
                
                # 保存刷新后的令牌到缓存
                auth_manager.cache_token_info(token_info)
                logger.info("用户令牌刷新成功")
            except Exception as e:
                logger.error(f"刷新用户令牌失败: {e}")
                return None
        
        # 使用缓存锁更新内存缓存
        with _user_tokens_lock:
            _user_tokens_cache[cache_key] = token_info
        
        # 创建Spotify客户端
        client = spotipy.Spotify(auth=token_info['access_token'])
        logger.info("已成功创建用户级别Spotify客户端")
        
        return client
    except Exception as e:
        logger.error(f"获取用户级别Spotify客户端失败: {e}")
        return None

def is_user_authenticated(session_id: Optional[str] = None) -> bool:
    """
    检查用户是否已授权
    
    Args:
        session_id: 可选的会话ID，用于多用户环境下的令牌隔离
        
    Returns:
        bool: 用户是否已授权
    """
    # 尝试获取用户客户端，如果成功则表示已授权
    client = get_user_spotify_client(session_id=session_id)
    if client is None:
        return False
    
    # 进一步验证，尝试获取当前用户信息
    try:
        client.current_user()
        return True
    except Exception as e:
        logger.warning(f"验证用户令牌有效性失败: {e}")
        return False

def get_project_token_status() -> Dict[str, Any]:
    """
    获取项目令牌的状态信息
    
    Returns:
        Dict[str, Any]: 包含令牌状态、过期时间等信息
    """
    with _client_lock:
        now = int(time.time())
        expires_at = _project_token_info.get('expires_at', 0)
        expires_in = max(0, expires_at - now)
        
        return {
            "status": _project_token_status,
            "expires_in": expires_in,
            "expires_at": expires_at,
            "last_refresh": _project_token_last_refresh,
            "refresh_attempts": _project_token_refresh_attempts,
            "has_valid_token": bool(_project_client) and expires_in > 0
        }

def clear_user_token(session_id: Optional[str] = None) -> bool:
    """
    清除用户令牌
    
    Args:
        session_id: 可选的会话ID，用于多用户环境下的令牌隔离
        
    Returns:
        bool: 是否成功清除
    """
    try:
        # 确定缓存路径
        cache_path = USER_TOKEN_CACHE_PATH
        if session_id:
            cache_path = os.path.join(USER_TOKEN_CACHE_DIR, f"spotify_token_{session_id}")
        
        # 清除内存缓存
        with _user_tokens_lock:
            cache_key = session_id or "default"
            if cache_key in _user_tokens_cache:
                del _user_tokens_cache[cache_key]
        
        # 清除文件缓存
        if os.path.exists(cache_path):
            os.remove(cache_path)
            logger.info(f"已清除用户令牌缓存: {cache_path}")
        
        return True
    except Exception as e:
        logger.error(f"清除用户令牌失败: {e}")
        return False

def get_user_token_info(session_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    获取用户令牌信息
    
    Args:
        session_id: 可选的会话ID，用于多用户环境下的令牌隔离
        
    Returns:
        Optional[Dict[str, Any]]: 令牌信息，如果不存在则返回None
    """
    try:
        # 缓存键
        cache_key = session_id or "default"
        
        # 首先检查内存缓存
        with _user_tokens_lock:
            if cache_key in _user_tokens_cache:
                token_info = _user_tokens_cache[cache_key]
                now = int(time.time())
                expires_at = token_info.get('expires_at', 0)
                
                return {
                    "is_valid": expires_at > now,
                    "expires_in": max(0, expires_at - now),
                    "expires_at": expires_at,
                    "token_type": token_info.get('token_type', 'Bearer'),
                    "scope": token_info.get('scope', SPOTIFY_SCOPES),
                    "has_refresh_token": 'refresh_token' in token_info
                }
        
        # 如果内存缓存中没有，尝试从磁盘加载
        auth_manager = get_auth_manager(session_id)
        token_info = auth_manager.get_cached_token()
        
        if token_info:
            now = int(time.time())
            expires_at = token_info.get('expires_at', 0)
            
            return {
                "is_valid": expires_at > now,
                "expires_in": max(0, expires_at - now),
                "expires_at": expires_at,
                "token_type": token_info.get('token_type', 'Bearer'),
                "scope": token_info.get('scope', SPOTIFY_SCOPES),
                "has_refresh_token": 'refresh_token' in token_info
            }
        
        return None
    except Exception as e:
        logger.error(f"获取用户令牌信息失败: {e}")
        return None 