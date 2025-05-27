#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
简单测试文本标准化和EnhancedMatcher.standardize_texts方法
"""

import sys
import os
import logging

# 添加项目路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s: %(message)s',
    stream=sys.stdout
)

# 导入必要的模块 - 确保导入正确的模块路径
from spotify_playlist_importer.spotify_playlist_importer.utils.enhanced_matcher import EnhancedMatcher
from spotify_playlist_importer.spotify_playlist_importer.utils.text_normalizer import normalize_text

def test_normalize_text():
    """测试文本标准化功能"""
    print("\n=== 测试文本标准化功能 ===")
    
    test_cases = [
        # 简体/繁体中文
        ("周杰倫", "周杰伦"),  # 繁体到简体
        ("張學友", "张学友"),  # 繁体到简体
        
        # 大小写统一
        ("Jay Chou", "jay chou"),
        ("EASON CHAN", "eason chan"),
        
        # 括号处理
        ("告白气球 (Live)", "告白气球 (live)"),
        ("告白气球 [Live]", "告白气球 [live]"),
    ]
    
    for original, expected in test_cases:
        try:
            normalized = normalize_text(original)
            result = "通过" if normalized == expected else f"失败 (得到: '{normalized}')"
            print(f"原文本: '{original}' -> 期望: '{expected}' -> {result}")
        except Exception as e:
            print(f"处理 '{original}' 时出错: {e}")

def test_standardize_texts():
    """测试EnhancedMatcher.standardize_texts方法"""
    print("\n=== 测试 EnhancedMatcher.standardize_texts 方法 ===")
    
    # 创建测试数据
    input_title = "周杰倫的告白氣球 (Live)"
    input_artists = ["周杰倫", "張學友"]
    
    candidates = [
        {
            "name": "告白气球",
            "artists": [
                {"name": "周杰伦"}
            ],
            "id": "123",
            "uri": "spotify:track:123"
        },
        {
            "name": "告白氣球 (Live)",
            "artists": [
                {"name": "周杰倫"},
                {"name": "張學友"}
            ],
            "id": "456",
            "uri": "spotify:track:456"
        }
    ]
    
    # 创建增强匹配器实例
    matcher = EnhancedMatcher()
    
    try:
        # 执行标准化
        std_title, std_artists, std_candidates = matcher.standardize_texts(
            input_title, input_artists, candidates)
        
        # 显示标准化结果
        print(f"\n原始输入: 标题='{input_title}', 艺术家={input_artists}")
        print(f"标准化结果: 标题='{std_title}', 艺术家={std_artists}")
        
        print("\n标准化后的候选歌曲:")
        for i, candidate in enumerate(std_candidates):
            artists_names = [a.get("name", "") for a in candidate.get("artists", [])]
            print(f"  候选 #{i+1}: '{candidate['name']}' - {artists_names}")
            
            if "original_name" in candidate:
                print(f"    原始标题: '{candidate['original_name']}'")
            
            if "original_artists" in candidate:
                orig_artists = [a.get("name", "") for a in candidate.get("original_artists", [])]
                if orig_artists != artists_names:
                    print(f"    原始艺术家: {orig_artists}")
    
    except Exception as e:
        print(f"测试过程中出错: {e}")

if __name__ == "__main__":
    test_normalize_text()
    test_standardize_texts() 