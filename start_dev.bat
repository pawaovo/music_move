@echo off
echo 正在启动Spotify歌单导入工具开发环境...
echo.

REM 检查是否存在.env文件
if not exist .env (
    echo 未找到.env文件。正在创建...
    python -m spotify_playlist_importer.create_env
    if errorlevel 1 (
        echo 创建.env文件失败，请手动创建。
        pause
        exit /b 1
    )
)

echo.
echo 正在启动后端API服务器...
start cmd /k "python -m spotify_playlist_importer.api.run_api"

echo.
echo 正在启动前端开发服务器...
cd frontend
start cmd /k "npm run dev"

echo.
echo 开发环境已启动!
echo 后端API: http://127.0.0.1:8888
echo 前端应用: http://localhost:3000
echo.
echo 按任意键退出此窗口（服务器将继续在后台运行）
pause > nul 