# 史诗 2: Spotify 用户认证 (Epic 2: Spotify User Authentication)

**负责人 (Owner):** Technical Lead / Developer Agent
**状态 (Status):** 已规划 (Planned)
**关联PRD功能 (Related PRD Features):** PRD FR5 的前置条件 (3.2.1 Spotify 身份验证)
**预计故事点 (Estimated Story Points):** 5 (示例值，需团队评估)
**最后更新 (Last Updated):** 2025-05-17

## 1. 史诗目标 (Epic Goal)

实现一个安全、可靠的 Spotify 用户认证模块，通过 OAuth 2.0 授权码流程 (Authorization Code Flow with PKCE) 获取并管理 API 访问令牌。该模块将为应用程序提供与用户 Spotify 账户交互（如读取用户信息、创建和修改播放列表）的必要权限。

## 2. 背景与原理 (Background and Rationale)

为了代表用户操作其 Spotify 数据（例如创建播放列表），应用程序必须首先获得用户的明确授权。Spotify API 使用 OAuth 2.0 协议进行授权。`spotipy` 库简化了此流程，但仍需正确配置和调用。此史诗专注于封装认证逻辑，使其易于在应用程序的其他部分使用。

## 3. 主要用户故事 / 功能需求 (Key User Stories / Features)

| 故事ID (Story ID) | 标题 (Title)                      | 用户故事/需求描述 (User Story / Description)                                                                                                 | 优先级 (Priority) | 备注 (Notes)                                                                    |
| :---------------- | :-------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------- | :-------------- | :------------------------------------------------------------------------------ |
| **Story 2.1** | 实现 Spotify OAuth 2.0 认证流程 | 作为应用程序，我需要能够引导用户完成 Spotify OAuth 2.0 授权，并获取一个有效的 `spotipy.Spotify` 客户端实例，以便后续进行 API 调用。                       | 高 (High)       | 关键在于正确使用 `spotipy.SpotifyOAuth` 和处理回调。                               |
| **Story 2.2** | 实现认证令牌的缓存与复用            | 作为应用程序，我应该缓存已获取的认证令牌，以便用户在后续运行应用时无需每次都重新授权，除非令牌过期或授权范围变更，从而提升用户体验。                           | 高 (High)       | `spotipy` 默认行为，需确保其正常工作。                                              |
| **Story 2.3** | 处理认证错误与用户取消            | 作为应用程序，当用户认证失败（例如，拒绝授权、无效凭据）或在认证过程中取消操作时，我需要能够优雅地处理这些情况，并向用户提供清晰的反馈或退出程序。                 | 中 (Medium)     | 增强应用的健壮性。                                                                |

## 4. 验收标准 (Acceptance Criteria for the Epic)

* `spotify_playlist_importer/spotify/auth.py` 模块已创建。
* 模块能够使用从 `core.config` 加载的 `SPOTIPY_CLIENT_ID`, `SPOTIPY_CLIENT_SECRET`, `SPOTIPY_REDIRECT_URI` 初始化 `spotipy.SpotifyOAuth`。
* 模块提供一个函数，调用该函数可以：
    * 如果缓存中没有有效令牌，则自动打开用户的默认浏览器，并导航到 Spotify 授权页面。
    * 成功授权后，能够获取访问令牌和刷新令牌。
    * 返回一个已配置并认证的 `spotipy.Spotify` 客户端实例。
* 认证所需的 Scopes (`user-read-private`, `playlist-modify-public`, `playlist-modify-private`) 已正确配置，符合 `docs/api-reference.md` 的要求。
* `spotipy` 的默认令牌缓存机制（例如在用户目录下的 `.cache-<username>` 文件）能够正常工作，用户在令牌有效期内再次运行脚本时无需重新授权。
* 如果用户在浏览器中拒绝授权或关闭授权窗口，应用程序能够捕获相应的 `spotipy` 异常并给出提示信息后退出。
* 如果提供的 Spotify API 凭据无效，程序应在尝试认证时失败并给出明确错误信息。

## 5. 技术说明与依赖 (Technical Notes & Dependencies)

* **依赖的其他史诗 (Depends on):** Epic 1 (特别是 Story 1.2, Story 1.5)
* **对其他史诗的影响 (Impacts):** Epic 3, Epic 4 中的 Spotify API 调用均依赖此史诗提供的认证客户端。
* **关键技术参考:**
    * `docs/api-reference.md` (认证 Authentication 部分)
    * `docs/architecture.md` (Spotify认证模块 `spotify/auth.py` 部分)
    * `docs/environment-vars.md` (Spotify API 凭据)
    * `prd.md` (3.2.1 Spotify 身份验证)
    * `spotipy` 库文档 ([https://spotipy.readthedocs.io/](https://spotipy.readthedocs.io/))，特别是关于 `SpotifyOAuth` 的部分。

## 6. 初步任务分解 (Initial Task Breakdown for Stories - Example for Story 2.1)

* **Story 2.1: 实现 Spotify OAuth 2.0 认证流程**
    * [ ] 任务2.1.1: 在 `spotify/auth.py` 中创建 `get_spotify_client()` 函数。
    * [ ] 任务2.1.2: 从 `core.config` 导入并使用 Spotify API 凭据。
    * [ ] 任务2.1.3: 定义所需的 Spotify API 权限范围 (scopes)。
    * [ ] 任务2.1.4: 实例化 `spotipy.SpotifyOAuth` 对象，传入凭据、回调URI和scopes。
    * [ ] 任务2.1.5: 调用 `sp_oauth.get_access_token(code, as_dict=False, check_cache=True)` (或类似方法，根据spotipy版本，通常 `spotipy.Spotify(auth_manager=sp_oauth)` 会自动处理) 来获取令牌。`spotipy` 会处理打开浏览器和本地服务器回调的逻辑。
    * [ ] 任务2.1.6: 使用获取到的认证信息（或 `auth_manager`）实例化并返回 `spotipy.Spotify` 客户端。
    * [ ] 任务2.1.7: 在 `main.py` 中（或一个测试脚本中）初步集成调用 `get_spotify_client()` 并尝试一个简单的API调用（例如 `sp.me()`）来验证认证是否成功。

## 7. 未解决的问题 / 风险 (Open Questions / Risks)

* 用户本地环境可能存在防火墙或浏览器配置问题，导致回调失败。`spotipy` 通常能处理标准情况。
* 确保 `SPOTIPY_REDIRECT_URI` 在 Spotify Developer Dashboard 和 `.env` 文件中完全一致，这是常见错误点。

## 8. 变更日志 (Changelog)

* 2025-05-17: 初稿创建 - 4-po-sm