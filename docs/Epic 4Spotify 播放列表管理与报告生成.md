

# Story 4.1: 实现创建 Spotify 播放列表功能

**Status:** Draft

## Goal & Context

**User Story:** 作为应用程序，我需要能够使用用户的 Spotify ID 和用户指定的播放列表名称（或默认名称）、描述和公开状态，在用户的账户中创建一个新的播放列表。

**Context:** 此故事是 Epic 4 的核心功能之一，直接对应 PRD FR5 (播放列表创建与导入) 中的创建播放列表部分。它依赖于 Epic 2 (Spotify 用户认证) 提供的已认证 `spotipy` 客户端。成功创建播放列表是后续添加歌曲的前提。

## Detailed Requirements

根据 `docs/epic4.md`:

  * 在 `spotify/client.py` 中实现创建新播放列表的逻辑。
  * 需要获取用户ID (`sp.current_user()['id']`)。
  * 调用 `sp.user_playlist_create()` 并能传递播放列表名称、公开性和描述。
  * 成功创建后，返回新播放列表的 ID 和 URL。
  * 处理API调用可能发生的错误。

## Acceptance Criteria (ACs)

  * AC1: `spotify_playlist_importer/spotify_playlist_importer/spotify/client.py` 中定义了一个函数，例如 `create_spotify_playlist(sp: spotipy.Spotify, playlist_name: str, is_public: bool, playlist_description: Optional[str]) -> Optional[dict]`。
      * 其中返回的 `dict` 应包含 `id` (播放列表ID) 和 `url` (播放列表的Spotify URL)。
  * AC2: 函数首先调用 `sp.current_user()` 来获取当前用户的 Spotify ID。如果此调用失败 (例如，由于权限不足或API错误)，函数应捕获 `spotipy.SpotifyException`，打印错误到 `stderr` (或日志)，并返回 `None`。
  * AC3: 函数随后调用 `sp.user_playlist_create(user=user_id, name=playlist_name, public=is_public, description=playlist_description)`。
  * AC4: 如果 `sp.user_playlist_create()` 调用成功，函数能从返回的播放列表对象中提取 `id` 和 `external_urls['spotify']`，并将它们作为字典返回 (例如, `{'id': playlist_id, 'url': playlist_url}`)。
  * AC5: 如果 `sp.user_playlist_create()` 调用失败 (例如，由于无效的播放列表名称、API错误或速率限制)，函数应捕获 `spotipy.SpotifyException`，打印错误到 `stderr` (或日志)，并返回 `None`。
  * AC6: `spotify/client.py` 模块的代码符合项目的编码标准。

## Technical Implementation Context

**Guidance:** 使用以下细节进行实施。如果需要更广泛的上下文，请参阅链接的 `docs/` 文件。

  * **Relevant Files:**

      * Files to Create/Modify:
          * `spotify_playlist_importer/spotify_playlist_importer/spotify/client.py` (Modify/Extend)
          * `tests/spotify/test_client.py` (Modify/Extend)
      * Files for context:
          * `spotify_playlist_importer/spotify/auth.py`
      * *(Hint: 参见 `docs/project-structure.md` 查看整体布局)*

  * **Key Technologies:**

      * Python
      * `spotipy` (特别是 `sp.current_user()` 和 `sp.user_playlist_create()`)
      * `typing.Optional`, `typing.Dict`
      * *(Hint: 参见 `docs/tech-stack.md` 查看完整列表)*

  * **API Interactions / SDK Usage:**

      * **`sp.current_user()`**:
          * 需要 `user-read-private` scope (已在Epic 2中请求)。
          * 返回包含用户信息的字典，从中提取 `['id']`。
      * **`sp.user_playlist_create(user, name, public, collaborative, description)`**:
          * `user`: 从 `sp.current_user()['id']` 获取。
          * `name`: 从函数参数传入。
          * `public`: 从函数参数传入。
          * `collaborative`: 设为 `False` (非协作播放列表)。
          * `description`: 从函数参数传入 (可以是 `None`)。
          * 需要 `playlist-modify-public` 或 `playlist-modify-private` scope (已在Epic 2中请求)。
          * 成功时返回代表新播放列表的对象。
      * *(Hint: 参见 `docs/api-reference.md` (获取当前用户信息, 创建播放列表部分) 和 `spotipy` 文档)*

  * **UI/UX Notes:** 此函数主要供内部调用，错误通过返回值和日志/打印到`stderr`来传递。

  * **Data Structures:**

      * 输出: `Optional[Dict[str, str]]` (包含 `id` 和 `url`)
      * *(Hint: 参见 `docs/data-models.md` 了解关键项目数据结构)*

  * **Environment Variables:**

      * N/A (间接依赖 `core.config` 初始化 `sp`)
      * *(Hint: 参见 `docs/environment-vars.md` 查看所有变量)*

  * **Coding Standards Notes:**

      * 清晰的错误处理和返回路径。
      * 类型提示。
      * *(Hint: 参见 `docs/coding-standards.md` 查看完整标准)*

## Tasks / Subtasks

  * [ ] 任务4.1.1: 打开 `spotify_playlist_importer/spotify_playlist_importer/spotify/client.py`。
  * [ ] 任务4.1.2: 导入 `Optional`, `Dict` from `typing` (如果尚未导入)。
  * [ ] 任务4.1.3: 定义或找到 `create_spotify_playlist` 函数的签名：
    ```python
    def create_spotify_playlist(
        sp: spotipy.Spotify, 
        playlist_name: str, 
        is_public: bool, 
        playlist_description: Optional[str]
    ) -> Optional[Dict[str, str]]:
    ```
  * [ ] 任务4.1.4: 在 `try-except spotipy.SpotifyException` 块中实现获取用户ID的逻辑：
    ```python
    try:
        user_profile = sp.current_user()
        if not user_profile or 'id' not in user_profile:
            print("Error: Could not retrieve valid user profile from Spotify.", file=sys.stderr) # Or log
            return None
        user_id = user_profile['id']
    except spotipy.SpotifyException as e:
        print(f"Spotify API error while fetching user profile: {e}", file=sys.stderr) # Or log
        return None
    except Exception as e:
        print(f"Unexpected error while fetching user profile: {e}", file=sys.stderr) # Or log
        return None
    ```
  * [ ] 任务4.1.5: 在获取到 `user_id` 后，在另一个 `try-except spotipy.SpotifyException` 块中实现创建播放列表的逻辑：
    ```python
    try:
        playlist = sp.user_playlist_create(
            user=user_id,
            name=playlist_name,
            public=is_public,
            description=playlist_description if playlist_description else "" # Ensure description is not None
        )
        if playlist and 'id' in playlist and 'external_urls' in playlist and 'spotify' in playlist['external_urls']:
            return {
                'id': playlist['id'],
                'url': playlist['external_urls']['spotify']
            }
        else:
            print(f"Error: Playlist creation did not return expected data. Name: {playlist_name}", file=sys.stderr) # Or log
            return None
            
    except spotipy.SpotifyException as e:
        print(f"Spotify API error while creating playlist '{playlist_name}': {e}", file=sys.stderr) # Or log
        return None
    except Exception as e:
        print(f"Unexpected error while creating playlist '{playlist_name}': {e}", file=sys.stderr) # Or log
        return None
    ```
    *(注意: `playlist_description` 如果是 `None`，`spotipy` 可能会报错或行为不确定，最好传递空字符串 `""` 如果用户未提供描述)*
  * [ ] 任务4.1.6: 更新 `tests/spotify/test_client.py` 并为 `create_spotify_playlist` 编写单元测试（见下方测试需求）。
  * [ ] 任务4.1.7: 运行 linting 和 formatting 工具。
  * [ ] 任务4.1.8: 将修改后的 `spotify/client.py` 和测试文件添加到Git并提交，提交信息如 "Implement create Spotify playlist functionality"。

## Testing Requirements

**Guidance:** 对照ACs通过以下方式验证实施。

  * **Unit Tests:**

      * 在 `tests/spotify/test_client.py` 中。
      * Mock `spotipy.Spotify` 实例及其 `current_user` 和 `user_playlist_create` 方法。
      * **测试用例1 (成功创建播放列表):**
          * Mock `sp.current_user()` 返回包含有效 `id` 的字典。
          * Mock `sp.user_playlist_create()` 返回包含 `id` 和 `external_urls['spotify']` 的字典。
          * 调用 `create_spotify_playlist`。
          * 断言返回的字典包含正确的 `id` 和 `url`。
      * **测试用例2 (获取用户ID失败):**
          * Mock `sp.current_user()` 引发 `spotipy.SpotifyException` 或返回无效数据。
          * 调用 `create_spotify_playlist`。
          * 断言返回值为 `None`。
          * (可选) 验证错误消息已打印到 `stderr`。
      * **测试用例3 (创建播放列表API失败):**
          * Mock `sp.current_user()` 成功返回用户ID。
          * Mock `sp.user_playlist_create()` 引发 `spotipy.SpotifyException`。
          * 调用 `create_spotify_playlist`。
          * 断言返回值为 `None`。
          * (可选) 验证错误消息已打印到 `stderr`。
      * **测试用例4 (创建播放列表返回数据不完整):**
          * Mock `sp.user_playlist_create()` 返回一个不包含 `id` 或 `external_urls` 的字典。
          * 调用 `create_spotify_playlist`。
          * 断言返回值为 `None`。

  * **Integration Tests:** (可选, 标记为慢速)

      * 需要有效认证的 `sp` 实例。
      * 调用 `create_spotify_playlist` 创建一个真实播放列表 (使用唯一的测试名称)。
      * 验证返回的字典不为 `None` 且包含 `id` 和 `url`。
      * **重要:** 测试后需要有清理步骤来删除创建的播放列表 (例如使用 `sp.current_user_unfollow_playlist(playlist_id)`)，或者接受测试账户中会留下测试数据。

  * **Manual/CLI Verification:**

      * 在获得认证的 `sp` 实例后，在Python解释器中：
          * 调用 `create_spotify_playlist(sp, "Test Manual Playlist", False, "A test playlist created manually.")`。
          * 打印返回值。检查是否是包含 `id` 和 `url` 的字典。
          * 登录Spotify查看播放列表是否已创建，名称、公开状态和描述是否正确。
          * 清理：手动删除创建的测试播放列表。

  * *(Hint: 参见 `docs/testing-strategy.md` 了解整体方法)*

-----

File: `ai/stories/epic4.story2.story.md`

# Story 4.2: 实现向 Spotify 播放列表添加歌曲功能

**Status:** Draft

## Goal & Context

**User Story:** 作为应用程序，我需要能够将一批 `MatchedSong` URI 添加到指定的 Spotify 播放列表中。我必须处理 Spotify API 关于单次请求最多添加100首歌曲的限制。

**Context:** 此故事紧随 Story 4.1 (创建播放列表) 之后，是实现 PRD FR5 (播放列表创建与导入) 的关键部分。它需要一个已创建的播放列表ID和一批成功匹配的歌曲的Spotify URI。正确处理批量添加和API限制对于大数据量的歌单导入至关重要。

## Detailed Requirements

根据 `docs/epic4.md`:

  * 在 `spotify/client.py` 中实现将歌曲批量添加到指定播放列表的逻辑。
  * 接收播放列表 ID 和 `MatchedSong` URI 列表。
  * 如果歌曲数量超过100首，能正确地将歌曲列表分块并进行多次 API 调用。
  * 成功添加歌曲后，返回成功状态。
  * 处理API调用可能发生的错误。

## Acceptance Criteria (ACs)

  * AC1: `spotify_playlist_importer/spotify_playlist_importer/spotify/client.py` 中定义了一个函数，例如 `add_tracks_to_spotify_playlist(sp: spotipy.Spotify, playlist_id: str, track_uris: List[str]) -> bool`。
      * 函数返回 `True` 表示所有歌曲（或所有批次）已成功（或尝试）添加到播放列表，返回 `False` 表示在过程中发生了不可恢复的错误。
  * AC2: 如果 `track_uris` 列表为空，函数应直接返回 `True` (或 `False` 并打印警告，取决于期望行为 - 返回`True`表示“无事可做，所以成功”更合理)。
  * AC3: 如果 `track_uris` 列表中的歌曲数量大于100，函数能将列表分割成多个不超过100个URI的子列表（chunks）。
  * AC4: 函数为每个URI子列表（或整个列表，如果少于100个）调用 `sp.playlist_add_items(playlist_id, chunk_of_uris)`。
  * AC5: 如果任何一次 `sp.playlist_add_items()` 调用失败并引发 `spotipy.SpotifyException`，函数应捕获该异常，打印错误到 `stderr` (或日志)，并可以选择：
      * a) 停止处理后续批次并立即返回 `False` (更安全的做法)。
      * b) 记录错误并继续尝试处理剩余批次，最后根据是否有任何批次失败返回 `False` (更具容错性，但可能导致部分添加)。
      * **为明确起见，选择 (a): 任何批次失败则整体失败并返回 `False`。**
  * AC6: 如果所有批次的 `sp.playlist_add_items()` 调用都成功（或没有抛出异常），函数返回 `True`。
  * AC7: `spotify/client.py` 模块的代码符合项目的编码标准。

## Technical Implementation Context

**Guidance:** 使用以下细节进行实施。如果需要更广泛的上下文，请参阅链接的 `docs/` 文件。

  * **Relevant Files:**

      * Files to Create/Modify:
          * `spotify_playlist_importer/spotify_playlist_importer/spotify/client.py` (Modify/Extend)
          * `tests/spotify/test_client.py` (Modify/Extend)
      * *(Hint: 参见 `docs/project-structure.md` 查看整体布局)*

  * **Key Technologies:**

      * Python (list slicing for chunking)
      * `spotipy` (特别是 `sp.playlist_add_items()`)
      * `typing.List`
      * *(Hint: 参见 `docs/tech-stack.md` 查看完整列表)*

  * **API Interactions / SDK Usage:**

      * **`sp.playlist_add_items(playlist_id, items, position=None)`**:
          * `playlist_id`: 从函数参数传入。
          * `items`: 一个包含 Spotify Track URI 的列表，**最多100个元素**。
          * 需要 `playlist-modify-public` 或 `playlist-modify-private` scope。
      * *(Hint: 参见 `docs/api-reference.md` (添加歌曲到播放列表部分) 和 `spotipy` 文档)*

  * **UI/UX Notes:** 错误通过返回值和日志/打印到`stderr`传递。调用方可以根据返回值向用户显示最终状态。

  * **Data Structures:**

      * 输入: `playlist_id: str`, `track_uris: List[str]`
      * *(Hint: 参见 `docs/data-models.md` 了解关键项目数据结构)*

  * **Environment Variables:**

      * N/A
      * *(Hint: 参见 `docs/environment-vars.md` 查看所有变量)*

  * **Coding Standards Notes:**

      * 清晰的列表分块逻辑。
      * *(Hint: 参见 `docs/coding-standards.md` 查看完整标准)*

## Tasks / Subtasks

  * [ ] 任务4.2.1: 打开 `spotify_playlist_importer/spotify_playlist_importer/spotify/client.py`。
  * [ ] 任务4.2.2: 定义或找到 `add_tracks_to_spotify_playlist` 函数的签名：
    ```python
    def add_tracks_to_spotify_playlist(
        sp: spotipy.Spotify, 
        playlist_id: str, 
        track_uris: List[str]
    ) -> bool:
    ```
  * [ ] 任务4.2.3: 处理 `track_uris` 为空的情况 (AC2)。
    ```python
    if not track_uris:
        # print("No track URIs provided to add to the playlist.", file=sys.stderr) # Or log as debug/info
        return True # Nothing to do, considered success
    ```
  * [ ] 任务4.2.4: 实现列表分块逻辑。
    ```python
    chunk_size = 100 # Spotify API limit
    all_successful = True
    for i in range(0, len(track_uris), chunk_size):
        chunk = track_uris[i:i + chunk_size]
        # ... process chunk ...
    return all_successful # This will be modified by the try/except logic
    ```
  * [ ] 任务4.2.5: 在循环中，为每个 `chunk` 调用 `sp.playlist_add_items`，并将其包裹在 `try-except spotipy.SpotifyException` 块中 (AC5)。
    ```python
    # Inside the loop from Task 4.2.4
        try:
            sp.playlist_add_items(playlist_id, chunk)
            # Optional: Add a small delay if processing many chunks to be kind to the API
            # import time
            # time.sleep(0.1) # 100ms delay
        except spotipy.SpotifyException as e:
            print(f"Spotify API error while adding tracks to playlist '{playlist_id}': {e}", file=sys.stderr) # Or log
            all_successful = False # Mark failure
            break # Stop processing further chunks as per AC5.a
        except Exception as e:
            print(f"Unexpected error while adding tracks to playlist '{playlist_id}': {e}", file=sys.stderr) # Or log
            all_successful = False
            break
    # The loop finishes, return all_successful
    ```
  * [ ] 任务4.2.6: 更新 `tests/spotify/test_client.py` 并为 `add_tracks_to_spotify_playlist` 编写单元测试（见下方测试需求）。
  * [ ] 任务4.2.7: 运行 linting 和 formatting 工具。
  * [ ] 任务4.2.8: 将修改后的 `spotify/client.py` 和测试文件添加到Git并提交，提交信息如 "Implement add tracks to Spotify playlist with batching"。

## Testing Requirements

**Guidance:** 对照ACs通过以下方式验证实施。

  * **Unit Tests:**

      * 在 `tests/spotify/test_client.py` 中。
      * Mock `spotipy.Spotify` 实例及其 `playlist_add_items` 方法。
      * **测试用例1 (少于100首歌，成功):**
          * 提供一个包含 (例如) 50个 URI 的 `track_uris` 列表。
          * Mock `sp.playlist_add_items()` 不引发异常。
          * 调用 `add_tracks_to_spotify_playlist`。
          * 断言 `sp.playlist_add_items` 被调用1次，且参数正确。
          * 断言函数返回 `True`。
      * **测试用例2 (多于100首歌，例如150首，全成功):**
          * 提供一个包含150个 URI 的 `track_uris` 列表。
          * Mock `sp.playlist_add_items()` 不引发异常。
          * 调用 `add_tracks_to_spotify_playlist`。
          * 断言 `sp.playlist_add_items` 被调用2次 (第一次用100个URI，第二次用50个URI)。
          * 断言函数返回 `True`。
      * **测试用例3 (多于100首歌，例如200首，全成功):**
          * 提供一个包含200个 URI 的 `track_uris` 列表。
          * 调用 `add_tracks_to_spotify_playlist`。
          * 断言 `sp.playlist_add_items` 被调用2次 (每次100个URI)。
          * 断言函数返回 `True`。
      * **测试用例4 (API调用失败 - 单一批次):**
          * 提供一个包含50个 URI 的 `track_uris` 列表。
          * Mock `sp.playlist_add_items()` 引发 `spotipy.SpotifyException`。
          * 调用 `add_tracks_to_spotify_playlist`。
          * 断言 `sp.playlist_add_items` 被调用1次。
          * 断言函数返回 `False`。
          * (可选) 验证错误消息已打印到 `stderr`。
      * **测试用例5 (API调用失败 - 多批次中的第一批失败):**
          * 提供一个包含150个 URI 的 `track_uris` 列表。
          * Mock `sp.playlist_add_items()` 在第一次调用时（前100个URI）引发 `spotipy.SpotifyException`。
          * 调用 `add_tracks_to_spotify_playlist`。
          * 断言 `sp.playlist_add_items` 仅被调用1次。
          * 断言函数返回 `False`。
      * **测试用例6 (空 URI 列表):**
          * 提供一个空的 `track_uris` 列表。
          * 调用 `add_tracks_to_spotify_playlist`。
          * 断言 `sp.playlist_add_items` 未被调用。
          * 断言函数返回 `True`。

  * **Integration Tests:** (可选, 标记为慢速)

      * 需要有效认证的 `sp` 实例和一个已创建的测试播放列表ID。
      * 准备一个包含少量有效Spotify Track URI的列表。
      * 调用 `add_tracks_to_spotify_playlist` 将这些歌曲添加到真实的测试播放列表。
      * 验证函数返回 `True`。
      * (可选) 使用 `sp.playlist_items(playlist_id)` 验证歌曲是否真的已添加。
      * **重要:** 测试后需要有清理步骤 (例如，从播放列表中移除添加的歌曲，或删除整个播放列表)。

  * **Manual/CLI Verification:**

      * 与集成测试类似，但在Python解释器中手动执行。
      * 创建一个测试播放列表。
      * 获取一些歌曲的URI。
      * 调用 `add_tracks_to_spotify_playlist`。
      * 登录Spotify检查歌曲是否已添加。
      * 测试超过100首歌曲的情况（如果方便收集大量URI）。
      * 清理测试数据。

  * *(Hint: 参见 `docs/testing-strategy.md` 了解整体方法)*

-----

File: `ai/stories/epic4.story3.story.md`

# Story 4.3: 编排完整导入流程并生成用户操作报告

**Status:** Draft

## Goal & Context

**User Story:** 作为应用程序，我需要协调整个导入流程——从读取输入、认证、搜索、创建播放列表到添加歌曲——并在操作结束后，向用户显示总结信息，并生成一份详细的文本报告文件，记录每首歌的处理结果和新播放列表的链接。

**Context:** 这是 Epic 4 的核心编排故事，也是整个应用程序MVP功能的集大成者。它将之前所有Epic和Story中实现的功能模块（输入解析、认证、歌曲搜索、播放列表创建、歌曲添加）串联起来，形成一个完整的用户流程。最终的用户反馈和持久化的报告是此故事的关键产出。此故事主要修改 `main.py` 中的 `import_songs` 命令。

## Detailed Requirements

根据 `docs/epic4.md`:

  * `main.py` (或其调用的核心逻辑模块) 能够按顺序执行完整流程。
  * 收集每首输入歌曲的 `MatchResult` 对象。
  * 在控制台输出操作摘要。
  * 生成一个详细的文本文件报告。
  * 如果没有任何歌曲成功匹配，则不应尝试创建播放列表。

## Acceptance Criteria (ACs)

  * AC1: `spotify_playlist_importer.main.import_songs` 命令函数能正确调用并使用以下模块/函数：
      * `core.input_parser.parse_song_file` (Story 3.1)
      * `spotify.auth.get_spotify_client` (Story 2.1)
      * `spotify.client.search_song_on_spotify` (Story 3.2, 假设其错误传递机制已优化，能让调用者区分 "NOT\_FOUND" 和 "API\_ERROR")
      * `spotify.client.create_spotify_playlist` (Story 4.1)
      * `spotify.client.add_tracks_to_spotify_playlist` (Story 4.2)
  * AC2: 对 `parse_song_file` 返回的每个 `ParsedSong` 对象，调用 `search_song_on_spotify`，并根据其结果（`MatchedSong` 或错误指示）创建一个 `MatchResult` 对象，将其添加到 `match_results_list` (如 Story 3.3 中细化的逻辑)。
  * AC3: 在处理完所有歌曲搜索后，检查 `match_results_list` 中有多少歌曲的状态为 "MATCHED" (或一个表示已成功找到对应Spotify歌曲的内部状态)。
  * AC4: 如果至少有一首歌曲成功匹配到Spotify URI (`MatchedSong`不为None且其`uri`有效)：
      * 调用 `create_spotify_playlist`。播放列表名称、公开状态和描述应来自CLI参数，如果用户未提供，则使用合理的默认值（例如，名称: "导入的歌曲 YYYY-MM-DD HH:MM:SS"，描述: "通过Spotify歌单导入工具导入的歌曲"，公开: False）。
      * 如果播放列表创建成功（返回播放列表详情字典），则从 `match_results_list` 中收集所有成功匹配歌曲的Spotify URI，并调用 `add_tracks_to_spotify_playlist`。
      * 相应的 `MatchResult` 对象中的 `status` 应更新为 "ADDED\_TO\_PLAYLIST" 或 "ADD\_FAILED"。
  * AC5: 如果没有任何歌曲成功匹配到Spotify URI，或者 `parse_song_file` 返回空列表，则不应调用 `create_spotify_playlist` 和 `add_tracks_to_spotify_playlist`。控制台应输出相应提示。
  * AC6: 操作完成后，在控制台打印总结信息，包括：
      * 处理的总歌曲行数。
      * 成功匹配并找到Spotify歌曲的数量。
      * 未找到/搜索失败的歌曲数量。
      * （如果创建了播放列表）成功添加到播放列表的歌曲数量。
      * （如果创建了播放列表）新创建的播放列表的Spotify URL。
  * AC7: 生成一个文本文件报告 (默认文件名 `matching_report_YYYY-MM-DD_HHMMSS.txt`，或用户通过 `--output-report` 指定的文件名)。报告内容应包含：
      * 报告生成时间。
      * 总结信息 (与AC6类似)。
      * （如果创建了播放列表）播放列表名称和URL。
      * 详细列表：每首原始输入歌曲一行，后跟：
          * 解析出的歌名和艺人。
          * 最终处理状态 (e.g., "MATCHED\_AND\_ADDED", "NOT\_FOUND\_ON\_SPOTIFY", "API\_ERROR\_DURING\_SEARCH", "ADD\_TO\_PLAYLIST\_FAILED", "INPUT\_FORMAT\_ERROR")。
          * 如果匹配成功，显示 Spotify 上的歌曲名称、艺术家、ID 和 URI。
          * 如果发生错误，简要说明错误信息（来自 `MatchResult.error_message`）。
  * AC8: 如果在任何关键步骤（如认证、文件解析、播放列表创建）发生不可恢复的错误，程序应能优雅退出，并尽可能提供有用的错误信息。

## Technical Implementation Context

**Guidance:** 使用以下细节进行实施。如果需要更广泛的上下文，请参阅链接的 `docs/` 文件。

  * **Relevant Files:**

      * Files to Create/Modify:
          * `spotify_playlist_importer/spotify_playlist_importer/main.py` (Major modifications to `import_songs` command)
          * `tests/test_main.py` (Major extensions for E2E-like CLI testing with mocks)
      * *(Hint: 参见 `docs/project-structure.md` 查看整体布局)*

  * **Key Technologies:**

      * Python (`datetime` for timestamps, file I/O for report)
      * `click` (CLI framework)
      * All previously implemented modules: `core.config`, `core.models`, `core.input_parser`, `spotify.auth`, `spotify.client`.
      * *(Hint: 参见 `docs/tech-stack.md` 查看完整列表)*

  * **API Interactions / SDK Usage:**

      * 间接通过调用 `spotify.client` 中的函数。
      * *(Hint: 参见 `docs/api-reference.md` 了解外部API和SDK的详细信息)*

  * **UI/UX Notes:** 控制台输出应简洁明了，报告文件应易于阅读和理解。进度指示（例如，每处理N首歌打印一个点）可以考虑，但对于MVP不是必需的。

  * **Data Structures:**

      * `List[ParsedSong]`
      * `List[MatchResult]` (核心数据结构，用于累积结果和生成报告)
      * `MatchedSong`
      * *(Hint: 参见 `docs/data-models.md` 了解关键项目数据结构)*

  * **Environment Variables:**

      * 依赖 `core.config` 来加载。
      * *(Hint: 参见 `docs/environment-vars.md` 查看所有变量)*

  * **Coding Standards Notes:**

      * `import_songs` 函数会变得比较长，考虑将其逻辑分解为几个私有辅助函数（例如 `_process_songs`, `_create_and_populate_playlist`, `_generate_report`）。
      * 清晰的错误处理和流程控制。
      * 报告生成逻辑应与核心处理逻辑分离。
      * *(Hint: 参见 `docs/coding-standards.md` 查看完整标准)*

## Tasks / Subtasks

  * [ ] 任务4.3.1: 打开 `spotify_playlist_importer/spotify_playlist_importer/main.py`。
  * [ ] 任务4.3.2: 在 `import_songs` 函数的开头，获取所有必要的依赖和参数。
      * 调用 `config = spotify_playlist_importer.core.config` (确保配置已加载)。
      * 调用 `sp = get_spotify_client()`。
      * 调用 `parsed_songs = parse_song_file(songs_file_path)`。处理其可能引发的 `FileNotFoundError`。
  * [ ] 任务4.3.3: 如果 `parsed_songs` 为空，打印消息并提前退出或跳过Spotify操作。
  * [ ] 任务4.3.4: 实现歌曲搜索和 `MatchResult` 对象列表的构建逻辑（基于Story 3.3修订后的任务T3.3.4，假设`search_song_on_spotify`能有效区分"NOT\_FOUND"和"API\_ERROR"）。
    ```python
    # ... (inside import_songs)
    match_results_list: List[MatchResult] = []
    successfully_matched_spotify_songs: List[MatchedSong] = []

    if not parsed_songs:
        click.echo("No songs found in the input file.")
        # Potentially generate an empty report or exit
        return # Or proceed to generate empty report

    click.echo(f"Found {len(parsed_songs)} song entries to process...")

    for parsed_song in parsed_songs:
        # (Logic from revised Task 3.3.4 to create MatchResult based on search_song_on_spotify outcome)
        # This involves calling search_song_on_spotify and populating status, error_message, etc.
        # If a MatchedSong is found, add it to successfully_matched_spotify_songs list.
        # Add the created MatchResult object to match_results_list.
    ```
  * [ ] 任务4.3.5: 根据 `successfully_matched_spotify_songs` 列表决定是否创建和填充播放列表。
    ```python
    playlist_url = None
    playlist_name_actual = None # Store the actual name used for the playlist

    if successfully_matched_spotify_songs:
        # Determine playlist name, description, public status from CLI options or defaults
        playlist_name_actual = playlist_name if playlist_name else f"导入的歌曲 {datetime.now().strftime('%Y-%m-%d %H%M%S')}"
        desc_actual = playlist_description if playlist_description else "通过Spotify歌单导入工具导入的歌曲"
        
        click.echo(f"\nAttempting to create playlist: '{playlist_name_actual}'...")
        playlist_details = create_spotify_playlist(sp, playlist_name_actual, is_public, desc_actual)

        if playlist_details:
            playlist_id = playlist_details['id']
            playlist_url = playlist_details['url']
            click.echo(f"Playlist '{playlist_name_actual}' created successfully: {playlist_url}")

            track_uris_to_add = [ms.uri for ms in successfully_matched_spotify_songs if ms.uri]
            if track_uris_to_add:
                click.echo(f"Adding {len(track_uris_to_add)} tracks to the playlist...")
                add_success = add_tracks_to_spotify_playlist(sp, playlist_id, track_uris_to_add)
                if add_success:
                    click.echo("Tracks added successfully (or all batches attempted).")
                    # Update MatchResult status for added songs
                    for mr in match_results_list:
                        if mr.status == "MATCHED" and mr.matched_song_details and mr.matched_song_details.uri in track_uris_to_add:
                            mr.status = "ADDED_TO_PLAYLIST"
                else:
                    click.echo("Failed to add some or all tracks to the playlist. Check console for API errors.", color="red")
                    # Potentially update MatchResult status to "ADD_FAILED" for relevant songs
            else:
                click.echo("No valid track URIs to add to the playlist.")
        else:
            click.echo(f"Failed to create playlist '{playlist_name_actual}'. Check console for API errors.", color="red")
            # Update MatchResult status for all MATCHED songs to something like "PLAYLIST_CREATION_FAILED"
    else:
        click.echo("\nNo songs were successfully matched on Spotify. Skipping playlist creation.")
    ```
  * [ ] 任务4.3.6: 实现控制台总结输出逻辑 (AC6)。
  * [ ] 任务4.3.7: 实现文本文件报告生成逻辑 (AC7)。文件名应使用 `datetime.now().strftime("matching_report_%Y-%m-%d_%H%M%S.txt")` 或用户提供的名称。
    ```python
    # Example snippet for report generation
    report_file_name = output_report_path if output_report_path else f"matching_report_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.txt"
    with open(report_file_name, "w", encoding="utf-8") as f_report:
        f_report.write(f"Spotify Playlist Importer - Report\n")
        f_report.write(f"Generated at: {datetime.now().isoformat()}\n")
        # ...write summary stats...
        if playlist_url and playlist_name_actual:
            f_report.write(f"Playlist Created: {playlist_name_actual}\n")
            f_report.write(f"Playlist URL: {playlist_url}\n")
        f_report.write("\n--- Detailed Results ---\n")
        for mr in match_results_list:
            f_report.write(f"\nInput: {mr.original_input_line}\n")
            f_report.write(f"  Parsed: '{mr.parsed_song_title}' - {mr.parsed_artists}\n")
            f_report.write(f"  Status: {mr.status}\n")
            if mr.matched_song_details and mr.status not in ["NOT_FOUND", "API_ERROR"]: # Or better status check
                f_report.write(f"  Spotify Match: '{mr.matched_song_details.name}' - {mr.matched_song_details.artists} (ID: {mr.matched_song_details.spotify_id}, URI: {mr.matched_song_details.uri})\n")
            if mr.error_message:
                f_report.write(f"  Error/Details: {mr.error_message}\n")
    click.echo(f"\nDetailed report saved to: {report_file_name}")
    ```
  * [ ] 任务4.3.8: 确保对 `click` 选项（`playlist_name`, `playlist_description`, `output_report_path`）的默认值处理逻辑正确。
  * [ ] 任务4.3.9: 编写或扩展 `tests/test_main.py` 来测试 `import_songs` 命令的整体流程（使用mocks）。
  * [ ] 任务4.3.10: 运行 linting 和 formatting 工具。
  * [ ] 任务4.3.11: 将修改后的 `main.py` 和相关测试文件添加到Git并提交，提交信息如 "Implement main import orchestration and reporting"。

## Testing Requirements

**Guidance:** 对照ACs通过以下方式验证实施。

  * **Unit Tests (for `main.py` or orchestrator logic):**

      * 在 `tests/test_main.py` 中。
      * 使用 `click.testing.CliRunner` 来调用 `import` 命令。
      * Mock所有外部依赖：
          * `core.input_parser.parse_song_file`
          * `spotify.auth.get_spotify_client`
          * `spotify.client.search_song_on_spotify` (mock其不同返回值/异常)
          * `spotify.client.create_spotify_playlist`
          * `spotify.client.add_tracks_to_spotify_playlist`
          * `datetime.now` (to control report filenames and timestamps)
          * `open` (to check report content, or use `Path.read_text()`)
      * **测试用例1 (完整成功流程):**
          * `parse_song_file` 返回几首 `ParsedSong`。
          * `search_song_on_spotify` 为它们都返回 `MatchedSong`。
          * `create_spotify_playlist` 返回播放列表详情。
          * `add_tracks_to_spotify_playlist` 返回 `True`。
          * 验证控制台输出包含成功摘要和播放列表URL。
          * 验证报告文件被创建，内容包含正确的总结和详细条目，状态为 "ADDED\_TO\_PLAYLIST"。
      * **测试用例2 (部分歌曲未找到，部分成功):**
          * `search_song_on_spotify` 对某些歌曲返回 `None` (NOT\_FOUND)，对另一些返回 `MatchedSong`。
          * 验证播放列表仍被创建并填充了找到的歌曲。
          * 验证报告和控制台输出正确反映了混合状态。
      * **测试用例3 (所有歌曲均未找到):**
          * `search_song_on_spotify` 对所有歌曲返回 `None` (NOT\_FOUND)。
          * 验证 `create_spotify_playlist` 和 `add_tracks_to_spotify_playlist` **未被调用**。
          * 验证报告和控制台输出指示没有歌曲被匹配，没有播放列表被创建。
      * **测试用例4 (播放列表创建失败):**
          * `search_song_on_spotify` 返回一些 `MatchedSong`。
          * `create_spotify_playlist` 返回 `None`。
          * 验证 `add_tracks_to_spotify_playlist` 未被调用。
          * 验证报告和控制台输出反映了播放列表创建失败。
      * **测试用例5 (添加到播放列表失败):**
          * `create_spotify_playlist` 成功。
          * `add_tracks_to_spotify_playlist` 返回 `False`。
          * 验证报告和控制台输出反映了添加失败。
      * **测试用例6 (输入文件解析失败或为空):**
          * `parse_song_file` 引发 `FileNotFoundError` 或返回空列表。
          * 验证程序优雅处理，不进行Spotify操作，并输出适当信息。
      * **测试用例7 (使用自定义报告文件名):**
          * 通过CLI选项 `--output-report custom_report.txt`。
          * 验证报告是否以 `custom_report.txt` 为名创建。

  * **Integration Tests:** (可作为手动E2E测试的一部分)

      * 运行实际的CLI命令，使用真实的（但可能是测试用的）`.env` 凭据。
      * 使用包含各种情况的小型歌曲列表文件。
      * 检查控制台输出、生成的报告文件以及Spotify账户中的实际播放列表。
      * **需要手动清理Spotify账户中的测试数据。**

  * **Manual/CLI Verification:**

      * 准备一个包含5-10首歌的 `test_songs.txt`，确保部分能匹配，部分可能匹配不到，部分包含特殊字符。
      * 运行 `poetry run importer test_songs.txt --playlist-name "My CLI Test Playlist" --public --description "Test via CLI"`。
      * 检查控制台输出的摘要。
      * 检查生成的报告文件内容是否准确、完整。
      * 登录Spotify，验证播放列表是否按预期创建，歌曲是否正确添加，名称、公开性、描述是否正确。
      * 测试不带可选参数的运行。
      * 测试 `--output-report` 选项。
      * 测试一个空的输入文件。
      * 测试一个包含格式完全错误的歌曲列表文件。

  * *(Hint: 参见 `docs/testing-strategy.md` 了解整体方法)*

-----

File: `ai/stories/epic4.story4.story.md`

# Story 4.4: 在主CLI中集成播放列表参数与流程控制

**Status:** Draft

## Goal & Context

**User Story:** 作为开发者，我需要在 `main.py` 中集成处理用户通过命令行指定的播放列表名称、描述和公开/私有状态的参数，并将这些参数传递给播放列表创建逻辑。

**Context:** 此故事是对 Story 1.3 (实现基本CLI入口) 和 Story 4.3 (编排完整流程) 的补充和细化。Story 1.3 定义了CLI参数的骨架，Story 4.3 使用了这些参数的占位符或默认值。本故事确保这些来自CLI的参数被正确地捕获、传递，并用于实际的播放列表创建调用 (Story 4.1)。它还确保了如果用户没有提供这些可选参数，应用程序会使用合理的默认值。

## Detailed Requirements

根据 `docs/epic4.md`:

  * `main.py` 中集成处理用户通过命令行指定的播放列表名称、描述和公开/私有状态的参数。
  * 将这些参数传递给播放列表创建逻辑。
  * 如果用户未提供，则使用合理的默认值。

## Acceptance Criteria (ACs)

  * AC1: `spotify_playlist_importer.main.import_songs` 函数能正确接收通过 `click` 选项传入的 `playlist_name: Optional[str]`, `is_public: bool`, 和 `playlist_description: Optional[str]`。
  * AC2: 当调用 `spotify.client.create_spotify_playlist` 时：
      * 如果用户通过 `--playlist-name` 提供了播放列表名称，则使用该名称。
      * 如果用户未提供 `--playlist-name`，则使用一个包含当前日期和时间的默认名称 (例如, "导入的歌曲 YYYY-MM-DD HH:MM:SS")。
  * AC3: 当调用 `spotify.client.create_spotify_playlist` 时：
      * `is_public` 参数直接使用从 `--public` 标志（默认为 `False`）获得的值。
  * AC4: 当调用 `spotify.client.create_spotify_playlist` 时：
      * 如果用户通过 `--description` 提供了描述，则使用该描述。
      * 如果用户未提供 `--description`，则使用一个合理的默认描述 (例如, "通过Spotify歌单导入工具导入的歌曲")。
  * AC5: 如果用户通过 `--output-report` 提供了报告文件名，则使用该文件名。如果未提供，则使用包含当前日期和时间的默认文件名 (例如, `matching_report_YYYY-MM-DD_HHMMSS.txt`)。
  * AC6: `main.py` 中处理这些参数和默认值的逻辑清晰、易于理解，并与 `README.md` 中的命令行选项描述一致。

## Technical Implementation Context

**Guidance:** 此故事主要修改 `main.py` 中 `import_songs` 函数内部的逻辑，以正确处理从 `click` 获得的参数值并应用默认值。

  * **Relevant Files:**

      * Files to Create/Modify:
          * `spotify_playlist_importer/spotify_playlist_importer/main.py` (Modify)
          * `tests/test_main.py` (Modify/Extend to test default value logic)
      * *(Hint: 参见 `docs/project-structure.md` 查看整体布局)*

  * **Key Technologies:**

      * Python (`datetime.datetime.now()` for default names/timestamps)
      * `click` (获取选项值)
      * *(Hint: 参见 `docs/tech-stack.md` 查看完整列表)*

  * **API Interactions / SDK Usage:**

      * N/A (此故事不直接调用外部API，而是准备参数给其他函数)
      * *(Hint: 参见 `docs/api-reference.md` 了解外部API和SDK的详细信息)*

  * **UI/UX Notes:** 默认值的选择应合理且对用户友好。帮助文本 (已在Story 1.3中定义) 应提及这些默认行为（如果 `click` 的 `show_default=True` 不够清晰）。

  * **Data Structures:**

      * N/A
      * *(Hint: 参见 `docs/data-models.md` 了解关键项目数据结构)*

  * **Environment Variables:**

      * N/A
      * *(Hint: 参见 `docs/environment-vars.md` 查看所有变量)*

  * **Coding Standards Notes:**

      * 默认值逻辑应在调用 `create_spotify_playlist` 或文件写入之前应用。
      * *(Hint: 参见 `docs/coding-standards.md` 查看完整标准)*

## Tasks / Subtasks

  * [ ] 任务4.4.1: 打开 `spotify_playlist_importer/spotify_playlist_importer/main.py`。
  * [ ] 任务4.4.2: 导入 `datetime` 模块: `from datetime import datetime`。
  * [ ] 任务4.4.3: 在 `import_songs` 函数内部，在调用 `create_spotify_playlist` 之前，确定实际要使用的播放列表名称、描述和报告文件名。
    ```python
    # Inside import_songs function, before calling create_spotify_playlist

    # playlist_name, is_public, playlist_description, output_report_path are already function parameters from Click

    actual_playlist_name: str
    if playlist_name: # User provided a name
        actual_playlist_name = playlist_name
    else:
        actual_playlist_name = f"导入的歌曲 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    actual_playlist_description: str
    if playlist_description: # User provided a description
        actual_playlist_description = playlist_description
    else:
        actual_playlist_description = "通过Spotify歌单导入工具导入的歌曲"
        
    # is_public is already handled by click's default=False for the flag

    actual_report_file_name: str
    if output_report_path: # User provided a report path
        actual_report_file_name = output_report_path
    else:
        actual_report_file_name = f"matching_report_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.txt"

    # ...
    # When calling create_spotify_playlist:
    # playlist_details = create_spotify_playlist(sp, actual_playlist_name, is_public, actual_playlist_description)
    # ...
    # When writing report:
    # with open(actual_report_file_name, "w", encoding="utf-8") as f_report:
    # ...
    ```
  * [ ] 任务4.4.4: 确保 `create_spotify_playlist` 调用时传递的是 `actual_playlist_name`, `is_public`, `actual_playlist_description`。
  * [ ] 任务4.4.5: 确保报告文件写入时使用的是 `actual_report_file_name`。
  * [ ] 任务4.4.6: 更新 `tests/test_main.py` 中的单元测试：
      * 添加测试用例，当不传递 `--playlist-name`, `--description`, `--output-report` 时，验证传递给 mock 的 `create_spotify_playlist` 的参数以及用于 `open` 的文件名是否使用了正确的、包含时间戳的默认值。
      * 添加测试用例，当传递这些选项时，验证传递给 mock 的参数是否为用户提供的值。
      * 使用 `freezegun` 库 (需要添加到dev依赖: `poetry add --group dev freezegun`) 来 mock `datetime.now()`，以便可以预测和断言包含时间戳的默认文件名和播放列表名。
  * [ ] 任务4.4.7: 运行 linting 和 formatting 工具。
  * [ ] 任务4.4.8: 将修改后的 `main.py` 和相关测试文件添加到Git并提交，提交信息如 "Integrate CLI parameters for playlist properties and apply defaults"。

## Testing Requirements

**Guidance:** 对照ACs通过以下方式验证实施。

  * **Unit Tests (for `main.py`):**

      * 在 `tests/test_main.py` 中，使用 `CliRunner` 和全面的 mocks。
      * **测试用例 (无可选参数):**
          * 调用 `importer import dummy_songs.txt` (不带 `--playlist-name`, `--description`, `--output-report`)。
          * Mock `datetime.now()` 返回一个固定时间点 (使用 `freezegun`)。
          * 验证传递给 mock 的 `create_spotify_playlist` 的 `name` 和 `description` 参数是基于固定时间点的默认值。
          * 验证传递给 mock 的 `open` (用于报告) 的文件名是基于固定时间点的默认值。
          * 验证传递给 `create_spotify_playlist` 的 `is_public` 参数为 `False`。
      * **测试用例 (带所有可选参数):**
          * 调用 `importer import dummy_songs.txt --playlist-name "My Custom Name" --public --description "My Custom Desc" --output-report "custom.txt"`。
          * 验证传递给 mock 的 `create_spotify_playlist` 的参数是 "My Custom Name", `True`, "My Custom Desc"。
          * 验证传递给 mock 的 `open` (用于报告) 的文件名是 "custom.txt"。
      * **测试用例 (部分可选参数):**
          * 例如，只提供 `--playlist-name`，验证描述和报告文件名使用默认值。

  * **Integration Tests:** (可作为手动E2E测试的一部分)

      * 运行CLI命令，不指定可选参数，检查Spotify中创建的播放列表名称和描述，以及本地生成的报告文件名是否符合默认格式。
      * 运行CLI命令，指定所有可选参数，检查Spotify和本地文件是否反映了这些指定值。

  * **Manual/CLI Verification:**

      * 1.  运行 `poetry run importer test_songs.txt` (不带任何可选的播放列表/报告参数)。
        <!-- end list -->
          * 检查Spotify中创建的播放列表名称是否包含日期时间。
          * 检查播放列表描述是否为默认值。
          * 检查播放列表是否为私有。
          * 检查本地生成的报告文件名是否包含日期时间。
      * 2.  运行 `poetry run importer test_songs.txt --playlist-name "Awesome Mix Vol. 1" --public --description "Legendary Hits" --output-report "my_mix_report.txt"`。
        <!-- end list -->
          * 检查Spotify中的播放列表是否使用了 "Awesome Mix Vol. 1"，公开，描述为 "Legendary Hits"。
          * 检查本地报告文件名是否为 `my_mix_report.txt`。

  * *(Hint: 参见 `docs/testing-strategy.md` 了解整体方法)*

-----
