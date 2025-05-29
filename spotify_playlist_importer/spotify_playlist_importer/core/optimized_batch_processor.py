import re
import logging
import asyncio
from typing import Optional, Tuple, List, Callable, Any, Dict
from functools import lru_cache

from spotify_playlist_importer.core.models import ParsedSong

# 使用LRU缓存优化parse_song_line函数
@lru_cache(maxsize=1024)
def parse_song_line(line: str) -> Tuple[Optional[str], List[str]]:
    """
    Parses a line from a song file into title and a list of artists.
    Expected format: "Title - Artist1 / Artist2" or "Title - Artist" or "Title"
    Uses rsplit to better handle hyphens in titles.
    
    This version is optimized with LRU caching for repeated lines.
    """
    line = line.strip()
    if not line:
        return None, []

    # 特殊情况处理: 仅包含艺术家名，格式为" - Artist"
    if line.startswith(" - "):
        return None, [line.replace(" - ", "").strip()]

    parts = line.rsplit(" - ", 1)
    
    title_str = ""
    artists_str_part = ""

    if len(parts) == 1: # No " - " separator found, or it was at the very beginning/end and got stripped
        title_str = parts[0].strip()
        artists_list = []
        if not title_str: # Handles cases like " - " or just " "
             return None, []
        return title_str, artists_list

    # len(parts) == 2, " - " separator was found
    title_str = parts[0].strip()
    artists_str_part = parts[1].strip()

    # 特殊情况处理: 标题后面没有艺术家，格式为"Title - "
    if not artists_str_part: # Case "Title - "
        return title_str, []
    else:
        artists_list = [artist.strip() for artist in artists_str_part.split(" / ") if artist.strip()]
    
    # If title_str becomes empty after stripping but artists_str_part was present (e.g. " - Artist")
    if not title_str and artists_str_part:
        return None, artists_list if any(artists_list) else []
    
    if not title_str and not any(artists_list): # e.g. line was " - "
        return None, []

    return title_str if title_str else None, artists_list

async def process_song_list_file(
    file_path: str, 
    normalizer, # TextNormalizer instance
    spotify_search_func, # async function like search_song_on_spotify_async
    on_result_callback = None, # Optional callback: func(original_line, title, artists, norm_title, norm_artists, search_results)
    batch_size: int = 50, # 批处理大小
    max_concurrency: int = 10, # 最大并发数
    verbose: bool = False # 控制日志详细程度
):
    """
    Processes a file containing a list of songs, normalizes them, 
    and searches them on Spotify.
    
    Args:
        file_path: 包含歌曲列表的文件路径
        normalizer: TextNormalizer实例，用于标准化歌曲标题和艺术家名称
        spotify_search_func: 异步函数，用于在Spotify上搜索歌曲
        on_result_callback: 可选回调函数，处理搜索结果
        batch_size: 批处理大小，每次处理的歌曲数量
        max_concurrency: 最大并发数，控制同时进行的API请求数量
        verbose: 是否显示详细日志，默认False
        
    Returns:
        Tuple[int, int, int]: (总歌曲数, 成功匹配数, 失败匹配数)
    """
    if not file_path:
        logging.error("未提供文件路径")
        return (0, 0, 0)
    
    try:
        # 读取歌曲列表文件
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
        
        if not lines:
            logging.warning(f"文件 {file_path} 为空")
            return (0, 0, 0)
            
        total_songs = len(lines)
        matched_songs = 0
        failed_songs = 0
        
        # 创建信号量控制并发
        semaphore = asyncio.Semaphore(max_concurrency)
        
        # 预先解析和标准化所有歌曲
        parsed_songs = []
        for line in lines:
            title, artists = parse_song_line(line)
            
            if not title and not artists:
                logging.warning(f"无法解析行: {line}")
                failed_songs += 1
                if on_result_callback:
                    await on_result_callback(line, None, [], None, [], None)
                continue
                
            # 标准化标题和艺术家
            normalized_title = normalizer.normalize(title) if title else None
            normalized_artists = [normalizer.normalize(artist) for artist in artists] if artists else []
            
            # 创建ParsedSong对象
            parsed_song = ParsedSong(
                original_line=line,
                title=normalized_title,
                artists=normalized_artists
            )
            parsed_songs.append((line, title, artists, normalized_title, normalized_artists, parsed_song))
        
        # 批量处理歌曲
        async def process_batch(batch):
            tasks = []
            for line, title, artists, normalized_title, normalized_artists, parsed_song in batch:
                tasks.append(process_single_song(
                    semaphore, line, title, artists, 
                    normalized_title, normalized_artists, 
                    parsed_song, spotify_search_func, on_result_callback, verbose
                ))
            return await asyncio.gather(*tasks)
        
        # 单首歌曲处理函数
        async def process_single_song(
            sem, line, title, artists, normalized_title, 
            normalized_artists, parsed_song, search_func, callback, is_verbose
        ):
            async with sem:
                try:
                    search_result, error_message = await search_func(parsed_song)
                    
                    if search_result:
                        # 简化日志，只记录原始输入和匹配结果，保持格式一致
                        logging.info(f"{line} => {search_result.name} - {', '.join(search_result.artists)}")
                        result = (True, None)
                    else:
                        # 简化日志，只记录原始输入和未找到状态
                        logging.warning(f"{line} => 未找到匹配")
                        result = (False, error_message)
                    
                    # 调用回调函数
                    if callback:
                        await callback(line, title, artists, normalized_title, normalized_artists, search_result)
                        
                    return result
                    
                except Exception as e:
                    # 记录错误，保持简洁格式
                    logging.error(f"{line} => 处理错误: {e}")
                        
                    if callback:
                        await callback(line, title, artists, normalized_title, normalized_artists, None)
                    return (False, str(e))
        
        # 分批处理所有歌曲
        results = []
        for i in range(0, len(parsed_songs), batch_size):
            batch = parsed_songs[i:i+batch_size]
            batch_results = await process_batch(batch)
            results.extend(batch_results)
        
        # 统计结果
        matched_songs = sum(1 for success, _ in results if success)
        failed_songs = len(results) - matched_songs
        
        logging.info(f"处理完成: 总歌曲数 {total_songs}, 成功匹配 {matched_songs}, 失败匹配 {failed_songs}")
        return (total_songs, matched_songs, failed_songs)
        
    except Exception as e:
        logging.error(f"处理歌曲列表文件时出错: {e}")
        return (0, 0, 0) 