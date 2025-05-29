"""
API路由定义模块 (修复版)

包含所有API端点的路由定义和处理逻辑。
使用相对导入而不是绝对导入。
"""
from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks, Header, Cookie, Request, Response
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Union
import logging
import asyncio
import json
import sys
import os
import uuid

# 新增导入 (从旧的 routes.py 迁移)
from spotify_playlist_importer.core.models import ParsedSong, MatchedSong # 假设这些模型定义存在且路径正确
from spotify_playlist_importer.utils.text_normalizer import TextNormalizer # 假设TextNormalizer存在且路径正确
from spotify_playlist_importer.spotify.sync_client import (
    search_song_on_spotify_sync_wrapped,
    create_spotify_playlist_sync_wrapped, # 虽然此端点不直接用，但为了完整性可以保留或按需移除
    add_tracks_to_spotify_playlist_sync_wrapped, # 同上
    create_concurrency_limiter
) # 假设这些函数存在且路径正确
from spotify_playlist_importer.core.optimized_batch_processor import process_song_list_file # 假设此函数存在且路径正确

# 从 client_manager 导入 (需要确保这个路径在修复后是正确的)
# 假设 client_manager 在 spotify_playlist_importer/spotify/client_manager.py
# 我们将在启动脚本中确保 spotify_playlist_importer 在 sys.path 中
from spotify.client_manager import get_auth_manager, get_project_spotify_client # 确保 get_project_spotify_client 也导入

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("spotify-playlist-importer-api")

# 创建API路由器
router = APIRouter(prefix="/api", tags=["spotify", "auth"])

# 定义认证相关的常量 (从 auth_routes.py 复制)
SESSION_COOKIE_NAME = "spotify_session_id"
SESSION_COOKIE_MAX_AGE = 60 * 60 * 24 * 30  # 30天

# 新增请求模型定义 (从旧的 routes.py 迁移)
class ProcessSongsRequest(BaseModel):
    song_list: str = Field(..., description="每行一首歌曲的列表")
    concurrency: int = Field(15, description="API请求并发数", ge=1, le=20) # 增加默认并发数
    batch_size: int = Field(30, description="批处理大小", ge=1, le=50) # 增加默认批处理大小

class CreatePlaylistRequest(BaseModel):
    name: str = Field(..., description="播放列表名称")
    description: str = Field("", description="播放列表描述")
    public: bool = Field(False, description="是否公开")
    uris: List[str] = Field(..., description="Spotify曲目URI列表")

# 获取或创建会话ID (从 auth_routes.py 复制)
async def get_or_create_session_id(
    request: Request,
    response: Response,
    session_id: Optional[str] = Cookie(None, alias=SESSION_COOKIE_NAME)
) -> str:
    if not session_id:
        session_id = str(uuid.uuid4())
        logger.info(f"为用户创建新的会话ID: {session_id}")
        # 在这里设置cookie
        response.set_cookie(
            key=SESSION_COOKIE_NAME,
            value=session_id,
            max_age=SESSION_COOKIE_MAX_AGE,
            httponly=True,
            samesite="none",  # 允许跨站请求
            secure=True,      # 只在HTTPS连接中发送
            domain=None       # 使用当前域名
        )
    return session_id

# 定义简单的健康检查端点
@router.get("/health")
async def health_check():
    """API健康检查端点"""
    return {"status": "ok", "message": "API服务器正常运行"}

# 定义状态端点
@router.get("/status")
async def api_status():
    """API状态端点"""
    return {
        "status": "ok",
        "version": "1.0.0",
        "endpoints": [
            {"path": "/api/health", "method": "GET", "description": "健康检查"},
            {"path": "/api/status", "method": "GET", "description": "API状态"}
        ]
    }

@router.get("/auth-status")
async def auth_status(
    request: Request,
    response: Response,
    session_id: str = Depends(get_or_create_session_id)
):
    """检查用户的Spotify认证状态
    
    返回用户是否已认证以及用户信息（如果已认证）
    """
    logger.info(f"检查认证状态，会话ID: {session_id}")
    
    # 确保响应总是包含会话cookie
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=session_id,
        max_age=SESSION_COOKIE_MAX_AGE,
        httponly=True,
        samesite="none",  # 允许跨站请求
        secure=True,      # 只在HTTPS连接中发送
        domain=None       # 使用当前域名
    )
    
    try:
        # 获取认证管理器
        auth_manager = get_auth_manager(session_id=session_id)
        
        # 检查是否有有效的令牌
        if auth_manager.validate_token(auth_manager.get_cached_token()):
            # 获取用户信息
            try:
                # 创建Spotify客户端
                import spotipy
                sp = spotipy.Spotify(auth_manager=auth_manager)
                
                # 获取用户信息
                user_info = sp.current_user()
                logger.info(f"成功获取用户信息，会话ID: {session_id}")
                
                return {
                    "is_authenticated": True,
                    "user_info": {
                        "id": user_info.get("id"),
                        "display_name": user_info.get("display_name"),
                        "email": user_info.get("email"),
                        "images": user_info.get("images", [])
                    }
                }
            except Exception as e:
                logger.error(f"获取用户信息失败: {e}, 会话ID: {session_id}")
                return {
                    "is_authenticated": False,
                    "user": None,
                    "message": f"获取用户信息失败: {str(e)}"
                }
        else:
            logger.info(f"用户未认证或令牌无效，会话ID: {session_id}")
            return {
                "is_authenticated": False,
                "user": None,
                "message": "用户未认证或令牌无效"
            }
    except Exception as e:
        logger.exception(f"检查认证状态时出错: {e}, 会话ID: {session_id}")
        return {
            "is_authenticated": False,
            "user": None,
            "message": f"检查认证状态时出错: {str(e)}"
        }

@router.get("/auth-url")
async def get_spotify_auth_url(
    request: Request,
    response: Response,
    session_id: str = Depends(get_or_create_session_id)
):
    """获取Spotify授权URL端点 (使用真实逻辑)
    
    返回用户需要访问的Spotify授权URL，用于启动OAuth流程。
    确保授权URL包含所有必要的权限范围，以支持后续操作。
    """
    logger.info(f"收到获取认证URL请求，会话ID: {session_id}")
    
    # 确保响应总是包含会话cookie
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=session_id,
        max_age=SESSION_COOKIE_MAX_AGE,
        httponly=True,
        samesite="none",  # 允许跨站请求
        secure=True,      # 只在HTTPS连接中发送
        domain=None       # 使用当前域名
    )
    
    try:
        # 使用会话ID创建认证管理器
        # 假设 get_auth_manager 能够处理 session_id 并返回配置好的 SpotifyOAuth 实例
        auth_manager = get_auth_manager(session_id=session_id) 
        
        # 生成授权URL，并将session_id作为state参数
        # 修改: 显式传递state参数，确保与session_id匹配
        auth_url = auth_manager.get_authorize_url(state=session_id)
        
        logger.info(f"生成的授权URL (会话: {session_id}): {auth_url}")
        
        # 确保返回的是Spotify登录页面URL
        if not auth_url or not auth_url.startswith('https://accounts.spotify.com/'):
            logger.error(f"生成的授权URL无效: {auth_url}，会话ID: {session_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="无法生成有效的Spotify授权URL"
            )
            
        return {"auth_url": auth_url}
    
    except Exception as e:
        logger.exception(f"获取授权URL时出错: {e}，会话ID: {session_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取授权URL时出错: {str(e)}"
        )

@router.get("/callback") # 和 Spotify 应用设置中的 Redirect URI 匹配
async def spotify_callback(
    request: Request, # 需要 Request 对象来获取查询参数
    response: Response # 需要 Response 对象来返回重定向
):
    """处理Spotify OAuth回调，然后重定向到前端的成功或失败页面。
    
    This endpoint is called by Spotify after user authorization.
    It processes the authorization code and redirects to the frontend.
    """
    # 获取前端URL（从环境变量中获取，默认为localhost:3000）
    frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:3000")
    
    query_params = request.query_params
    code = query_params.get("code")
    error = query_params.get("error")
    state = query_params.get("state")  # 这里的state应该包含session_id

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
            key=SESSION_COOKIE_NAME,
            value=session_id,
            max_age=SESSION_COOKIE_MAX_AGE,
            httponly=True,
            samesite="none",  # 允许跨站请求
            secure=True,      # 只在HTTPS连接中发送
            domain=None       # 使用当前域名
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
            key=SESSION_COOKIE_NAME,
            value=session_id,
            max_age=SESSION_COOKIE_MAX_AGE,
            httponly=True,
            samesite="none",  # 允许跨站请求
            secure=True,      # 只在HTTPS连接中发送
            domain=None       # 使用当前域名
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
                key=SESSION_COOKIE_NAME,
                value=session_id,
                max_age=SESSION_COOKIE_MAX_AGE,
                httponly=True,
                samesite="none",  # 允许跨站请求
                secure=True,      # 只在HTTPS连接中发送
                domain=None       # 使用当前域名
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
            key=SESSION_COOKIE_NAME,
            value=session_id,
            max_age=SESSION_COOKIE_MAX_AGE,
            httponly=True,
            samesite="none",  # 允许跨站请求
            secure=True,      # 只在HTTPS连接中发送
            domain=None       # 使用当前域名
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
            key=SESSION_COOKIE_NAME,
            value=session_id,
            max_age=SESSION_COOKIE_MAX_AGE,
            httponly=True,
            samesite="none",  # 允许跨站请求
            secure=True,      # 只在HTTPS连接中发送
            domain=None       # 使用当前域名
        )
        
        return redirect_response

# 添加直接的/callback路由
@router.get("/callback")
async def spotify_callback_direct(request: Request, response: Response):
    """直接处理Spotify OAuth回调，然后重定向到前端的成功或失败页面。
    
    这是一个额外的路由，专门用于处理Spotify Developer Dashboard中配置的重定向URI。
    功能与/api/callback完全一致，只是路径不同。
    """
    return await spotify_callback(request, response)

# 实际项目中，在修复模块导入问题后，可以再添加其他复杂端点 

# --- 开始添加 /api/process-songs 端点 ---
@router.post("/process-songs", summary="处理歌曲列表并搜索匹配项 (项目凭证)")
async def process_songs_endpoint(
    request_data: ProcessSongsRequest,
    request: Request,
    response: Response,
    session_id: str = Depends(get_or_create_session_id)
):
    # 确保响应总是包含会话cookie
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=session_id,
        max_age=SESSION_COOKIE_MAX_AGE,
        httponly=True,
        samesite="none",  # 允许跨站请求
        secure=True,      # 只在HTTPS连接中发送
        domain=None       # 使用当前域名
    )
    
    try:
        logger.info(f"收到处理歌曲列表请求，歌曲数量: {len(request_data.song_list.splitlines())}")
        
        spotify_client = get_project_spotify_client()
        if not spotify_client:
            logger.error("无法获取项目级别的Spotify客户端")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Spotify服务暂时不可用 (无法获取项目客户端)"
            )

        normalizer = TextNormalizer()
        semaphore = create_concurrency_limiter(request_data.concurrency)
        
        import tempfile
        temp_file_path = None
        try:
            # Ensure tempfile.NamedTemporaryFile is handled correctly for async context if necessary,
            # though for simple write and path usage, it might be fine.
            with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt", encoding="utf-8") as temp_file:
                temp_file.write(request_data.song_list)
                temp_file_path = temp_file.name
            
            successfully_matched_songs = []
            unmatched_songs = []  # 新增：存储未匹配歌曲信息
            # 添加集合用于跟踪已匹配的Spotify曲目URI，防止重复
            matched_uris = set()
            
            async def search_func_wrapper(parsed_song: ParsedSong):
                return await search_song_on_spotify_sync_wrapped(
                    parsed_song,
                    semaphore=semaphore,
                    spotify_client=spotify_client
                )
            
            async def on_song_result_wrapper(original_line, title, artists, norm_title, norm_artists, search_result):
                if search_result:
                    # 检查是否已有相同URI的曲目，避免重复
                    if search_result.uri not in matched_uris:
                        matched_uris.add(search_result.uri)
                        successfully_matched_songs.append(search_result)
                    else:
                        logger.warning(f"发现重复曲目，已跳过: {search_result.name} - {', '.join(search_result.artists)}, URI: {search_result.uri}")
                else:
                    # 新增：记录未匹配歌曲信息
                    unmatched_songs.append({
                        "original_input": original_line,
                        "title": title,
                        "artists": artists,
                        "reason": "未找到匹配的歌曲"
                    })
            
            # Ensure process_song_list_file is truly async or run it in a thread pool executor
            # if it's a blocking IO-bound operation.
            # For now, assuming it's awaitable as in the original code.
            total, matched, failed = await process_song_list_file(
                file_path=temp_file_path,
                normalizer=normalizer,
                spotify_search_func=search_func_wrapper,
                on_result_callback=on_song_result_wrapper,
                batch_size=request_data.batch_size,
                max_concurrency=request_data.concurrency
            )
            
        finally:
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except Exception as e_unlink:
                    logger.error(f"删除临时文件失败 {temp_file_path}: {e_unlink}")
        
        response_data = {
            "total_songs": total,
            "matched_songs": [
                {
                    "original_input": song.original_line,
                    "spotify_id": song.spotify_id,
                    "spotify_uri": song.uri,
                    "title": song.name,
                    "artists": song.artists,
                    "matched_score": song.matched_score,
                    "is_low_confidence": song.is_low_confidence,
                    "album": song.album_name,
                    "album_image_url": song.album_image_urls[0] if song.album_image_urls else None
                }
                for song in successfully_matched_songs
            ],
            "unmatched_songs": unmatched_songs,  # 新增：添加未匹配歌曲信息
            "unmatched_songs_count": failed,
        }
        
        logger.info(f"歌曲处理完成，总数: {total}，匹配: {matched}，失败: {failed}，去重后匹配: {len(successfully_matched_songs)}")
        
        return {
            "status": "success",
            "message": f"已处理 {total} 首歌曲，成功匹配 {len(successfully_matched_songs)} 首，失败 {failed} 首",
            "data": response_data
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"处理歌曲列表时发生内部错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"处理歌曲时发生内部错误: {str(e)}"
        )
# --- 结束添加 /api/process-songs 端点 ---

# --- 开始添加 /api/create-playlist 端点 ---
@router.post("/create-playlist", summary="创建Spotify播放列表并添加歌曲 (用户授权)")
async def create_playlist_endpoint(
    request_data: CreatePlaylistRequest,
    request: Request,
    response: Response,
    session_id: str = Depends(get_or_create_session_id)
):
    # 确保响应总是包含会话cookie
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=session_id,
        max_age=SESSION_COOKIE_MAX_AGE,
        httponly=True,
        samesite="none",  # 允许跨站请求
        secure=True,      # 只在HTTPS连接中发送
        domain=None       # 使用当前域名
    )
    
    logger.info(f"收到创建播放列表请求，播放列表名称: {request_data.name}，歌曲数量: {len(request_data.uris)}")
    logger.info(f"播放列表描述: '{request_data.description}'，是否公开: {request_data.public}")
    
    # 检查用户是否已授权
    auth_manager = get_auth_manager(session_id=session_id)
    if not auth_manager or not auth_manager.validate_token(auth_manager.get_cached_token()):
        logger.warning(f"未授权的播放列表创建请求，会话ID: {session_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户未授权，请先完成Spotify登录"
        )
    
    try:
        # 获取用户Spotify客户端
        import spotipy
        spotify_client = spotipy.Spotify(auth_manager=auth_manager)
        
        # 创建并发限制器
        semaphore = create_concurrency_limiter(5)
        
        # 创建播放列表
        logger.info(f"开始创建播放列表: {request_data.name}, 描述: '{request_data.description}'")
        playlist_id, playlist_url, error = await create_spotify_playlist_sync_wrapped(
            playlist_name=request_data.name,
            is_public=request_data.public,
            playlist_description=request_data.description,
            semaphore=semaphore,
            spotify_client=spotify_client
        )
        
        if error:
            logger.error(f"创建播放列表失败: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"创建播放列表失败: {error}"
            )
        
        logger.info(f"播放列表创建成功，ID: {playlist_id}，准备添加歌曲")
        
        # 添加歌曲到播放列表
        success, added_tracks, failed_tracks, error = await add_tracks_to_spotify_playlist_sync_wrapped(
            playlist_id=playlist_id,
            track_uris=request_data.uris,
            semaphore=semaphore,
            spotify_client=spotify_client
        )
        
        if not success:
            logger.error(f"向播放列表添加歌曲失败: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"向播放列表添加歌曲失败: {error}"
            )
        
        logger.info(f"成功添加歌曲，添加: {added_tracks}，失败: {failed_tracks}")
        
        # 返回成功响应
        return {
            "status": "success",
            "message": f"已成功创建播放列表并添加 {added_tracks} 首歌曲",
            "data": {
                "playlist_id": playlist_id,
                "playlist_url": playlist_url,
                "name": request_data.name,
                "added_tracks": added_tracks,
                "failed_tracks": failed_tracks
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"创建播放列表时出错: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建播放列表时出错: {str(e)}"
        )
# --- 结束添加 /api/create-playlist 端点 ---

@router.post("/logout")
async def logout_user(
    request: Request,
    response: Response,
    session_id: str = Depends(get_or_create_session_id)
):
    # 确保删除会话cookie
    response.delete_cookie(key=SESSION_COOKIE_NAME)
    
    logger.info(f"用户请求登出，会话ID: {session_id}")
    
    try:
        # 获取认证管理器
        auth_manager = get_auth_manager(session_id=session_id)
        
        # 尝试清除令牌缓存
        try:
            # 如果缓存中存在令牌文件，尝试清除
            cache_path = auth_manager.cache_handler.cache_path if hasattr(auth_manager, 'cache_handler') else None
            if cache_path and os.path.exists(cache_path):
                logger.info(f"清除令牌缓存文件: {cache_path}")
                # 尝试清除缓存文件内容而不是删除文件
                with open(cache_path, 'w') as f:
                    f.write('{}')
        except Exception as e:
            logger.warning(f"清除令牌缓存失败: {e}，会话ID: {session_id}")
            # 继续处理，不阻止登出流程
        
        return {"status": "success", "message": "用户已成功登出"}
    
    except Exception as e:
        logger.exception(f"登出用户时出错: {e}，会话ID: {session_id}")
        # 即使发生错误，也尝试清除Cookie
        response.delete_cookie(
            key=SESSION_COOKIE_NAME,
            httponly=True,
            samesite="none",  # 允许跨站请求
            secure=True,      # 只在HTTPS连接中发送
            domain=None       # 使用当前域名
        )
        
        # 返回400而不是500，因为前端只需要知道登出操作尝试了，但失败了
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"登出用户时出错: {str(e)}"
        )

# 实际项目中，在修复模块导入问题后，可以再添加其他复杂端点 