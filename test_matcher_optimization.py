#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试匹配优化效果
"""

import logging
import sys
import os
from typing import List, Dict, Any

# 添加当前目录到搜索路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# 直接导入当前目录下的增强匹配器
from spotify_playlist_importer.utils.enhanced_matcher import EnhancedMatcher, get_enhanced_match

def test_optimization():
    """测试匹配优化效果"""
    print("=== 测试匹配优化效果 ===")
    
    # 测试用例 - 高标题分数，低艺术家分数
    input_title = "测试歌曲标题"
    input_artists = ["测试艺术家A", "测试艺术家B"]
    
    # 模拟候选歌曲 - 标题完全匹配，艺术家完全不匹配
    candidates = [
        {
            "name": "测试歌曲标题",
            "artists": [
                {"name": "完全不同艺术家1"},
                {"name": "完全不同艺术家2"}
            ],
            "id": "123",
            "uri": "spotify:track:123"
        },
        {
            "name": "其他歌曲",
            "artists": [
                {"name": "测试艺术家A"},
                {"name": "测试艺术家B"}
            ],
            "id": "456",
            "uri": "spotify:track:456"
        }
    ]
    
    # 创建匹配器
    matcher = EnhancedMatcher()
    
    print("\n测试1: 一般匹配 - 标题匹配，艺术家不匹配")
    matches = matcher.match(input_title, input_artists, candidates, testing=True)
    
    if matches:
        best_match = matches[0]
        scores = best_match["similarity_scores"]
        print(f"标题分数: {scores.get('title_similarity', 0):.2f}")
        print(f"艺术家分数: {scores.get('artist_similarity', 0):.2f}")
        print(f"第一阶段分数: {scores.get('first_stage_score', 0):.2f}")
        print(f"括号调整: {scores.get('bracket_adjustment', 0):+.2f}")
        print(f"最终分数: {scores.get('final_score', 0):.2f}")
        
        if "base_final_score" in scores and "dynamic_floor" in scores:
            print(f"原始最终分数: {scores.get('base_final_score', 0):.2f}")
            print(f"最高单项分数: {scores.get('highest_component_score', 0):.2f}")
            print(f"动态下限: {scores.get('dynamic_floor', 0):.2f}")
    else:
        print("没有找到匹配")
        
    print("\n测试2: 艺术家搜索")
    artist_match = get_enhanced_match(
        input_title, input_artists, candidates, 
        is_artist_only_search=True, testing=True
    )
    
    if artist_match:
        scores = artist_match["similarity_scores"]
        print(f"标题分数: {scores.get('title_similarity', 0):.2f}")
        print(f"艺术家分数: {scores.get('artist_similarity', 0):.2f}")
        print(f"最终分数: {scores.get('final_score', 0):.2f}")
        print(f"低置信度: {scores.get('is_low_confidence', False)}")
    else:
        print("没有找到艺术家搜索匹配")
        
    # 测试用例3 - 标题一般匹配，艺术家高分匹配
    print("\n测试3: 艺术家高分，标题一般")
    input_title3 = "不太相似的标题"
    matches3 = matcher.match(input_title3, input_artists, candidates)
    
    if matches3:
        best_match3 = matches3[0]
        scores3 = best_match3["similarity_scores"]
        print(f"标题分数: {scores3.get('title_similarity', 0):.2f}")
        print(f"艺术家分数: {scores3.get('artist_similarity', 0):.2f}")
        print(f"第一阶段分数: {scores3.get('first_stage_score', 0):.2f}")
        print(f"括号调整: {scores3.get('bracket_adjustment', 0):+.2f}")
        print(f"最终分数: {scores3.get('final_score', 0):.2f}")
    else:
        print("没有找到匹配")

if __name__ == "__main__":
    test_optimization() 