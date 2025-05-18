import os
import sys
import pytest
from unittest.mock import MagicMock, patch

# 添加项目根目录到sys.path，使测试可以导入项目模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from spotify_playlist_importer.spotify.client import search_song_on_spotify, create_spotify_playlist, add_tracks_to_spotify_playlist
from spotify_playlist_importer.core.models import ParsedSong, MatchedSong
from spotipy.exceptions import SpotifyException


# 创建ParsedSong实例的辅助函数
def create_parsed_song(title="Test Song", artists=None):
    if artists is None:
        artists = ["Test Artist"]
    return ParsedSong(
        original_line=f"{title} - {' / '.join(artists)}",
        title=title,
        artists=artists
    )


# 创建模拟的Spotify搜索结果
def create_mock_spotify_search_result(id="test_id", name="Test Song", 
                                     artists=None, uri="spotify:track:test_id",
                                     album_name="Test Album", duration_ms=300000):
    if artists is None:
        artists = [{"name": "Test Artist"}]
    
    return {
        'tracks': {
            'items': [
                {
                    'id': id,
                    'name': name,
                    'artists': artists,
                    'uri': uri,
                    'album': {'name': album_name},
                    'duration_ms': duration_ms
                }
            ]
        }
    }


class TestSearchSongOnSpotify:
    
    def test_search_song_success(self):
        """测试成功搜索歌曲的情况"""
        # 创建测试数据
        parsed_song = create_parsed_song("Bohemian Rhapsody", ["Queen"])
        mock_result = create_mock_spotify_search_result(
            id="1AhDOtG9vPSOmsWgNW0BEY",
            name="Bohemian Rhapsody",
            artists=[{"name": "Queen"}],
            uri="spotify:track:1AhDOtG9vPSOmsWgNW0BEY",
            album_name="A Night At The Opera (2011 Remaster)",
            duration_ms=354947
        )
        
        # 创建模拟的Spotify客户端
        mock_sp = MagicMock()
        mock_sp.search.return_value = mock_result
        
        # 调用被测试的函数
        result = search_song_on_spotify(mock_sp, parsed_song)
        
        # 验证结果
        assert result is not None
        assert result.spotify_id == "1AhDOtG9vPSOmsWgNW0BEY"
        assert result.name == "Bohemian Rhapsody"
        assert result.artists == ["Queen"]
        assert result.uri == "spotify:track:1AhDOtG9vPSOmsWgNW0BEY"
        assert result.album_name == "A Night At The Opera (2011 Remaster)"
        assert result.duration_ms == 354947
        assert result.parsed_song == parsed_song
        
        # 验证search调用
        mock_sp.search.assert_called_once_with(
            q="track:Bohemian Rhapsody artist:Queen", 
            limit=1, 
            type='track'
        )
    
    def test_search_song_not_found(self):
        """测试未找到歌曲的情况"""
        # 创建测试数据
        parsed_song = create_parsed_song("Non Existent Song", ["Unknown Artist"])
        
        # 创建模拟的Spotify客户端，返回空结果
        mock_sp = MagicMock()
        mock_sp.search.return_value = {'tracks': {'items': []}}
        
        # 调用被测试的函数
        result = search_song_on_spotify(mock_sp, parsed_song)
        
        # 验证结果
        assert result is None
        
        # 验证search调用
        mock_sp.search.assert_called_once_with(
            q="track:Non Existent Song artist:Unknown Artist", 
            limit=1, 
            type='track'
        )
    
    def test_search_song_api_error(self):
        """测试API错误的情况"""
        # 创建测试数据
        parsed_song = create_parsed_song("Error Song", ["Error Artist"])
        
        # 创建模拟的Spotify客户端，抛出SpotifyException
        mock_sp = MagicMock()
        mock_sp.search.side_effect = SpotifyException(
            http_status=429, 
            code=-1, 
            msg="API rate limit exceeded"
        )
        
        # 调用被测试的函数
        result = search_song_on_spotify(mock_sp, parsed_song)
        
        # 验证结果
        assert result is None
        
        # 验证search调用
        mock_sp.search.assert_called_once_with(
            q="track:Error Song artist:Error Artist", 
            limit=1, 
            type='track'
        )
    
    def test_search_song_without_artist(self):
        """测试没有艺术家的情况"""
        # 创建测试数据
        parsed_song = create_parsed_song("Only Title", [])
        mock_result = create_mock_spotify_search_result(
            name="Only Title",
            artists=[{"name": "Some Artist"}]
        )
        
        # 创建模拟的Spotify客户端
        mock_sp = MagicMock()
        mock_sp.search.return_value = mock_result
        
        # 调用被测试的函数
        result = search_song_on_spotify(mock_sp, parsed_song)
        
        # 验证结果
        assert result is not None
        assert result.name == "Only Title"
        assert result.artists == ["Some Artist"]
        
        # 验证search调用（只有标题，没有艺术家）
        mock_sp.search.assert_called_once_with(
            q="track:Only Title", 
            limit=1, 
            type='track'
        )
    
    def test_search_song_empty_title(self):
        """测试标题为空的情况"""
        # 创建测试数据
        parsed_song = create_parsed_song("", ["Some Artist"])
        
        # 创建模拟的Spotify客户端
        mock_sp = MagicMock()
        
        # 调用被测试的函数
        result = search_song_on_spotify(mock_sp, parsed_song)
        
        # 验证结果
        assert result is None
        
        # 验证search没有被调用
        mock_sp.search.assert_not_called()
    
    def test_search_song_special_characters(self, capsys):
        """测试标题或艺术家包含特殊字符的情况"""
        # 创建测试数据
        parsed_song = create_parsed_song("Song with !@#$%^", ["Artist & 123"])
        mock_result = create_mock_spotify_search_result(
            name="Song with !@#$%^",
            artists=[{"name": "Artist & 123"}]
        )
        
        # 创建模拟的Spotify客户端
        mock_sp = MagicMock()
        mock_sp.search.return_value = mock_result
        
        # 调用被测试的函数
        result = search_song_on_spotify(mock_sp, parsed_song)
        
        # 验证结果
        assert result is not None
        assert result.name == "Song with !@#$%^"
        assert result.artists == ["Artist & 123"]
        
        # 验证search调用（特殊字符不需要手动编码，spotipy会处理）
        mock_sp.search.assert_called_once_with(
            q="track:Song with !@#$%^ artist:Artist & 123", 
            limit=1, 
            type='track'
        ) 


class TestCreateSpotifyPlaylist:
    """测试创建Spotify播放列表的功能"""
    
    def test_create_playlist_success(self):
        """测试成功创建播放列表的情况"""
        # 创建模拟的Spotify客户端
        mock_sp = MagicMock()
        
        # 设置current_user返回值
        mock_sp.current_user.return_value = {"id": "test_user_id"}
        
        # 设置user_playlist_create返回值
        mock_sp.user_playlist_create.return_value = {
            "id": "test_playlist_id",
            "external_urls": {
                "spotify": "https://open.spotify.com/playlist/test_playlist_id"
            }
        }
        
        # 调用被测试的函数
        result = create_spotify_playlist(
            sp=mock_sp,
            playlist_name="Test Playlist",
            is_public=False,
            playlist_description="A test playlist"
        )
        
        # 验证结果
        assert result is not None
        assert result['id'] == "test_playlist_id"
        assert result['url'] == "https://open.spotify.com/playlist/test_playlist_id"
        
        # 验证函数调用
        mock_sp.current_user.assert_called_once()
        mock_sp.user_playlist_create.assert_called_once_with(
            user="test_user_id",
            name="Test Playlist",
            public=False,
            description="A test playlist"
        )
    
    def test_create_playlist_without_description(self):
        """测试没有描述时创建播放列表的情况"""
        # 创建模拟的Spotify客户端
        mock_sp = MagicMock()
        
        # 设置current_user返回值
        mock_sp.current_user.return_value = {"id": "test_user_id"}
        
        # 设置user_playlist_create返回值
        mock_sp.user_playlist_create.return_value = {
            "id": "test_playlist_id",
            "external_urls": {
                "spotify": "https://open.spotify.com/playlist/test_playlist_id"
            }
        }
        
        # 调用被测试的函数，不提供描述
        result = create_spotify_playlist(
            sp=mock_sp,
            playlist_name="Test Playlist",
            is_public=True,
            playlist_description=None
        )
        
        # 验证结果
        assert result is not None
        assert result['id'] == "test_playlist_id"
        
        # 验证函数调用，确认description为空字符串而不是None
        mock_sp.user_playlist_create.assert_called_once_with(
            user="test_user_id",
            name="Test Playlist",
            public=True,
            description=""
        )
    
    def test_get_user_id_failed(self):
        """测试获取用户ID失败的情况"""
        # 创建模拟的Spotify客户端
        mock_sp = MagicMock()
        
        # 设置current_user抛出异常
        mock_sp.current_user.side_effect = SpotifyException(
            http_status=401, 
            code=-1, 
            msg="Token expired"
        )
        
        # 调用被测试的函数
        result = create_spotify_playlist(
            sp=mock_sp,
            playlist_name="Test Playlist",
            is_public=False,
            playlist_description="A test playlist"
        )
        
        # 验证结果
        assert result is None
        
        # 验证函数调用
        mock_sp.current_user.assert_called_once()
        mock_sp.user_playlist_create.assert_not_called()
    
    def test_create_playlist_api_error(self):
        """测试创建播放列表时API错误的情况"""
        # 创建模拟的Spotify客户端
        mock_sp = MagicMock()
        
        # 设置current_user返回值
        mock_sp.current_user.return_value = {"id": "test_user_id"}
        
        # 设置user_playlist_create抛出异常
        mock_sp.user_playlist_create.side_effect = SpotifyException(
            http_status=403, 
            code=-1, 
            msg="Insufficient scope"
        )
        
        # 调用被测试的函数
        result = create_spotify_playlist(
            sp=mock_sp,
            playlist_name="Test Playlist",
            is_public=False,
            playlist_description="A test playlist"
        )
        
        # 验证结果
        assert result is None
        
        # 验证函数调用
        mock_sp.current_user.assert_called_once()
        mock_sp.user_playlist_create.assert_called_once()
    
    def test_create_playlist_incomplete_response(self):
        """测试API返回数据不完整的情况"""
        # 创建模拟的Spotify客户端
        mock_sp = MagicMock()
        
        # 设置current_user返回值
        mock_sp.current_user.return_value = {"id": "test_user_id"}
        
        # 设置user_playlist_create返回不完整的数据
        mock_sp.user_playlist_create.return_value = {
            # 缺少id或external_urls字段
            "name": "Test Playlist"
        }
        
        # 调用被测试的函数
        result = create_spotify_playlist(
            sp=mock_sp,
            playlist_name="Test Playlist",
            is_public=False,
            playlist_description="A test playlist"
        )
        
        # 验证结果
        assert result is None 


class TestAddTracksToSpotifyPlaylist:
    """测试向Spotify播放列表添加歌曲的功能"""
    
    def test_add_tracks_less_than_100_success(self):
        """测试成功添加少于100首歌曲的情况"""
        # 创建测试数据
        track_uris = [f"spotify:track:test{i}" for i in range(50)]
        playlist_id = "test_playlist_id"
        
        # 创建模拟的Spotify客户端
        mock_sp = MagicMock()
        mock_sp.playlist_add_items.return_value = {"snapshot_id": "test_snapshot"}
        
        # 调用被测试的函数
        result = add_tracks_to_spotify_playlist(mock_sp, playlist_id, track_uris)
        
        # 验证结果
        assert result is True
        
        # 验证playlist_add_items被调用了1次，且参数正确
        mock_sp.playlist_add_items.assert_called_once_with(playlist_id, track_uris)
    
    def test_add_tracks_more_than_100_success(self):
        """测试成功添加超过100首歌曲的情况（需要分批）"""
        # 创建测试数据 - 150首歌曲
        track_uris = [f"spotify:track:test{i}" for i in range(150)]
        playlist_id = "test_playlist_id"
        
        # 创建模拟的Spotify客户端
        mock_sp = MagicMock()
        mock_sp.playlist_add_items.return_value = {"snapshot_id": "test_snapshot"}
        
        # 调用被测试的函数
        result = add_tracks_to_spotify_playlist(mock_sp, playlist_id, track_uris)
        
        # 验证结果
        assert result is True
        
        # 验证playlist_add_items被调用了2次，第一次100首，第二次50首
        assert mock_sp.playlist_add_items.call_count == 2
        mock_sp.playlist_add_items.assert_any_call(playlist_id, track_uris[:100])
        mock_sp.playlist_add_items.assert_any_call(playlist_id, track_uris[100:])
    
    def test_add_tracks_exactly_200_success(self):
        """测试成功添加刚好200首歌曲的情况（需要分批）"""
        # 创建测试数据 - 200首歌曲
        track_uris = [f"spotify:track:test{i}" for i in range(200)]
        playlist_id = "test_playlist_id"
        
        # 创建模拟的Spotify客户端
        mock_sp = MagicMock()
        mock_sp.playlist_add_items.return_value = {"snapshot_id": "test_snapshot"}
        
        # 调用被测试的函数
        result = add_tracks_to_spotify_playlist(mock_sp, playlist_id, track_uris)
        
        # 验证结果
        assert result is True
        
        # 验证playlist_add_items被调用了2次，每次100首
        assert mock_sp.playlist_add_items.call_count == 2
        mock_sp.playlist_add_items.assert_any_call(playlist_id, track_uris[:100])
        mock_sp.playlist_add_items.assert_any_call(playlist_id, track_uris[100:200])
    
    def test_add_tracks_api_error_single_batch(self):
        """测试添加单批歌曲时API错误的情况"""
        # 创建测试数据
        track_uris = [f"spotify:track:test{i}" for i in range(50)]
        playlist_id = "test_playlist_id"
        
        # 创建模拟的Spotify客户端，设置API异常
        mock_sp = MagicMock()
        mock_sp.playlist_add_items.side_effect = SpotifyException(
            http_status=403, 
            code=-1, 
            msg="Insufficient scope"
        )
        
        # 调用被测试的函数
        result = add_tracks_to_spotify_playlist(mock_sp, playlist_id, track_uris)
        
        # 验证结果
        assert result is False
        
        # 验证playlist_add_items被调用了1次
        mock_sp.playlist_add_items.assert_called_once_with(playlist_id, track_uris)
    
    def test_add_tracks_api_error_first_batch(self):
        """测试添加多批歌曲时第一批失败的情况"""
        # 创建测试数据 - 150首歌曲
        track_uris = [f"spotify:track:test{i}" for i in range(150)]
        playlist_id = "test_playlist_id"
        
        # 创建模拟的Spotify客户端，设置第一次调用抛出异常
        mock_sp = MagicMock()
        mock_sp.playlist_add_items.side_effect = SpotifyException(
            http_status=403, 
            code=-1, 
            msg="Insufficient scope"
        )
        
        # 调用被测试的函数
        result = add_tracks_to_spotify_playlist(mock_sp, playlist_id, track_uris)
        
        # 验证结果
        assert result is False
        
        # 验证playlist_add_items只被调用了1次（失败后不再继续）
        mock_sp.playlist_add_items.assert_called_once_with(playlist_id, track_uris[:100])
    
    def test_add_tracks_empty_uri_list(self):
        """测试添加空URI列表的情况"""
        # 创建测试数据 - 空列表
        track_uris = []
        playlist_id = "test_playlist_id"
        
        # 创建模拟的Spotify客户端
        mock_sp = MagicMock()
        
        # 调用被测试的函数
        result = add_tracks_to_spotify_playlist(mock_sp, playlist_id, track_uris)
        
        # 验证结果
        assert result is True
        
        # 验证playlist_add_items未被调用
        mock_sp.playlist_add_items.assert_not_called() 