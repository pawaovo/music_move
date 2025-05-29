#!/usr/bin/env python3
import os
import sys
import spotipy
from spotipy.oauth2 import SpotifyOAuth

def main():
    """测试 Spotify API 认证"""
    # 首先设置必要的环境变量
    os.environ["SPOTIPY_CLIENT_ID"] = "d76bf1bba8174e4c9ac28dc3404bd8ac"
    os.environ["SPOTIPY_CLIENT_SECRET"] = "0b11ec134c984fae883bb1fd966d8ed2"
    os.environ["SPOTIPY_REDIRECT_URI"] = "http://127.0.0.1:8888/callback"
    
    print("=== Spotify API 认证测试 ===")
    print(f"SPOTIPY_CLIENT_ID: {os.environ.get('SPOTIPY_CLIENT_ID')}")
    print(f"SPOTIPY_CLIENT_SECRET: {os.environ.get('SPOTIPY_CLIENT_SECRET')}")
    print(f"SPOTIPY_REDIRECT_URI: {os.environ.get('SPOTIPY_REDIRECT_URI')}")
    
    try:
        # 创建 Spotify 客户端
        scope = "user-library-read"
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
        
        # 测试一个简单的 API 调用
        results = sp.current_user_saved_tracks(limit=5)
        
        print("\n认证成功！获取到用户保存的曲目:")
        for idx, item in enumerate(results['items']):
            track = item['track']
            print(f"{idx+1}. {track['artists'][0]['name']} - {track['name']}")
        
        return True
    except Exception as e:
        print(f"\n认证失败: {e}")
        return False

if __name__ == "__main__":
    success = main()
    print("\n=== 测试完成 ===")
    print(f"测试结果: {'成功' if success else '失败'}")
    sys.exit(0 if success else 1) 