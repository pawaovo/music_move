#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试仅艺术家搜索匹配分设置为0分的功能
"""

import logging
import sys
import os

# 添加项目根目录到路径
current_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, current_dir)

# 配置日志 - 只显示警告以上级别
logging.basicConfig(
    level=logging.WARNING,
    format='%(levelname)s: %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# 尝试不同的导入路径
try:
    # 首先尝试直接导入
    from spotify_playlist_importer.utils.enhanced_matcher import get_enhanced_match
except ImportError:
    try:
        # 如果失败，尝试从当前目录导入
        sys.path.append(os.path.join(current_dir, "spotify_playlist_importer"))
        from utils.enhanced_matcher import get_enhanced_match
    except ImportError as e:
        print(f"导入错误: {e}")
        print("导入路径:")
        for p in sys.path:
            print(f" - {p}")
        sys.exit(1)

def test_artist_only_search():
    """测试仅艺术家搜索匹配分设置为0分的功能"""
    print("\n=== 测试仅艺术家搜索匹配分设置为0分 ===")
    
    # 定义测试数据
    input_title = "告白气球"
    input_artists = ["周杰伦"]
    
    # 创建一个匹配良好的候选歌曲
    candidates = [
        {
            "name": "告白气球",  # 标题完全匹配
            "artists": [
                {"name": "周杰伦"}  # 艺术家完全匹配
            ],
            "id": "123",
            "uri": "spotify:track:123"
        }
    ]
    
    try:
        # 测试普通搜索（非仅艺术家搜索）
        print("\n- 测试普通搜索（非仅艺术家搜索）:")
        match_normal = get_enhanced_match(
            input_title, input_artists, candidates, is_artist_only_search=False
        )
        
        if match_normal:
            score_normal = match_normal["similarity_scores"].get("final_score", 0)
            print(f"  普通搜索匹配分数: {score_normal:.2f}")
            print(f"  低置信度标记: {match_normal['similarity_scores'].get('is_low_confidence', False)}")
        else:
            print("  未找到匹配项")
        
        # 测试仅艺术家搜索
        print("\n- 测试仅艺术家搜索:")
        match_artist_only = get_enhanced_match(
            input_title, input_artists, candidates, is_artist_only_search=True
        )
        
        if match_artist_only:
            score_artist_only = match_artist_only["similarity_scores"].get("final_score", 0)
            original_score = match_artist_only["similarity_scores"].get("original_score", 0)
            print(f"  仅艺术家搜索匹配分数: {score_artist_only:.2f}")
            print(f"  原始计算分数: {original_score:.2f}")
            print(f"  低置信度标记: {match_artist_only['similarity_scores'].get('is_low_confidence', False)}")
            
            # 验证是否正确设置为0分
            assert score_artist_only == 0, "仅艺术家搜索匹配分数应为0分"
            print("  验证通过: 仅艺术家搜索匹配分数成功设置为0分")
        else:
            print("  未找到匹配项")
    
    except Exception as e:
        print(f"测试过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_artist_only_search() 