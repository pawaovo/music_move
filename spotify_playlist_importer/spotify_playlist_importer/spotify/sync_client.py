#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Spotify同步客户端封装模块。

此模块基于spotipy库提供同步API调用功能，并添加了：
1. 错误处理和重试逻辑
2. 并发控制支持（通过与asyncio配合使用）
3. 速率限制监控和处理
4. 性能跟踪和日志记录

该模块的主要目的是通过asyncio.to_thread提供并发的同步API调用功能，
同时保持代码简单易用。它兼顾了同步代码的简洁性和异步执行的高效性。
"""

import time
import logging
import asyncio
import re
from typing import Optional, Dict, Any, List, Tuple, Callable, TypeVar, Generic, Union
from functools import wraps
import sys

import spotipy
from spotipy.exceptions import SpotifyException
from spotipy.oauth2 import SpotifyOAuth

from spotify_playlist_importer.core.models import ParsedSong, MatchedSong
# 导入单例模块
from spotify_playlist_importer.spotify.singleton_client import get_spotify_client_instance
# 保留旧的导入，以便向后兼容
from spotify_playlist_importer.spotify.auth import get_spotify_client

# 尝试从相对路径导入logger
try:
    from ..utils.logger import get_logger, log_function_call, log_class_methods
except ImportError:
    # 如果相对导入失败，则尝试完全路径导入
    try:
        from spotify_playlist_importer.utils.logger import get_logger, log_function_call, log_class_methods
    except ImportError:
        # 如果仍然失败，使用标准logging作为备用
        import logging
        import functools
        
        def get_logger(name):
            return logging.getLogger(name)
            
        def log_function_call(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
            
        def log_class_methods(cls):
            return cls

from spotify_playlist_importer.core.config import (
    API_CONCURRENT_REQUESTS,
    API_RATE_LIMIT_RETRIES,
    API_BASE_DELAY,
    API_MAX_DELAY,
    SEARCH_LIMIT
)

# 配置日志
logger = get_logger(__name__)

# 定义类型变量用于通用返回值
T = TypeVar('T')


class SpotifyAPIError(Exception):
    """Spotify API错误基类"""

    def __init__(self, message: str, status_code: Optional[int] = None, retryable: bool = False):
        self.message = message
        self.status_code = status_code
        self.retryable = retryable
        super().__init__(message)


class RateLimitError(SpotifyAPIError):
    """API速率限制错误"""

    def __init__(self, message: str, retry_after: Optional[int] = None):
        super().__init__(message, status_code=429, retryable=True)
        self.retry_after = retry_after


class AuthenticationError(SpotifyAPIError):
    """认证错误"""

    def __init__(self, message: str):
        super().__init__(message, status_code=401, retryable=False)


class NetworkError(SpotifyAPIError):
    """网络连接错误"""

    def __init__(self, message: str):
        super().__init__(message, retryable=True)


def with_retry(max_retries: int = API_RATE_LIMIT_RETRIES, base_delay: float = API_BASE_DELAY):
    """
    装饰器：为函数添加自动重试功能
    
    Args:
        max_retries: 最大重试次数
        base_delay: 初始重试延迟（秒）
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    # 添加重试次数信息到日志
                    if attempt > 0:
                        logger.debug(f"第 {attempt} 次重试 {func.__name__}...")
                    
                    # 执行原始函数
                    return func(*args, **kwargs)
                    
                except RateLimitError as e:
                    # 处理速率限制错误
                    last_exception = e
                    retry_after = e.retry_after or base_delay * (2 ** attempt)  # 指数退避
                    retry_after = min(retry_after, API_MAX_DELAY)  # 设置上限
                    
                    logger.warning(
                        f"API速率限制触发，等待 {retry_after} 秒后重试... ({attempt}/{max_retries})")
                    time.sleep(retry_after)
                    
                except SpotifyAPIError as e:
                    # 处理其他API错误
                    last_exception = e
                    if not e.retryable:
                        # 不可重试的错误直接抛出
                        logger.error(f"不可重试的API错误: {e}")
                        raise
                    
                    # 可重试的错误
                    delay = base_delay * (2 ** attempt)  # 指数退避
                    delay = min(delay, API_MAX_DELAY)  # 设置上限
                    
                    logger.warning(
                        f"API错误: {e}，等待 {delay} 秒后重试... ({attempt}/{max_retries})")
                    time.sleep(delay)
                    
                except Exception as e:
                    # 处理其他未预期的错误
                    last_exception = e
                    logger.error(f"未预期的错误: {e}")
                    raise
            
            # 如果所有重试都失败
            logger.error(f"{func.__name__}在 {max_retries} 次重试后仍然失败")
            if last_exception:
                raise last_exception
            raise RuntimeError(f"{func.__name__}在 {max_retries} 次重试后仍然失败")
            
        return wrapper
    return decorator


@log_class_methods
class SpotifySyncClient:
    """
    同步Spotify客户端封装类，提供对spotipy库的封装，
    添加错误处理、重试逻辑、日志记录以及异步支持。
    """
    
    def __init__(self, sp_client: Optional[spotipy.Spotify] = None):
        """
        初始化同步Spotify客户端封装
        
        Args:
            sp_client: 可选的已初始化的spotipy.Spotify客户端实例
                      如果未提供，将使用单例模式获取共享实例
        """
        logger.debug("初始化SpotifySyncClient...")
        if sp_client is not None:
            # 如果明确提供了客户端实例，则使用它
            self.sp = sp_client
        else:
            # 否则，使用单例模式获取共享实例
            try:
                # 使用新的单例模式获取实例
                self.sp = get_spotify_client_instance()
                logger.debug("使用共享的Spotify客户端单例实例")
            except Exception as e:
                # 如果单例模式获取失败，回退到原始方法（仅作为备用）
                logger.warning(f"无法获取Spotify客户端单例实例，回退到传统方法: {e}")
                self.sp = get_spotify_client()
        
        self.semaphore = None  # 将在异步上下文中使用
        logger.debug("SpotifySyncClient初始化完成")

    def set_semaphore(self, semaphore: asyncio.Semaphore):
        """
        设置控制并发的信号量
        
        Args:
            semaphore: asyncio.Semaphore实例，用于控制并发
        """
        self.semaphore = semaphore

    @with_retry()
    def search(self, query: str, search_type: str = 'track', limit: int = SEARCH_LIMIT) -> Dict[str, Any]:
        """
        搜索Spotify资源
        
        Args:
            query: 搜索查询
            search_type: 搜索类型 ('track', 'album', 'artist', 'playlist')
            limit: 返回结果数量
            
        Returns:
            Dict[str, Any]: 搜索结果
            
        Raises:
            SpotifyAPIError: API调用错误
        """
        try:
            start_time = time.time()
            result = self.sp.search(q=query, type=search_type, limit=limit)
            end_time = time.time()
            
            # 记录性能指标
            logger.debug(f"Spotify search请求耗时: {(end_time - start_time):.3f}秒")
            
            return result
        except SpotifyException as e:
            # 将spotipy异常转换为自定义异常
            status_code = getattr(e, 'http_status', None)
            
            if status_code == 429:
                retry_after = None
                headers = getattr(e, 'headers', {})
                if headers and 'Retry-After' in headers:
                    retry_after = int(headers['Retry-After'])
                raise RateLimitError(f"API速率限制: {e}", retry_after=retry_after)
            elif status_code == 401:
                raise AuthenticationError(f"认证失败: {e}")
            else:
                raise SpotifyAPIError(
                    f"Spotify API错误: {e}", status_code=status_code, retryable=status_code in (500, 502, 503, 504))
        except Exception as e:
            raise SpotifyAPIError(f"未预期的错误: {e}", retryable=False)

    @with_retry()
    def user_info(self) -> Dict[str, Any]:
        """
        获取当前用户信息
        
        Returns:
            Dict[str, Any]: 用户信息
            
        Raises:
            SpotifyAPIError: API调用错误
        """
        try:
            return self.sp.me()
        except SpotifyException as e:
            status_code = getattr(e, 'http_status', None)
            if status_code == 429:
                retry_after = None
                headers = getattr(e, 'headers', {})
                if headers and 'Retry-After' in headers:
                    retry_after = int(headers['Retry-After'])
                raise RateLimitError(f"API速率限制: {e}", retry_after=retry_after)
            elif status_code == 401:
                raise AuthenticationError(f"认证失败: {e}")
            else:
                raise SpotifyAPIError(
                    f"Spotify API错误: {e}", status_code=status_code, retryable=status_code in (500, 502, 503, 504))
        except Exception as e:
            raise SpotifyAPIError(f"未预期的错误: {e}", retryable=False)

    @with_retry()
    def create_playlist(self, name: str, public: bool = False, description: str = "") -> Dict[str, Any]:
        """
        创建播放列表
        
        Args:
            name: 播放列表名称
            public: 是否公开
            description: 播放列表描述
            
        Returns:
            Dict[str, Any]: 创建的播放列表信息
            
        Raises:
            SpotifyAPIError: API调用错误
        """
        try:
            # 获取当前用户ID
            user_info = self.user_info()
            user_id = user_info['id']
            
            # 确保description不为None
            if description is None:
                description = ""
                
            # 处理空描述情况 - 在API中明确指定为空字符串而不是None
            has_description = bool(description.strip())
            
            # 记录播放列表创建详情
            logger.info(f"正在创建播放列表：名称='{name}', 描述='{description}', 有效描述={has_description}, 公开={public}, 用户ID={user_id}")
            
            # 创建播放列表参数
            playlist_args = {
                "user": user_id,
                "name": name,
                "public": public
            }
            
            # 只有当描述非空时才添加描述参数
            if has_description:
                playlist_args["description"] = description
                logger.info(f"添加描述参数: '{description}'")
            
            # 创建播放列表
            result = self.sp.user_playlist_create(**playlist_args)
            
            # 记录结果
            logger.info(f"播放列表创建成功：ID={result['id']}, URL={result['external_urls']['spotify']}")
            if 'description' in result:
                logger.info(f"返回的播放列表描述：'{result['description']}'")
            else:
                logger.warning("返回的播放列表信息中没有description字段")
            
            return result
        except SpotifyAPIError:
            # 重新抛出自定义异常
            raise
        except SpotifyException as e:
            status_code = getattr(e, 'http_status', None)
            raise SpotifyAPIError(f"创建播放列表失败: {e}", status_code=status_code, retryable=status_code in (
                429, 500, 502, 503, 504))
        except Exception as e:
            raise SpotifyAPIError(f"创建播放列表时出现未预期的错误: {e}", retryable=False)

    @with_retry()
    def add_tracks_to_playlist(self, playlist_id: str, track_uris: List[str]) -> bool:
        """
        向播放列表添加曲目
        
        Args:
            playlist_id: 播放列表ID
            track_uris: 曲目URI列表
            
        Returns:
            bool: 是否成功
            
        Raises:
            SpotifyAPIError: API调用错误
        """
        try:
            self.sp.playlist_add_items(playlist_id, track_uris)
            return True
        except SpotifyAPIError:
            # 重新抛出自定义异常
            raise
        except SpotifyException as e:
            status_code = getattr(e, 'http_status', None)
            raise SpotifyAPIError(f"添加曲目失败: {e}", status_code=status_code, retryable=status_code in (
                429, 500, 502, 503, 504))
        except Exception as e:
            raise SpotifyAPIError(f"添加曲目时出现未预期的错误: {e}", retryable=False)


# 异步包装函数
async def search_track_async(query: str, limit: int = SEARCH_LIMIT, semaphore: Optional[asyncio.Semaphore] = None) -> Tuple[Optional[List[Dict[str, Any]]], Optional[str]]:
    """
    异步搜索Spotify曲目，内部使用同步client通过线程池执行
    使用共享的Spotify客户端实例，避免在每次调用时创建新实例
    
    Args:
        query: 搜索查询
        limit: 最大结果数量
        semaphore: 可选的用于控制并发的信号量
        
    Returns:
        Tuple[Optional[List[Dict[str, Any]]], Optional[str]]: (搜索结果列表, 错误消息)
    """
    async def _search():
        try:
            # 使用共享的Spotify客户端实例
            client = SpotifySyncClient()  # 内部会使用单例实例
            search_results = client.search(query=query, limit=limit)
            
            if not search_results or 'tracks' not in search_results or 'items' not in search_results['tracks'] or len(search_results['tracks']['items']) == 0:
                return [], None  # 未找到匹配项，但非错误
                
            return search_results['tracks']['items'], None
            
        except SpotifyAPIError as e:
            return None, f"Spotify API错误: {e.message}"
            
        except Exception as e:
            return None, f"搜索曲目时出现未预期的错误: {e}"
    
    # 使用信号量控制并发（如果提供）
    if semaphore:
        async with semaphore:
            return await asyncio.to_thread(_search)
    else:
        return await asyncio.to_thread(_search)


async def search_song_on_spotify_sync_wrapped(
    parsed_song: ParsedSong, 
    semaphore: Optional[asyncio.Semaphore] = None,
    spotify_client: Optional[spotipy.Spotify] = None
) -> Tuple[Optional[MatchedSong], Optional[str]]:
    """
    在Spotify上搜索歌曲（同步版本的异步包装器）
    
    此函数将同步的Spotify搜索包装为异步函数，支持并发控制。
    
    Args:
        parsed_song: 已解析的歌曲信息
        semaphore: 可选的信号量，用于控制并发
        spotify_client: 可选的Spotify客户端实例，如果提供则使用该实例
        
    Returns:
        Tuple[Optional[MatchedSong], Optional[str]]: 匹配的歌曲或None，错误消息或None
    """
    logger.debug(f"在Spotify上搜索: {parsed_song.title} - {parsed_song.artists}")
    
    # 异步执行同步搜索函数
    try:
        # 使用信号量控制并发（如果提供）
        if semaphore:
            async with semaphore:
                result, error = await asyncio.to_thread(_search_with_sync_client, parsed_song, spotify_client)
        else:
            result, error = await asyncio.to_thread(_search_with_sync_client, parsed_song, spotify_client)
            
        return result, error
    except Exception as e:
        error_msg = f"在Spotify上搜索时出错: {e}"
        logger.error(error_msg)
        return None, error_msg
    
def _search_with_sync_client(parsed_song: ParsedSong, spotify_client: Optional[spotipy.Spotify] = None) -> Tuple[Optional[MatchedSong], Optional[str]]:
    """
    使用同步客户端在Spotify上搜索歌曲
    
    此函数将由asyncio.to_thread在线程池中执行
    
    使用四阶段降级搜索逻辑：
    1. 去括号标题 + 前两位艺术家（最精确）
    2. 仅去括号标题（不考虑艺术家）
    3. 标题关键词 + 艺术家（更宽松的匹配）
    4. 仅艺术家（最宽松的条件）
    
    Args:
        parsed_song: 已解析的歌曲信息
        spotify_client: 可选的Spotify客户端实例，如果提供则使用该实例
        
    Returns:
        Tuple[Optional[MatchedSong], Optional[str]]: 匹配的歌曲或None，错误消息或None
    """
    from spotify_playlist_importer.spotify.matcher import (
        select_best_match, create_matched_song
    )
    from spotify_playlist_importer.utils.enhanced_matcher import BracketAwareMatcher, EnhancedMatcher
    import re
    
    # 创建客户端实例，如果没有提供，则使用共享实例
    if spotify_client is None:
        client = SpotifySyncClient()
    else:
        client = SpotifySyncClient(sp_client=spotify_client)
    
    # 保存原始标题，用于日志和匹配
    original_title = parsed_song.title
    
    # 去除括号内容的标题
    clean_title = re.sub(r'\([^)]*\)|\[[^\]]*\]|\{[^}]*\}', '', original_title).strip() if original_title else ""
    
    # 提取标题关键词（用于第三阶段）
    title_keywords = []
    if original_title:
        # 提取标题中的所有单词，限制为前3个有意义的词
        words = re.findall(r'\w+', original_title)
        title_keywords = words[:min(3, len(words))] if words else []
    
    # 匹配结果变量，用于跟踪是否已找到匹配
    matched_song = None
    final_error = None
    
    # 定义一个安全搜索函数，处理各种异常
    def safe_search(query, stage_name):
        nonlocal final_error
        try:
            # 执行搜索（此处的client.search已经包含了重试逻辑）
            search_results = client.search(query, limit=SEARCH_LIMIT)
            return search_results, None
        except RateLimitError as e:
            # 记录速率限制错误，但不立即失败，可能稍后重试
            logger.warning(f"{stage_name}搜索遇到API速率限制: {e}，等待后可能重试")
            final_error = f"{stage_name}API速率限制: {e}"
            return None, e
        except AuthenticationError as e:
            # 认证错误，无法继续
            logger.error(f"{stage_name}认证失败: {e}")
            final_error = f"{stage_name}认证失败: {e}"
            return None, e
        except SpotifyAPIError as e:
            # 其他API错误，如果可重试，稍后可能重试
            if e.retryable:
                logger.warning(f"{stage_name}遇到可重试的API错误: {e}")
                final_error = f"{stage_name}API错误(可重试): {e}"
            else:
                logger.error(f"{stage_name}遇到不可重试的API错误: {e}")
                final_error = f"{stage_name}API错误: {e}"
            return None, e
        except Exception as e:
            # 未预期的错误
            logger.exception(f"{stage_name}搜索时遇到未预期的错误: {e}")
            final_error = f"{stage_name}未预期的错误: {e}"
            return None, e
    
    # ===== 第一阶段：去括号标题 + 前两位艺术家（最精确） =====
    if clean_title and parsed_song.artists and len(parsed_song.artists) > 0:
        # 获取前两位艺术家（如果有）
        artists_to_use = parsed_song.artists[:min(2, len(parsed_song.artists))]
        artists_query = " ".join(f"artist:\"{artist}\"" for artist in artists_to_use)
        query = f"track:\"{clean_title}\" {artists_query}"
        
        logger.debug(f"第一阶段搜索查询（去括号标题+艺术家）: {query}")
        
        # 执行搜索，安全处理异常
        search_results, error = safe_search(query, "第一阶段")
        
        if search_results:
            # 从搜索结果中提取曲目列表
            tracks = search_results.get('tracks', {}).get('items', [])
            
            if tracks:
                # 使用匹配器选择最佳匹配
                best_match = select_best_match(parsed_song, tracks)
                
                if best_match:
                    # 从最佳匹配创建MatchedSong对象
                    matched_song = create_matched_song(best_match, parsed_song.original_line)
                    logger.info(f"第一阶段搜索成功匹配: {parsed_song.original_line} => {matched_song.name} - {', '.join(matched_song.artists)}")
                    return matched_song, None
        elif error and not isinstance(error, RateLimitError) and not (isinstance(error, SpotifyAPIError) and error.retryable):
            # 如果是不可重试的错误，直接返回
            return None, f"第一阶段搜索失败: {error}"
    
    # ===== 第二阶段：仅使用去除括号的标题 =====
    if clean_title and not matched_song:
        # 仅使用去除括号的标题
        title_query = f"track:\"{clean_title}\""
        
        logger.debug(f"第二阶段搜索查询（仅去括号标题）: {title_query}")
        
        # 执行搜索，安全处理异常
        title_search_results, error = safe_search(title_query, "第二阶段")
        
        if title_search_results:
            # 从搜索结果中提取曲目列表
            title_tracks = title_search_results.get('tracks', {}).get('items', [])
            
            if title_tracks:
                # 使用匹配器选择最佳匹配
                title_best_match = select_best_match(parsed_song, title_tracks)
                
                if title_best_match:
                    # 从最佳匹配创建MatchedSong对象
                    matched_song = create_matched_song(title_best_match, parsed_song.original_line)
                    logger.info(f"第二阶段搜索成功匹配（仅去括号标题）: {parsed_song.original_line} => {matched_song.name} - {', '.join(matched_song.artists)}")
                    return matched_song, None
        elif error and not isinstance(error, RateLimitError) and not (isinstance(error, SpotifyAPIError) and error.retryable):
            # 如果是不可重试的错误，直接返回
            return None, f"第二阶段搜索失败: {error}"
    
    # ===== 第三阶段：标题关键词 + 艺术家 =====
    if title_keywords and parsed_song.artists and len(parsed_song.artists) > 0 and not matched_song:
        # 使用标题关键词和第一个艺术家
        keywords = " ".join(title_keywords)
        artist = parsed_song.artists[0]
        keyword_artist_query = f"{keywords} artist:\"{artist}\""
        
        logger.debug(f"第三阶段搜索查询（标题关键词+艺术家）: {keyword_artist_query}")
        
        # 执行搜索，安全处理异常
        keyword_search_results, error = safe_search(keyword_artist_query, "第三阶段")
        
        if keyword_search_results:
            # 从搜索结果中提取曲目列表
            keyword_tracks = keyword_search_results.get('tracks', {}).get('items', [])
            
            if keyword_tracks:
                # 使用匹配器选择最佳匹配
                keyword_best_match = select_best_match(parsed_song, keyword_tracks)
                
                if keyword_best_match:
                    # 从最佳匹配创建MatchedSong对象
                    matched_song = create_matched_song(keyword_best_match, parsed_song.original_line)
                    # 将第三阶段的搜索结果设置为低匹配度
                    matched_song.is_low_confidence = True
                    logger.info(f"第三阶段搜索成功匹配（标题关键词+艺术家）: {parsed_song.original_line} => {matched_song.name} - {', '.join(matched_song.artists)} (低匹配度)")
                    return matched_song, None
        elif error and not isinstance(error, RateLimitError) and not (isinstance(error, SpotifyAPIError) and error.retryable):
            # 如果是不可重试的错误，直接返回
            return None, f"第三阶段搜索失败: {error}"
    
    # ===== 第四阶段：仅使用艺术家（最宽松的条件） =====
    if parsed_song.artists and len(parsed_song.artists) > 0 and not matched_song:
        # 仅使用第一个艺术家
        artist = parsed_song.artists[0]
        artist_query = f"artist:\"{artist}\""
        
        logger.debug(f"第四阶段搜索查询（仅艺术家）: {artist_query}")
        
        # 执行搜索，安全处理异常
        artist_search_results, error = safe_search(artist_query, "第四阶段")
        
        if artist_search_results:
            # 从搜索结果中提取曲目列表
            artist_tracks = artist_search_results.get('tracks', {}).get('items', [])
            
            if artist_tracks:
                # 使用匹配器选择最佳匹配
                artist_best_match = select_best_match(parsed_song, artist_tracks)
                
                if artist_best_match:
                    # 从最佳匹配创建MatchedSong对象
                    matched_song = create_matched_song(artist_best_match, parsed_song.original_line)
                    # 将第四阶段的搜索结果设置为低匹配度
                    matched_song.is_low_confidence = True
                    logger.info(f"第四阶段搜索成功匹配（仅艺术家）: {parsed_song.original_line} => {matched_song.name} - {', '.join(matched_song.artists)} (低匹配度)")
                    return matched_song, None
        elif error and not isinstance(error, RateLimitError) and not (isinstance(error, SpotifyAPIError) and error.retryable):
            # 如果是不可重试的错误，直接返回
            return None, f"第四阶段搜索失败: {error}"
    
    # 如果所有阶段都没有找到匹配，检查是否有暂时性错误
    if final_error:
        # 可能有API限制或其他可重试的错误，记录并返回错误信息
        logger.warning(f"所有搜索阶段均未成功，最后的错误: {final_error}")
        return None, final_error
    
    # 所有阶段都没有找到匹配，且没有错误，可能是真的找不到
    logger.info(f"所有搜索阶段均未找到与 '{parsed_song.original_line}' 匹配的歌曲")
    return None, f"未找到与 '{parsed_song.original_line}' 匹配的歌曲"


async def create_spotify_playlist_sync_wrapped(
    playlist_name: str,
    is_public: bool = False,
    playlist_description: Optional[str] = None,
    semaphore: Optional[asyncio.Semaphore] = None,
    spotify_client: Optional[spotipy.Spotify] = None
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    创建Spotify播放列表（同步版本的异步包装器）
    
    Args:
        playlist_name: 播放列表名称
        is_public: 是否公开
        playlist_description: 播放列表描述
        semaphore: 可选的信号量，用于控制并发
        spotify_client: 可选的Spotify客户端实例，如果提供则使用该实例
        
    Returns:
        Tuple[Optional[str], Optional[str], Optional[str]]: (播放列表ID, 播放列表URL, 错误消息)
    """
    logger.debug(f"创建Spotify播放列表: {playlist_name}, 公开: {is_public}")
    
    # 异步执行同步创建函数
    try:
        # 使用信号量控制并发（如果提供）
        if semaphore:
            async with semaphore:
                playlist_id, playlist_url, error = await asyncio.to_thread(
                    _create_playlist_sync, playlist_name, is_public, playlist_description, spotify_client)
        else:
            playlist_id, playlist_url, error = await asyncio.to_thread(
                _create_playlist_sync, playlist_name, is_public, playlist_description, spotify_client)

        return playlist_id, playlist_url, error
    except Exception as e:
        error_msg = f"创建Spotify播放列表时出错: {e}"
        logger.error(error_msg)
        return None, None, error_msg

def _create_playlist_sync(
    playlist_name: str,
    is_public: bool = False,
    playlist_description: Optional[str] = None,
    spotify_client: Optional[spotipy.Spotify] = None
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    使用同步客户端创建Spotify播放列表
    
    此函数将由asyncio.to_thread在线程池中执行
    
    Args:
        playlist_name: 播放列表名称
        is_public: 是否公开
        playlist_description: 播放列表描述
        spotify_client: 可选的Spotify客户端实例，如果提供则使用该实例
        
    Returns:
        Tuple[Optional[str], Optional[str], Optional[str]]: (播放列表ID, 播放列表URL, 错误消息)
    """
    try:
        # 创建客户端实例，如果没有提供，则使用共享实例
        if spotify_client is None:
            client = SpotifySyncClient()
        else:
            client = SpotifySyncClient(sp_client=spotify_client)
        
        # 处理描述参数
        final_description = ""
        if playlist_description is not None:
            final_description = playlist_description
        
        logger.info(f"创建播放列表前参数检查: 名称='{playlist_name}', 描述='{final_description}'")
        
        # 创建播放列表
        playlist = client.create_playlist(
            name=playlist_name,
            public=is_public,
            description=final_description
        )
        
        # 获取播放列表ID和URL
        playlist_id = playlist['id']
        playlist_url = playlist['external_urls']['spotify']
        
        logger.info(f"播放列表创建成功: ID={playlist_id}, URL={playlist_url}")
        
        return playlist_id, playlist_url, None
    except SpotifyAPIError as e:
        error_msg = f"Spotify API错误: {e}"
        logger.error(error_msg)
        return None, None, error_msg
    except Exception as e:
        error_msg = f"创建播放列表时出现未预期的错误: {e}"
        logger.exception(error_msg)
        return None, None, error_msg

async def add_tracks_to_spotify_playlist_sync_wrapped(
    playlist_id: str,
    track_uris: List[str],
    semaphore: Optional[asyncio.Semaphore] = None,
    spotify_client: Optional[spotipy.Spotify] = None
) -> Tuple[bool, int, int, Optional[str]]:
    """
    向Spotify播放列表添加曲目（同步版本的异步包装器）
    
    Args:
        playlist_id: 播放列表ID
        track_uris: 曲目URI列表
        semaphore: 可选的信号量，用于控制并发
        spotify_client: 可选的Spotify客户端实例，如果提供则使用该实例
        
    Returns:
        Tuple[bool, int, int, Optional[str]]: (是否成功, 添加成功数, 添加失败数, 错误消息)
    """
    logger.debug(f"向播放列表 {playlist_id} 添加 {len(track_uris)} 首曲目")
    
    # 异步执行同步添加函数
    try:
        # 使用信号量控制并发（如果提供）
        if semaphore:
            async with semaphore:
                success, added_tracks, failed_tracks, error = await asyncio.to_thread(
                    _add_tracks_sync, playlist_id, track_uris, spotify_client)
        else:
            success, added_tracks, failed_tracks, error = await asyncio.to_thread(
                _add_tracks_sync, playlist_id, track_uris, spotify_client)
                
        return success, added_tracks, failed_tracks, error
    except Exception as e:
        error_msg = f"向播放列表添加曲目时出错: {e}"
        logger.error(error_msg)
        return False, 0, len(track_uris), error_msg
    
def _add_tracks_sync(
    playlist_id: str,
    track_uris: List[str],
    spotify_client: Optional[spotipy.Spotify] = None
) -> Tuple[bool, int, int, Optional[str]]:
    """
    使用同步客户端向Spotify播放列表添加曲目
    
    此函数将由asyncio.to_thread在线程池中执行
    
    Args:
        playlist_id: 播放列表ID
        track_uris: 曲目URI列表
        spotify_client: 可选的Spotify客户端实例，如果提供则使用该实例
        
    Returns:
        Tuple[bool, int, int, Optional[str]]: (是否成功, 添加成功数, 添加失败数, 错误消息)
    """
    try:
        # 创建客户端实例，如果没有提供，则使用共享实例
        if spotify_client is None:
            client = SpotifySyncClient()
        else:
            client = SpotifySyncClient(sp_client=spotify_client)
        
        # 过滤空URI
        valid_uris = [uri for uri in track_uris if uri]
        invalid_count = len(track_uris) - len(valid_uris)
        
        if not valid_uris:
            logger.warning("没有有效的曲目URI可添加")
            return True, 0, invalid_count, None  # 视为成功，因为没有错误
        
        # 分批添加曲目（Spotify API限制一次最多100首）
        batch_size = 100
        total_added = 0
        failed_tracks = 0
        
        for i in range(0, len(valid_uris), batch_size):
            batch = valid_uris[i:i+batch_size]
            try:
                client.add_tracks_to_playlist(playlist_id, batch)
                total_added += len(batch)
                logger.info(f"已添加 {total_added}/{len(valid_uris)} 首曲目")
            except SpotifyAPIError as e:
                # 记录错误但继续处理下一批
                logger.error(f"添加曲目批次失败 ({i}/{len(valid_uris)}): {e}")
                failed_tracks += len(batch)
        
        # 计算总失败数（包括无效URI和添加失败的）
        total_failed = failed_tracks + invalid_count
        
        if total_added > 0:
            logger.info(f"成功添加 {total_added} 首曲目到播放列表 {playlist_id}，失败 {total_failed} 首")
            return True, total_added, total_failed, None
        else:
            error_msg = "所有曲目添加都失败了"
            logger.error(error_msg)
            return False, 0, total_failed, error_msg
    except SpotifyAPIError as e:
        error_msg = f"Spotify API错误: {e}"
        logger.error(error_msg)
        return False, 0, len(track_uris), error_msg
    except Exception as e:
        error_msg = f"添加曲目时出现未预期的错误: {e}"
        logger.exception(error_msg)
        return False, 0, len(track_uris), error_msg


# 创建并发控制机制的工厂函数
def create_concurrency_limiter(limit: int = API_CONCURRENT_REQUESTS) -> asyncio.Semaphore:
    """
    创建用于控制API并发请求的信号量
    
    Args:
        limit: 最大并发请求数
        
    Returns:
        asyncio.Semaphore: 用于控制并发的信号量
    """
    return asyncio.Semaphore(limit) 
