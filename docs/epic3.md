# 史诗 3: 歌曲处理与 Spotify 搜索 (Epic 3: Song Processing & Spotify Search)

**负责人 (Owner):** Technical Lead / Developer Agent
**状态 (Status):** 已规划 (Planned)
**关联PRD功能 (Related PRD Features):** PRD FR1, FR2 (Spotify部分), FR3
**预计故事点 (Estimated Story Points):** 8 (示例值，需团队评估)
**最后更新 (Last Updated):** 2025-05-17

## 1. 史诗目标 (Epic Goal)

实现对用户提供的歌曲列表文件的健壮解析，并将每首歌曲的信息（标题和艺术家）用于通过 Spotify API 搜索匹配的曲目。为每首输入的歌曲确定一个最佳匹配（默认选择第一个结果）或标记为未找到。

## 2. 背景与原理 (Background and Rationale)

核心功能的第一步是理解用户的输入。这需要一个能够处理特定格式文本文件的解析器。一旦歌曲信息被结构化，就需要与 Spotify 的庞大曲库进行匹配。有效的 API 查询和对搜索结果的正确解读是确保高匹配质量的关键。

## 3. 主要用户故事 / 功能需求 (Key User Stories / Features)

| 故事ID (Story ID) | 标题 (Title)                      | 用户故事/需求描述 (User Story / Description)                                                                                                  | 优先级 (Priority) | 备注 (Notes)                                                               |
| :---------------- | :-------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------- | :-------------- | :------------------------------------------------------------------------- |
| **Story 3.1** | 实现输入歌曲列表文件解析器          | 作为应用程序，我需要能够读取用户指定的文本文件，并按照 "歌曲名称 - 艺人1 / 艺人2" 的格式解析每一行，将其转换为内部的 `ParsedSong` 数据结构。                 | 高 (High)       | 参考 `prd.md` (3.1.1) 和 `docs/data-models.md` (`ParsedSong`)            |
| **Story 3.2** | 实现 Spotify 歌曲搜索与匹配逻辑   | 作为应用程序，我需要针对每个 `ParsedSong` 对象，使用 Spotify API 搜索相应的歌曲。我将默认选择搜索结果中的第一个曲目作为匹配项，并记录其详细信息为 `MatchedSong` 对象。 | 高 (High)       | 参考 `prd.md` (3.2.2) 和 `docs/api-reference.md` (搜索部分)                |
| **Story 3.3** | 处理歌曲未找到或搜索API错误的情况 | 作为应用程序，当在 Spotify 上找不到某首歌曲，或在搜索过程中发生 API 错误时，我需要能够记录此状态，并为该歌曲生成一个包含相关错误信息的 `MatchResult`。         | 中 (Medium)     | 确保流程的完整性和用户反馈的准确性。                                           |

## 4. 验收标准 (Acceptance Criteria for the Epic)

* `spotify_playlist_importer/core/input_parser.py` 模块能够正确解析符合预定格式（“歌曲名称 - 艺人1 / 艺人2”）的歌曲文件，并针对每一行返回一个 `ParsedSong` 对象列表。
* 解析器能够处理艺人名称中包含 " / " 分隔符的情况，以识别多个合作艺人。
* 对于格式不符合预期的行，解析器应能跳过并记录（或标记）错误，而不是使整个程序崩溃。
* `spotify_playlist_importer/spotify/client.py` 中包含一个函数，该函数接收 `ParsedSong` 对象和已认证的 `spotipy.Spotify` 客户端实例。
* 该函数能正确构造 Spotify API 搜索查询字符串（例如，`f"track:{歌曲标题} artist:{主要艺人名}"`），并调用 `sp.search(q, type='track', limit=1)`。
* 如果 Spotify API 返回匹配的歌曲，函数能从搜索结果中提取必要的歌曲信息（ID, 名称, 艺人列表, URI, 专辑名, 时长等），并填充到一个 `MatchedSong` 对象中。
* 如果 Spotify API 未返回匹配的歌曲（例如，`items` 列表为空），函数能识别此情况。
* 如果 Spotify API 调用在搜索过程中失败（例如，网络错误、无效请求），函数能捕获 `spotipy.SpotifyException` 并处理。
* 对于每首处理的歌曲（无论成功、失败或未找到），都能生成一个包含状态和相关信息的 `MatchResult` 对象。

## 5. 技术说明与依赖 (Technical Notes & Dependencies)

* **依赖的其他史诗 (Depends on):** Epic 1 (特别是 Story 1.4, Story 1.5), Epic 2 (Story 2.1)
* **对其他史诗的影响 (Impacts):** Epic 4 依赖此史诗产出的 `MatchedSong` 和 `MatchResult` 对象列表。
* **关键技术参考:**
    * `prd.md` (特别是 3.1.1 输入文本解析模块, 3.2.2 Spotify 歌曲搜索和匹配)
    * `docs/data-models.md` (`ParsedSong`, `MatchedSong`, `MatchResult`)
    * `docs/api-reference.md` (Search for Item 部分)
    * `docs/coding-standards.md` (错误处理部分)
    * `spotipy` 库文档。

## 6. 初步任务分解 (Initial Task Breakdown for Stories - Example for Story 3.1)

* **Story 3.1: 实现输入歌曲列表文件解析器**
    * [ ] 任务3.1.1: 在 `core/input_parser.py` 中定义 `parse_song_file(file_path: str) -> List[ParsedSong]` 函数。
    * [ ] 任务3.1.2: 实现文件读取逻辑，使用 `with open(...)` 处理文件。
    * [ ] 任务3.1.3: 逐行解析文件内容。
    * [ ] 任务3.1.4: 对于每一行，使用 " - " 作为分隔符拆分歌曲标题和艺术家字符串。进行适当的strip()操作。
    * [ ] 任务3.1.5: 解析艺术家字符串，使用 " / " 作为分隔符处理多个艺术家。
    * [ ] 任务3.1.6: 将解析出的信息实例化为 `ParsedSong` 对象。
    * [ ] 任务3.1.7: 实现对无效行格式的错误处理（例如，记录警告并跳过该行）。
    * [ ] 任务3.1.8: 编写单元测试，覆盖各种有效的输入格式、无效格式和边界情况。

## 7. 未解决的问题 / 风险 (Open Questions / Risks)

* 用户输入的歌曲名称或艺术家名称可能与 Spotify 数据库中的不完全一致，导致“首个结果匹配”策略的准确性有限。这是PRD中已知的简化。
* 不同语言或特殊字符的歌曲/艺术家名称的处理。Python的UTF-8处理应能覆盖多数情况。

## 8. 变更日志 (Changelog)

* 2025-05-17: 初稿创建 - 4-po-sm