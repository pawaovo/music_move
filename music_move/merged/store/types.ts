// 定义状态管理相关类型

// Spotify 用户信息类型
export interface SpotifyUserInfo {
  id: string;
  display_name: string;
  email?: string;
  images?: { url: string }[];
}

// Spotify 认证状态响应类型
export interface AuthStatusResponse {
  isAuthenticated: boolean;
  userInfo: SpotifyUserInfo | null;
  spotifyLoginStatus?: boolean;
  error?: string;
}

// 匹配歌曲信息类型
export interface MatchedSong {
  original_input: string;
  spotify_id: string; 
  spotify_uri: string;
  title: string;
  artists: string[];
  matched_score: number;
  is_low_confidence: boolean;
  album?: string;
  album_image?: string;
  original_line?: string;
}

// 未匹配歌曲信息类型
export interface UnmatchedSong {
  original_input: string;
  reason: string;
}

// ProcessSongs API 返回数据类型
export interface ProcessSongsData {
  total_songs: number;
  matched_songs: MatchedSong[];
  unmatched_songs: UnmatchedSong[];
  processing_time?: number;
}

// 创建播放列表 API 返回数据类型
export interface CreatePlaylistData {
  playlist_id: string;
  playlist_url: string;
  playlist_name: string;
  added_tracks_count: number;
  failed_tracks_count?: number;
}

// API 错误类型
export interface ApiError {
  code: string;
  message: string;
  details?: any;
} 