# Spotify 歌单导入工具数据模型

本文档定义了 "Spotify 歌单导入工具" 应用程序在内部处理和传递数据时使用的核心数据结构。推荐使用 Python 的 `dataclasses` 或 `Pydantic` 来定义这些模型，以获得类型安全和（对于 Pydantic）数据验证的好处。

## 核心应用实体 / 领域对象

### 1. `ParsedSong` (已解析的歌曲信息)

* **描述**: 代表从用户提供的输入文件中解析出来的单首歌曲的基本信息。
* **来源**: 由 `core/input_parser.py` 模块在解析输入文件时创建。
* **模式 / 接口定义**:
    ```python
    from dataclasses import dataclass, field
    from typing import List

    @dataclass
    class ParsedSong:
        """代表从用户输入解析出的一首歌的基本信息"""
        original_line: str  # 用户在文件中提供的原始行文本
        title: str          # 解析出的歌曲标题
        artists: List[str]  # 解析出的艺人列表 (可能有多位艺人)
    ```
* **字段说明**:
    * `original_line` (str): 用户在输入文件中提供的原始文本行，用于最终报告的追溯。
    * `title` (str): 从原始行中提取的歌曲标题。
    * `artists` (List[str]): 从原始行中提取的艺人名称列表。

### 2. `MatchedSong` (已匹配的 Spotify 歌曲信息)

* **描述**: 代表在 Spotify 平台上成功搜索并匹配到的歌曲的详细信息。
* **来源**: 由 `spotify/client.py` 模块在与 Spotify API 交互并成功找到匹配歌曲后创建。
* **模式 / 接口定义**:
    ```python
    from dataclasses import dataclass
    from typing import List, Optional
    # from .parsed_song import ParsedSong # 假设 ParsedSong 在同一models文件或可导入

    @dataclass
    class MatchedSong:
        """代表在 Spotify 上成功匹配到的歌曲的详细信息"""
        parsed_song: ParsedSong     # 对应的原始解析歌曲信息
        spotify_id: str             # Spotify 平台上的歌曲唯一ID
        name: str                   # Spotify 返回的歌曲名称 (可能与用户输入略有不同)
        artists: List[str]          # Spotify 返回的该歌曲的艺人列表
        uri: str                    # Spotify 歌曲的 URI (例如: "spotify:track:TRACK_ID")
        album_name: Optional[str] = None # Spotify 返回的歌曲所属专辑名称 (可选)
        duration_ms: Optional[int] = None # Spotify 返回的歌曲时长 (毫秒, 可选)
        # 可根据需要添加更多字段，如 preview_url, external_urls['spotify'] 等
    ```
* **字段说明**:
    * `parsed_song` (`ParsedSong`): 关联的 `ParsedSong` 对象，提供了原始输入信息。
    * `spotify_id` (str): Spotify 曲目的唯一标识符。
    * `name` (str): Spotify API 返回的官方歌曲名称。
    * `artists` (List[str]): Spotify API 返回的官方艺人名称列表。
    * `uri` (str): Spotify 曲目的 URI，用于添加到播放列表等操作。
    * `album_name` (Optional[str]): 歌曲所属专辑的名称（如果API返回）。
    * `duration_ms` (Optional[int]): 歌曲时长，单位为毫秒（如果API返回）。

### 3. `MatchResult` (单首歌曲的匹配结果)

* **描述**: 用于汇总一首输入歌曲的完整处理状态和匹配详情，最终用于生成用户报告。
* **来源**: 主要在 `main.py` 或协调模块中，根据 `ParsedSong` 和 `MatchedSong` (如果匹配成功) 创建。
* **模式 / 接口定义**:
    ```python
    from dataclasses import dataclass
    from typing import List, Optional
    # from .parsed_song import ParsedSong # 假设 ParsedSong 在同一models文件或可导入
    # from .matched_song import MatchedSong # 假设 MatchedSong 在同一models文件或可导入

    @dataclass
    class MatchResult:
        """汇总一首输入歌曲的处理状态和匹配详情"""
        original_input_line: str
        parsed_song_title: str
        parsed_artists: List[str]
        status: str  # 例如: "已匹配", "未找到", "搜索API错误"
        matched_song_details: Optional[MatchedSong] = None # 如果匹配成功，则包含MatchedSong对象
        error_message: Optional[str] = None # 如果处理过程中发生错误，记录错误信息
    ```
* **字段说明**:
    * `original_input_line` (str): 用户提供的原始文本行。
    * `parsed_song_title` (str): 解析出的歌曲标题。
    * `parsed_artists` (List[str]): 解析出的艺人列表。
    * `status` (str): 标记该歌曲的处理状态，例如：
        * "MATCHED" (已匹配)
        * "NOT_FOUND" (未在 Spotify 上找到)
        * "API_ERROR" (调用 Spotify API 搜索时发生错误)
        * "INPUT_FORMAT_ERROR" (输入行格式错误)
    * `matched_song_details` (Optional[`MatchedSong`]): 如果 `status` 为 "MATCHED"，此字段将包含对应的 `MatchedSong` 对象。
    * `error_message` (Optional[str]): 如果在处理此特定歌曲时发生错误 (例如 API 错误)，此字段可以记录相关的错误信息。

## API 载荷模式 (Spotify API - 仅作参考)

本项目主要 *消费* Spotify API，而不是 *提供* API。以下仅为与 Spotify API 交互时涉及的关键数据结构的简化表示，具体以 `spotipy`库的返回对象或 Spotify Web API 文档为准。

### Spotify 搜索结果项 (`TrackObjectSimplified` 的一部分)

当通过 `sp.search()` 查询歌曲时，返回结果中的每个曲目项大致包含：

* `id`: (str) 歌曲的 Spotify ID。
* `name`: (str) 歌曲名称。
* `artists`: (List[ArtistObjectSimplified]) 艺人对象列表，每个包含 `name`, `id`, `uri`。
* `album`: (AlbumObjectSimplified) 专辑对象，包含 `name`, `id`, `uri`, `images`。
* `uri`: (str) 歌曲的 Spotify URI。
* `duration_ms`: (int) 歌曲时长 (毫秒)。
* `preview_url`: (Optional[str]) 歌曲预览片段的 URL。
* `external_urls`: (Dict[str, str]) 包含例如 `{"spotify": "歌曲的Spotify页面URL"}`。

### Spotify 播放列表对象 (`PlaylistObjectSimplified` 或 `PlaylistObjectFull`)

当创建播放列表或获取播放列表信息时：

* `id`: (str) 播放列表的 Spotify ID。
* `name`: (str) 播放列表名称。
* `owner`: (PublicUserObject) 播放列表所有者信息。
* `public`: (bool) 是否为公开播放列表。
* `tracks`: (PagingObject[PlaylistTrackObject]) 包含播放列表中的曲目信息。
* `uri`: (str) 播放列表的 Spotify URI。
* `external_urls`: (Dict[str, str]) 包含例如 `{"spotify": "播放列表的Spotify页面URL"}`。

*这些仅为示意，实际开发中会直接使用 `spotipy` 返回的对象属性。*

## 变更日志

| 变更描述             | 日期       | 版本 | 作者        |
| -------------------- | ---------- | ---- | ----------- |
| 初稿 - Spotify-only | 2025-05-17 | 0.1  | 3-Architect |
| ...                  | ...        | ...  | ...         |