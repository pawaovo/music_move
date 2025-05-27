#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
简化的测试脚本，测试仅艺术家搜索匹配分设置为0分的功能
"""

import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# 模拟EnhancedMatcher.match返回结果
def mock_match(title, artists, candidates):
    """模拟匹配函数，返回一个匹配结果"""
    return [{
        "name": "告白气球",
        "artists": [{"name": "周杰伦"}],
        "id": "123",
        "uri": "spotify:track:123",
        "similarity_scores": {
            "title_similarity": 100.0,
            "artist_similarity": 100.0,
            "final_score": 100.0,
            "first_stage_score": 100.0,
            "is_low_confidence": False
        }
    }]

# 实现我们修改后的get_enhanced_match函数
def get_enhanced_match(input_title, input_artists, candidates, is_artist_only_search=False):
    """
    使用增强匹配器获取最佳匹配结果
    """
    # 模拟EnhancedMatcher.match调用
    matches = mock_match(input_title, input_artists, candidates)
    
    if matches:
        best_match = matches[0]
        
        # 如果是通过仅艺术家搜索获得的候选，将分数强制设置为0
        if is_artist_only_search:
            # 保存原始分数用于日志记录
            original_score = best_match["similarity_scores"].get("final_score", 0)
            
            # 将匹配标记为低置信度，并且强制设置最终分数为0
            best_match["similarity_scores"]["is_low_confidence"] = True
            best_match["similarity_scores"]["original_score"] = original_score  # 保存原始分数
            best_match["similarity_scores"]["final_score"] = 0  # 设置最终分数为0
            
            logging.info(f"从仅艺术家搜索获得的候选，将分数从 {original_score:.2f} 强制设置为 0")
        
        return best_match
    else:
        return None

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

if __name__ == "__main__":
    test_artist_only_search() 