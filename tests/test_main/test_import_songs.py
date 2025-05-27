import os
import sys
import pytest
from unittest.mock import patch, MagicMock, mock_open
from click.testing import CliRunner
from datetime import datetime

# 添加项目根目录到sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from spotify_playlist_importer.core.models import ParsedSong, MatchedSong
from spotify_playlist_importer.main import import_songs, cli
from spotipy.exceptions import SpotifyException


class TestImportSongs:
    
    def setup_method(self):
        """测试前的初始化"""
        self.runner = CliRunner()
        
        # 创建常用的测试数据
        self.test_parsed_songs = [
            ParsedSong(original_line="Song 1 - Artist 1", title="Song 1", artists=["Artist 1"]),
            ParsedSong(original_line="Song 2 - Artist 2", title="Song 2", artists=["Artist 2"]),
            ParsedSong(original_line="Song 3 - Artist 3", title="Song 3", artists=["Artist 3"]),
        ]
        
        # 模拟匹配的歌曲
        self.test_matched_songs = [
            MatchedSong(
                parsed_song=self.test_parsed_songs[0],
                spotify_id="id1",
                name="Song 1",
                artists=["Artist 1"],
                uri="spotify:track:id1",
                album_name="Album 1",
                duration_ms=300000
            ),
            MatchedSong(
                parsed_song=self.test_parsed_songs[1],
                spotify_id="id2",
                name="Song 2",
                artists=["Artist 2"],
                uri="spotify:track:id2",
                album_name="Album 2",
                duration_ms=310000
            )
        ]
        
    @patch('spotify_playlist_importer.main.get_spotify_client')
    @patch('spotify_playlist_importer.main.parse_song_file')
    @patch('spotify_playlist_importer.main.search_song_on_spotify')
    @patch('spotify_playlist_importer.main.create_spotify_playlist')
    @patch('spotify_playlist_importer.main.add_tracks_to_spotify_playlist')
    @patch('spotify_playlist_importer.main.open', new_callable=mock_open)
    @patch('spotify_playlist_importer.main.datetime')
    def test_import_songs_complete_flow(self, mock_datetime, mock_file, 
                                         mock_add_tracks, mock_create_playlist, 
                                         mock_search, mock_parse, mock_get_client):
        """测试完整的导入流程（所有匹配、创建播放列表、添加歌曲）"""
        # 设置mock行为
        mock_sp = MagicMock()
        mock_get_client.return_value = mock_sp
        mock_parse.return_value = self.test_parsed_songs
        
        # 设置搜索结果：前两首歌找到匹配，第三首未找到
        mock_search.side_effect = [
            self.test_matched_songs[0], 
            self.test_matched_songs[1], 
            None
        ]
        
        # 设置创建播放列表结果
        playlist_details = {
            'id': 'test_playlist_id',
            'url': 'https://open.spotify.com/playlist/test_playlist_id'
        }
        mock_create_playlist.return_value = playlist_details
        
        # 设置添加歌曲结果
        mock_add_tracks.return_value = True
        
        # 设置固定的日期时间
        fixed_date = datetime(2023, 1, 1, 12, 0, 0)
        mock_datetime.now.return_value = fixed_date
        mock_datetime.isoformat = datetime.isoformat  # 保留原始方法
        
        # 使用隔离文件系统创建测试文件
        with self.runner.isolated_filesystem():
            # 创建测试文件
            with open('test_songs.txt', 'w') as f:
                f.write("Song 1 - Artist 1\n")
                f.write("Song 2 - Artist 2\n")
                f.write("Song 3 - Artist 3\n")
            
            # 执行cli命令
            result = self.runner.invoke(cli, ['import', 'test_songs.txt', 
                                             '--playlist-name', 'Test Playlist', 
                                             '--public', 
                                             '--description', 'Test Description',
                                             '--output-report', 'test_report.txt'])
            
            # 验证执行是否成功
            assert result.exit_code == 0
            
            # 验证各个mock函数是否被正确调用
            mock_get_client.assert_called_once()
            mock_parse.assert_called_once_with('test_songs.txt')
            assert mock_search.call_count == 3
            
            # 验证创建播放列表调用
            mock_create_playlist.assert_called_once_with(
                mock_sp, 'Test Playlist', True, 'Test Description'
            )
            
            # 验证添加歌曲调用
            expected_uris = ['spotify:track:id1', 'spotify:track:id2']
            mock_add_tracks.assert_called_once_with(mock_sp, 'test_playlist_id', expected_uris)
            
            # 验证生成报告文件
            mock_file.assert_called_with('test_report.txt', 'w', encoding='utf-8')
            
            # 验证输出包含预期信息
            assert '成功匹配: 2' in result.output
            assert '未找到: 1' in result.output
            assert '已创建播放列表: Test Playlist' in result.output
            assert '已添加 2 首歌曲' in result.output
    
    @patch('spotify_playlist_importer.main.get_spotify_client')
    @patch('spotify_playlist_importer.main.parse_song_file')
    @patch('spotify_playlist_importer.main.search_song_on_spotify')
    @patch('spotify_playlist_importer.main.create_spotify_playlist')
    @patch('spotify_playlist_importer.main.add_tracks_to_spotify_playlist')
    @patch('spotify_playlist_importer.main.open', new_callable=mock_open)
    @patch('spotify_playlist_importer.main.datetime')
    def test_import_songs_no_matches(self, mock_datetime, mock_file, 
                                     mock_add_tracks, mock_create_playlist, 
                                     mock_search, mock_parse, mock_get_client):
        """测试当没有找到匹配歌曲时的导入流程"""
        # 设置mock行为
        mock_sp = MagicMock()
        mock_get_client.return_value = mock_sp
        mock_parse.return_value = self.test_parsed_songs
        
        # 设置搜索结果：所有歌曲都未找到匹配
        mock_search.return_value = None
        
        # 设置固定的日期时间
        fixed_date = datetime(2023, 1, 1, 12, 0, 0)
        mock_datetime.now.return_value = fixed_date
        mock_datetime.isoformat = datetime.isoformat  # 保留原始方法
        
        # 使用隔离文件系统创建测试文件
        with self.runner.isolated_filesystem():
            # 创建测试文件
            with open('test_songs.txt', 'w') as f:
                f.write("Song 1 - Artist 1\n")
                f.write("Song 2 - Artist 2\n")
                f.write("Song 3 - Artist 3\n")
            
            # 执行cli命令
            result = self.runner.invoke(cli, ['import', 'test_songs.txt'])
            
            # 验证执行是否成功
            assert result.exit_code == 0
            
            # 验证搜索被调用但播放列表创建和添加歌曲没有被调用
            assert mock_search.call_count == 3
            mock_create_playlist.assert_not_called()
            mock_add_tracks.assert_not_called()
            
            # 验证生成报告文件
            report_filename = f"matching_report_{fixed_date.strftime('%Y-%m-%d_%H%M%S')}.txt"
            mock_file.assert_called_with(report_filename, 'w', encoding='utf-8')
            
            # 验证输出包含预期信息
            assert '成功匹配: 0' in result.output
            assert '未找到: 3' in result.output
            assert '没有歌曲成功匹配到Spotify' in result.output
            assert '未创建播放列表' in result.output
    
    @patch('spotify_playlist_importer.main.get_spotify_client')
    @patch('spotify_playlist_importer.main.parse_song_file')
    @patch('spotify_playlist_importer.main.search_song_on_spotify')
    @patch('spotify_playlist_importer.main.create_spotify_playlist')
    @patch('spotify_playlist_importer.main.add_tracks_to_spotify_playlist')
    @patch('spotify_playlist_importer.main.open', new_callable=mock_open)
    @patch('spotify_playlist_importer.main.datetime')
    def test_import_songs_playlist_creation_failed(self, mock_datetime, mock_file, 
                                                  mock_add_tracks, mock_create_playlist, 
                                                  mock_search, mock_parse, mock_get_client):
        """测试创建播放列表失败的情况"""
        # 设置mock行为
        mock_sp = MagicMock()
        mock_get_client.return_value = mock_sp
        mock_parse.return_value = self.test_parsed_songs
        
        # 设置搜索结果：找到匹配
        mock_search.return_value = self.test_matched_songs[0]
        
        # 设置创建播放列表失败
        mock_create_playlist.return_value = None
        
        # 设置固定的日期时间
        fixed_date = datetime(2023, 1, 1, 12, 0, 0)
        mock_datetime.now.return_value = fixed_date
        mock_datetime.isoformat = datetime.isoformat  # 保留原始方法
        
        # 使用隔离文件系统创建测试文件
        with self.runner.isolated_filesystem():
            # 创建测试文件
            with open('test_songs.txt', 'w') as f:
                f.write("Song 1 - Artist 1\n")
                f.write("Song 2 - Artist 2\n")
                f.write("Song 3 - Artist 3\n")
            
            # 执行cli命令
            result = self.runner.invoke(cli, ['import', 'test_songs.txt'])
            
            # 验证执行是否成功
            assert result.exit_code == 0
            
            # 验证创建播放列表被调用但添加歌曲没有被调用
            mock_create_playlist.assert_called_once()
            mock_add_tracks.assert_not_called()
            
            # 验证生成报告文件
            report_filename = f"matching_report_{fixed_date.strftime('%Y-%m-%d_%H%M%S')}.txt"
            mock_file.assert_called_with(report_filename, 'w', encoding='utf-8')
            
            # 验证输出包含预期信息
            assert '成功匹配: 3' in result.output
            assert '创建播放列表' in result.output
            assert '失败' in result.output
            assert '未创建播放列表' in result.output
    
    @patch('spotify_playlist_importer.main.get_spotify_client')
    @patch('spotify_playlist_importer.main.parse_song_file')
    @patch('spotify_playlist_importer.main.search_song_on_spotify')
    @patch('spotify_playlist_importer.main.create_spotify_playlist')
    @patch('spotify_playlist_importer.main.add_tracks_to_spotify_playlist')
    @patch('spotify_playlist_importer.main.open', new_callable=mock_open)
    @patch('spotify_playlist_importer.main.datetime')
    def test_import_songs_add_tracks_failed(self, mock_datetime, mock_file, 
                                           mock_add_tracks, mock_create_playlist, 
                                           mock_search, mock_parse, mock_get_client):
        """测试添加歌曲失败的情况"""
        # 设置mock行为
        mock_sp = MagicMock()
        mock_get_client.return_value = mock_sp
        mock_parse.return_value = self.test_parsed_songs
        
        # 设置搜索结果：找到匹配
        mock_search.return_value = self.test_matched_songs[0]
        
        # 设置创建播放列表成功但添加歌曲失败
        playlist_details = {
            'id': 'test_playlist_id',
            'url': 'https://open.spotify.com/playlist/test_playlist_id'
        }
        mock_create_playlist.return_value = playlist_details
        mock_add_tracks.return_value = False
        
        # 设置固定的日期时间
        fixed_date = datetime(2023, 1, 1, 12, 0, 0)
        mock_datetime.now.return_value = fixed_date
        mock_datetime.isoformat = datetime.isoformat  # 保留原始方法
        
        # 使用隔离文件系统创建测试文件
        with self.runner.isolated_filesystem():
            # 创建测试文件
            with open('test_songs.txt', 'w') as f:
                f.write("Song 1 - Artist 1\n")
                f.write("Song 2 - Artist 2\n")
                f.write("Song 3 - Artist 3\n")
            
            # 执行cli命令
            result = self.runner.invoke(cli, ['import', 'test_songs.txt'])
            
            # 验证执行是否成功
            assert result.exit_code == 0
            
            # 验证创建播放列表和添加歌曲都被调用
            mock_create_playlist.assert_called_once()
            mock_add_tracks.assert_called_once()
            
            # 验证生成报告文件
            report_filename = f"matching_report_{fixed_date.strftime('%Y-%m-%d_%H%M%S')}.txt"
            mock_file.assert_called_with(report_filename, 'w', encoding='utf-8')
            
            # 验证输出包含预期信息
            assert '成功匹配: 3' in result.output
            assert '向播放列表添加部分或全部歌曲失败' in result.output
    
    @patch('spotify_playlist_importer.main.get_spotify_client')
    @patch('spotify_playlist_importer.main.parse_song_file')
    @patch('spotify_playlist_importer.main.open', new_callable=mock_open)
    @patch('spotify_playlist_importer.main.datetime')
    def test_import_songs_empty_file(self, mock_datetime, mock_file, 
                                     mock_parse, mock_get_client):
        """测试输入文件为空的情况"""
        # 设置mock行为
        mock_sp = MagicMock()
        mock_get_client.return_value = mock_sp
        mock_parse.return_value = []  # 返回空列表表示没有解析到歌曲
        
        # 设置固定的日期时间
        fixed_date = datetime(2023, 1, 1, 12, 0, 0)
        mock_datetime.now.return_value = fixed_date
        mock_datetime.isoformat = datetime.isoformat  # 保留原始方法
        
        # 使用隔离文件系统创建测试文件
        with self.runner.isolated_filesystem():
            # 创建一个空文件
            with open('empty_file.txt', 'w') as f:
                pass  # 不写入任何内容
            
            # 执行cli命令
            result = self.runner.invoke(cli, ['import', 'empty_file.txt'])
            
            # 验证执行是否成功
            assert result.exit_code == 0
            
            # 验证报告文件生成
            report_filename = f"matching_report_{fixed_date.strftime('%Y-%m-%d_%H%M%S')}.txt"
            mock_file.assert_called_with(report_filename, 'w', encoding='utf-8')
            
            # 验证输出包含预期信息
            assert '警告: 输入文件中未找到有效的歌曲条目' in result.output
    
    @patch('spotify_playlist_importer.main.get_spotify_client')
    def test_import_songs_file_not_found(self, mock_get_client):
        """测试输入文件不存在的情况"""
        # 设置mock行为
        mock_sp = MagicMock()
        mock_get_client.return_value = mock_sp
        
        # 执行cli命令，使用测试模式的文件系统，没有实际文件
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(cli, ['import', 'nonexistent_file.txt'])
            
            # 验证执行失败
            assert result.exit_code != 0
            
            # 验证错误消息
            assert "File 'nonexistent_file.txt' does not exist" in result.output
    
    @patch('spotify_playlist_importer.main.get_spotify_client')
    def test_import_songs_authentication_failed(self, mock_get_client):
        """测试认证失败的情况"""
        # 设置mock行为：认证失败
        mock_get_client.side_effect = Exception("Authentication failed")
        
        # 使用隔离文件系统创建测试文件
        with self.runner.isolated_filesystem():
            # 创建测试文件
            with open('test_songs.txt', 'w') as f:
                f.write("Song 1 - Artist 1\n")
            
            # 执行cli命令
            result = self.runner.invoke(cli, ['import', 'test_songs.txt'])
            
            # 验证执行失败
            assert result.exit_code != 0
            
            # 验证错误消息
            assert '获取Spotify客户端失败' in result.output 