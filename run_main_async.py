#!/usr/bin/env python3
import os
import sys
import subprocess

# 设置 Spotify API 所需的环境变量
os.environ["SPOTIPY_CLIENT_ID"] = "d76bf1bba8174e4c9ac28dc3404bd8ac"
os.environ["SPOTIPY_CLIENT_SECRET"] = "0b11ec134c984fae883bb1fd966d8ed2"
os.environ["SPOTIPY_REDIRECT_URI"] = "http://127.0.0.1:8888/callback"

print("已设置 Spotify API 环境变量:")
print(f"SPOTIPY_CLIENT_ID: {os.environ.get('SPOTIPY_CLIENT_ID')}")
print(f"SPOTIPY_CLIENT_SECRET: {os.environ.get('SPOTIPY_CLIENT_SECRET')}")
print(f"SPOTIPY_REDIRECT_URI: {os.environ.get('SPOTIPY_REDIRECT_URI')}")

# 构建命令行参数
cmd = ["python", "-m", "spotify_playlist_importer.main_async"]
cmd.extend(sys.argv[1:])  # 添加所有传递给此脚本的参数

print(f"执行命令: {' '.join(cmd)}")

# 执行命令
try:
    result = subprocess.run(cmd, check=True)
    sys.exit(result.returncode)
except subprocess.CalledProcessError as e:
    print(f"执行失败，错误码: {e.returncode}")
    sys.exit(e.returncode)
except Exception as e:
    print(f"发生错误: {e}")
    sys.exit(1) 