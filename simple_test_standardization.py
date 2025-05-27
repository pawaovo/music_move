"""
简单测试StringMatcher使用标准化文本的功能
"""
import sys
import logging
from typing import List, Dict, Any

# 设置日志级别
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s: %(message)s',
    stream=sys.stdout
)

# 导入需要的模块
from spotify_playlist_importer.utils.string_matcher import StringMatcher
from spotify_playlist_importer.utils.text_normalizer import normalize_text

def test_title_similarity():
    """测试标题相似度计算使用标准化文本"""
    print("\n=== 测试标题相似度计算使用标准化文本 ===")
    
    string_matcher = StringMatcher()
    
    # 测试用例
    test_cases = [
        # 简繁体差异测试
        ("测试歌曲", "測試歌曲"),
        # 括号格式差异测试
        ("测试歌曲（现场版）", "测试歌曲 (Live)"),
        # 空格和标点差异测试
        ("测试 歌曲", "测试，歌曲"),
        # 大小写差异测试
        ("Test Song", "test song"),
        # 全角半角符号差异测试
        ("Ｔｅｓｔ　Ｓｏｎｇ", "Test Song"),
    ]
    
    for input_title, candidate_title in test_cases:
        print(f"\n测试：'{input_title}' vs '{candidate_title}'")
        
        # 手动标准化
        std_input = normalize_text(input_title)
        std_candidate = normalize_text(candidate_title)
        
        print(f"标准化后：'{std_input}' vs '{std_candidate}'")
        
        # 直接使用原始文本计算相似度
        orig_similarity = string_matcher.calculate_title_similarity(input_title, candidate_title)
        print(f"原始文本相似度：{orig_similarity:.2f}")
        
        # 使用标准化文本计算相似度
        std_similarity = string_matcher.calculate_title_similarity(std_input, std_candidate)
        print(f"标准化文本相似度：{std_similarity:.2f}")
        
        # 验证是否直接使用了输入文本
        if std_input == std_candidate and std_similarity == 100.0:
            print("✓ 标准化文本完全匹配")
        else:
            print("× 相似度低于预期，可能在计算过程中进行了二次标准化")

def test_artist_similarity():
    """测试艺术家相似度计算使用标准化文本"""
    print("\n=== 测试艺术家相似度计算使用标准化文本 ===")
    
    string_matcher = StringMatcher()
    
    # 测试用例
    test_cases = [
        # 简繁体差异测试
        (["艺术家A", "艺术家B"], ["藝術家A", "藝術家B"]),
        # 大小写和顺序差异测试
        (["Artist One", "Artist Two"], ["artist two", "artist one"]),
        # 全角半角符号差异测试
        (["Ａｒｔｉｓｔ　Ｏｎｅ"], ["Artist One"]),
    ]
    
    for input_artists, candidate_artists in test_cases:
        print(f"\n测试：{input_artists} vs {candidate_artists}")
        
        # 手动标准化
        std_inputs = [normalize_text(artist) for artist in input_artists]
        std_candidates = [normalize_text(artist) for artist in candidate_artists]
        
        print(f"标准化后：{std_inputs} vs {std_candidates}")
        
        # 直接使用原始文本计算相似度
        orig_similarity = string_matcher.calculate_artists_similarity(input_artists, candidate_artists)
        print(f"原始文本相似度：{orig_similarity:.2f}")
        
        # 使用标准化文本计算相似度
        std_similarity = string_matcher.calculate_artists_similarity(std_inputs, std_candidates)
        print(f"标准化文本相似度：{std_similarity:.2f}")
        
        # 验证艺术家名称匹配
        if set(std_inputs) == set(std_candidates) and std_similarity >= 95.0:
            print("✓ 标准化艺术家完全匹配")
        else:
            print("× 相似度低于预期，可能在计算过程中进行了二次标准化")

if __name__ == "__main__":
    print("启动简单标准化测试...\n")
    
    # 测试标题相似度
    test_title_similarity()
    
    # 测试艺术家相似度
    test_artist_similarity()
    
    print("\n测试完成！") 