#!/usr/bin/env python3
"""
测试仅艺术家搜索时的分数设置
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'spotify_playlist_importer', 'spotify_playlist_importer'))

from models.song import ParsedSong
from spotify.sync_client import search_song_on_spotify_sync_wrapped

async def test_artist_only_search():
    """测试仅艺术家搜索的分数设置"""
    
    # 创建一个测试歌曲，这个歌曲在Spotify上不存在，会触发仅艺术家搜索
    test_song = ParsedSong(
        title="Call of Silence x YouSeeBIGGIRL",
        artists=["EYAir"],
        album=None,
        duration=None
    )
    
    print(f"测试歌曲: {test_song.title} - {', '.join(test_song.artists)}")
    print("=" * 50)
    
    try:
        # 执行搜索
        result, error = await search_song_on_spotify_sync_wrapped(test_song)
        
        if error:
            print(f"搜索失败: {error}")
            return
            
        if result:
            print(f"匹配结果:")
            print(f"  歌曲名: {result.name}")
            print(f"  艺术家: {', '.join(result.artists)}")
            print(f"  匹配分数: {result.matched_score}")
            print(f"  低置信度: {result.is_low_confidence}")
            
            # 验证分数
            if result.is_low_confidence and result.matched_score == 0.0:
                print("✅ 测试通过：仅艺术家搜索时分数正确设置为0分")
            elif result.is_low_confidence and result.matched_score == 50.0:
                print("❌ 测试失败：仅艺术家搜索时分数仍然是50分")
            else:
                print(f"⚠️  意外结果：分数={result.matched_score}, 低置信度={result.is_low_confidence}")
        else:
            print("没有找到匹配结果")
            
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_artist_only_search()) 