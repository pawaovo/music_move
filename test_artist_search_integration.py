#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试仅艺术家搜索匹配分设置为0分的修改与现有代码逻辑的集成
"""

import logging
import sys
import os

# 添加项目根目录到路径
current_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, current_dir)

# 配置日志
logging.basicConfig(
    level=logging.WARNING,
    format='%(levelname)s: %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# 导入需要的模块
try:
    from spotify_playlist_importer.utils.enhanced_matcher import EnhancedMatcher, get_enhanced_match
except ImportError as e:
    print(f"导入错误: {e}")
    print("导入路径:")
    for p in sys.path:
        print(f" - {p}")
    sys.exit(1)

def create_test_data():
    """创建用于测试的数据"""
    # 输入歌曲信息
    input_title = "告白气球"
    input_artists = ["周杰伦"]
    
    # 创建候选歌曲
    candidates = [
        {
            "name": "告白气球",  # 完全匹配
            "artists": [
                {"name": "周杰伦"}
            ],
            "id": "123",
            "uri": "spotify:track:123"
        },
        {
            "name": "告白气球 (Live)",  # 部分匹配
            "artists": [
                {"name": "周杰伦"}
            ],
            "id": "456",
            "uri": "spotify:track:456"
        },
        {
            "name": "Another Song",  # 不匹配
            "artists": [
                {"name": "Other Artist"}
            ],
            "id": "789",
            "uri": "spotify:track:789"
        }
    ]
    
    return input_title, input_artists, candidates

def test_artist_only_search_integration():
    """测试仅艺术家搜索匹配分设置为0分的修改与现有代码逻辑的集成"""
    print("\n=== 测试仅艺术家搜索匹配分设置为0分的集成 ===")
    
    # 创建测试数据
    input_title, input_artists, candidates = create_test_data()
    
    # 测试1: 直接使用EnhancedMatcher类
    print("\n- 测试1: 直接使用EnhancedMatcher类")
    matcher = EnhancedMatcher()
    matches = matcher.match(input_title, input_artists, candidates)
    
    if matches:
        best_match = matches[0]
        score = best_match["similarity_scores"].get("final_score", 0)
        print(f"  最佳匹配标题: '{best_match.get('name', '')}'")
        print(f"  最佳匹配分数: {score:.2f}")
        print(f"  低置信度标记: {best_match['similarity_scores'].get('is_low_confidence', False)}")
    else:
        print("  未找到匹配项")
    
    # 测试2: 使用get_enhanced_match函数，非仅艺术家搜索
    print("\n- 测试2: 使用get_enhanced_match函数，非仅艺术家搜索")
    match_normal = get_enhanced_match(
        input_title, input_artists, candidates, is_artist_only_search=False
    )
    
    if match_normal:
        score = match_normal["similarity_scores"].get("final_score", 0)
        print(f"  最佳匹配标题: '{match_normal.get('name', '')}'")
        print(f"  最佳匹配分数: {score:.2f}")
        print(f"  低置信度标记: {match_normal['similarity_scores'].get('is_low_confidence', False)}")
    else:
        print("  未找到匹配项")
    
    # 测试3: 使用get_enhanced_match函数，仅艺术家搜索
    print("\n- 测试3: 使用get_enhanced_match函数，仅艺术家搜索")
    match_artist_only = get_enhanced_match(
        input_title, input_artists, candidates, is_artist_only_search=True
    )
    
    if match_artist_only:
        score = match_artist_only["similarity_scores"].get("final_score", 0)
        original_score = match_artist_only["similarity_scores"].get("original_score", "未保存")
        print(f"  最佳匹配标题: '{match_artist_only.get('name', '')}'")
        print(f"  最佳匹配分数: {score:.2f}")
        print(f"  原始计算分数: {original_score}")
        print(f"  低置信度标记: {match_artist_only['similarity_scores'].get('is_low_confidence', False)}")
        
        # 验证仅艺术家搜索匹配分是否被设置为0
        assert score == 0, "仅艺术家搜索匹配分应为0分"
        print("  验证通过: 仅艺术家搜索匹配分成功设置为0分")
    else:
        print("  未找到匹配项")
    
if __name__ == "__main__":
    try:
        test_artist_only_search_integration()
        print("\n所有测试通过!")
    except Exception as e:
        print(f"\n测试失败: {str(e)}")
        import traceback
        traceback.print_exc() 