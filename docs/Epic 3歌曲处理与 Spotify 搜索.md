

# Story 3.1: 实现输入歌曲列表文件解析器

**Status:** Draft

## Goal & Context

**User Story:** 作为应用程序，我需要能够读取用户指定的文本文件，并按照 "歌曲名称 - 艺人1 / 艺人2" 的格式解析每一行，将其转换为内部的 `ParsedSong` 数据结构。

**Context:** 此故事是 Epic 3 的起点，依赖于 Epic 1 中定义的核心数据模型 (Story 1.4) 和 CLI 入口 (Story 1.3，用于接收文件路径)。正确解析用户输入是后续在 Spotify 上搜索歌曲的前提。如果输入无法正确理解，整个流程将无法进行。

## Detailed Requirements

根据 `docs/epic3.md`：

  * 创建 `spotify_playlist_importer/core/input_parser.py` 模块。
  * 模块能读取指定路径的文本文件。
  * 能正确解析符合 "歌名 - 艺人" 格式的行。
  * 能正确处理包含多个艺人（以 " / " 分隔）的情况。
  * 对于格式不正确的行，能进行标记或优雅地跳过，并记录相关信息。
  * 返回 `ParsedSong` 对象列表。

## Acceptance Criteria (ACs)

  * AC1: `spotify_playlist_importer/spotify_playlist_importer/core/input_parser.py` 文件已创建。
  * AC2: `input_parser.py` 中定义了一个函数，例如 `parse_song_file(file_path: str) -> List[ParsedSong]`。
  * AC3: 调用 `parse_song_file` 时，如果 `file_path` 指向的文件不存在或不可读，函数应引发 `FileNotFoundError` 或类似的 `IOError`。
  * AC4: 函数能成功读取并逐行处理 UTF-8 编码的文本文件。
  * AC5: 对于每一行，函数能正确使用 " - " (空格-连字符-空格) 作为分隔符来区分歌曲标题和艺术家字符串。解析时应去除标题和艺术家字符串两端的空白。
  * AC6: 函数能正确解析艺术家字符串，如果其中包含 " / " (空格/空格)，则将其分割为多个艺术家姓名组成的列表。每个艺术家姓名应去除两端空白。
  * AC7: 对于成功解析的每一行，函数都创建一个 `ParsedSong` 实例，并正确填充 `original_line`, `title`, 和 `artists` 字段。
  * AC8: 如果某一行不包含 " - " 分隔符，或者分隔后某一部分为空，该行应被视为格式错误。函数应能选择一种策略处理（例如，打印警告到 `stderr` 并跳过该行，或者将其包含在某种形式的错误报告中，但对于本故事，简单跳过并打印警告即可）。它不应使整个解析过程失败。
  * AC9: 函数返回一个 `ParsedSong` 对象列表，其中仅包含成功解析的歌曲。如果文件为空或所有行都格式错误，则返回空列表。
  * AC10: `input_parser.py` 模块的代码符合项目的编码标准。

## Technical Implementation Context

**Guidance:** 使用以下细节进行实施。如果需要更广泛的上下文，请参阅链接的 `docs/` 文件。

  * **Relevant Files:**

      * Files to Create:
          * `spotify_playlist_importer/spotify_playlist_importer/core/input_parser.py`
          * `tests/core/test_input_parser.py`
          * `tests/test_data/sample_songs.txt` (用于测试的示例文件)
          * `tests/test_data/empty_file.txt`
          * `tests/test_data/malformed_songs.txt`
      * Files to Modify: N/A
      * *(Hint: 参见 `docs/project-structure.md` 查看整体布局)*

  * **Key Technologies:**

      * Python (文件 I/O, string manipulation)
      * `typing.List`
      * `spotify_playlist_importer.core.models.ParsedSong`
      * `sys` (for `sys.stderr`)
      * *(Hint: 参见 `docs/tech-stack.md` 查看完整列表)*

  * **API Interactions / SDK Usage:**

      * N/A
      * *(Hint: 参见 `docs/api-reference.md` 了解外部API和SDK的详细信息)*

  * **UI/UX Notes:** 如果跳过格式错误的行，应通过 `stderr` 或日志（如果日志系统已实现）通知用户。

  * **Data Structures:**

      * `ParsedSong` (从 `core.models` 导入并使用)
      * *(Hint: 参见 `docs/data-models.md` 了解关键项目数据结构)*

  * **Environment Variables:**

      * N/A
      * *(Hint: 参见 `docs/environment-vars.md` 查看所有变量)*

  * **Coding Standards Notes:**

      * 使用 `with open(file_path, 'r', encoding='utf-8') as f:` 来安全地打开和读取文件。
      * 字符串解析时注意使用 `.strip()` 来处理潜在的前导/尾随空格。
      * 错误处理：对 `IOError` 使用 `try-except`。对于行格式错误，在函数内部处理。
      * *(Hint: 参见 `docs/coding-standards.md` 查看完整标准)*

## Tasks / Subtasks

根据 `docs/epic3.md` 中 Story 3.1 的初步任务分解进行细化：

  * [ ] 任务3.1.1: 创建 `spotify_playlist_importer/spotify_playlist_importer/core/input_parser.py` 文件。
  * [ ] 任务3.1.2: 在文件顶部导入 `ParsedSong` 和 `List`, `sys`。
    ```python
    import sys
    from typing import List
    from ..models import ParsedSong # Assuming models.py is in the same 'core' package
                                    # Or from spotify_playlist_importer.core.models import ParsedSong
    ```
  * [ ] 任务3.1.3: 定义 `parse_song_file(file_path: str) -> List[ParsedSong]:` 函数。
  * [ ] 任务3.1.4: 在函数内部，初始化一个空的 `parsed_songs` 列表。
  * [ ] 任务3.1.5: 使用 `try-except FileNotFoundError` 块包裹文件打开和读取逻辑。
    ```python
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_number, original_line in enumerate(f, 1):
                # ... parsing logic ...
    except FileNotFoundError:
        print(f"Error: Input file not found at '{file_path}'", file=sys.stderr)
        raise # Re-raise the exception after printing the message or handle as per error strategy
    except IOError as e:
        print(f"Error: Could not read input file at '{file_path}'. Reason: {e}", file=sys.stderr)
        raise # Re-raise
    return parsed_songs
    ```
  * [ ] 任务3.1.6: 在 `for` 循环中，处理每一行 `original_line.strip()`。如果行为空，则跳过。
  * [ ] 任务3.1.7: 使用 `" - "` 分割行。检查分割结果是否为两部分。如果不是，打印警告到 `sys.stderr` (包含行号和内容) 并 `continue` 到下一行。
  * [ ] 任务3.1.8: 提取歌曲标题和艺术家字符串，并对两者都使用 `.strip()`。如果任一者为空字符串，同样打印警告并跳过。
  * [ ] 任务3.1.9: 解析艺术家字符串：使用 `" / "` 分割，并对每个分割出的艺术家姓名 `.strip()`。
  * [ ] 任务3.1.10: 创建 `ParsedSong` 实例并添加到 `parsed_songs` 列表。
  * [ ] 任务3.1.11: 创建 `tests/test_data/` 目录。
  * [ ] 任务3.1.12: 创建 `tests/test_data/sample_songs.txt` 包含各种有效歌曲行：
    ```
    Bohemian Rhapsody - Queen
    Stairway to Heaven - Led Zeppelin
    Hotel California - Eagles
    Imagine - John Lennon / Plastic Ono Band
      White Wedding   -   Billy Idol  
    ```
  * [ ] 任务3.1.13: 创建 `tests/test_data/malformed_songs.txt` 包含无效和混合行：
    ```
    Good Song - Good Artist
    NoSeparatorHere
     - Just Artist
    Just Title - 
    Another Good Song - Artist1 / Artist2 / Artist3
    Empty Line Next

    Weird Separator - Artist A ; Artist B 
    ```
  * [ ] 任务3.1.14: 创建 `tests/test_data/empty_file.txt` (空文件)。
  * [ ] 任务3.1.15: 创建 `tests/core/test_input_parser.py` 并编写单元测试（见下方测试需求）。
  * [ ] 任务3.1.16: 运行 linting 和 formatting 工具。
  * [ ] 任务3.1.17: 将新文件添加到Git并提交，提交信息如 "Implement song file parser module"。

## Testing Requirements

**Guidance:** 对照ACs通过以下方式验证实施。

  * **Unit Tests:**

      * 创建 `tests/core/test_input_parser.py`。
      * **测试用例1 (成功解析):**
          * 使用 `tests/test_data/sample_songs.txt`。
          * 调用 `parse_song_file`。
          * 断言返回的 `ParsedSong` 对象列表长度正确。
          * 逐个检查几个 `ParsedSong` 对象的 `title` 和 `artists` 列表是否与预期一致 (注意处理空格和多个艺术家的情况)。例如，"White Wedding" 的标题应为 "White Wedding"，艺人为 `["Billy Idol"]`。
      * **测试用例2 (处理格式错误的行):**
          * 使用 `tests/test_data/malformed_songs.txt`。
          * 调用 `parse_song_file`。
          * 断言返回的列表仅包含有效解析的歌曲 (例如，"Good Song - Good Artist", "Another Good Song - Artist1 / Artist2 / Artist3")。
          * (可选) 使用 `capsys` fixture 捕获 `stderr` 并验证是否为无效行打印了警告消息。
      * **测试用例3 (空文件):**
          * 使用 `tests/test_data/empty_file.txt`。
          * 调用 `parse_song_file`。
          * 断言返回空列表。
      * **测试用例4 (文件不存在):**
          * 使用 `pytest.raises(FileNotFoundError)` 来断言调用 `parse_song_file` 并传入一个不存在的文件路径时会引发 `FileNotFoundError`。
      * **测试用例5 (艺术家名称中的额外空格):**
          * 创建包含如 ` Song - Artist1  /  Artist2    ` 的测试行。
          * 验证解析出的艺术家列表为 `["Artist1", "Artist2"]` (没有多余空格)。

  * **Integration Tests:** N/A

  * **Manual/CLI Verification:**

      * 创建不同内容的测试txt文件。
      * 在Python解释器或一个临时脚本中，导入 `parse_song_file` 函数并使用这些测试文件调用它。
      * 打印返回的 `ParsedSong` 对象列表，检查其内容是否符合预期。
      * 测试文件不存在的情况。
      * 检查当文件包含格式错误的行时，控制台是否按预期打印了警告。

  * *(Hint: 参见 `docs/testing-strategy.md` 了解整体方法)*

-----

File: `ai/stories/epic3.story2.story.md`

# Story 3.2: 实现 Spotify 歌曲搜索与匹配逻辑

**Status:** Draft

## Goal & Context

**User Story:** 作为应用程序，我需要针对每个 `ParsedSong` 对象，使用 Spotify API 搜索相应的歌曲。我将默认选择搜索结果中的第一个曲目作为匹配项，并记录其详细信息为 `MatchedSong` 对象。

**Context:** 此故事建立在 Story 3.1 (输入文件解析器) 和 Epic 2 (Spotify 用户认证) 的基础上。它负责将用户提供的歌曲信息与 Spotify 的庞大曲库进行实际的匹配。这是核心功能链中的关键一步，将解析出的数据转化为可在 Spotify 上操作的实体。

## Detailed Requirements

根据 `docs/epic3.md`：

  * 在 `spotify_playlist_importer/spotify/client.py` 中实现搜索逻辑。
  * 接收 `ParsedSong` 对象和已认证的 `spotipy` 客户端。
  * 构造查询字符串。
  * 调用 Spotify API 的搜索端点，默认选择第一个结果。
  * 将结果转换为 `MatchedSong` 对象。
  * 处理未找到或API错误的情况（此部分由Story 3.3重点覆盖，但本故事需要基础的错误识别）。

## Acceptance Criteria (ACs)

  * AC1: `spotify_playlist_importer/spotify_playlist_importer/spotify/client.py` 文件已创建（如果尚不存在）或已准备好添加新功能。
  * AC2: `client.py` 中定义了一个函数，例如 `search_song_on_spotify(sp: spotipy.Spotify, parsed_song: ParsedSong) -> Optional[MatchedSong]`。
  * AC3: 函数能从 `parsed_song` 参数中获取歌曲标题和主要艺术家（列表中的第一个艺术家，如果列表不为空）。
  * AC4: 函数能正确构造 Spotify API 搜索查询字符串，格式为 `f"track:{title} artist:{artist}"`。标题和艺术家应进行适当的清理（例如，去除多余空格，但不需要复杂的URL编码，`spotipy`会处理）。
  * AC5: 函数使用提供的 `sp` (认证的 `spotipy.Spotify` 实例) 调用 `sp.search(q=query_string, type='track', limit=1, market=None)` (或考虑使用 `market='from_token'` 如果 `sp.me()` 可用且返回市场信息)。
  * AC6: 如果 `sp.search()` 调用成功并且 `results['tracks']['items']` 列表不为空：
      * 函数能从第一个条目 (`results['tracks']['items'][0]`) 中提取 Spotify ID (`id`), 歌曲名称 (`name`), 艺术家列表 (每个艺术家的 `name`), Spotify URI (`uri`), 专辑名称 (`album['name']`), 和歌曲时长 (`duration_ms`)。
      * 函数创建一个 `MatchedSong` 实例，并用提取到的信息以及原始的 `parsed_song` 对象来填充它，然后返回此实例。
  * AC7: 如果 `sp.search()` 调用成功但 `results['tracks']['items']` 列表为空（即未找到歌曲），函数返回 `None`。
  * AC8: 如果 `sp.search()` 调用时发生 `spotipy.SpotifyException` (例如，由于网络问题、无效请求参数（不太可能，因为参数固定）或速率限制)，函数应捕获此异常，打印错误到 `stderr` (或使用日志)，然后返回 `None`。
  * AC9: `spotify/client.py` 模块的代码符合项目的编码标准。

## Technical Implementation Context

**Guidance:** 使用以下细节进行实施。如果需要更广泛的上下文，请参阅链接的 `docs/` 文件。

  * **Relevant Files:**

      * Files to Create/Modify:
          * `spotify_playlist_importer/spotify_playlist_importer/spotify/client.py` (Create or Modify)
          * `tests/spotify/test_client.py` (Create or Modify)
      * Files to use for context:
          * `spotify_playlist_importer/core/models.py` (for `ParsedSong`, `MatchedSong`)
          * `spotify_playlist_importer/spotify/auth.py` (to understand how `sp` instance is obtained)
      * *(Hint: 参见 `docs/project-structure.md` 查看整体布局)*

  * **Key Technologies:**

      * Python
      * `spotipy` (特别是 `sp.search()` 方法)
      * `typing.Optional`, `typing.List`
      * `spotify_playlist_importer.core.models.ParsedSong`, `spotify_playlist_importer.core.models.MatchedSong`
      * `sys` (for `sys.stderr`) or a proper logging setup if available.
      * *(Hint: 参见 `docs/tech-stack.md` 查看完整列表)*

  * **API Interactions / SDK Usage:**

      * **`sp.search(q, limit, offset, type, market)`**:
          * `q`: 构造为 `f"track:{title} artist:{artist}"`。
          * `limit`: `1`
          * `type`: `'track'`
          * `market`: 考虑设为 `None` (默认) 或 `'from_token'`。`'from_token'` 需要确保 `sp` 实例是通过用户认证流程创建的，该流程可能已将市场信息与令牌关联。如果 `sp.me()` 可用，可以从中尝试获取市场。为简单起见，`None` 也可以接受，Spotify会尝试根据认证用户推断。
      * 响应结构: `results['tracks']['items']` 是一个列表。关注 `items[0]` 中的 `id`, `name`, `artists` (这是一个对象列表，每个对象有 `name`), `uri`, `album['name']`, `duration_ms`。
      * *(Hint: 参见 `docs/api-reference.md` (搜索歌曲部分) 和 `spotipy` 文档)*

  * **UI/UX Notes:** 错误/未找到的信息主要由调用此函数的逻辑处理 (Story 3.3, Story 4.3)，但此函数应提供清晰的返回值 (`MatchedSong` 或 `None`) 和适当的错误日志。

  * **Data Structures:**

      * 输入: `ParsedSong`
      * 输出: `Optional[MatchedSong]`
      * *(Hint: 参见 `docs/data-models.md` 了解关键项目数据结构)*

  * **Environment Variables:**

      * N/A (间接依赖于 `core.config` 来初始化 `sp` 实例)
      * *(Hint: 参见 `docs/environment-vars.md` 查看所有变量)*

  * **Coding Standards Notes:**

      * 函数和变量名使用 `snake_case`。
      * 包含类型提示。
      * 错误处理：捕获 `spotipy.SpotifyException`。
      * 从 `results['tracks']['items'][0]['artists']` 提取艺术家名称时，它是一个艺术家对象列表，需要遍历并提取每个对象的 `name` 属性，形成一个字符串列表。
      * *(Hint: 参见 `docs/coding-standards.md` 查看完整标准)*

## Tasks / Subtasks

  * [ ] 任务3.2.1: 创建或打开 `spotify_playlist_importer/spotify_playlist_importer/spotify/client.py`。
  * [ ] 任务3.2.2: 在文件顶部导入必要的模块和类:
    ```python
    import spotipy
    from typing import Optional, List
    import sys # Or your logging module
    from ..core.models import ParsedSong, MatchedSong # Adjust import path as needed
    ```
  * [ ] 任务3.2.3: 定义 `search_song_on_spotify(sp: spotipy.Spotify, parsed_song: ParsedSong) -> Optional[MatchedSong]:` 函数。
  * [ ] 任务3.2.4: 从 `parsed_song.title` 获取标题。从 `parsed_song.artists` 获取主要艺术家 (例如，列表中的第一个，如果列表为空则行为待定 - 简单起见，假设艺术家列表至少有一个元素，或在查询中省略艺术家部分)。
    ```python
    title = parsed_song.title.strip()
    # For simplicity, use the first artist if available. More robust logic could join all artists.
    primary_artist = parsed_song.artists[0].strip() if parsed_song.artists else "" 

    if not title: # Cannot search without a title
        # print(f"Warning: Cannot search for song with empty title from line: {parsed_song.original_line}", file=sys.stderr)
        return None

    query = f"track:{title}"
    if primary_artist:
        query += f" artist:{primary_artist}"
    # else:
        # print(f"Warning: No artist provided for title '{title}', searching by title only.", file=sys.stderr)

    ```
  * [ ] 任务3.2.5: 实现 `try-except spotipy.SpotifyException` 块来包裹 `sp.search()` 调用。
    ```python
    try:
        results = sp.search(q=query, limit=1, type='track') # market can be omitted or set
    except spotipy.SpotifyException as e:
        print(f"Spotify API error while searching for '{query}': {e}", file=sys.stderr)
        return None
    except Exception as e: # Catch any other unexpected error during search
        print(f"Unexpected error while searching for '{query}': {e}", file=sys.stderr)
        return None
    ```
  * [ ] 任务3.2.6: 在 `try` 块内部，检查 `results` 和 `results['tracks']['items']`。
    ```python
    if results and results['tracks'] and results['tracks']['items']:
        track_info = results['tracks']['items'][0]
        
        spotify_artists = [artist['name'] for artist in track_info.get('artists', [])]
        album_name = track_info.get('album', {}).get('name')
        duration_ms = track_info.get('duration_ms')

        matched_song = MatchedSong(
            parsed_song=parsed_song,
            spotify_id=track_info['id'],
            name=track_info['name'],
            artists=spotify_artists,
            uri=track_info['uri'],
            album_name=album_name,
            duration_ms=duration_ms
        )
        return matched_song
    else:
        # print(f"No results found on Spotify for query: {query}", file=sys.stderr) # More verbose logging
        return None
    ```
  * [ ] 任务3.2.7: 创建或更新 `tests/spotify/test_client.py` 并为 `search_song_on_spotify` 编写单元测试（见下方测试需求）。
  * [ ] 任务3.2.8: 运行 linting 和 formatting 工具。
  * [ ] 任务3.2.9: 将 `spotify/client.py` 和相关测试文件添加到Git并提交，提交信息如 "Implement Spotify song search functionality"。

## Testing Requirements

**Guidance:** 对照ACs通过以下方式验证实施。

  * **Unit Tests:**

      * 在 `tests/spotify/test_client.py` 中。
      * 需要 mock `spotipy.Spotify` 实例及其 `search` 方法。
      * **测试用例1 (成功找到歌曲):**
          * 准备一个 `ParsedSong` 实例。
          * Mock `sp.search()` 返回一个包含预期Spotify曲目数据的字典结构 (模拟 `results['tracks']['items'][0]`)。
          * 调用 `search_song_on_spotify`。
          * 断言返回的 `MatchedSong` 对象不为 `None`，并且其字段 (`spotify_id`, `name`, `artists`, `uri`, `album_name`, `duration_ms`, `parsed_song`) 被正确填充。
      * **测试用例2 (未找到歌曲):**
          * 准备一个 `ParsedSong` 实例。
          * Mock `sp.search()` 返回一个 `results['tracks']['items']` 为空列表的字典。
          * 调用 `search_song_on_spotify`。
          * 断言返回值为 `None`。
      * **测试用例3 (Spotify API 异常):**
          * 准备一个 `ParsedSong` 实例。
          * Mock `sp.search()` 引发 `spotipy.SpotifyException`。
          * 调用 `search_song_on_spotify`。
          * 断言返回值为 `None`。
          * (可选) 使用 `capsys` 捕获 `stderr` 并验证是否打印了错误消息。
      * **测试用例4 (不同输入):**
          * 测试 `ParsedSong` 只有标题没有艺术家的情况。
          * 测试 `ParsedSong` 标题或艺术家包含特殊字符（但不需要手动URL编码，验证查询字符串构造即可）。
      * **示例 Mock 结构 for `sp.search` success:**
        ```python
        mock_spotify_track_item = {
            'id': 'sample_id',
            'name': 'Sample Song Name',
            'artists': [{'name': 'Artist One'}, {'name': 'Artist Two'}],
            'uri': 'spotify:track:sample_id',
            'album': {'name': 'Sample Album'},
            'duration_ms': 240000
        }
        mock_search_results = {'tracks': {'items': [mock_spotify_track_item]}}
        # mock_sp_instance.search.return_value = mock_search_results
        ```

  * **Integration Tests:** （可选，如果需要测试与真实API的交互，但应标记为慢速并小心使用API配额）

      * 可以编写一个需要有效 `.env` 文件和用户授权的集成测试。
      * 调用真实的 `sp.search()` (对于一首肯定存在的歌曲)。
      * 验证返回结果的结构是否符合预期（但不依赖具体值，因为它们可能改变）。
      * **此步骤对于单元测试不是必需的，更多是用于开发时的手动验证或专门的E2E测试。**

  * **Manual/CLI Verification:**

      * 在获得一个已认证的 `sp` 对象后 (来自 Epic 2)，在Python解释器或临时脚本中：
          * 创建一个 `ParsedSong` 实例。
          * 调用 `search_song_on_spotify(sp, parsed_song_instance)`。
          * 打印返回的 `MatchedSong` 对象或 `None`。
          * 验证对于已知歌曲是否能返回正确匹配的歌曲信息。
          * 验证对于虚构的歌曲是否返回 `None`。

  * *(Hint: 参见 `docs/testing-strategy.md` 了解整体方法)*

-----

File: `ai/stories/epic3.story3.story.md`

# Story 3.3: 处理歌曲未找到或搜索API错误的情况

**Status:** Draft

## Goal & Context

**User Story:** 作为应用程序，当在 Spotify 上找不到某首歌曲，或在搜索过程中发生 API 错误时，我需要能够记录此状态，并为该歌曲生成一个包含相关错误信息的 `MatchResult`。

**Context:** 此故事是对 Story 3.2 (实现 Spotify 歌曲搜索与匹配逻辑) 的补充和细化，确保了搜索流程的完整性。虽然 Story 3.2 的 ACs 已经要求 `search_song_on_spotify` 在这些情况下返回 `None` 并打印/记录错误，但此故事更侧重于调用方（通常是 `main.py` 中的主流程编排逻辑）如何使用这个结果来构建一个全面的 `MatchResult` 对象。`MatchResult` 将用于最终的用户报告。

## Detailed Requirements

根据 `docs/epic3.md`：

  * 应用程序需要能够记录歌曲未找到或搜索API错误的状态。
  * 为这类歌曲生成一个包含相关错误信息的 `MatchResult`。

**注意:** 此故事的实现主要发生在调用 `search_song_on_spotify` 的地方（例如，`main.py` 中的循环处理逻辑），而不是在 `search_song_on_spotify` 函数内部创建 `MatchResult`。`search_song_on_spotify` 的职责是返回 `MatchedSong` 或 `None` 以及指示错误。

## Acceptance Criteria (ACs)

  * AC1: 当 `search_song_on_spotify` (from Story 3.2) 因未在Spotify找到歌曲而返回 `None` 时，调用它的代码（例如 `main.py` 中的歌曲处理循环）能够创建一个 `MatchResult` 实例。
      * 该 `MatchResult` 实例的 `status` 字段应设为 "NOT\_FOUND"。
      * `matched_song_details` 字段应为 `None`。
      * `error_message` 字段可以为 `None` 或一条类似 "Song not found on Spotify." 的消息。
      * `original_input_line`, `parsed_song_title`, `parsed_artists` 字段从原始的 `ParsedSong` 对象中正确填充。
  * AC2: 当 `search_song_on_spotify` 因Spotify API错误（例如 `SpotifyException`）而返回 `None` 时，调用它的代码能够创建一个 `MatchResult` 实例。
      * 该 `MatchResult` 实例的 `status` 字段应设为 "API\_ERROR"。
      * `matched_song_details` 字段应为 `None`。
      * `error_message` 字段应包含从捕获到的异常中提取的或一个通用的API错误消息（例如，"Spotify API error during search: [error details from exception]"）。
      * `original_input_line`, `parsed_song_title`, `parsed_artists` 字段从原始的 `ParsedSong` 对象中正确填充。
  * AC3: 如果 `search_song_on_spotify` 成功返回一个 `MatchedSong` 对象，调用它的代码能够创建一个 `MatchResult` 实例。
      * `status` 字段应设为 "MATCHED"。
      * `matched_song_details` 字段应包含返回的 `MatchedSong` 对象。
      * `error_message` 字段应为 `None`。
      * `original_input_line`, `parsed_song_title`, `parsed_artists` 字段从原始的 `ParsedSong` 对象中正确填充。

## Technical Implementation Context

**Guidance:** 代码实现主要在 `main.py` (或将要在Epic 4 Story 4.3中详细定义的编排逻辑模块) 中，而不是 `spotify/client.py`。

  * **Relevant Files:**

      * Files to Create/Modify:
          * `spotify_playlist_importer/spotify_playlist_importer/main.py` (Modify - 在歌曲处理循环中添加此逻辑)
          * (或者，如果编排逻辑被移到新模块，则修改该模块)
          * `tests/test_main.py` (or tests for the new orchestrator module) (Modify - 添加测试用例)
      * Files for context:
          * `spotify_playlist_importer/core/models.py` (for `ParsedSong`, `MatchedSong`, `MatchResult`)
          * `spotify_playlist_importer/spotify/client.py` (to understand `search_song_on_spotify`'s return)
      * *(Hint: 参见 `docs/project-structure.md` 查看整体布局)*

  * **Key Technologies:**

      * Python
      * `spotify_playlist_importer.core.models.MatchResult`
      * `spotify_playlist_importer.core.models.ParsedSong`
      * `spotify_playlist_importer.core.models.MatchedSong`
      * `spotify_playlist_importer.spotify.client.search_song_on_spotify` (调用它)
      * *(Hint: 参见 `docs/tech-stack.md` 查看完整列表)*

  * **API Interactions / SDK Usage:**

      * 间接通过调用 `search_song_on_spotify`。
      * *(Hint: 参见 `docs/api-reference.md` 了解外部API和SDK的详细信息)*

  * **UI/UX Notes:** `MatchResult` 对象中的 `status` 和 `error_message` 将用于生成最终的用户报告，因此信息的准确性和清晰度很重要。

  * **Data Structures:**

      * 输入: `ParsedSong` 对象 (来自文件解析器), `Optional[MatchedSong]` (来自 `search_song_on_spotify`)
      * 输出: `MatchResult` 对象
      * *(Hint: 参见 `docs/data-models.md` 了解关键项目数据结构)*

  * **Environment Variables:**

      * N/A
      * *(Hint: 参见 `docs/environment-vars.md` 查看所有变量)*

  * **Coding Standards Notes:**

      * 清晰的条件逻辑 (if/else) 来处理 `search_song_on_spotify` 的不同返回情况。
      * 正确实例化 `MatchResult`。
      * *(Hint: 参见 `docs/coding-standards.md` 查看完整标准)*

## Tasks / Subtasks

这些任务将在 `main.py`（或负责编排的模块）中实现，通常在一个循环遍历 `ParsedSong` 对象的代码块内。

  * [ ] 任务3.3.1: 在 `main.py` 的 `import_songs` 命令函数（或其调用的处理函数）中，获取 `ParsedSong` 对象列表 (来自 Story 3.1 的 `parse_song_file`) 和认证的 `spotipy.Spotify` 实例 (来自 Story 2.1 的 `get_spotify_client`)。
  * [ ] 任务3.3.2: 初始化一个空列表 `match_results_list: List[MatchResult] = []`。
  * [ ] 任务3.3.3: 遍历 `ParsedSong` 对象列表。对于每个 `parsed_song`:
      * 调用 `matched_song_object = search_song_on_spotify(sp, parsed_song)`。
      * **IF `matched_song_object` is not None (i.e., search successful):**
          * 创建一个 `MatchResult` 实例:
            ```python
            result = MatchResult(
                original_input_line=parsed_song.original_line,
                parsed_song_title=parsed_song.title,
                parsed_artists=parsed_song.artists,
                status="MATCHED", # Or a more specific status like "FOUND_ON_SPOTIFY" initially
                matched_song_details=matched_song_object,
                error_message=None
            )
            ```
      * **ELSE (`matched_song_object` is None):**
          * 这里需要区分是“未找到”还是“API错误”。`search_song_on_spotify` 的实现（Story 3.2 AC8）是在发生API异常时打印到stderr并返回None。为了让调用者知道是API错误还是仅仅未找到，`search_song_on_spotify` 可能需要返回一个更丰富的对象（比如一个元组 `(Optional[MatchedSong], Optional[str_error_type])`）或者在 `ParsedSong` 或 `MatchedSong` 自身中包含一个错误状态字段（这会使模型更复杂）。
          * **简化方案 (基于当前 Story 3.2 ACs):** 如果 `search_song_on_spotify` 仅返回 `None` 并在内部处理打印/日志API错误，调用方将难以区分。
          * **修改建议 for Story 3.2 / Task for Story 3.3:**
              * 修改 `search_song_on_spotify` 的返回类型为 `Tuple[Optional[MatchedSong], Optional[str]]`，其中第二个元素是错误消息字符串（如果是API错误）或特定错误类型指示符。
              * **或者，更简单：** 假设如果 `search_song_on_spotify` 返回 `None`，我们可以暂时将其归类为 "NOT\_FOUND\_OR\_API\_ERROR"。最终的用户报告可以更笼统。或者，如果 `search_song_on_spotify` 内部打印了API错误，`main` 模块可以假设 `None` 通常意味着 "NOT\_FOUND"，除非有其他全局错误标志被设置。
              * **采纳方案 (为本故事):** 暂时假设 `search_song_on_spotify` 的AC8（打印错误到stderr并返回None）是其主要错误报告机制。调用方将基于返回`None`来判断。为了区分，我们可以先假定 `None` 是 `NOT_FOUND`，除非在 `search_song_on_spotify` 的`except`块中我们能设置一个可被调用者检查的临时状态或错误消息。
              * **更实际的采纳方案:** `search_song_on_spotify` 在API错误时返回 `None`。调用者如果收到 `None`，则默认为 `NOT_FOUND`。API错误信息已由`search_song_on_spotify`打印。这对于 `MatchResult` 来说，`status="NOT_FOUND"` 和 `error_message=None` (因为具体API错误已输出)；或 `status="API_ERROR_SUSPECTED"` 和 `error_message="Search failed, check logs/console for details."`。
              * **最终决定 (简化处理，以符合ACs):** 如果 `search_song_on_spotify` 返回 `None`，我们先统一处理为 `NOT_FOUND`。API错误的具体信息已由该函数打印。
            <!-- end list -->
            ```python
            # In main.py, inside the loop
            # ...
            # else (if matched_song_object is None):
            # This part needs refinement based on how Story 3.2 truly signals API error vs. not found
            # For now, let's assume if None, it's "NOT_FOUND" based on current ACs of this story.
            # Story 3.2's AC8 has `search_song_on_spotify` print the API error and return None.
            # So, the caller can assume `None` means "search was attempted but no definitive MatchedSong".
            # A more robust solution would involve `search_song_on_spotify` returning a more detailed error status.

            # To meet AC1 & AC2 specifically, we need a way to differentiate.
            # Let's assume `search_song_on_spotify` is modified to return:
            # Tuple[Optional[MatchedSong], Optional[str_error_type_or_message]]
            # For now, sticking to the problem statement of THIS story (3.3),
            # which is about CREATING MatchResult based on outcome.
            # The following logic is a placeholder assuming a mechanism to differentiate.
            # IF search_song_on_spotify returned (None, "API_ERROR_TYPE"):
            # result = MatchResult(
            # original_input_line=parsed_song.original_line,
            # parsed_song_title=parsed_song.title,
            # parsed_artists=parsed_song.artists,
            # status="API_ERROR",
            # matched_song_details=None,
            # error_message="Spotify API error during search. Check console output."
            # )
            # ELIF search_song_on_spotify returned (None, None): // Meaning truly not found
            result = MatchResult(
                original_input_line=parsed_song.original_line,
                parsed_song_title=parsed_song.title,
                parsed_artists=parsed_song.artists,
                status="NOT_FOUND", # Default for None return if API error already logged by search_song
                matched_song_details=None,
                error_message="Song not found on Spotify." # Or None if API error handled it
            )
            # This logic needs to be robust based on final decision for Story 3.2's error propagation.
            # For now, simplified:
            # if matched_song_object is None: # Placeholder, assuming search_song handles API error logging
            #     status = "NOT_FOUND" # Or a general "SEARCH_FAILED"
            #     error_msg = "Song not found or API error occurred during search. See console for details."
            #     result = MatchResult(
            #         original_input_line=parsed_song.original_line,
            #         parsed_song_title=parsed_song.title,
            #         parsed_artists=parsed_song.artists,
            #         status=status,
            #         matched_song_details=None,
            #         error_message=error_msg
            #     )
            ```
          * **修正后的简化逻辑，与ACs对齐：** 调用方不知道 `search_song_on_spotify` 返回 `None` 的具体原因（是真没找到还是API错）。它只知道没有 `MatchedSong`。`search_song_on_spotify` 自己负责记录API错误细节。
            ```python
            # In main.py, inside the loop
            # ...
            # else (if matched_song_object is None):
            # As per Story 3.2 AC8, search_song_on_spotify prints API errors and returns None.
            # As per Story 3.3 AC1, if None from search -> status="NOT_FOUND".
            # As per Story 3.3 AC2, if None from search due to API error -> status="API_ERROR".
            # This implies `main.py` needs to know *why* it's None.
            # This story's "Detailed Requirements" says "generate a MatchResult ...包含相关错误信息".
            # This is a slight conflict if search_song_on_spotify hides the error type.
            # RESOLUTION: For this story, we will assume the `main` loop needs to determine the status.
            # To do this, `search_song_on_spotify` should ideally either raise distinct exceptions
            # or return a more complex object/tuple.
            #
            # If we strictly follow Story 3.2 AC8 (prints error, returns None), then main.py cannot easily set
            # a differentiated error_message for MatchResult. It would set status to NOT_FOUND for all None cases.
            #
            # Let's assume for Story 3.3 the goal is to correctly *construct* MatchResult given some (hypothetical)
            # information about why search_song_on_spotify failed or returned None.
            # The actual mechanism for search_song_on_spotify to provide this info might be a task for that story or a refactor.

            # Let's re-frame this:
            # The main loop calls search_song_on_spotify.
            # If it throws an exception (e.g. a wrapped SpotifyException if we modify search_song),
            # then it's an API_ERROR. Otherwise, if it returns None, it's NOT_FOUND.
            # This requires search_song_on_spotify in Story 3.2 to re-throw or pass specific errors.
            #
            # Sticking to Story 3.2 AC8 (prints error, returns None):
            # Then main.py does:
            # try:
            #   matched_song = search_song_on_spotify(sp, parsed_song)
            #   if matched_song:
            #     # AC3
            #   else:
            #     # AC1 - cannot differentiate API error from true not_found by return value alone
            #     # The API error was printed by search_song_on_spotify as per its AC8.
            #     # So, if None is returned, we assume it's primarily a "not found" from main's perspective.
            #     # The MatchResult.error_message can reflect that the details are in console.
            # except Exception as e: # If search_song_on_spotify re-throws a new type of error
            #   # AC2

            # Let's simplify: The task of `main.py` is to create a `MatchResult`.
            # The `status` field is key.
            # For Story 3.3, we will assume `main.py` can determine this status.
            # The actual implementation detail of *how* `search_song_on_spotify` communicates
            # "API error" vs "not found" is an implementation detail that might need
            # adjustment in Story 3.2's tasks or a new refactoring story.
            #
            # For now, let's assume `search_song_on_spotify` is updated to:
            # return "SUCCESS", matched_song
            # return "NOT_FOUND", None
            # return "API_ERROR", error_details_from_exception
            # This is a change to Story 3.2.
            #
            # **If we DON'T change Story 3.2:**
            #   If search_song_on_spotify returns None:
            #     status = "SEARCH_FAILED" (generic)
            #     error_message = "Song not found or API error during search. Check console output from search attempt."
            #     Populate MatchResult with this. This meets the spirit of Story 3.3.
            ```
  * [ ] 任务3.3.4: (Continuing from 3.3.3, using the simplified "SEARCH\_FAILED" approach if Story 3.2 is not changed to provide more detailed error status)
    ````python
            # In main.py or orchestrator, after calling search_song_on_spotify(sp, parsed_song)
            # Let's say matched_song_object = search_song_on_spotify(sp, parsed_song)

            current_status = ""
            current_error_message: Optional[str] = None
            final_matched_song_details: Optional[MatchedSong] = None

            if matched_song_object:
                current_status = "MATCHED" # Will be updated further in Epic 4 after adding to playlist
                final_matched_song_details = matched_song_object
            else:
                # Story 3.2 AC8 says search_song_on_spotify prints API error and returns None.
                # So if we get None, it could be "not found" or "API error happened and was logged".
                # We can't distinguish from here without changing Story 3.2's return.
                # So, we set a status that reflects this ambiguity for now.
                # A better way: search_song_on_spotify raises specific exceptions for main to catch.
                # Let's assume for now it just returns None on any failure/not found.
                current_status = "NOT_FOUND_OR_API_ERROR_DURING_SEARCH"
                current_error_message = "Song not found on Spotify, or an API error occurred during search. Check console output for details from the search attempt."

            result = MatchResult(
                original_input_line=parsed_song.original_line,
                parsed_song_title=parsed_song.title,
                parsed_artists=parsed_song.artists,
                status=current_status,
                matched_song_details=final_matched_song_details,
                error_message=current_error_message
            )
            match_results_list.append(result)
            ```
    ````
  * [ ] 任务3.3.5: 编写单元测试（例如在 `tests/test_main.py` 或测试编排逻辑的地方），mock `search_song_on_spotify` 的不同返回值，并验证是否为每种情况正确创建了 `MatchResult` 对象，其 `status`, `matched_song_details`, 和 `error_message` 字段符合ACs。
  * [ ] 任务3.3.6: 运行 linting 和 formatting 工具。
  * [ ] 任务3.3.7: 将修改后的文件添加到Git并提交，提交信息如 "Handle search outcomes by creating MatchResult objects"。

**Self-Correction/Refinement for Task 3.3.4 to better align with ACs of *this* story (3.3):**
The ACs for Story 3.3 imply that the calling code *can* differentiate. This means `search_song_on_spotify` (from Story 3.2) must provide a way to do so.
**Revised approach for Story 3.2 (to be implemented there, but assumed here for Story 3.3):**
`search_song_on_spotify` should:

1.  Return `MatchedSong` object if found.
2.  Return `None` if not found (no API error).
3.  Raise a specific custom exception (e.g., `SpotifySearchAPIError(SpotifyException)`) if an API error occurs during search, containing the original exception.

**Revised Task 3.3.4 based on this assumption:**

  * [ ] (Revised) 任务3.3.4: 在 `main.py` 的歌曲处理循环中:
    ```python
            # In main.py or orchestrator
            # from spotify_playlist_importer.spotify.client import search_song_on_spotify, SpotifySearchAPIError (assume this new exc)
            # from spotify_playlist_importer.core.models import MatchResult, MatchedSong, ParsedSong
            # ...

            current_status = ""
            current_error_message: Optional[str] = None
            final_matched_song_details: Optional[MatchedSong] = None

            try:
                final_matched_song_details = search_song_on_spotify(sp, parsed_song) # sp is authenticated spotipy instance
                if final_matched_song_details:
                    current_status = "MATCHED" # AC3
                else:
                    current_status = "NOT_FOUND" # AC1
                    current_error_message = "Song not found on Spotify." # AC1
            except SpotifySearchAPIError as e: # Assuming search_song_on_spotify raises this for API errors
                current_status = "API_ERROR" # AC2
                current_error_message = f"Spotify API error during search: {str(e)}" # AC2
            # except Exception as e: # Catch other unexpected errors from search_song_on_spotify
            #     current_status = "UNKNOWN_ERROR_DURING_SEARCH"
            #     current_error_message = f"An unexpected error occurred: {str(e)}"

            result = MatchResult(
                original_input_line=parsed_song.original_line,
                parsed_song_title=parsed_song.title,
                parsed_artists=parsed_song.artists,
                status=current_status,
                matched_song_details=final_matched_song_details, # will be None if not found or API error
                error_message=current_error_message
            )
            match_results_list.append(result)
    ```

This revised task for 3.3.4 implies a modification to how errors/not-found are signaled by `search_song_on_spotify` from Story 3.2. The developer agent implementing Story 3.2 should ensure its `search_song_on_spotify` raises `SpotifySearchAPIError` on API exceptions rather than just printing and returning None, to enable this differentiation. If Story 3.2 is already complete and only prints/returns None, then the simpler "SEARCH\_FAILED" status from the original Task 3.3.4 is the fallback. The "Revised Task 3.3.4" is preferred for better adherence to Story 3.3's ACs.

## Testing Requirements

**Guidance:** 对照ACs通过以下方式验证实施。 (测试将主要在 `test_main.py` 或等效的编排逻辑测试文件中)

  * **Unit Tests:**

      * Mock `parse_song_file` to return a list of `ParsedSong` objects.
      * Mock `get_spotify_client` to return a mock `sp` instance.
      * **Test Case (Song Found):**
          * Mock `search_song_on_spotify(mock_sp, specific_parsed_song)` to return a `MatchedSong` instance.
          * Run the main processing loop (or the part that calls search and creates `MatchResult`).
          * Verify that a `MatchResult` is created with `status="MATCHED"`, `matched_song_details` populated, and `error_message=None`.
      * **Test Case (Song Not Found):**
          * Mock `search_song_on_spotify(mock_sp, specific_parsed_song)` to return `None` (and not raise an API error).
          * Run the loop.
          * Verify that a `MatchResult` is created with `status="NOT_FOUND"`, `matched_song_details=None`, and an appropriate `error_message` (or None).
      * **Test Case (API Error during Search):**
          * Mock `search_song_on_spotify(mock_sp, specific_parsed_song)` to raise `SpotifySearchAPIError("details")` (assuming this custom exception is implemented in Story 3.2).
          * Run the loop.
          * Verify that a `MatchResult` is created with `status="API_ERROR"`, `matched_song_details=None`, and `error_message` containing "Spotify API error during search: details".

  * **Integration Tests:** N/A for this specific logic, as dependencies are mocked.

  * **Manual/CLI Verification:**

      * This logic is internal to the main processing flow. Its correctness will be verified when the full `import` command is run (Epic 4) and the output report is generated, by:
          * Providing a song list with songs očekivano da se nađu.
          * Providing a song list with songs očekivano da se ne nađu.
          * (If possible to reliably trigger) Simulating an API error during search and checking the report.

  * *(Hint: 参见 `docs/testing-strategy.md` 了解整体方法)*

-----
