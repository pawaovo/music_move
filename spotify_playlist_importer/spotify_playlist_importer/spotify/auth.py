import sys
import re
import urllib.error
import os
from pathlib import Path
import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyOauthError
from spotify_playlist_importer.core import config

# 尝试从相对路径导入logger
try:
    from ..utils.logger import get_logger
except ImportError:
    # 如果相对导入失败，则尝试完全路径导入
    try:
        from spotify_playlist_importer.utils.logger import get_logger
    except ImportError:
        # 如果仍然失败，使用标准logging作为备用
        import logging
        get_logger = lambda name: logging.getLogger(name)

# 获取日志器
logger = get_logger(__name__)

"""
Spotify认证模块，处理OAuth 2.0授权流程。

此模块提供了获取已认证的Spotify客户端实例的功能。它利用spotipy库的SpotifyOAuth
实现以处理OAuth 2.0授权码流程(PKCE)，并使用从core.config模块加载的API凭据。

令牌缓存与复用:
------------
spotipy库默认会自动缓存获取的认证令牌到本地文件系统。默认情况下，这个缓存文件
名为.cache或.cache-{username}，存储在程序执行目录中。这意味着：

1. 首次认证成功后，令牌会被缓存到此文件
2. 后续调用get_spotify_client()函数时，如果缓存文件存在且令牌未过期，
   用户无需重新进行浏览器授权
3. 如果令牌已过期但刷新令牌有效，spotipy会自动刷新令牌
4. 仅当缓存文件不存在、被删除或令牌失效(且无法刷新)时，才会触发新的浏览器授权流程

这种缓存机制大大提升了用户体验，避免了每次运行程序时都需要重新授权。

错误处理:
-------
本模块详细处理了认证过程中可能出现的各种错误场景，包括：

1. 用户取消授权：用户在Spotify授权页面点击"取消"或关闭窗口
2. 凭据错误：无效的客户端ID/密钥或回调URI不匹配
3. 网络问题：连接到Spotify服务器时遇到的网络错误
4. 授权后API错误：使用获取的令牌调用API时发生的错误

每种错误都会提供详细的错误信息和可能的解决建议。
"""


def get_spotify_client() -> spotipy.Spotify:
    """
    获取已认证的Spotify客户端实例。
    
    此函数使用从环境变量或.env文件中加载的Spotify API凭据，尝试通过缓存的访问令牌
    或刷新令牌获取Spotify客户端实例。如果缓存的令牌无效，将自动打开浏览器请求用户授权。
    
    Returns:
        spotipy.Spotify: 已认证的Spotify客户端实例
        
    Raises:
        SystemExit: 如果认证失败，函数会向stderr打印错误消息并退出程序
    """
    # Spotify API需要的权限范围
    SPOTIFY_SCOPES = "user-read-private playlist-modify-public playlist-modify-private"
    
    try:
        # 使用简单的缓存路径减少初始化延迟
        cache_path = ".spotify_cache"
        
        logger.debug("正在创建SpotifyOAuth认证管理器...")
        print("\n==== Spotify认证开始 ====")
        
        # 创建SpotifyOAuth管理器，启用自动浏览器打开
        auth_manager = SpotifyOAuth(
            client_id=config.SPOTIPY_CLIENT_ID,
            client_secret=config.SPOTIPY_CLIENT_SECRET,
            redirect_uri=config.SPOTIPY_REDIRECT_URI,
            scope=SPOTIFY_SCOPES,
            open_browser=True,  # 自动打开浏览器
            cache_path=cache_path
        )
        
        # 检查是否有可用的缓存令牌
        token_info = auth_manager.cache_handler.get_cached_token()
        
        if token_info and not auth_manager.is_token_expired(token_info):
            logger.info("使用缓存的认证令牌")
            print("✅ 使用缓存的认证令牌，无需重新授权")
        else:
            # 如果没有有效的缓存令牌，则需要进行新的授权
            logger.info("需要新的Spotify授权")
            print("\n==== 需要Spotify账号授权 ====")
            print("✓ 将自动打开浏览器进行授权")
            print("✓ 请在浏览器中登录您的Spotify账号并点击\"同意\"授权")
            print("✓ 授权完成后会自动跳转到本地回调服务器（无需手动操作）")
            print("✓ 整个过程完全自动，无需手动复制粘贴任何内容")
            print("✓ 请不要关闭当前程序，保持网络连接正常")
            
            # 获取访问令牌 - SpotifyOAuth会自动处理浏览器授权流程
            try:
                token_info = auth_manager.get_access_token(as_dict=True)
                print("✅ 授权成功，已获取访问令牌")
            except Exception as e:
                logger.error(f"获取访问令牌失败: {e}")
                print(f"\n❌ 获取访问令牌失败: {e}")
                
                # 输出可能的解决方案
                print("\n可能的原因和解决方案:")
                print("1. 网络连接问题: 请检查您的互联网连接")
                print("2. 浏览器问题: 请确保浏览器能正常打开并访问Spotify")
                print("3. 授权被取消: 您可能取消了授权请求")
                
                sys.exit(1)
        
        # 创建Spotify客户端实例
        logger.debug("正在创建Spotify客户端实例...")
        sp = spotipy.Spotify(auth_manager=auth_manager)
        
        # 验证认证是否成功
        logger.debug("正在验证认证是否成功...")
        try:
            user_info = sp.me()
            username = user_info.get('display_name') or user_info.get('id')
            logger.info(f"Spotify认证成功，用户名: {username}")
            print(f"\n✅ Spotify认证成功！已登录为: {username}")
            print("您现在可以使用所有功能。\n")
            return sp
        except Exception as e:
            logger.error(f"令牌验证失败: {e}")
            print(f"\n❌ 令牌验证失败: {e}")
            print(f"请尝试删除缓存文件 ({cache_path}) 并重新运行程序。")
            sys.exit(1)
        
    except SpotifyOauthError as e:
        error_msg = str(e).lower()
        
        # 尝试识别特定类型的OAuth错误
        if "access_denied" in error_msg or "user denied" in error_msg or "cancelled" in error_msg:
            # 用户取消授权
            logger.error("Spotify授权已取消: 用户拒绝了授权请求")
            print(f"\n❌ Spotify授权已取消: 用户拒绝了授权请求", file=sys.stderr)
            print("请在Spotify授权页面点击'同意'以授予应用程序访问您账户的权限。", file=sys.stderr)
        elif "invalid_client" in error_msg:
            # 客户端ID/密钥无效
            logger.error(f"Spotify认证错误: 客户端ID或密钥无效")
            print(f"\n❌ Spotify认证错误: 客户端ID或密钥无效", file=sys.stderr)
            print("请检查您的.env文件中的SPOTIPY_CLIENT_ID和SPOTIPY_CLIENT_SECRET是否正确。", file=sys.stderr)
            print(f"错误详情: {e}", file=sys.stderr)
        elif "redirect_uri_mismatch" in error_msg:
            # 回调URI不匹配
            logger.error(f"Spotify认证错误: 回调URI不匹配")
            print(f"\n❌ Spotify认证错误: 回调URI不匹配", file=sys.stderr)
            print(f"请确保您的.env文件中的SPOTIPY_REDIRECT_URI ({config.SPOTIPY_REDIRECT_URI})", file=sys.stderr)
            print("与Spotify Developer Dashboard中配置的回调URI完全匹配。", file=sys.stderr)
            print(f"错误详情: {e}", file=sys.stderr)
        else:
            # 其他OAuth错误
            logger.error(f"Spotify认证错误: {e}")
            print(f"\n❌ Spotify认证错误: {e}", file=sys.stderr)
            print("请检查您的.env文件中的Spotify API凭据和Spotify Developer Dashboard中的回调URI配置是否正确且匹配。", file=sys.stderr)
        
        sys.exit(1)
        
    except spotipy.SpotifyException as e:
        # 处理认证后的API错误
        status_code = getattr(e, 'http_status', None)
        cache_path = ".spotify_cache"
        
        if status_code == 401:
            # 未授权 - 通常是令牌问题
            logger.error(f"Spotify API错误: 认证令牌无效或已过期")
            print(f"\n❌ Spotify API错误: 认证令牌无效或已过期", file=sys.stderr)
            print(f"请尝试删除缓存文件 ({cache_path}) 并重新运行程序以重新授权。", file=sys.stderr)
            print(f"错误详情: {e}", file=sys.stderr)
        elif status_code == 403:
            # 禁止 - 通常是权限问题
            logger.error(f"Spotify API错误: 权限不足")
            print(f"\n❌ Spotify API错误: 权限不足", file=sys.stderr)
            print("应用程序没有执行此操作的足够权限。可能需要申请更多的权限范围。", file=sys.stderr)
            print(f"错误详情: {e}", file=sys.stderr)
        elif status_code in (429, 500, 502, 503):
            # 速率限制或服务器错误
            logger.error(f"Spotify API错误: 服务器问题 (状态码: {status_code})")
            print(f"\n❌ Spotify API错误: 服务器问题 (状态码: {status_code})", file=sys.stderr)
            print("Spotify服务器可能繁忙或暂时不可用。请稍后重试。", file=sys.stderr)
            print(f"错误详情: {e}", file=sys.stderr)
        else:
            # 其他API错误
            logger.error(f"Spotify API错误: {e}")
            print(f"\n❌ Spotify API错误: {e}", file=sys.stderr)
            print("与Spotify API通信时发生错误。", file=sys.stderr)
        
        sys.exit(1)
    
    except urllib.error.URLError as e:
        # 处理网络连接错误
        logger.error(f"网络错误: 无法连接到Spotify服务")
        print(f"\n❌ 网络错误: 无法连接到Spotify服务", file=sys.stderr)
        print("请检查您的互联网连接是否正常。", file=sys.stderr)
        print(f"错误详情: {e}", file=sys.stderr)
        sys.exit(1)
        
    except Exception as e:
        # 捕获认证过程中的任何其他意外错误
        cache_path = ".spotify_cache"
        logger.error(f"Spotify认证过程中发生意外错误: {e}")
        print(f"\n❌ Spotify认证过程中发生意外错误: {e}", file=sys.stderr)
        print(f"如果问题持续存在，请尝试删除缓存文件 ({cache_path}) 并重新运行程序。", file=sys.stderr)
        
        # 检查是否为SSL相关错误
        if "ssl" in str(e).lower():
            print("\n⚠️ 似乎是SSL证书验证问题。可以尝试以下临时解决方案(不建议长期使用):")
            print("设置环境变量: PYTHONHTTPSVERIFY=0，然后重新运行程序")
            print("在Windows命令行中: set PYTHONHTTPSVERIFY=0")
            print("在Linux/Mac终端中: export PYTHONHTTPSVERIFY=0\n")
        
        sys.exit(1) 