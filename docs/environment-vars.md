# Spotify 歌单导入工具环境变量

本文档列出了运行 "Spotify 歌单导入工具" 所需的环境变量及其描述。这些变量主要用于配置与 Spotify API 的连接和认证。

## 配置加载机制

* **本地开发**: 应用程序通过 `python-dotenv` 库从项目根目录下的 `.env` 文件加载环境变量。
* **部署环境 (如果打包为可执行文件或在其他环境运行)**: 用户可能需要手动设置这些环境变量，或者通过特定于平台的配置方式提供。

## 必需的环境变量

| 变量名称                | 描述                                                                | 示例值                                      | 是否必需 | 是否敏感 |
| :---------------------- | :------------------------------------------------------------------ | :------------------------------------------ | :------- | :------- |
| `SPOTIPY_CLIENT_ID`     | 您在 Spotify Developer Dashboard 上创建的应用的 Client ID。            | `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`          | 是       | 是       |
| `SPOTIPY_CLIENT_SECRET` | 您在 Spotify Developer Dashboard 上创建的应用的 Client Secret。          | `yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy`          | 是       | 是       |
| `SPOTIPY_REDIRECT_URI`  | 您在 Spotify Developer Dashboard 上为应用配置的回调 URI (Redirect URI)。 | `http://localhost:8888/callback` 或 `http://localhost/callback` | 是       | 否       |

## 可选的环境变量

| 变量名称         | 描述                                                              | 示例值 / 默认值       | 是否必需 | 是否敏感 |
| :--------------- | :---------------------------------------------------------------- | :------------------ | :------- | :------- |
| `LOG_LEVEL`      | 设置应用程序的日志记录级别。可选值: `DEBUG`, `INFO`, `WARNING`, `ERROR`。 | `INFO`              | 否       | 否       |
| `SPOTIPY_CACHE_PATH` | (由 `spotipy` 内部使用或可配置) 用于存储 OAuth 令牌缓存的文件路径。 | `.cache-yourusername` (默认) | 否       | 是       |

## 设置说明

1.  **获取 Spotify API 凭据**:
    * 访问 Spotify Developer Dashboard: [https://developer.spotify.com/dashboard/](https://developer.spotify.com/dashboard/)
    * 登录并创建一个新的应用程序。
    * 记下 `Client ID` 和 `Client Secret`。
    * 在应用的设置中，添加一个 `Redirect URI`。这个 URI **必须**与您在 `.env` 文件中为 `SPOTIPY_REDIRECT_URI` 设置的值完全匹配。对于本地 CLI 工具，`http://localhost:8888/callback` 或 `http://localhost/callback` 是常用选项。

2.  **创建 `.env` 文件**:
    * 在项目根目录下，复制 `env.example` 文件并将其重命名为 `.env`。
    * 编辑 `.env` 文件，填入您从 Spotify Developer Dashboard 获取的 `SPOTIPY_CLIENT_ID`, `SPOTIPY_CLIENT_SECRET`, 和您选择并配置的 `SPOTIPY_REDIRECT_URI`。

    **.env 文件示例内容:**
    ```dotenv
    SPOTIPY_CLIENT_ID='YOUR_SPOTIFY_CLIENT_ID'
    SPOTIPY_CLIENT_SECRET='YOUR_SPOTIFY_CLIENT_SECRET'
    SPOTIPY_REDIRECT_URI='http://localhost:8888/callback'
    # LOG_LEVEL='DEBUG' # 可选
    ```

## 注意事项

* **安全**: `.env` 文件包含敏感的 API 凭据，**绝不能**将其提交到公共代码仓库 (如 GitHub)。确保 `.env` 文件已被添加到 `.gitignore` 文件中。
* **一致性**: `SPOTIPY_REDIRECT_URI` 的值必须在您的 Spotify 应用设置和 `.env` 文件中完全一致，否则 OAuth 认证流程将会失败。
* **令牌缓存**: `spotipy` 库会自动处理 OAuth 令牌的获取和缓存 (通常在用户主目录下的 `.cache-你的用户名` 文件，或由 `SPOTIPY_CACHE_PATH` 指定的路径)。这个缓存文件使得用户在后续运行脚本时无需每次都重新授权，除非令牌过期或权限范围发生变化。这个缓存文件也应被视为敏感信息。

## 变更日志

| 变更描述             | 日期       | 版本 | 作者        |
| -------------------- | ---------- | ---- | ----------- |
| 初稿 - Spotify-only | 2025-05-17 | 0.1  | 3-Architect |
| ...                  | ...        | ...  | ...         |