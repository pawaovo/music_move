#!/usr/bin/env python3
import asyncio
import sys
import os
sys.path.insert(0, '.')

from models.song import ParsedSong
from spotify.sync_client import search_song_on_spotify_sync_wrapped

async def main():
    # 创建测试歌曲
    song = ParsedSong(
        title="Call of Silence x YouSeeBIGGIRL",
        artists=["EYAir"],
        album=None,
        duration=None
    )
    
    print(f"测试歌曲: {song.title} - {song.artists[0]}")
    print("=" * 50)
    
    try:
        result, error = await search_song_on_spotify_sync_wrapped(song)
        
        if error:
            print(f"❌ 搜索失败: {error}")
            return
            
        if result:
            print(f"✅ 找到匹配:")
            print(f"   歌曲名: {result.name}")
            print(f"   艺术家: {', '.join(result.artists)}")
            print(f"   匹配分数: {result.matched_score}")
            print(f"   低置信度: {result.is_low_confidence}")
            print()
            
            # 验证修复
            if result.is_low_confidence and result.matched_score == 0.0:
                print("🎉 测试通过: 仅艺术家搜索分数正确设置为0分!")
            elif result.is_low_confidence and result.matched_score == 50.0:
                print("❌ 测试失败: 仅艺术家搜索分数仍为50分")
            else:
                print(f"⚠️  意外结果: 分数={result.matched_score}, 低置信度={result.is_low_confidence}")
        else:
            print("❌ 没有找到匹配结果")
            
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 