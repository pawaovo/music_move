# Spotify 歌单导入工具 API 参考

本文档主要描述本应用程序与外部 API (即 Spotify Web API) 的交互方式。本应用作为 Spotify API 的客户端，消费其提供的服务。

## 外部 API 消耗: Spotify Web API

本应用程序通过 `spotipy` Python 库与 Spotify Web API 进行交互。

* **目的**: 访问 Spotify 的歌曲数据库进行搜索，获取歌曲详细信息，以及在用户授权后管理用户的播放列表（创建播放列表、添加歌曲到播放列表）。
* **官方 API 文档**: [https://developer.spotify.com/documentation/web-api/](https://developer.spotify.com/documentation/web-api/)
* **`spotipy` 库文档**: [https://spotipy.readthedocs.io/](https://spotipy.readthedocs.io/)

### 认证 (Authentication)

* **方法**: OAuth 2.0 授权码流程 (Authorization Code Flow with PKCE)。
* **库实现**: 由 `spotipy.SpotifyOAuth` 类处理。
* **凭据**:
    * `SPOTIPY_CLIENT_ID`: 您的 Spotify 应用的客户端 ID。
    * `SPOTIPY_CLIENT_SECRET`: 您的 Spotify 应用的客户端密钥。
    * `SPOTIPY_REDIRECT_URI`: 在您的 Spotify 应用设置中配置的回调 URI。
    * (这些凭据通过 `docs/environment-vars.md` 中描述的环境变量进行配置)。
* **所需权限范围 (Scopes)**:
    * `user-read-private`: 读取用户的私有信息（例如用户 ID，用于创建播放列表）。
    * `playlist-modify-public`: 创建和修改用户的公开播放列表。
    * `playlist-modify-private`: 创建和修改用户的私有播放列表。
    *(通常会同时请求 `playlist-modify-public` 和 `playlist-modify-private` 以提供灵活性)*

### 主要使用的 API 端点 (通过 `spotipy` 方法调用)

#### 1. 搜索歌曲 (Search for Item)

* **`spotipy` 方法**: `sp.search(q, limit, offset, type, market)`
* **HTTP 端点**: `GET https://api.spotify.com/v1/search`
* **目的**: 根据用户提供的歌曲名称和艺人名搜索 Spotify 曲库。
* **关键参数使用**:
    * `q` (str): 查询字符串。本应用构造为 `f"track:{歌曲标题} artist:{主要艺人名}"`。
    * `type` (str): 设置为 `'track'` 以仅搜索歌曲。
    * `limit` (int): 设置为 `1`，因为本应用默认选择第一个搜索结果。
    * `market` (Optional[str]): 可以设置为用户的市场代码 (例如 `'US'`) 或 `'from_token'` (如果可用) 以获取特定市场的结果。
* **成功响应**: 返回一个包含曲目列表的 Paging Object。我们主要关注 `['tracks']['items']` 中的第一个元素。
    * 关键字段: `id`, `name`, `artists` (列表,每个元素包含 `name`), `album` (包含 `name`), `uri`, `duration_ms`。
* **错误响应**: `spotipy` 会将 Spotify API 的错误（如 4xx, 5xx 状态码）转换成 `SpotifyException`。

#### 2. 获取当前用户信息 (Get Current User's Profile)

* **`spotipy` 方法**: `sp.current_user()`
* **HTTP 端点**: `GET https://api.spotify.com/v1/me`
* **目的**: 获取当前已认证用户的 Spotify 用户 ID，用于创建播放列表。
* **所需 Scope**: `user-read-private`。
* **成功响应**: 返回一个包含用户信息的对象。我们主要关注 `['id']` 字段。

#### 3. 创建播放列表 (Create Playlist)

* **`spotipy` 方法**: `sp.user_playlist_create(user, name, public, collaborative, description)`
* **HTTP 端点**: `POST https://api.spotify.com/v1/users/{user_id}/playlists`
* **目的**: 在当前用户账户下创建一个新的播放列表。
* **关键参数使用**:
    * `user` (str): 用户的 Spotify ID (从 `sp.current_user()['id']` 获取)。
    * `name` (str): 新播放列表的名称 (用户通过命令行参数指定或使用默认值)。
    * `public` (bool): 播放列表是否公开 (默认为 `False`)。
    * `description` (str): 播放列表的描述 (可选)。
* **所需 Scope**: `playlist-modify-public` 或 `playlist-modify-private` (取决于 `public` 参数)。
* **成功响应**: 返回一个代表新创建播放列表的对象，包含其 `id` 和 `uri`。

#### 4. 添加歌曲到播放列表 (Add Items to Playlist)

* **`spotipy` 方法**: `sp.playlist_add_items(playlist_id, items, position=None)`
* **HTTP 端点**: `POST https://api.spotify.com/v1/playlists/{playlist_id}/tracks`
* **目的**: 将一批歌曲添加到指定的播放列表。
* **关键参数使用**:
    * `playlist_id` (str): 目标播放列表的 ID。
    * `items` (List[str]): 要添加的歌曲的 Spotify URI 列表。
* **所需 Scope**: `playlist-modify-public` 或 `playlist-modify-private`。
* **重要限制**:
    * 每次 API 调用最多只能添加 **100** 首歌曲。如果歌曲数量超过 100，应用程序需要将歌曲 URI 列表分块，并进行多次调用。
* **成功响应**: 通常返回一个快照 ID (`snapshot_id`)，表示播放列表内容已更新。

### API 速率限制 (Rate Limiting)

Spotify API 对请求频率有限制。如果超出限制，API 将返回 `429 Too Many Requests` 状态码。

* `spotipy` 库自身可能包含一些简单的重试逻辑。
* 如果遇到持续的速率限制问题，应用程序应实现更健壮的退避和重试策略 (例如指数退避)，或者提示用户稍后再试。
* API 响应头中可能包含 `Retry-After` 字段，指示需要等待多少秒才能再次请求。

## 内部 API (不适用)

本应用程序是一个 CLI 工具，不提供任何供其他服务调用的内部 API。

## 变更日志

| 变更描述             | 日期       | 版本 | 作者        |
| -------------------- | ---------- | ---- | ----------- |
| 初稿 - Spotify-only | 2025-05-17 | 0.1  | 3-Architect |
| ...                  | ...        | ...  | ...         |