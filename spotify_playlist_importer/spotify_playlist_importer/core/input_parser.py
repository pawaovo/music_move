import sys
from typing import List

from .models import ParsedSong


def parse_song_file(file_path: str) -> List[ParsedSong]:
    """
    解析歌曲列表文件，每行格式应为 "歌曲名称 - 艺人1 / 艺人2"
    
    Args:
        file_path (str): 歌曲列表文件的路径
        
    Returns:
        List[ParsedSong]: 解析出的歌曲列表
        
    Raises:
        FileNotFoundError: 当文件不存在时
        IOError: 当文件无法读取时
    """
    parsed_songs = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_number, original_line in enumerate(f, 1):
                original_line = original_line.strip()
                if not original_line:
                    continue
                    
                # 使用 " - " 分割歌曲标题和艺术家
                parts = original_line.split(" - ")
                if len(parts) != 2:
                    print(f"警告: 行 {line_number} 格式不正确 (缺少 ' - ' 分隔符): {original_line}", file=sys.stderr)
                    continue
                    
                title, artists_str = parts[0].strip(), parts[1].strip()
                
                if not title or not artists_str:
                    print(f"警告: 行 {line_number} 格式不正确 (标题或艺术家为空): {original_line}", file=sys.stderr)
                    continue
                    
                # 解析艺术家列表，使用 " / " 分隔
                artists = [artist.strip() for artist in artists_str.split(" / ")]
                
                # 创建ParsedSong对象并添加到列表
                parsed_song = ParsedSong(
                    original_line=original_line,
                    title=title,
                    artists=artists
                )
                parsed_songs.append(parsed_song)
                
    except FileNotFoundError:
        print(f"错误: 文件不存在: '{file_path}'", file=sys.stderr)
        raise
    except IOError as e:
        print(f"错误: 无法读取文件 '{file_path}'. 原因: {e}", file=sys.stderr)
        raise
        
    return parsed_songs 