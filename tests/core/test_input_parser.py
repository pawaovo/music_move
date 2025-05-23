import os
import sys
import pytest
from typing import List

# 添加项目根目录到sys.path，使测试可以导入项目模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from spotify_playlist_importer.core.input_parser import parse_song_file
from spotify_playlist_importer.core.models import ParsedSong


# 获取测试数据文件的路径
def get_test_data_path(filename: str) -> str:
    """返回测试数据文件的绝对路径"""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '../test_data', filename))


def test_parse_song_file_valid_songs():
    """测试解析包含有效歌曲的文件"""
    file_path = get_test_data_path('sample_songs.txt')
    parsed_songs = parse_song_file(file_path)
    
    # 验证解析出正确数量的歌曲
    assert len(parsed_songs) == 5
    
    # 验证第一首歌的信息
    assert parsed_songs[0].title == "Bohemian Rhapsody"
    assert parsed_songs[0].artists == ["Queen"]
    assert parsed_songs[0].original_line == "Bohemian Rhapsody - Queen"
    
    # 验证带有多位艺术家的歌曲
    assert parsed_songs[3].title == "Imagine"
    assert parsed_songs[3].artists == ["John Lennon", "Plastic Ono Band"]
    
    # 验证带有额外空格的歌曲
    assert parsed_songs[4].title == "White Wedding"
    assert parsed_songs[4].artists == ["Billy Idol"]


def test_parse_song_file_malformed_songs(capsys):
    """测试解析包含格式错误歌曲的文件"""
    file_path = get_test_data_path('malformed_songs.txt')
    parsed_songs = parse_song_file(file_path)
    
    # 检查成功解析的歌曲数量（应该有3首有效歌曲）
    assert len(parsed_songs) == 3
    
    # 验证成功解析的歌曲
    assert parsed_songs[0].title == "Good Song"
    assert parsed_songs[0].artists == ["Good Artist"]
    
    assert parsed_songs[1].title == "Another Good Song"
    assert parsed_songs[1].artists == ["Artist1", "Artist2", "Artist3"]
    
    assert parsed_songs[2].title == "Weird Separator"
    assert parsed_songs[2].artists == ["Artist A ; Artist B"]
    
    # 验证是否打印了警告信息
    captured = capsys.readouterr()
    assert "格式不正确" in captured.err
    assert "NoSeparatorHere" in captured.err


def test_parse_song_file_empty_file():
    """测试解析空文件"""
    file_path = get_test_data_path('empty_file.txt')
    parsed_songs = parse_song_file(file_path)
    
    # 验证返回空列表
    assert len(parsed_songs) == 0
    assert parsed_songs == []


def test_parse_song_file_nonexistent_file():
    """测试解析不存在的文件"""
    file_path = get_test_data_path('nonexistent_file.txt')
    
    # 验证是否抛出FileNotFoundError
    with pytest.raises(FileNotFoundError):
        parse_song_file(file_path)


def test_artist_extra_spaces():
    """测试解析艺术家名称中有额外空格的情况"""
    # 创建临时测试文件路径
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False) as temp_file:
        temp_file.write("Song Title -  Artist1  /  Artist2    ")
        temp_file_path = temp_file.name
    
    try:
        # 解析文件
        parsed_songs = parse_song_file(temp_file_path)
        
        # 验证解析结果
        assert len(parsed_songs) == 1
        assert parsed_songs[0].title == "Song Title"
        assert parsed_songs[0].artists == ["Artist1", "Artist2"]
    finally:
        # 清理临时文件
        os.unlink(temp_file_path) 