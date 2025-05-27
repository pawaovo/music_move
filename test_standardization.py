"""
测试 EnhancedMatcher 类中的文本标准化功能
"""

import logging
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 设置日志级别
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s: %(message)s',
    stream=sys.stdout
)

# 导入必要的模块
from spotify_playlist_importer.utils.enhanced_matcher import EnhancedMatcher
from spotify_playlist_importer.utils.text_normalizer import normalize_text, split_text

def test_standardize_texts():
    """测试 standardize_texts 方法"""
    print("\n=== 测试 EnhancedMatcher.standardize_texts 方法 ===")
    
    # 创建测试数据
    input_title = "Perfect Match (Live)"
    input_artists = ["Artist1", "Artist2"]
    
    candidates = [
        {
            'name': 'Perfect Match',
            'artists': [{'name': 'Artist1'}, {'name': 'Artist2'}],
            'id': 'track1'
        },
        {
            'name': 'Perfect Match (Live)',
            'artists': [{'name': 'Artist1'}, {'name': 'Artist2'}],
            'id': 'track2'
        }
    ]
    
    # 创建增强匹配器实例
    matcher = EnhancedMatcher()
    
    # 执行标准化
    std_title, std_artists, std_candidates = matcher.standardize_texts(input_title, input_artists, candidates)
    
    # 显示标准化结果
    print(f"原始输入: 标题='{input_title}', 艺术家={input_artists}")
    print(f"标准化结果: 标题='{std_title}', 艺术家={std_artists}")
    print("\n标准化后的候选歌曲:")
    for i, candidate in enumerate(std_candidates):
        print(f"  候选 #{i+1}: '{candidate['name']}' - {[a['name'] for a in candidate['artists']]}")
        if 'original_name' in candidate:
            print(f"    原始标题: '{candidate['original_name']}'")

def test_match_with_standardization():
    """测试 match 方法使用标准化文本"""
    print("\n=== 测试 EnhancedMatcher.match 方法使用标准化文本 ===")
    
    # 创建测试数据
    input_title = "Perfect Match (Live)"
    input_artists = ["Artist1", "Artist2"]
    
    candidates = [
        {
            'name': 'Perfect Match',
            'artists': [{'name': 'Artist1'}, {'name': 'Artist2'}],
            'id': 'track1'
        },
        {
            'name': 'Perfect Match (Live)',
            'artists': [{'name': 'Artist1'}, {'name': 'Artist2'}],
            'id': 'track2'
        },
        {
            'name': 'Different Song',
            'artists': [{'name': 'Artist3'}],
            'id': 'track3'
        }
    ]
    
    # 创建增强匹配器实例
    matcher = EnhancedMatcher()
    
    # 执行匹配
    matches = matcher.match(input_title, input_artists, candidates)
    
    # 显示匹配结果
    print("\n匹配结果:")
    if matches:
        best_match = matches[0]
        print(f"  最佳匹配: '{best_match['name']}' (ID: {best_match['id']})")
        if 'original_name' in best_match:
            print(f"  原始标题: '{best_match['original_name']}'")
        if 'similarity_scores' in best_match:
            scores = best_match['similarity_scores']
            print(f"  匹配分数: {scores.get('final_score', 0):.2f}")
            print(f"  低置信度: {scores.get('is_low_confidence', False)}")
    else:
        print("  未找到匹配")

def test_chinese_text_standardization():
    """测试中文文本标准化"""
    print("\n=== 测试中文文本标准化 ===")
    
    # 创建测试数据
    input_title = "完美匹配 (现场版)"
    input_artists = ["艺术家１", "艺术家２"]
    
    candidates = [
        {
            'name': '完美匹配',
            'artists': [{'name': '艺术家１'}, {'name': '艺术家２'}],
            'id': 'track1'
        },
        {
            'name': '完美匹配 (现场版)',
            'artists': [{'name': '艺术家１'}, {'name': '艺术家２'}],
            'id': 'track2'
        }
    ]
    
    # 创建增强匹配器实例
    matcher = EnhancedMatcher()
    
    # 执行标准化
    std_title, std_artists, std_candidates = matcher.standardize_texts(input_title, input_artists, candidates)
    
    # 显示标准化结果
    print(f"原始输入: 标题='{input_title}', 艺术家={input_artists}")
    print(f"标准化结果: 标题='{std_title}', 艺术家={std_artists}")
    print("\n标准化后的候选歌曲:")
    for i, candidate in enumerate(std_candidates):
        print(f"  候选 #{i+1}: '{candidate['name']}' - {[a['name'] for a in candidate['artists']]}")
        if 'original_name' in candidate:
            print(f"    原始标题: '{candidate['original_name']}'")

def test_get_enhanced_match():
    """测试 get_enhanced_match 函数"""
    print("\n=== 测试 get_enhanced_match 函数 ===")
    
    # 创建测试数据
    input_title = "Perfect Match (Live)"
    input_artists = ["Artist1", "Artist2"]
    
    candidates = [
        {
            'name': 'Perfect Match',
            'artists': [{'name': 'Artist1'}, {'name': 'Artist2'}],
            'id': 'track1'
        },
        {
            'name': 'Perfect Match (Live)',
            'artists': [{'name': 'Artist1'}, {'name': 'Artist2'}],
            'id': 'track2'
        }
    ]
    
    # 导入函数
    from spotify_playlist_importer.utils.enhanced_matcher import get_enhanced_match
    
    # 执行匹配
    best_match = get_enhanced_match(input_title, input_artists, candidates)
    
    # 显示匹配结果
    print("\n匹配结果:")
    if best_match:
        print(f"  最佳匹配: '{best_match['name']}' (ID: {best_match['id']})")
        if 'original_name' in best_match:
            print(f"  原始标题: '{best_match['original_name']}'")
        if 'similarity_scores' in best_match:
            scores = best_match['similarity_scores']
            print(f"  匹配分数: {scores.get('final_score', 0):.2f}")
            print(f"  低置信度: {scores.get('is_low_confidence', False)}")
    else:
        print("  未找到匹配")

if __name__ == "__main__":
    test_standardize_texts()
    test_match_with_standardization()
    test_chinese_text_standardization()
    test_get_enhanced_match() 