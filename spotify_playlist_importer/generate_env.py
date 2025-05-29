#!/usr/bin/env python
"""
生成 .env 文件的工具脚本

该脚本以交互式方式引导用户输入必要的环境变量值，并生成 .env 文件。
用户可以选择性地跳过某些环境变量，这些变量将使用默认值。
"""

import os
import sys
import re

def print_header():
    print("\n" + "=" * 60)
    print("              Spotify 歌单导入工具 - 环境配置")
    print("=" * 60)
    print("\n该工具将帮助您创建 .env 文件，用于配置 Spotify 歌单导入工具所需的环境变量。")
    print("您需要提供一些基本信息，如 Spotify API 凭据等。")
    print("\n提示: 按回车键将使用默认值，输入 'q' 或 'quit' 将退出配置过程。")
    print("=" * 60 + "\n")

def get_input(prompt, default=None, password=False, validator=None):
    if default:
        prompt = f"{prompt} (默认: {default}): "
    else:
        prompt = f"{prompt}: "
    
    while True:
        if password:
            import getpass
            value = getpass.getpass(prompt)
        else:
            value = input(prompt)
        
        if value.lower() in ('q', 'quit', 'exit'):
            print("配置已取消。")
            sys.exit(0)
        
        if not value and default is not None:
            value = default
            break
        
        if value or default is None:
            if validator and not validator(value):
                print("输入无效，请重试。")
                continue
            break
    
    return value

def validate_url(value):
    return value.startswith(('http://', 'https://'))

def generate_env_file():
    env_path = ".env"
    
    if os.path.exists(env_path):
        overwrite = get_input("检测到已存在的 .env 文件，是否覆盖？(yes/no)", default="no")
        if overwrite.lower() not in ('yes', 'y'):
            alternative_path = get_input("请输入备用文件名", default=".env.new")
            env_path = alternative_path
    
    print("\n=== Spotify API 凭据 ===")
    print("您需要在 Spotify Developer Dashboard 创建应用以获取这些凭据:")
    print("https://developer.spotify.com/dashboard/applications\n")
    
    client_id = get_input("Spotify Client ID", password=False)
    client_secret = get_input("Spotify Client Secret", password=True)
    redirect_uri = get_input("Spotify Redirect URI", 
                            default="http://127.0.0.1:8888/callback", 
                            validator=validate_url)
    
    print("\n=== 前后端配置 ===")
    frontend_url = get_input("前端 URL", 
                            default="http://localhost:3000", 
                            validator=validate_url)
    allowed_origins = get_input("允许的跨域来源 (逗号分隔)", 
                                default="http://localhost:3000,http://127.0.0.1:3000")
    
    print("\n=== API 服务器配置 ===")
    api_host = get_input("API 服务器主机", default="0.0.0.0")
    api_port = get_input("API 服务器端口", default="8888")
    api_debug = get_input("启用调试模式? (true/false)", default="false")
    
    print("\n=== 令牌缓存配置 ===")
    project_token_cache = get_input("项目令牌缓存路径", default=".spotify_project_cache")
    user_token_cache = get_input("用户令牌缓存路径", default=".spotify_cache")
    user_token_dir = get_input("用户令牌缓存目录", default=".spotify_user_tokens")
    
    # 创建 .env 文件
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write("# Spotify API 凭据\n")
        f.write(f'SPOTIPY_CLIENT_ID="{client_id}"\n')
        f.write(f'SPOTIPY_CLIENT_SECRET="{client_secret}"\n')
        f.write(f'SPOTIPY_REDIRECT_URI="{redirect_uri}"\n\n')
        
        f.write("# 前后端配置\n")
        f.write(f'FRONTEND_URL="{frontend_url}"\n')
        f.write(f'ALLOWED_ORIGINS="{allowed_origins}"\n\n')
        
        f.write("# API 服务器配置\n")
        f.write(f'API_HOST="{api_host}"\n')
        f.write(f'API_PORT={api_port}\n')
        f.write(f'API_DEBUG={api_debug}\n\n')
        
        f.write("# 令牌缓存配置\n")
        f.write(f'PROJECT_TOKEN_CACHE_PATH="{project_token_cache}"\n')
        f.write(f'USER_TOKEN_CACHE_PATH="{user_token_cache}"\n')
        f.write(f'USER_TOKEN_CACHE_DIR="{user_token_dir}"\n')
    
    print(f"\n环境配置已保存到 {env_path} 文件。")
    print("请确保该文件不会被提交到版本控制系统中！")
    print("开发团队成员应独立配置自己的环境变量。\n")
    
    print("=" * 60)
    print("配置完成！您现在可以启动应用了。")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    print_header()
    generate_env_file() 