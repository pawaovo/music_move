#!/usr/bin/env python3
import os
import logging
from dotenv import load_dotenv, set_key
import pathlib

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """更新.env文件，添加SPOTIPY_CLIENT_ID、SPOTIPY_CLIENT_SECRET和SPOTIPY_REDIRECT_URI环境变量"""
    env_path = pathlib.Path("D:/ai/music_move/.env")
    
    if not env_path.exists():
        logger.error(f"找不到环境变量文件: {env_path}")
        return
        
    # 加载环境变量
    load_dotenv(dotenv_path=env_path)
    logger.info(f"已加载环境变量文件: {env_path}")
    
    # 获取当前变量值
    spotify_client_id = os.environ.get('SPOTIFY_CLIENT_ID')
    spotify_client_secret = os.environ.get('SPOTIFY_CLIENT_SECRET')
    
    if not spotify_client_id or not spotify_client_secret:
        logger.error("未找到SPOTIFY_CLIENT_ID或SPOTIFY_CLIENT_SECRET环境变量")
        return
    
    # 写入SPOTIPY_CLIENT_ID和SPOTIPY_CLIENT_SECRET
    logger.info("正在添加SPOTIPY_CLIENT_ID和SPOTIPY_CLIENT_SECRET环境变量...")
    set_key(env_path, "SPOTIPY_CLIENT_ID", spotify_client_id)
    set_key(env_path, "SPOTIPY_CLIENT_SECRET", spotify_client_secret)
    
    # 添加SPOTIPY_REDIRECT_URI (如果需要)
    # Spotify API要求的重定向URI，使用默认值"http://localhost:8888/callback"
    spotipy_redirect_uri = "http://localhost:8888/callback"
    logger.info(f"正在添加SPOTIPY_REDIRECT_URI环境变量: {spotipy_redirect_uri}")
    set_key(env_path, "SPOTIPY_REDIRECT_URI", spotipy_redirect_uri)
    
    logger.info("环境变量已更新，现在可以重新运行spotify_playlist_importer了")
    logger.info(f"SPOTIFY_CLIENT_ID: {spotify_client_id} -> SPOTIPY_CLIENT_ID")
    logger.info(f"SPOTIFY_CLIENT_SECRET: {spotify_client_secret} -> SPOTIPY_CLIENT_SECRET")
    logger.info(f"SPOTIPY_REDIRECT_URI: {spotipy_redirect_uri}")

# 设置 Spotify API 凭据
os.environ["SPOTIPY_CLIENT_ID"] = "d76bf1bba8174e4c9ac28dc3404bd8ac"
os.environ["SPOTIPY_CLIENT_SECRET"] = "0b11ec134c984fae883bb1fd966d8ed2"
os.environ["SPOTIPY_REDIRECT_URI"] = "http://127.0.0.1:8888/callback"

print("已设置 Spotify API 环境变量")
print(f"SPOTIPY_CLIENT_ID: {os.environ.get('SPOTIPY_CLIENT_ID')}")
print(f"SPOTIPY_CLIENT_SECRET: {os.environ.get('SPOTIPY_CLIENT_SECRET')}")
print(f"SPOTIPY_REDIRECT_URI: {os.environ.get('SPOTIPY_REDIRECT_URI')}")

if __name__ == "__main__":
    main() 