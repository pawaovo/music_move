#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试文本标准化和增强匹配器的实现
"""

import logging
import sys
import os
from typing import List, Dict, Any

# 添加项目路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# 导入要测试的模块
from spotify_playlist_importer.utils.text_normalizer import normalize_text, get_text_pinyin
from spotify_playlist_importer.utils.enhanced_matcher import EnhancedMatcher

def test_text_normalization():
    """测试文本标准化功能"""
    print("\n=== 测试文本标准化功能 ===")
    
    test_cases = [
        # 简体/繁体中文
        ("周杰倫", "周杰伦"),  # 繁体到简体
        ("張學友", "张学友"),  # 繁体到简体
        
        # 大小写统一
        ("Jay Chou", "jay chou"),
        ("EASON CHAN", "eason chan"),
        
        # 全角/半角字符
        ("ＪＡＹ　ＣＨＯＵ", "jay chou"),
        ("周杰倫（ＪＡＹ　ＣＨＯＵ）", "周杰伦(jay chou)"),
        
        # 括号处理
        ("告白气球 (Live)", "告白气球 (live)"),
        ("告白气球 [Live]", "告白气球 [live]"),
        
        # 特殊标记处理
        ("月亮代表我的心 feat. 张学友", "月亮代表我的心 feat 张学友"),
        ("月亮代表我的心 ft. 张学友", "月亮代表我的心 feat 张学友"),
        
        # 空白字符处理
        ("告白   气球", "告白 气球"),
        ("告白\t气球", "告白 气球"),
        
        # 混合情况
        ("告白气球 (Live Version) feat. 張學友", "告白气球 (live version) feat 张学友"),
    ]
    
    for original, expected in test_cases:
        normalized = normalize_text(original)
        result = "通过" if normalized == expected else f"失败 (得到: '{normalized}')"
        print(f"原文本: '{original}' -> 期望: '{expected}' -> {result}")
    
    # 测试保留/不保留括号内容
    original = "告白气球 (Live Version)"
    with_brackets = normalize_text(original, keep_brackets=True)
    without_brackets = normalize_text(original, keep_brackets=False)
    print(f"\n保留括号: '{original}' -> '{with_brackets}'")
    print(f"不保留括号: '{original}' -> '{without_brackets}'")

def test_pinyin_conversion():
    """测试中文转拼音功能"""
    print("\n=== 测试中文转拼音功能 ===")
    
    test_cases = [
        ("周杰伦", "zhou jie lun"),
        ("张学友", "zhang xue you"),
        ("告白气球", "gao bai qi qiu"),
        ("月亮代表我的心", "yue liang dai biao wo de xin"),
    ]
    
    for chinese, expected_pinyin in test_cases:
        try:
            pinyin = get_text_pinyin(chinese)
            result = "通过" if pinyin.lower() == expected_pinyin else f"失败 (得到: '{pinyin}')"
            print(f"中文: '{chinese}' -> 期望拼音: '{expected_pinyin}' -> {result}")
        except Exception as e:
            print(f"中文: '{chinese}' -> 转换失败: {e}")

def test_enhanced_matcher():
    """测试增强匹配器功能"""
    print("\n=== 测试增强匹配器功能 ===")
    
    # 创建匹配器实例
    matcher = EnhancedMatcher()
    
    # 测试案例1: 简体/繁体差异
    print("\n测试1: 简繁体差异")
    test_simplify_traditional(matcher)
    
    # 测试案例2: 括号内容差异
    print("\n测试2: 括号内容差异")
    test_bracket_content(matcher)
    
    # 测试案例3: 艺术家匹配 (拼音)
    print("\n测试3: 艺术家名称拼音匹配")
    test_artist_pinyin(matcher)
    
    # 测试案例4: 动态分数下限
    print("\n测试4: 动态分数下限")
    test_dynamic_score_floor(matcher)

def test_simplify_traditional(matcher):
    """测试简体/繁体差异匹配"""
    input_title = "告白气球"
    input_artists = ["周杰伦"]
    
    # 候选项 - 使用繁体
    candidates = [
        {
            "name": "告白氣球",  # 繁体
            "artists": [
                {"name": "周杰倫"}  # 繁体
            ],
            "id": "123",
            "uri": "spotify:track:123"
        }
    ]
    
    # 执行匹配
    matches = matcher.match(input_title, input_artists, candidates)
    
    # 打印结果
    if matches:
        best_match = matches[0]
        scores = best_match["similarity_scores"]
        print(f"标题相似度: {scores.get('title_similarity', 0):.2f}")
        print(f"艺术家相似度: {scores.get('artist_similarity', 0):.2f}")
        print(f"最终分数: {scores.get('final_score', 0):.2f}")
    else:
        print("没有找到匹配项")

def test_bracket_content(matcher):
    """测试括号内容差异匹配"""
    input_title = "告白气球 (Live)"
    input_artists = ["周杰伦"]
    
    # 候选列表 - 三种情况
    candidates = [
        {
            "name": "告白气球",  # 无括号
            "artists": [{"name": "周杰伦"}],
            "id": "123",
            "uri": "spotify:track:123"
        },
        {
            "name": "告白气球 (Live)",  # 相同括号
            "artists": [{"name": "周杰伦"}],
            "id": "456",
            "uri": "spotify:track:456"
        },
        {
            "name": "告白气球 (Remix)",  # 不同括号
            "artists": [{"name": "周杰伦"}],
            "id": "789",
            "uri": "spotify:track:789"
        }
    ]
    
    # 执行匹配
    matches = matcher.match(input_title, input_artists, candidates)
    
    # 打印结果
    print("匹配排序结果:")
    for i, match in enumerate(matches):
        scores = match["similarity_scores"]
        print(f"{i+1}. '{match['name']}' - 最终分数: {scores.get('final_score', 0):.2f}")
        print(f"   标题相似度: {scores.get('title_similarity', 0):.2f}, 艺术家相似度: {scores.get('artist_similarity', 0):.2f}")
        if 'bracket_adjustment' in scores:
            print(f"   括号调整: {scores.get('bracket_adjustment', 0):+.2f}")

def test_artist_pinyin(matcher):
    """测试艺术家名称拼音匹配"""
    input_title = "告白气球"
    input_artists = ["周杰伦"]  # 简体中文
    
    # 候选 - 使用拼音
    candidates = [
        {
            "name": "告白气球",
            "artists": [
                {"name": "Zhou Jie Lun"}  # 拼音
            ],
            "id": "123",
            "uri": "spotify:track:123"
        }
    ]
    
    # 执行匹配
    matches = matcher.match(input_title, input_artists, candidates)
    
    # 打印结果
    if matches:
        best_match = matches[0]
        scores = best_match["similarity_scores"]
        print(f"标题相似度: {scores.get('title_similarity', 0):.2f}")
        print(f"艺术家相似度: {scores.get('artist_similarity', 0):.2f}")
        print(f"最终分数: {scores.get('final_score', 0):.2f}")
    else:
        print("没有找到匹配项")

def test_dynamic_score_floor(matcher):
    """测试动态分数下限"""
    input_title = "特殊测试标题"
    input_artists = ["测试艺术家"]
    
    # 候选 - 标题完全匹配，艺术家完全不匹配
    candidates = [
        {
            "name": "特殊测试标题",  # 完全匹配标题
            "artists": [
                {"name": "完全不相关艺术家"}  # 完全不匹配艺术家
            ],
            "id": "123",
            "uri": "spotify:track:123"
        }
    ]
    
    # 执行匹配
    matches = matcher.match(input_title, input_artists, candidates)
    
    # 打印结果
    if matches:
        best_match = matches[0]
        scores = best_match["similarity_scores"]
        print(f"标题相似度: {scores.get('title_similarity', 0):.2f}")
        print(f"艺术家相似度: {scores.get('artist_similarity', 0):.2f}")
        print(f"基础最终分数: {scores.get('base_final_score', 0):.2f}")
        print(f"动态下限: {scores.get('dynamic_floor', 0):.2f}")
        print(f"最终分数: {scores.get('final_score', 0):.2f}")
    else:
        print("没有找到匹配项")

if __name__ == "__main__":
    try:
        # 执行各项测试
        test_text_normalization()
        test_pinyin_conversion()
        test_enhanced_matcher()
    except Exception as e:
        print(f"测试过程中出错: {e}") 