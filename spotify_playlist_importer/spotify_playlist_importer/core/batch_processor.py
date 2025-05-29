import re
import logging
import asyncio
from typing import Optional, Tuple, List, Callable, Any

from spotify_playlist_importer.core.models import ParsedSong

def parse_song_line(line: str) -> Tuple[Optional[str], List[str]]:
    """
    Parses a line from a song file into title and a list of artists.
    Expected format: "Title - Artist1 / Artist2" or "Title - Artist" or "Title"
    Uses rsplit to better handle hyphens in titles.
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
    on_result_callback = None # Optional callback: func(original_line, title, artists, norm_title, norm_artists, search_results)
):
    """
    Processes a file containing a list of songs, normalizes them, 
    and searches them on Spotify.
    
    Args:
        file_path: 包含歌曲列表的文件路径
        normalizer: TextNormalizer实例，用于标准化歌曲标题和艺术家名称
        spotify_search_func: 异步函数，用于在Spotify上搜索歌曲
        on_result_callback: 可选回调函数，处理搜索结果
        
    Returns:
        Tuple[int, int, int]: (总歌曲数, 成功匹配数, 失败匹配数)
    """
    if not file_path:
        logging.error("未提供文件路径")
        return (0, 0, 0)
    
    try:
        # 读取歌曲列表文件
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if not lines:
            logging.warning(f"文件 {file_path} 为空")
            return (0, 0, 0)
            
        total_songs = 0
        matched_songs = 0
        failed_songs = 0
        
        # 处理每一行
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            total_songs += 1
            logging.debug(f"处理行: {line}")
            
            # 解析歌曲标题和艺术家
            title, artists = parse_song_line(line)
            
            if not title:
                logging.warning(f"无法解析歌曲标题: {line}")
                failed_songs += 1
                if on_result_callback:
                    await on_result_callback(line, None, artists, None, [], None)
                continue
            
            # 标准化标题和艺术家
            normalized_title = normalizer.normalize(title)
            normalized_artists = [normalizer.normalize(artist) for artist in artists]
            
            # 创建ParsedSong对象
            parsed_song = ParsedSong(
                original_line=line,
                title=normalized_title,
                artists=normalized_artists
            )
            
            # 在Spotify上搜索歌曲
            try:
                search_result, error_message = await spotify_search_func(parsed_song)
                
                if search_result:
                    matched_songs += 1
                    logging.info(f"找到匹配歌曲: {title} - {', '.join(artists)} => {search_result.name} - {', '.join(search_result.artists)}")
                else:
                    failed_songs += 1
                    logging.warning(f"未找到匹配歌曲: {title} - {', '.join(artists)}, 错误: {error_message}")
                
                # 调用回调函数
                if on_result_callback:
                    await on_result_callback(line, title, artists, normalized_title, normalized_artists, search_result)
                    
            except Exception as e:
                failed_songs += 1
                logging.error(f"处理歌曲时出错: {e}")
                if on_result_callback:
                    await on_result_callback(line, title, artists, normalized_title, normalized_artists, None)
        
        logging.info(f"处理完成: 总歌曲数 {total_songs}, 成功匹配 {matched_songs}, 失败匹配 {failed_songs}")
        return (total_songs, matched_songs, failed_songs)
        
    except Exception as e:
        logging.error(f"处理歌曲列表文件时出错: {e}")
        return (0, 0, 0) 