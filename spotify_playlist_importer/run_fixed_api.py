#!/usr/bin/env python
"""
Spotify Playlist Importer API服务器启动脚本 (修复版)

该脚本用于启动修复版FastAPI服务器，提供Spotify Playlist Importer的API接口。
"""
import os
import sys
import logging
import uvicorn
from dotenv import load_dotenv

# 尝试加载.env文件中的环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("spotify-playlist-importer-api")

# 获取当前脚本所在目录的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))

# 将当前目录添加到Python路径
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 设置环境变量 - 如果未在.env中设置，则使用默认值
if "SPOTIFY_AUTH_CACHE_PATH" not in os.environ:
    os.environ["SPOTIFY_AUTH_CACHE_PATH"] = ".spotify_cache"

if "FRONTEND_URL" not in os.environ:
    os.environ["FRONTEND_URL"] = "http://localhost:3000"

if "ALLOWED_ORIGINS" not in os.environ:
    os.environ["ALLOWED_ORIGINS"] = "http://localhost:3000,http://127.0.0.1:3000"

# 检查必要的Spotify API凭据是否存在
required_vars = ["SPOTIPY_CLIENT_ID", "SPOTIPY_CLIENT_SECRET", "SPOTIPY_REDIRECT_URI"]
missing_vars = [var for var in required_vars if not os.environ.get(var)]

if missing_vars:
    logger.error(f"缺少必要的环境变量: {', '.join(missing_vars)}")
    logger.error("请创建.env文件并设置这些环境变量，或使用命令行导出它们")
    logger.error("参考.env.example文件获取所需的环境变量列表")
    sys.exit(1)

# 打印环境变量以便调试（注意隐藏敏感信息）
logger.info("Spotify API 环境变量设置:")
logger.info(f"SPOTIPY_CLIENT_ID: {'设置完成' if os.environ.get('SPOTIPY_CLIENT_ID') else '未设置'}")
logger.info(f"SPOTIPY_CLIENT_SECRET: {'设置完成' if os.environ.get('SPOTIPY_CLIENT_SECRET') else '未设置'}")
logger.info(f"SPOTIPY_REDIRECT_URI: {os.environ.get('SPOTIPY_REDIRECT_URI')}")

# 打印Python路径以便调试
logger.info("Python模块搜索路径:")
for path in sys.path:
    logger.info(f"  - {path}")

# 获取服务器配置
host = os.environ.get("API_HOST", "0.0.0.0")
port = int(os.environ.get("PORT", os.environ.get("API_PORT", "8888")))
debug = os.environ.get("API_DEBUG", "").lower() in ("true", "1", "yes")

logger.info("正在启动API服务器...")
logger.info(f"服务器将在 http://{host}:{port} 上运行")
logger.info(f"前端URL: {os.environ['FRONTEND_URL']}")
logger.info(f"允许的CORS来源: {os.environ['ALLOWED_ORIGINS']}")
logger.info(f"调试模式: {'启用' if debug else '禁用'}")

# 直接使用uvicorn启动服务器
if __name__ == "__main__":
    try:
        uvicorn.run(
            "api.api_server_fixed:app",
            host=host,
            port=port,
            reload=debug,
            log_level="info" if not debug else "debug"
        )
    except Exception as e:
        logger.error(f"启动API服务器时出错: {e}")
        sys.exit(1) 