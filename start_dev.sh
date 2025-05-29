#!/bin/bash

echo "正在启动Spotify歌单导入工具开发环境..."
echo

# 检查是否存在.env文件
if [ ! -f ".env" ]; then
    echo "未找到.env文件。正在创建..."
    python -m spotify_playlist_importer.create_env
    if [ $? -ne 0 ]; then
        echo "创建.env文件失败，请手动创建。"
        exit 1
    fi
fi

echo
echo "正在启动后端API服务器..."
python -m spotify_playlist_importer.api.run_api &
API_PID=$!

echo
echo "正在启动前端开发服务器..."
cd frontend
npm run dev &
FRONTEND_PID=$!

echo
echo "开发环境已启动!"
echo "后端API: http://127.0.0.1:8888"
echo "前端应用: http://localhost:3000"
echo
echo "按Ctrl+C停止所有服务"

# 设置陷阱以捕获SIGINT (Ctrl+C) 并清理子进程
trap "kill $API_PID $FRONTEND_PID; exit" INT

# 等待直到用户按下Ctrl+C
wait 