# Vercel + Render 部署指南：Next.js 前端与 FastAPI 后端

本文档详细介绍了如何将您的 Next.js 前端应用部署到 Vercel，以及如何将您的 Python FastAPI 后端应用部署到 Render。

## 前提条件

1.  **Git 仓库：** 您的项目代码 (包括前端和后端) 需要托管在 Git 仓库中 (例如 GitHub, GitLab, Bitbucket)。
2.  **账号注册：**
    *   注册 Vercel 账号 ([vercel.com](http://vercel.com))，建议使用您的 GitHub 账号关联登录。
    *   注册 Render 账号 ([render.com](http://render.com))，同样建议使用 GitHub 账号关联。
3.  **Spotify Developer App：** 确保您在 Spotify Developer Dashboard ([developer.spotify.com/dashboard](https://developer.spotify.com/dashboard)) 中有一个配置好的应用，并且拥有 Client ID 和 Client Secret。

---

## 第一部分：部署后端 (Python/FastAPI) 到 Render

1.  **登录 Render 并创建新服务：**
    *   访问 [dashboard.render.com](http://dashboard.render.com)。
    *   点击 "New +"按钮，然后选择 "Web Service"。

2.  **连接 Git 仓库：**
    *   选择 "Build and deploy from a Git repository"。
    *   如果尚未连接，请连接您的 GitHub (或其他 Git 服务商) 账户。
    *   选择包含您项目的仓库。

3.  **配置 Web Service：**
    *   **Name:** 给您的后端服务起一个名字 (例如 `my-music-importer-backend`)。
    *   **Region:** 选择一个区域。
    *   **Branch:** 选择您要部署的分支 (例如 `main`)。
    *   **Root Directory:** 如果您的后端代码在仓库的子目录中 (例如 `spotify_playlist_importer/`)，请在此指定。否则留空。
    *   **Runtime:** 选择 "Python 3"。
    *   **Build Command:** 通常是 `pip install -r requirements.txt`。
    *   **Start Command:** 例如 `gunicorn -w 4 -k uvicorn.workers.UvicornWorker spotify_playlist_importer.api.api_server_fixed:app -b 0.0.0.0:$PORT`。
        *   请根据您的实际 FastAPI 应用实例路径 (`spotify_playlist_importer.api.api_server_fixed:app`) 进行调整。
        *   `$PORT` 是 Render 提供的环境变量。
    *   **Instance Type:** 选择 "Free"。

4.  **添加环境变量：**
    *   在 "Environment" 部分添加以下变量：
        *   `PYTHON_VERSION`: 您项目使用的 Python 版本 (例如 `3.10.7`)。
        *   `SPOTIPY_CLIENT_ID`: 您的 Spotify App Client ID。
        *   `SPOTIPY_CLIENT_SECRET`: 您的 Spotify App Client Secret。
        *   `SPOTIPY_REDIRECT_URI`: **暂时留空或填占位符** (例如 `http://placeholder.com/callback`)。
        *   `FRONTEND_URL`: **暂时留空或填占位符**。
        *   `ALLOWED_ORIGINS`: **暂时留空或填占位符** (例如 `http://localhost:3000`)。
        *   `SPOTIFY_AUTH_CACHE_PATH`: (例如 `.spotify_cache`)。注意免费版 Render 文件系统是临时的。

5.  **高级设置 (可选)：**
    *   **Auto-Deploy:** 建议启用 "Yes"。
    *   **Health Check Path:** 可选，例如 `/health`。

6.  **创建 Web Service：**
    *   点击 "Create Web Service"。
    *   部署成功后，Render 会提供一个 `.onrender.com` 的 URL (例如 `https://my-music-importer-backend.onrender.com`)。**复制此 URL。**

7.  **更新 `SPOTIPY_REDIRECT_URI` 和 Spotify Dashboard：**
    *   回到 Render 后端服务的 "Environment" 设置。
    *   修改 `SPOTIPY_REDIRECT_URI` 为 `{您的Render后端URL}/callback` (例如 `https://my-music-importer-backend.onrender.com/callback`)。确保 `/callback` 与您的 FastAPI 回调路由路径一致。
    *   登录 Spotify Developer Dashboard，将应用的 "Redirect URIs" 设置为相同的 Render 回调 URL。

---

## 第二部分：部署前端 (Next.js) 到 Vercel

1.  **登录 Vercel 并导入项目：**
    *   访问 [vercel.com/dashboard](http://vercel.com/dashboard)。
    *   点击 "Add New..." -> "Project"。
    *   选择您的 Git 仓库。

2.  **配置项目：**
    *   **Project Name:** Vercel 会自动生成，可修改。
    *   **Framework Preset:** 应自动选为 "Next.js"。
    *   **Root Directory:** 如果您的 Next.js 前端代码在仓库的子目录中 (例如 `music_move/`)，请在此指定。否则留空。

3.  **添加环境变量：**
    *   展开 "Environment Variables"。
    *   添加：
        *   `NEXT_PUBLIC_API_URL`: 设置为您的 Render 后端 URL (例如 `https://my-music-importer-backend.onrender.com`)。

4.  **部署：**
    *   点击 "Deploy"。
    *   部署成功后，Vercel 会提供一个 `.vercel.app` 的 URL (例如 `https://my-music-importer.vercel.app`)。**复制此 URL。**

---

## 第三部分：最终配置和测试

1.  **更新 Render 后端环境变量：**
    *   回到 Render 后端服务的 "Environment" 设置。
    *   更新：
        *   `FRONTEND_URL`: 设置为您的 Vercel 前端 URL (例如 `https://my-music-importer.vercel.app`)。
        *   `ALLOWED_ORIGINS`: 添加您的 Vercel 前端 URL。如果已有值，用逗号分隔 (例如 `https://my-music-importer.vercel.app,http://localhost:3000`)。
    *   保存更改，Render 可能会重新部署。

2.  **检查 CORS 配置：**
    *   您的 FastAPI 后端 `CORSMiddleware` 应使用 `ALLOWED_ORIGINS` 环境变量。
    *   代码示例 (`spotify_playlist_importer/api/api_server_fixed.py`):
      ```python
      app.add_middleware(
          CORSMiddleware,
          allow_origins=os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000").split(","),
          allow_credentials=True,
          allow_methods=["*"],
          allow_headers=["*"],
      )
      ```

3.  **确认回调路径：**
    *   您的 FastAPI 回调路径为 `/callback` (基于 `spotify_playlist_importer/api/api_server_fixed.py`中的 `@app.get("/callback")`)。这与 `SPOTIPY_REDIRECT_URI` 中的路径应一致。

4.  **全面测试：**
    *   访问您的 Vercel 前端 URL。
    *   **清除浏览器缓存和 Cookie。**
    *   测试完整的用户流程：Spotify 授权、导入播放列表、歌曲匹配。
    *   检查浏览器开发者工具 ("Console", "Network")、Render 日志和 Vercel 日志。

5.  **处理 `.spotify_cache` 持久化问题：**
    *   Render 免费实例的文件系统是临时的，`.spotify_cache` 会在服务重启/重新部署后丢失，导致用户需要重新授权。
    *   **短期方案：** 接受此行为。
    *   **长期方案 (推荐)：** 修改后端代码，将授权令牌信息存储到持久化存储中 (例如 Render 的免费 PostgreSQL 数据库)。

---

## 总结：重要配置值参考

(请将示例 URL 和值替换为您的实际值)

*   **Render (Backend - `your-backend-name.onrender.com`):**
    *   **Start Command:** `gunicorn -w 4 -k uvicorn.workers.UvicornWorker your_module.path:app -b 0.0.0.0:$PORT`
    *   Env Var `SPOTIPY_CLIENT_ID`: `your_spotify_client_id`
    *   Env Var `SPOTIPY_CLIENT_SECRET`: `your_spotify_client_secret`
    *   Env Var `SPOTIPY_REDIRECT_URI`: `https://your-backend-name.onrender.com/callback`
    *   Env Var `FRONTEND_URL`: `https://your-frontend-name.vercel.app`
    *   Env Var `ALLOWED_ORIGINS`: `https://your-frontend-name.vercel.app`
    *   Env Var `PYTHON_VERSION`: (e.g., `3.10.7`)

*   **Vercel (Frontend - `your-frontend-name.vercel.app`):**
    *   Env Var `NEXT_PUBLIC_API_URL`: `https://your-backend-name.onrender.com`

*   **Spotify Developer Dashboard:**
    *   Redirect URIs: `https://your-backend-name.onrender.com/callback`

---
部署过程中遇到任何问题，请参考各平台的官方文档或寻求社区帮助。 