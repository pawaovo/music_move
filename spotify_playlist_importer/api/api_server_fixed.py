"""
Spotify Playlist Importer API服务器 (修复版)

提供Spotify播放列表导入服务的API接口。
"""
import os
import logging
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from fastapi import status
from starlette.middleware.base import BaseHTTPMiddleware

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("spotify-playlist-importer-api")

# 环境变量配置
FRONTEND_URL = os.environ.get("FRONTEND_URL", "https://music-move.vercel.app")
BACKEND_URL = os.environ.get("BACKEND_URL", "https://music-move.onrender.com")

# 记录URL配置
logger.info(f"前端URL: {FRONTEND_URL}")
logger.info(f"后端URL: {BACKEND_URL}")

# 创建FastAPI应用
app = FastAPI(
    title="Spotify Playlist Importer API",
    description="Spotify播放列表导入工具API",
    version="1.0.0"
)

# 自定义中间件，处理CORS预检请求
class PreflightCORSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method == "OPTIONS":
            logger.info(f"处理预检请求: {request.url.path}")
            
            # 获取请求头中的Origin
            origin = request.headers.get("Origin", "")
            logger.info(f"预检请求来源: {origin}")
            
            # 当使用credentials=true时，不能使用*作为Allow-Origin
            # 必须明确指定Origin，或者根据请求中的Origin头动态设置
            allow_origin = origin if origin else "null"
            
            # 返回预检响应
            response = Response(
                status_code=200,
                headers={
                    "Access-Control-Allow-Origin": allow_origin,
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With, Cookie",
                    "Access-Control-Allow-Credentials": "true",
                    "Access-Control-Max-Age": "3600",
                    "Vary": "Origin",  # 添加Vary头，告诉缓存根据Origin变化
                }
            )
            logger.info(f"返回预检响应，允许来源: {allow_origin}")
            return response
            
        # 处理非预检请求
        return await call_next(request)

# 添加自定义中间件
app.add_middleware(PreflightCORSMiddleware)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://music-move.vercel.app",
        "http://localhost:3000",
        "https://music-move.onrender.com",
        # 添加任何其他前端URL
    ],
    allow_credentials=True,  # 允许跨域请求携带凭据（Cookie）
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,  # 预检请求缓存时间
)

# 导入路由
from .routes_fixed import router as spotify_router

# 注册路由
app.include_router(spotify_router)

# 根路径重定向
@app.get("/")
async def root():
    return {"message": "欢迎使用Spotify Playlist Importer API", "docs": "/docs"}

# 添加健康检查端点
@app.get("/health")
async def health_check():
    """健康检查端点，用于Render平台的健康检查"""
    return {"status": "ok", "message": "服务正常运行"}

# 直接在app上注册/callback路由，不通过router
@app.get("/callback")
async def spotify_callback_root(request: Request, response: Response):
    """处理Spotify OAuth回调，然后重定向到前端的成功或失败页面。
    
    这个路由直接注册在主应用上，不通过router，用于处理Spotify回调。
    功能与/api/callback完全一致。
    """
    # 使用环境变量中的前端URL
    frontend_url = FRONTEND_URL
    
    query_params = request.query_params
    code = query_params.get("code")
    error = query_params.get("error")
    state = query_params.get("state")

    logger.info(f"收到OAuth回调: code={code}, error={error}, state={state}")

    # 关键：从 state 参数中恢复 session_id
    session_id = state 
    if not session_id:
        logger.error("回调中缺少 state (session_id)")
        # 如果缺少state参数，生成一个新的session_id
        import uuid
        session_id = str(uuid.uuid4())
        logger.info(f"生成新的会话ID: {session_id}")

    logger.info(f"处理回调，会话ID: {session_id}")

    if error:
        logger.error(f"Spotify授权错误: {error}, 会话ID: {session_id}")
        # 使用URL安全的方式处理错误消息
        safe_error_message = "授权失败"
        try:
            # 尝试使用错误消息，但确保URL安全
            safe_error_message = error.encode('ascii', 'ignore').decode('ascii')
        except:
            pass
        # 重定向到前端错误页面，并附带错误信息
        redirect_response = Response(
            status_code=status.HTTP_302_FOUND,
            headers={"Location": f"{frontend_url}/spotify-auth-error?message={safe_error_message}"}
        )
        
        # 设置会话Cookie
        redirect_response.set_cookie(
            key="spotify_session_id",
            value=session_id,
            max_age=60 * 60 * 24 * 30,  # 30天
            httponly=True,
            samesite="none",  # 允许跨站请求
            secure=True,      # 只在HTTPS连接中发送
            domain=""       # 不限制域名，这样可以在任何域名下使用Cookie
        )
        
        return redirect_response

    if not code:
        logger.error(f"回调中缺少授权码, 会话ID: {session_id}")
        # 重定向到前端错误页面
        redirect_response = Response(
            status_code=status.HTTP_302_FOUND,
            headers={"Location": f"{frontend_url}/spotify-auth-error?message=missing_code"}
        )
        
        # 设置会话Cookie
        redirect_response.set_cookie(
            key="spotify_session_id",
            value=session_id,
            max_age=60 * 60 * 24 * 30,  # 30天
            httponly=True,
            samesite="none",  # 允许跨站请求
            secure=True,      # 只在HTTPS连接中发送
            domain=""       # 不限制域名，这样可以在任何域名下使用Cookie
        )
        
        return redirect_response

    try:
        from spotify.client_manager import get_auth_manager
        auth_manager = get_auth_manager(session_id=session_id)
        logger.info(f"为会话 {session_id} 获取到 auth_manager，准备交换令牌")
        
        # 使用授权码获取访问令牌
        token_info = auth_manager.get_access_token(code, as_dict=True, check_cache=False)
        
        if not token_info or "access_token" not in token_info:
            logger.error(f"未能从Spotify获取有效的令牌信息, 会话ID: {session_id}, 令牌信息: {token_info}")
            # 重定向到前端错误页面
            redirect_response = Response(
                status_code=status.HTTP_302_FOUND,
                headers={"Location": f"{frontend_url}/spotify-auth-error?message=token_exchange_failed"}
            )
            
            # 设置会话Cookie
            redirect_response.set_cookie(
                key="spotify_session_id",
                value=session_id,
                max_age=60 * 60 * 24 * 30,  # 30天
                httponly=True,
                samesite="none",  # 允许跨站请求
                secure=True,      # 只在HTTPS连接中发送
                domain=""       # 不限制域名，这样可以在任何域名下使用Cookie
            )
            
            return redirect_response

        logger.info(f"成功获取并缓存了访问令牌, 会话ID: {session_id}")
        
        # 设置会话Cookie，确保客户端能够识别会话
        redirect_response = Response(
            status_code=status.HTTP_302_FOUND,
            headers={"Location": f"{frontend_url}/spotify-auth-success?status=true"}
        )
        
        # 设置会话Cookie
        redirect_response.set_cookie(
            key="spotify_session_id",
            value=session_id,
            max_age=60 * 60 * 24 * 30,  # 30天
            httponly=True,
            samesite="none",  # 允许跨站请求
            secure=True,      # 只在HTTPS连接中发送
            domain=""       # 不限制域名，这样可以在任何域名下使用Cookie
        )
        
        return redirect_response

    except Exception as e:
        logger.exception(f"处理Spotify回调时出错: {e}, 会话ID: {session_id}")
        # 重定向到前端错误页面，并附带一般错误信息
        redirect_response = Response(
            status_code=status.HTTP_302_FOUND,
            headers={"Location": f"{frontend_url}/spotify-auth-error?message=internal_error"}
        )
        
        # 设置会话Cookie
        redirect_response.set_cookie(
            key="spotify_session_id",
            value=session_id,
            max_age=60 * 60 * 24 * 30,  # 30天
            httponly=True,
            samesite="none",  # 允许跨站请求
            secure=True,      # 只在HTTPS连接中发送
            domain=""       # 不限制域名，这样可以在任何域名下使用Cookie
        )
        
        return redirect_response

# 异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"全局异常: {exc}")
    return {"status": "error", "message": str(exc)}

# 启动函数
def start(host="0.0.0.0", port=8888, reload=False):
    """启动API服务器"""
    logger.info(f"启动API服务器: {host}:{port}")
    uvicorn.run(
        "api.api_server_fixed:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    ) 