import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# 添加项目根目录到sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from spotify_playlist_importer.core.models import ParsedSong, MatchedSong
from spotify_playlist_importer.main import process_songs
from spotipy.exceptions import SpotifyException


class TestProcessSongs:
    
    def test_process_songs_matched(self):
        """测试处理找到匹配的歌曲的情况"""
        # 准备测试数据
        parsed_songs = [
            ParsedSong(original_line="Test Song - Test Artist", title="Test Song", artists=["Test Artist"])
        ]
        
        # 创建模拟的匹配歌曲对象
        mock_matched_song = MatchedSong(
            parsed_song=parsed_songs[0],
            spotify_id="test_id",
            name="Test Song",
            artists=["Test Artist"],
            uri="spotify:track:test_id",
            album_name="Test Album",
            album_image_urls=["https://example.com/image.jpg"],
            duration_ms=300000
        )
        
        # 使用patch模拟search_song_on_spotify和get_spotify_client函数
        with patch('spotify_playlist_importer.main.get_spotify_client') as mock_get_client, \
             patch('spotify_playlist_importer.main.search_song_on_spotify') as mock_search:
            # 设置mock行为
            mock_sp = MagicMock()
            mock_get_client.return_value = mock_sp
            mock_search.return_value = mock_matched_song
            
            # 调用函数
            results = process_songs(parsed_songs, should_print=False)
            
            # 验证结果
            assert len(results) == 1
            assert results[0].status == "MATCHED"
            assert results[0].matched_song_details == mock_matched_song
            assert results[0].error_message is None
    
    def test_process_songs_not_found(self):
        """测试处理未找到匹配的歌曲的情况"""
        # 准备测试数据
        parsed_songs = [
            ParsedSong(original_line="Unknown Song - Unknown Artist", title="Unknown Song", artists=["Unknown Artist"])
        ]
        
        # 使用patch模拟search_song_on_spotify和get_spotify_client函数
        with patch('spotify_playlist_importer.main.get_spotify_client') as mock_get_client, \
             patch('spotify_playlist_importer.main.search_song_on_spotify') as mock_search:
            # 设置mock行为
            mock_sp = MagicMock()
            mock_get_client.return_value = mock_sp
            mock_search.return_value = None  # 模拟未找到
            
            # 调用函数
            results = process_songs(parsed_songs, should_print=False)
            
            # 验证结果
            assert len(results) == 1
            assert results[0].status == "NOT_FOUND"
            assert results[0].matched_song_details is None
            assert results[0].error_message == "Song not found on Spotify."
    
    def test_process_songs_api_error(self):
        """测试处理API错误的情况"""
        # 准备测试数据
        parsed_songs = [
            ParsedSong(original_line="Error Song - Error Artist", title="Error Song", artists=["Error Artist"])
        ]
        
        # 使用patch模拟search_song_on_spotify和get_spotify_client函数
        with patch('spotify_playlist_importer.main.get_spotify_client') as mock_get_client, \
             patch('spotify_playlist_importer.main.search_song_on_spotify') as mock_search:
            # 设置mock行为
            mock_sp = MagicMock()
            mock_get_client.return_value = mock_sp
            mock_search.side_effect = SpotifyException(http_status=429, code=-1, msg="API rate limit exceeded")
            
            # 调用函数
            results = process_songs(parsed_songs, should_print=False)
            
            # 验证结果
            assert len(results) == 1
            assert results[0].status == "API_ERROR"
            assert results[0].matched_song_details is None
            assert "API rate limit exceeded" in results[0].error_message
    
    def test_process_songs_multiple(self):
        """测试处理多首歌曲，包括不同状态的情况"""
        # 准备测试数据
        parsed_songs = [
            ParsedSong(original_line="Song 1 - Artist 1", title="Song 1", artists=["Artist 1"]),
            ParsedSong(original_line="Song 2 - Artist 2", title="Song 2", artists=["Artist 2"]),
            ParsedSong(original_line="Song 3 - Artist 3", title="Song 3", artists=["Artist 3"]),
        ]
        
        # 创建模拟的匹配歌曲对象
        mock_matched_song = MatchedSong(
            parsed_song=parsed_songs[0],
            spotify_id="test_id",
            name="Song 1",
            artists=["Artist 1"],
            uri="spotify:track:test_id",
            album_name="Test Album",
            album_image_urls=["https://example.com/image.jpg"],
            duration_ms=300000
        )
        
        # 使用patch模拟search_song_on_spotify和get_spotify_client函数
        with patch('spotify_playlist_importer.main.get_spotify_client') as mock_get_client, \
             patch('spotify_playlist_importer.main.search_song_on_spotify') as mock_search:
            # 设置mock行为
            mock_sp = MagicMock()
            mock_get_client.return_value = mock_sp
            
            # 第一首歌找到匹配，第二首未找到，第三首引发API错误
            mock_search.side_effect = [
                mock_matched_song,  # 第一首歌
                None,               # 第二首歌
                SpotifyException(http_status=429, code=-1, msg="API rate limit exceeded")  # 第三首歌
            ]
            
            # 调用函数
            results = process_songs(parsed_songs, should_print=False)
            
            # 验证结果
            assert len(results) == 3
            
            # 验证第一首歌
            assert results[0].status == "MATCHED"
            assert results[0].matched_song_details == mock_matched_song
            assert results[0].error_message is None
            
            # 验证第二首歌
            assert results[1].status == "NOT_FOUND"
            assert results[1].matched_song_details is None
            assert results[1].error_message == "Song not found on Spotify."
            
            # 验证第三首歌
            assert results[2].status == "API_ERROR"
            assert results[2].matched_song_details is None
            assert "API rate limit exceeded" in results[2].error_message 