# 史诗 4: Spotify 播放列表管理与报告生成 (Epic 4: Spotify Playlist Management & Reporting)

**负责人 (Owner):** Technical Lead / Developer Agent
**状态 (Status):** 已规划 (Planned)
**关联PRD功能 (Related PRD Features):** PRD FR4, FR5 (Spotify部分)
**预计故事点 (Estimated Story Points):** 10 (示例值，需团队评估)
**最后更新 (Last Updated):** 2025-05-17

## 1. 史诗目标 (Epic Goal)

基于已成功匹配的 Spotify 歌曲列表，在用户的 Spotify 账户中自动创建一个新的播放列表，并将这些歌曲添加到新创建的播放列表中。同时，生成一份详细的操作报告，总结哪些歌曲被成功导入，哪些未能找到或处理失败，并向用户提供新播放列表的链接。

## 2. 背景与原理 (Background and Rationale)

此史诗是应用程序核心价值的最终实现：将用户的本地歌曲列表有效地迁移到 Spotify。这涉及到与 Spotify API 的进一步交互，包括获取用户信息、创建播放列表和批量添加曲目。清晰的用户反馈和一份详细的报告对于用户理解操作结果至关重要。

## 3. 主要用户故事 / 功能需求 (Key User Stories / Features)

| 故事ID (Story ID) | 标题 (Title)                              | 用户故事/需求描述 (User Story / Description)                                                                                                                              | 优先级 (Priority) | 备注 (Notes)                                                                          |
| :---------------- | :---------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :-------------- | :------------------------------------------------------------------------------------ |
| **Story 4.1** | 实现创建 Spotify 播放列表功能             | 作为应用程序，我需要能够使用用户的 Spotify ID 和用户指定的播放列表名称（或默认名称）、描述和公开状态，在用户的账户中创建一个新的播放列表。                                              | 高 (High)       | 参考 `prd.md` (3.2.3 - 创建播放列表部分)                                                  |
| **Story 4.2** | 实现向 Spotify 播放列表添加歌曲功能       | 作为应用程序，我需要能够将一批 `MatchedSong` URI 添加到指定的 Spotify 播放列表中。我必须处理 Spotify API 关于单次请求最多添加100首歌曲的限制。                                  | 高 (High)       | 参考 `prd.md` (3.2.3 - 添加歌曲部分), `docs/api-reference.md` (添加歌曲限制)           |
| **Story 4.3** | 编排完整导入流程并生成用户操作报告          | 作为应用程序，我需要协调整个导入流程——从读取输入、认证、搜索、创建播放列表到添加歌曲——并在操作结束后，向用户显示总结信息，并生成一份详细的文本报告文件，记录每首歌的处理结果和新播放列表的链接。 | 高 (High)       | 参考 `prd.md` (3.1.3 匹配列表生成, 5. 用户反馈), `README.md` (输出部分)                     |
| **Story 4.4** | 在主CLI中集成播放列表参数与流程控制     | 作为开发者，我需要在 `main.py` 中集成处理用户通过命令行指定的播放列表名称、描述和公开/私有状态的参数，并将这些参数传递给播放列表创建逻辑。                                   | 中 (Medium)     | 确保用户可以通过命令行自定义播放列表的属性。                                                  |

## 4. 验收标准 (Acceptance Criteria for the Epic)

* `spotify_playlist_importer/spotify/client.py` 模块包含创建新播放列表的函数：
    * 该函数能使用认证后的 `spotipy` 客户端获取当前用户的 Spotify ID (`sp.current_user()['id']`)。
    * 该函数能调用 `sp.user_playlist_create()`，并正确传递播放列表名称、公开性（public/private）和描述参数。
    * 成功创建后，返回新播放列表的ID和URL。
* `spotify_playlist_importer/spotify/client.py` 模块包含向指定播放列表添加歌曲的函数：
    * 该函数接收目标播放列表ID和 Spotify Track URI 列表。
    * 如果Track URI列表中的歌曲数量超过100首，该函数能自动将列表分块，并为每个块调用 `sp.playlist_add_items()`。
    * 处理API调用可能发生的错误。
* `spotify_playlist_importer/main.py` (或其调用的核心逻辑模块) 能够：
    * 按顺序执行：认证 -> 解析输入文件 -> 循环搜索每首歌 -> (如果至少有一首匹配) 创建播放列表 -> 添加所有匹配的歌曲到播放列表。
    * 收集每首输入歌曲的处理结果，并存储为 `MatchResult` 对象列表。
    * 在所有操作完成后，在控制台打印总结信息，包括成功导入的歌曲数量、失败或未找到的数量，以及新创建播放列表的 Spotify URL。
    * 生成一个文本文件报告 (`matching_report_YYYY-MM-DD_HHMMSS.txt` 或用户指定的文件名)，详细列出：
        * 原始输入的每一行。
        * 解析出的歌曲名和艺术家。
        * 匹配状态 (例如："已匹配到Spotify", "未在Spotify找到", "搜索API错误", "已添加到播放列表", "添加失败")。
        * 如果匹配成功，显示 Spotify 上的歌曲名称、艺术家、ID 和 URI。
* 用户可以通过命令行参数（例如 `--playlist-name`, `--public`, `--description`）控制新创建播放列表的属性。
* 如果没有任何歌曲成功匹配，则不应尝试创建播放列表，并应在报告和控制台输出中明确说明。
* 错误处理：API调用错误（如创建播放列表失败、添加歌曲失败）应被捕获，并在报告和控制台输出中有所体现，程序应尽可能完成其余操作或优雅退出。

## 5. 技术说明与依赖 (Technical Notes & Dependencies)

* **依赖的其他史诗 (Depends on):** Epic 1, Epic 2, Epic 3
* **对其他史诗的影响 (Impacts):** 此史诗代表了MVP的核心用户可见功能。
* **关键技术参考:**
    * `prd.md` (特别是 3.1.3 匹配列表生成模块, 3.2.3 Spotify 播放列表创建与导入, 5. 用户反馈)
    * `docs/api-reference.md` (Get Current User's Profile, Create Playlist, Add Items to Playlist 部分)
    * `docs/data-models.md` (`MatchResult`)
    * `README.md` (输出部分, 命令行参数部分)
    * `spotipy` 库文档。

## 6. 初步任务分解 (Initial Task Breakdown for Stories - Example for Story 4.1)

* **Story 4.1: 实现创建 Spotify 播放列表功能**
    * [ ] 任务4.1.1: 在 `spotify/client.py` 中定义 `create_playlist(sp: spotipy.Spotify, user_id: str, name: str, public: bool, description: Optional[str]) -> Optional[Dict]` 函数。
    * [ ] 任务4.1.2: (获取 user_id 的逻辑通常在调用此函数之前，例如在 `main.py` 中调用 `sp.current_user()['id']` 一次)。
    * [ ] 任务4.1.3: 调用 `sp.user_playlist_create(user=user_id, name=name, public=public, description=description)`。
    * [ ] 任务4.1.4: 从返回的播放列表对象中提取并返回 `id` 和 `external_urls['spotify']`。
    * [ ] 任务4.1.5: 实现对 `spotipy.SpotifyException` 的捕获和处理，在发生错误时返回 `None` 或抛出自定义异常。
    * [ ] 任务4.1.6: 编写单元测试，mock `sp.user_playlist_create` 以测试成功和失败场景。

## 7. 未解决的问题 / 风险 (Open Questions / Risks)

* 用户可能意外达到其Spotify账户的播放列表数量上限（尽管此上限很高）。
* 如果歌曲列表非常庞大，多次分块添加歌曲可能会耗时较长，需要考虑给用户提供进度反馈。

## 8. 变更日志 (Changelog)

* 2025-05-17: 初稿创建 - 4-po-sm