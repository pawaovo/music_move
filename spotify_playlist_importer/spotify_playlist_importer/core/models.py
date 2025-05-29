from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ParsedSong:
    """代表从用户输入解析出的一首歌的基本信息"""

    original_line: str
    title: str
    artists: List[str]


@dataclass
class MatchedSong:
    """代表在 Spotify 上成功匹配到的歌曲的详细信息"""

    parsed_song: ParsedSong
    spotify_id: str
    name: str
    artists: List[str]
    uri: str
    original_line: Optional[str] = None  # 添加原始输入行信息字段
    album_name: Optional[str] = None
    album_image_urls: Optional[List[str]] = None  # 添加专辑封面图片URL列表
    duration_ms: Optional[int] = None
    is_low_confidence: bool = False  # 新增字段：指示这是否为低匹配度匹配
    matched_score: float = 0.0  # 新增字段：匹配分数


@dataclass
class MatchResult:
    """汇总一首输入歌曲的处理状态和匹配详情"""

    original_input_line: str
    parsed_song_title: str
    parsed_artists: List[str]
    status: str  # 例如: "MATCHED", "NOT_FOUND", "API_ERROR", "INPUT_FORMAT_ERROR"
    matched_song_details: Optional[MatchedSong] = None
    error_message: Optional[str] = None
