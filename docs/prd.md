# 产品功能需求及实施方案：音乐平台歌曲匹配与歌单导入器

## 1\. 引言

### 1.1 目的

本文档概述了一个脚本/应用程序的功能需求和详细实施方案，该脚本/应用程序旨在解析用户提供的歌曲列表，在选定的音乐平台（Spotify 或 Apple Music）上匹配这些歌曲，并将匹配的歌曲导入到用户在所选平台上的新播放列表中。

### 1.2 产品概述

该产品将为用户提供一种将歌曲列表迁移到 Spotify 或 Apple Music 的简单方法。用户将提供文本输入，其中每行代表一首歌曲（歌曲名称和艺术家）。然后，应用程序将在选定的平台上搜索这些歌曲，匹配第一个搜索结果，编译匹配歌曲的列表，最后在用户选定平台的帐户中创建一个包含这些匹配歌曲的新播放列表。

### 1.3 文档范围

本文档涵盖：

  * 基于用户指定步骤的核心功能需求。
  * 针对 Spotify 和 Apple Music 集成的详细实施计划，包括 API 使用、身份验证、数据解析和播放列表操作。
  * 数据处理、错误管理和安全性的关键考虑因素。

## 2\. 通用功能需求

根据用户要求，该应用程序将执行以下高级功能：

1.  **FR1: 用户输入处理：** 接受用户的多行文本输入。每行将包含格式为“歌曲名称 - 艺术家1 / 艺术家2”的歌曲信息。
2.  **FR2: 平台选择与迭代搜索：** 允许用户选择 Spotify 或 Apple Music 作为目标平台。对于输入文本中的每首歌曲，在选定的平台上执行搜索。
3.  **FR3: 首个结果匹配与记录：** 对于每次搜索，将第一个歌曲结果识别为正确匹配并记录其详细信息。
4.  **FR4: 匹配列表生成：** 编译一个全面的列表，显示每首歌曲的原始文本输入以及在音乐平台上匹配的歌曲的详细信息。
5.  **FR5: 播放列表创建与导入：** 在用户选定平台的帐户中创建一个新的播放列表，并将所有成功匹配的歌曲添加到此播放列表中。这需要用户使用所选音乐平台进行身份验证。

## 3\. 详细功能需求和实施方案

本节将实施方案分解为核心模块和特定于平台的详细信息。

### 3.1 核心模块（通用逻辑）

#### 3.1.1 输入文本解析模块 (涉及 FR1)

  * **功能需求：** 系统必须解析多行文本输入。应处理每一行以提取歌曲标题和艺术家。
      * 歌曲标题是“ - ”之前的部分。
      * 艺术家字符串是“ - ”之后的部分。
      * 如果艺术家字符串中存在多个艺术家，则用“ / ”分隔。
  * **实施细节：**
      * 逐行读取输入文本。
      * 对于每一行：
          * 按分隔符“ - ”（确保处理分隔符周围潜在的前导/尾随空格）拆分字符串。
          * 第一部分是 `song_title`。
          * 第二部分是 `artist_string`。
          * 按“ / ”拆分 `artist_string` 以获取 `artists` 列表。
          * 存储这些解析的 `song_title` 和 `artists`（例如，作为字典列表）。
      * 处理潜在错误，例如不符合预期格式的行。

#### 3.1.2 平台选择模块 (涉及 FR2)

  * **功能需求：** 系统必须提供一种机制，供用户选择“Spotify”或“Apple Music”作为搜索和播放列表创建的目标平台。
  * **实施细节：**
      * 这可以是命令行参数、简单的文本输入提示，或者如果开发了图形界面，则为 UI 元素。
      * 该选择将确定随后调用哪些特定于平台的模块（身份验证、搜索、播放列表创建）。

#### 3.1.3 匹配列表生成模块 (涉及 FR4)

  * **功能需求：** 处理完所有输入歌曲后，系统必须生成一个列表，将每个原始输入行与目标平台上匹配的歌曲的详细信息（如果找到匹配项）相关联。
  * **实施细节：**
      * 在搜索过程中维护一个数据结构（例如，对象/字典列表）。
      * 此列表中的每个条目应包含：
          * `original_input_line`：用户提供的原始文本行。
          * `parsed_song_title`：提取的歌曲标题。
          * `parsed_artists`：提取的艺术家列表。
          * `status`：例如，“已匹配”、“未找到”、“搜索期间出错”。
          * `matched_platform`：“Spotify”或“Apple Music”。
          * `matched_song_id`：平台上歌曲的 ID。
          * `matched_song_name`：平台 API 返回的歌曲名称。
          * `matched_song_artists`：平台 API 返回的歌曲的艺术家列表。
          * `matched_song_uri_or_url`：匹配歌曲的 URI (Spotify) 或 URL (Apple Music)。
      * 此列表将用于向用户显示，并作为播放列表导入步骤的输入。

### 3.2 Spotify 实施方案

#### 3.2.1 Spotify 身份验证 (FR5 的先决条件)

  * **功能需求：** 系统必须安全地向 Spotify 验证用户身份，以获取读取用户信息（获取用户 ID）和创建/修改播放列表的权限。
  * **实施细节：**
      * **库：** 使用 `spotipy` Python 库 [1, 2]。
      * **流程：** 实施 OAuth 2.0 授权码流程（适用于 Web 服务器应用程序）或带 PKCE 的授权码流程（适用于无法安全存储客户端密钥的本地脚本/桌面应用程序）[3, 4, 1]。`spotipy.SpotifyOAuth` 可以管理此流程 [1, 5]。
      * **凭据：**
          * 在 Spotify 开发者仪表板上注册一个应用程序以获取 `Client ID` 和 `Client Secret` [6]。
          * 在 Spotify 开发者仪表板中配置一个 `Redirect URI`，并在 `SpotifyOAuth` 配置中使用完全相同的 URI [6]。
      * **范围 (Scopes)：** 请求以下范围 [1, 7, 8]：
          * `user-read-private`：获取用户的 Spotify ID（创建特定用户的播放列表时需要）。
          * `playlist-modify-public`：创建公共播放列表。
          * `playlist-modify-private`：创建私有播放列表（建议同时请求公共和私有修改范围以获得灵活性，或者如果默认播放列表创建是私有的）。社区反馈表明，即使向公共播放列表添加项目，有时也可能意外需要 `playlist-read-private`，因此如果出现问题，请考虑这一点 [9]。
      * **令牌处理：** `spotipy` 将处理令牌交换和刷新。如果应用程序需要在会话之间保持授权，请安全地存储令牌。

#### 3.2.2 Spotify 歌曲搜索和匹配 (涉及 FR2, FR3)

  * **功能需求：** 对于从输入中解析的每首歌曲（标题和艺术家），在 Spotify 上搜索并选择第一个结果作为匹配项。
  * **实施细节：**
      * **API 端点：** `GET /v1/search` [6]。
      * **`spotipy` 方法：** 使用 `sp.search()`。
      * **查询构建 (`q` 参数)：**
          * 使用字段过滤器组合歌曲标题和主要艺术家以获得更高的准确性：`track:{song_title} artist:{primary_artist_name}` [6, 10]。
          * URL 编码查询组件。`spotipy` 通常会处理此问题。
      * **参数：**
          * `type='track'` [6]。
          * `limit=1`（仅获取第一个结果）[6]。
          * 可选地，`market='from_token'` 或特定的市场代码（如果已知），以获取用户市场中可用的结果 [6, 11]。
      * **响应解析：**
          * 匹配的曲目将位于 `results['tracks']['items']` 中。如果 `limit=1`，这将是一个包含一个元素的数组（如果找到匹配项）。
          * 提取：
              * 歌曲 ID：`item['id']` [6, 12, 11]。
              * 歌曲名称：`item['name']` [6, 12, 11]。
              * 艺术家：`item['artists']`（艺术家对象列表，提取名称）[6, 12, 11]。
              * 歌曲 URI：`item['uri']`（例如，`spotify:track:TRACK_ID`）[6, 12, 11]。添加到播放列表时需要此 URI。
              * 可选地，`item['duration_ms']` 用于未来的匹配增强 [12, 11]。
      * **记录：** 将此信息添加到匹配列表（参见 3.1.3）。如果没有返回任何项目，则标记为“未找到”。

#### 3.2.3 Spotify 播放列表创建和导入 (涉及 FR5)

  * **功能需求：** 在经过身份验证的用户的 Spotify 帐户中创建一个新的播放列表，并将所有成功匹配的歌曲添加到其中。
  * **实施细节：**
    1.  **获取用户 ID：**
          * API 端点：`GET /v1/me`（由 `user-read-private` 范围涵盖）。
          * `spotipy` 方法：`sp.current_user()['id']` [2]。
    2.  **创建播放列表：**
          * API 端点：`POST /v1/users/{user_id}/playlists` [13]。
          * `spotipy` 方法：`sp.user_playlist_create(user=user_id, name="My Imported Songs", public=False, description="Songs imported via script")`。
              * `name`：用户可配置或默认名称。
              * `public`：布尔值，用户偏好。
              * `description`：可选。
          * 响应包含新的 `playlist_id` [13]。
    3.  **将歌曲添加到播放列表：**
          * API 端点：`POST /v1/playlists/{playlist_id}/tracks` [14]。
          * `spotipy` 方法：`sp.playlist_add_items(playlist_id, track_uris)`。
          * `track_uris`：从匹配歌曲中获取的 Spotify 曲目 URI 列表。
          * **批处理：** API 端点每个请求最多限制 100 首曲目 [14]。如果匹配的歌曲超过 100 首，则需要将 `track_uris` 列表分成 100 个的块，并为每个块进行多次 `playlist_add_items` 调用。

### 3.3 Apple Music 实施方案

#### 3.3.1 Apple Music 身份验证 (FR5 的先决条件)

  * **功能需求：** 系统必须安全地向 Apple Music 验证应用程序身份（开发者令牌），然后获取用户授权（音乐用户令牌）以访问其资料库并创建播放列表。
  * **实施细节：** 这是一个双令牌过程 [15, 16]。
    1.  **开发者令牌：**
          * **用途：** 向 Apple Music API 验证您的应用程序（开发者）身份 [16]。所有 API 调用都需要。
          * **生成：**
              * 使用 ES256 算法签名的 JSON Web 令牌 (JWT) [16]。
              * **所需凭据：**
                  * `Private Key (.p8 file)`：从 Apple 开发者帐户下载（MusicKit 密钥）[16]。
                  * `Key ID (kid)`：与私钥关联 [16]。
                  * `Team ID (iss)`：在 Apple 开发者帐户会员资格详细信息中找到 [16]。
              * **JWT 结构：**
                  * 标头：`{"alg": "ES256", "kid": "YOUR_KEY_ID"}`。
                  * 有效负载：`{"iss": "YOUR_TEAM_ID", "iat": issued_at_timestamp, "exp": expiration_timestamp}`（最长 6 个月有效期）[16]。
              * **Python 库：** 可使用 `PyJWT` 和 `cryptography` 进行生成。
          * **用法：** 在 `Authorization: Bearer <developer_token>` HTTP 标头中发送 [16]。
    2.  **音乐用户令牌：**
          * **用途：** 授权您的应用程序访问特定用户的 Apple Music 资料库（创建播放列表、将曲目添加到资料库播放列表）[15]。
          * **获取（对于非 MusicKit JS 后端脚本而言复杂）：**
              * Apple 官方推荐 Web 应用程序通过在用户浏览器中运行的 **MusicKit JS** 来获取音乐用户令牌 [15]。
              * **推荐流程（如果脚本具有 Web 组件或可以将用户引导至一次性 Web 身份验证页面）：**
                1.  **前端（网页）：**
                      * 嵌入 MusicKit JS (`<script src="https://js-cdn.music.apple.com/musickit/v1/musickit.js"></script>`) [17, 18]。
                      * 使用您的开发者令牌配置 MusicKit JS：`MusicKit.configure({ developerToken: 'YOUR_DEVELOPER_TOKEN', app: { name: 'Your App Name', build: '1.0' } });` [17]。
                      * 调用 `musicKitInstance.authorize()` [19, 17, 20, 21]。这将提示用户使用其 Apple ID 登录并授予权限。
                      * 成功授权后，`authorize()` 方法返回一个解析为 `musicUserToken`（字符串）的 Promise [17, 21]。
                2.  **令牌传输：** 然后，前端 JavaScript 必须安全地将此 `musicUserToken` 发送到您的后端 Python 脚本（例如，如果脚本运行临时服务器，则通过 HTTPS POST 请求到本地服务器端点；如果是简单的 CLI，则用户复制粘贴）。
              * **替代方案（无头浏览器 - 不推荐）：** 从技术上讲，可以自动化无头浏览器来执行 MusicKit JS 授权，但这非常复杂、脆弱，并且可能违反 Apple 的服务条款 [15]。
              * **服务器端直接 OAuth 重定向流程：** Apple 文档未明确概述标准的服务器到服务器 OAuth 2.0 重定向流程，以专门用于获取 Apple Music API 的音乐用户令牌，其方式与 Spotify 类似。文档中描述的 OAuth 流程（例如，用于设备管理 [22] 或通过 Apple 登录 [23]）适用于不同的服务或身份验证，并且可能无法直接产生可用于 `api.music.apple.com` 进行资料库操作的音乐用户令牌。Web 的主要文档路径是 MusicKit JS [24, 15]。
          * **用法：** 在需要用户资料库访问权限的请求的 `Music-User-Token: <music_user_token>` HTTP 标头中发送 [15]。
          * **令牌生命周期：** 音乐用户令牌的生命周期有限（可能长达 6 个月，但 MusicKit JS 可能会在内部处理刷新或在浏览器本地存储中存储重新身份验证数据）[19]。如果令牌过期，脚本可能需要用户重新进行身份验证。

#### 3.3.2 Apple Music 歌曲搜索和匹配 (涉及 FR2, FR3)

  * **功能需求：** 对于每个解析的歌曲，使用开发者令牌在 Apple Music 上搜索并选择第一个结果。
  * **实施细节：**
      * **库：** `requests` 用于直接 API 调用。`apple-music-python` 库可以执行目录搜索，但明确指出它不支持用户资料库资源（例如创建播放列表）[25, 26, 27]。
      * **获取用户的店面 (推荐在搜索前进行)：**
          * API 端点：`GET https://api.music.apple.com/v1/me/storefront`
          * 标头：`Authorization: Bearer <developer_token>`, `Music-User-Token: <music_user_token>`
          * 响应：包含 `data.id` 的 JSON，即店面（例如，“us”）。这有助于定制搜索结果。
      * **API 端点：** `GET https://api.music.apple.com/v1/catalog/{storefront}/search` [28]。
      * **标头：** `Authorization: Bearer <developer_token>`。（目录搜索本身通常不需要音乐用户令牌）。
      * **查询构建 (`term` 参数)：**
          * 组合歌曲标题和主要艺术家名称。用 `+` 替换空格。例如，`term=Song+Title+Artist+Name` [29, 28, 30, 31]。
      * **参数：**
          * `types=songs`（仅搜索歌曲）[29, 28]。
          * `limit=1`（仅获取第一个结果）[29, 28]。最大限制通常为 25。
      * **响应解析：**
          * 匹配的歌曲将位于 `response.json()['results']['songs']['data']` 中。如果 `limit=1`，这将是一个包含一个元素的数组（如果找到）。
          * 提取：
              * 歌曲目录 ID：`item['id']`（这是用于添加到播放列表的 ID）[28, 32, 33, 34]。
              * 歌曲名称：`item['attributes']['name']` [28, 32, 31]。
              * 艺术家名称：`item['attributes']['artistName']` [28, 32, 31]。
              * 专辑名称：`item['attributes']['albumName']` [28, 32]。
              * 时长：`item['attributes']['durationInMillis']` [28, 32]。
              * URL：`item['attributes']['url']`（可共享 URL）[32]。
      * **记录：** 将此信息添加到匹配列表。如果 `data` 数组为空，则标记为“未找到”。

#### 3.3.3 Apple Music 播放列表创建和导入 (涉及 FR5)

  * **功能需求：** 在经过身份验证的用户的 Apple Music 资料库中创建一个新的播放列表，并将所有成功匹配的歌曲添加到其中。需要开发者令牌和音乐用户令牌。
  * **实施细节：**
    1.  **创建播放列表：**
          * API 端点：`POST https://api.music.apple.com/v1/me/library/playlists` [35, 36]。
          * 标头：`Authorization: Bearer <developer_token>`, `Music-User-Token: <music_user_token>`, `Content-Type: application/json`。
          * **请求正文 (JSON)：** [35, 37, 36]json
            {
            "attributes": {
            "name": "My Imported Songs", // 必需
            "description": "Songs imported via script" // 可选
            }
            // 可选地，可以在创建时直接添加曲目，见下文
            }
            ````
            要在创建时添加曲目：
            ```json
            {
              "attributes": {... },
              "relationships": {
                "tracks": {
                  "data": [ // 歌曲对象数组
                    { "id": "song_catalog_id_1", "type": "songs" },
                    { "id": "song_catalog_id_2", "type": "songs" }
                  ]
                }
              }
            }
            ````
          * 响应 (201 Created)：包含新资料库播放列表详细信息的 JSON，包括其 `id`（例如，`p.xxxxxxxxx`）[35]。
    2.  **将歌曲添加到播放列表（如果在创建时未添加）：**
          * API 端点：`POST https://api.music.apple.com/v1/me/library/playlists/{playlist_id}/tracks` [24, 15, 38, 39]。
          * `{playlist_id}`：上一步创建的资料库播放列表的 ID。
          * 标头：`Authorization: Bearer <developer_token>`, `Music-User-Token: <music_user_token>`, `Content-Type: application/json`。
          * **请求正文 (JSON)：** [38]
            ```json
            {
              "data": [ // 要添加的歌曲对象数组
                { "id": "song_catalog_id_1", "type": "songs" },
                { "id": "song_catalog_id_2", "type": "songs" }
                //... 更多歌曲
              ]
            }
            ```
            每个 `id` 是歌曲的 Apple Music 目录 ID，`type` 是“songs”。
          * 响应：成功时为 201 Created [38]。
          * **批处理：** Apple Music API 文档未明确指出单个请求中添加到播放列表的项目数量上限。但是，对于非常大的列表，请考虑进行批处理以避免请求正文过大或潜在的速率限制/超时。通过 `relationships` 对象在播放列表创建期间添加曲目可能是初始曲目集的更有效方法 [35]。
          * **关于添加曲目的说明：** 歌曲通常附加到播放列表的末尾；此 API 端点不直接支持在特定索引处插入 [39]。

## 4\. 数据结构（概念性）

### 4.1 输入歌曲表示（解析后）

```
{
  "original_line": "歌曲名称 - 艺术家1 / 艺术家2",
  "title": "歌曲名称",
  "artists": ["艺术家1", "艺术家2"]
}
```

### 4.2 匹配歌曲表示（特定于平台）

**Spotify:**

```
{
  "id": "spotify_track_id",
  "name": "Spotify 上匹配的歌曲名称",
  "artists":,
  "uri": "spotify:track:spotify_track_id",
  "duration_ms": 200000
}
```

**Apple Music:**

```
{
  "catalog_id": "apple_music_song_catalog_id",
  "name": "Apple Music 上匹配的歌曲名称",
  "artist_name": "Apple Music 上匹配的艺术家名称", // 主要艺术家
  "album_name": "专辑名称",
  "duration_in_millis": 200000,
  "url": "apple_music_song_url"
}
```

### 4.3 最终匹配列表条目

```
{
  "original_input_line": "歌曲名称 - 艺术家1 / 艺术家2",
  "parsed_song_title": "歌曲名称",
  "parsed_artists": ["艺术家1", "艺术家2"],
  "status": "已匹配" / "未找到" / "错误",
  "platform": "Spotify" / "Apple Music",
  "matched_song_details": {} // 4.2 中的结构
}
```

## 5\. 错误处理和用户反馈

  * **输入解析错误：** 通知用户不符合预期的“歌曲 - 艺术家”格式的行。
  * **身份验证失败：**
      * Spotify：如果令牌过期或范围不足，引导用户重新进行身份验证。`spotipy` 可以引发特定异常。
      * Apple Music：清楚地解释开发者令牌设置的需求（脚本开发者一次性设置）和音乐用户令牌获取过程（用户可能需要重复操作）。处理音乐用户令牌无效或过期的错误。
  * **API 错误：**
      * 为速率限制错误 (HTTP 429) 实施指数退避和重试 [16, 35]。
      * 处理其他常见的 HTTP 错误：401（未授权）、403（禁止）、404（特定 API 调用未找到，与搜索未产生结果不同）、5xx（服务器错误）[13, 28, 15, 16, 35, 38, 40]。
      * 记录详细的错误消息以进行调试。
  * **未找到歌曲：** 在最终匹配列表中明确指出在所选平台上找不到哪些歌曲。
  * **播放列表创建/导入错误：** 报告播放列表创建或添加曲目期间的任何问题。
  * **用户反馈：** 在长时间操作期间提供进度更新（例如，“正在搜索歌曲 X，共 Y 首...”、“正在将 N 首歌曲添加到播放列表...”）。显示最终匹配列表并在成功创建播放列表后显示确认消息。

## 6\. 安全注意事项

  * **Spotify 凭据：** `Client ID` 和 `Client Secret` 必须安全存储（例如，环境变量、`.env` 文件、安全保管库），并且不能硬编码，尤其是在分发脚本时 [6]。如果需要持久身份验证，还应安全存储 `Refresh tokens`。
  * **Apple Music 凭据：**
      * 用于生成开发者令牌的 `Private Key (.p8 file)` 高度敏感，必须使用严格的访问控制进行存储 [16]。
      * `Key ID` 和 `Team ID` 可以作为配置存储。
      * `Music User Tokens` 特定于用户并授予对其资料库的访问权限。如果由后端存储，则必须对其进行保护。鉴于其通过前端获取的方法，请确保安全传输到后端 (HTTPS)。
  * **API 调用：** 所有 API 调用都应通过 HTTPS 进行。
  * **用户数据：** 注意处理或存储的任何用户数据。遵守平台开发者关于数据隐私和使用的政策 [24, 41, 2]。

## 7\. “匹配第一个结果”策略注意事项

  * **准确性：** 此策略很简单，但可能并不总是准确。第一个结果可能是混音、翻唱、现场版或名称相似但不同的歌曲 [42, 43, 44, 45, 46]。这是基于用户对简单性要求的已知限制。
  * **用户期望：** 向用户清楚地传达此匹配策略，以便他们了解其潜在限制。
  * **未来增强：** 匹配列表 (FR4) 应提供足够的详细信息供用户查看匹配项。未来版本可以包含更复杂的匹配逻辑（参见第 8 节）。

## 8\. 未来增强功能（可选）

  * **高级匹配逻辑：**
      * 标题和艺术家的模糊字符串匹配（例如，使用 Levenshtein 距离和 `python-Levenshtein` 等库）[47, 48, 49, 50, 51]。
      * 比较曲目时长（允许较小的容差）[12, 11]。
      * 专辑名称比较。
      * 如果可用，使用 ISRC 代码（尽管当前输入格式不支持）[12, 13, 32, 45, 11]。
  * **交互式匹配：** 对于低置信度的匹配，允许用户从前 N 个搜索结果中进行选择。
  * **配置文件：** 用于 API 密钥、播放列表命名约定等。
  * **GUI：** 图形用户界面，更易于使用。
  * **支持更多平台。**
  * **持久令牌存储：** 安全地缓存和重用身份验证令牌以减少登录频率。

本文档提供了基础计划。开发过程应包括迭代测试，尤其是在身份验证流程和不同歌曲输入的匹配准确性方面。

```
```