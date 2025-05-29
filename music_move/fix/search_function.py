import asyncio
import spotipy
from typing import Optional, Tuple
from music_move.models import ParsedSong, MatchedSong
from music_move.utils import logger

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