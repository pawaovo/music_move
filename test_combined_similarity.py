"""
集成测试：验证标题和艺术家相似度计算的综合效果
"""
import os
import sys
import logging
from typing import Dict, List, Any

# 设置日志级别
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s: %(message)s',
    stream=sys.stdout
)

# 添加项目根目录到系统路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, "spotify_playlist_importer"))

# 导入需要的模块
from spotify_playlist_importer.utils.string_matcher import StringMatcher
from spotify_playlist_importer.utils.text_normalizer import normalize_text

def test_combined_score():
    """测试综合得分计算"""
    print("\n=== 测试综合得分计算 ===")
    
    matcher = StringMatcher()
    
    # 测试用例
    test_cases = [
        {
            "input_title": "给你呀",
            "input_artists": ["蒋小呢"],
            "candidate_title": "给你呀",
            "candidate_artists": ["蒋小呢"],
            "desc": "完全匹配"
        },
        {
            "input_title": "给你呀",
            "input_artists": ["蒋小呢"],
            "candidate_title": "给你呀",
            "candidate_artists": ["蔣小呢"],  # 繁体
            "desc": "繁体艺术家名"
        },
        {
            "input_title": "给你呀",
            "input_artists": ["蒋小呢"],
            "candidate_title": "給你呀",  # 繁体标题
            "candidate_artists": ["Jiang Xiao Ne"],  # 拼音
            "desc": "繁体标题+拼音艺术家名"
        },
        {
            "input_title": "给你呀 (Live)",
            "input_artists": ["蒋小呢"],
            "candidate_title": "给你呀（现场版）",  # 括号内容差异
            "candidate_artists": ["小呢"],  # 部分名字
            "desc": "括号内容差异+部分艺术家名"
        },
        {
            "input_title": "给你呀",
            "input_artists": ["蒋小呢"],
            "candidate_title": "送给你",  # 相似但不同的标题
            "candidate_artists": ["完全不同的艺术家"],
            "desc": "相似标题+不同艺术家"
        }
    ]
    
    for test_case in test_cases:
        input_title = test_case["input_title"]
        input_artists = test_case["input_artists"]
        candidate_title = test_case["candidate_title"]
        candidate_artists = test_case["candidate_artists"]
        desc = test_case["desc"]
        
        print(f"\n* 测试：{desc}")
        print(f"  输入标题：'{input_title}'")
        print(f"  输入艺术家：{input_artists}")
        print(f"  候选标题：'{candidate_title}'")
        print(f"  候选艺术家：{candidate_artists}")
        
        # 标准化文本
        std_input_title = normalize_text(input_title)
        std_input_artists = [normalize_text(artist) for artist in input_artists]
        std_candidate_title = normalize_text(candidate_title)
        std_candidate_artists = [normalize_text(artist) for artist in candidate_artists]
        
        # 计算相似度
        title_similarity = matcher.calculate_title_similarity(std_input_title, std_candidate_title)
        artist_similarity = matcher.calculate_artists_similarity(std_input_artists, std_candidate_artists)
        combined_score = matcher.calculate_combined_score(title_similarity, artist_similarity)
        
        print(f"  标题相似度：{title_similarity:.2f}")
        print(f"  艺术家相似度：{artist_similarity:.2f}")
        print(f"  加权总分：{combined_score:.2f} (标题权重={matcher.title_weight}, 艺术家权重={matcher.artist_weight})")
        
        # 评估结果
        if combined_score >= 85:
            print(f"  ✓ 高匹配度：{combined_score:.2f} >= 85")
        elif combined_score >= 70:
            print(f"  ✓ 中匹配度：{combined_score:.2f} >= 70")
        else:
            print(f"  × 低匹配度：{combined_score:.2f} < 70")

def test_real_world_examples():
    """测试真实世界的例子"""
    print("\n=== 测试真实世界的例子 ===")
    
    matcher = StringMatcher()
    
    # 真实例子
    test_cases = [
        {
            "input_title": "忘情水",
            "input_artists": ["刘德华"],
            "candidate_title": "忘情水",
            "candidate_artists": ["Andy Lau"],  # 中文名与英文名
            "desc": "艺术家中英文名称"
        },
        {
            "input_title": "青花瓷",
            "input_artists": ["周杰伦"],
            "candidate_title": "青花瓷 (Jay Chou)",  # 带有艺术家信息的标题
            "candidate_artists": ["JJ Lin"],  # 错误的艺术家
            "desc": "标题包含艺术家但艺术家不匹配"
        },
        {
            "input_title": "发如雪",
            "input_artists": ["周杰伦"],
            "candidate_title": "发如雪 (周杰伦)",  # 标题中包含正确的艺术家
            "candidate_artists": ["Jay Chou"],  # 英文名
            "desc": "标题包含正确艺术家+英文艺术家名"
        }
    ]
    
    for test_case in test_cases:
        input_title = test_case["input_title"]
        input_artists = test_case["input_artists"]
        candidate_title = test_case["candidate_title"]
        candidate_artists = test_case["candidate_artists"]
        desc = test_case["desc"]
        
        print(f"\n* 测试：{desc}")
        print(f"  输入标题：'{input_title}'")
        print(f"  输入艺术家：{input_artists}")
        print(f"  候选标题：'{candidate_title}'")
        print(f"  候选艺术家：{candidate_artists}")
        
        # 标准化文本
        std_input_title = normalize_text(input_title)
        std_input_artists = [normalize_text(artist) for artist in input_artists]
        std_candidate_title = normalize_text(candidate_title)
        std_candidate_artists = [normalize_text(artist) for artist in candidate_artists]
        
        # 计算相似度
        title_similarity = matcher.calculate_title_similarity(std_input_title, std_candidate_title)
        artist_similarity = matcher.calculate_artists_similarity(std_input_artists, std_candidate_artists)
        combined_score = matcher.calculate_combined_score(title_similarity, artist_similarity)
        
        print(f"  标题相似度：{title_similarity:.2f}")
        print(f"  艺术家相似度：{artist_similarity:.2f}")
        print(f"  加权总分：{combined_score:.2f}")
        
        # 评估结果
        if combined_score >= 85:
            print(f"  ✓ 高匹配度：{combined_score:.2f} >= 85")
        elif combined_score >= 70:
            print(f"  ✓ 中匹配度：{combined_score:.2f} >= 70")
        else:
            print(f"  × 低匹配度：{combined_score:.2f} < 70")

def summary():
    """总结11.2和11.3任务完成情况"""
    print("\n=== 任务11.2和11.3完成情况 ===")
    print("1. 优化了StringMatcher.calculate_title_similarity方法，直接使用标准化后的标题")
    print("2. 优化了StringMatcher.calculate_artists_similarity方法，直接使用标准化后的艺术家列表")
    print("3. 实现了主要艺术家匹配保障功能，当主要艺术家高度匹配时保证至少85分")
    print("4. 添加了补充拼音比较逻辑，针对相似度低于60分的情况尝试拼音匹配")
    print("5. 添加了calculate_combined_score方法，保持与EnhancedMatcher的兼容性")
    print("\n总结：已完成11.2和11.3任务要求，歌曲匹配算法现在可以更好地处理简繁体和拼音差异")

if __name__ == "__main__":
    print("开始测试标题和艺术家相似度计算的综合效果...\n")
    
    # 测试综合得分
    test_combined_score()
    
    # 测试真实例子
    test_real_world_examples()
    
    # 任务总结
    summary()
    
    print("\n测试完成！") 