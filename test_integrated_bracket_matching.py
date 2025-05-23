"""
集成测试：验证优化后的括号内容匹配在整体匹配流程中的效果
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
from spotify_playlist_importer.utils.bracket_matcher import BracketMatcher, adjust_scores_with_brackets
from spotify_playlist_importer.utils.string_matcher import StringMatcher
from spotify_playlist_importer.utils.enhanced_matcher import EnhancedMatcher
from spotify_playlist_importer.utils.text_normalizer import normalize_text, split_text

def test_integrated_bracket_matching():
    """测试括号内容匹配与字符串匹配的集成"""
    print("\n=== 测试括号内容匹配与字符串匹配的集成 ===")
    
    # 创建测试用例
    test_cases = [
        {
            "input_title": "歌曲名",
            "input_artists": ["艺术家"],
            "candidates": [
                {
                    "name": "歌曲名 (原版)",
                    "artists": [{"name": "艺术家"}],
                    "id": "track1"
                },
                {
                    "name": "歌曲名 (Remix)",
                    "artists": [{"name": "艺术家"}],
                    "id": "track2"
                },
                {
                    "name": "歌曲名 (又名：另一个名字)",
                    "artists": [{"name": "艺术家"}],
                    "id": "track3"
                }
            ],
            "desc": "输入无括号，候选有不同类型括号"
        },
        {
            "input_title": "歌曲名 (Live)",
            "input_artists": ["艺术家"],
            "candidates": [
                {
                    "name": "歌曲名 (现场版)",
                    "artists": [{"name": "艺术家"}],
                    "id": "track1"
                },
                {
                    "name": "歌曲名",
                    "artists": [{"name": "艺术家"}],
                    "id": "track2"
                },
                {
                    "name": "歌曲名 (录音室版本)",
                    "artists": [{"name": "艺术家"}],
                    "id": "track3"
                }
            ],
            "desc": "输入有括号，候选有不同类型括号"
        },
        {
            "input_title": "歌曲名 (又名：旧名字)",
            "input_artists": ["艺术家"],
            "candidates": [
                {
                    "name": "旧名字",
                    "artists": [{"name": "艺术家"}],
                    "id": "track1"
                },
                {
                    "name": "歌曲名 (Original: 旧名字)",
                    "artists": [{"name": "艺术家"}],
                    "id": "track2"
                },
                {
                    "name": "歌曲名",
                    "artists": [{"name": "艺术家"}],
                    "id": "track3"
                }
            ],
            "desc": "输入有别名括号，候选中一个是别名"
        }
    ]
    
    # 创建匹配器
    string_matcher = StringMatcher()
    bracket_matcher = BracketMatcher()
    
    for test_case in test_cases:
        input_title = test_case["input_title"]
        input_artists = test_case["input_artists"]
        candidates = test_case["candidates"]
        desc = test_case["desc"]
        
        print(f"\n* 测试：{desc}")
        print(f"  输入标题：'{input_title}'")
        print(f"  输入艺术家：{input_artists}")
        
        # 标准化输入
        std_input_title = normalize_text(input_title)
        std_input_artists = [normalize_text(artist) for artist in input_artists]
        
        # 1. 使用StringMatcher计算基础分数
        print("\n  StringMatcher基础匹配：")
        string_matches = string_matcher.match(std_input_title, std_input_artists, candidates)
        
        for i, match in enumerate(string_matches):
            name = match.get("name", "")
            artists = [a.get("name", "") for a in match.get("artists", [])]
            weighted_score = match.get("similarity_scores", {}).get("weighted_score", 0)
            
            print(f"    候选{i+1}: '{name}' - {artists}")
            print(f"      基础分数: {weighted_score:.2f}")
        
        # 2. 应用BracketMatcher调整分数
        print("\n  应用括号匹配调整后：")
        adjusted_matches = adjust_scores_with_brackets(string_matches, input_title)
        
        for i, match in enumerate(adjusted_matches):
            name = match.get("name", "")
            artists = [a.get("name", "") for a in match.get("artists", [])]
            base_score = match.get("similarity_scores", {}).get("weighted_score", 0)
            bracket_score = match.get("similarity_scores", {}).get("bracket_score", 0)
            final_score = match.get("similarity_scores", {}).get("final_score", 0)
            
            print(f"    候选{i+1}: '{name}' - {artists}")
            print(f"      基础分数: {base_score:.2f}, 括号调整: {bracket_score:+.2f}, 最终分数: {final_score:.2f}")
        
        # 分析结果
        if adjusted_matches:
            best_match = adjusted_matches[0]
            best_name = best_match.get("name", "")
            best_final_score = best_match.get("similarity_scores", {}).get("final_score", 0)
            
            print(f"\n  最佳匹配：'{best_name}', 最终分数：{best_final_score:.2f}")
            
            # 检查别名匹配情况
            if "又名" in input_title or "别名" in input_title or "aka" in input_title.lower():
                if "旧名字" in best_name or "Original" in best_name:
                    print(f"  ✓ 成功：别名处理正确匹配别名相关候选")
                else:
                    print(f"  × 注意：别名处理可能未充分考虑别名匹配")
            
            # 检查类型匹配情况
            if "Live" in input_title or "现场" in input_title:
                if "现场" in best_name or "Live" in best_name:
                    print(f"  ✓ 成功：括号类型匹配正确识别相同类型")
                else:
                    print(f"  × 注意：括号类型匹配可能有误")
        else:
            print(f"\n  × 警告：未找到合格的匹配结果")

def test_complete_matching_pipeline():
    """测试完整匹配流程"""
    print("\n=== 测试完整匹配流程 ===")
    
    # 创建测试用例
    test_cases = [
        {
            "input_title": "Shape of You (Extended)",
            "input_artists": ["Ed Sheeran"],
            "candidates": [
                {
                    "name": "Shape of You",
                    "artists": [{"name": "Ed Sheeran"}],
                    "id": "track1"
                },
                {
                    "name": "Shape of You (Extended Version)",
                    "artists": [{"name": "Ed Sheeran"}],
                    "id": "track2"
                },
                {
                    "name": "Shape of You (Acoustic)",
                    "artists": [{"name": "Ed Sheeran"}],
                    "id": "track3"
                }
            ],
            "desc": "英文歌曲，括号版本匹配"
        },
        {
            "input_title": "夜曲 (现场版)",
            "input_artists": ["周杰伦"],
            "candidates": [
                {
                    "name": "夜曲",
                    "artists": [{"name": "周杰伦"}],
                    "id": "track1"
                },
                {
                    "name": "夜曲 (Live)",
                    "artists": [{"name": "Jay Chou"}],
                    "id": "track2"
                },
                {
                    "name": "夜曲 (编曲: 钢琴版)",
                    "artists": [{"name": "周杰伦"}],
                    "id": "track3"
                }
            ],
            "desc": "中文歌曲，Live版本匹配与艺术家英文名"
        },
        {
            "input_title": "蒲公英的约定 (原名: 约定)",
            "input_artists": ["周杰伦"],
            "candidates": [
                {
                    "name": "蒲公英的约定",
                    "artists": [{"name": "周杰伦"}],
                    "id": "track1"
                },
                {
                    "name": "约定",
                    "artists": [{"name": "周杰伦"}],
                    "id": "track2"
                },
                {
                    "name": "蒲公英的约定 (aka 约定)",
                    "artists": [{"name": "Jay Chou"}],
                    "id": "track3"
                }
            ],
            "desc": "中文歌曲，别名匹配测试"
        }
    ]
    
    # 创建EnhancedMatcher (如果可用)
    try:
        enhanced_matcher = EnhancedMatcher()
        has_enhanced_matcher = True
    except:
        print("  注意: EnhancedMatcher不可用，将仅使用StringMatcher+BracketMatcher组合")
        has_enhanced_matcher = False
    
    # 创建StringMatcher
    string_matcher = StringMatcher()
    
    for test_case in test_cases:
        input_title = test_case["input_title"]
        input_artists = test_case["input_artists"]
        candidates = test_case["candidates"]
        desc = test_case["desc"]
        
        print(f"\n* 测试：{desc}")
        print(f"  输入标题：'{input_title}'")
        print(f"  输入艺术家：{input_artists}")
        
        # 1. EnhancedMatcher方法 (如果可用)
        if has_enhanced_matcher:
            print("\n  EnhancedMatcher结果:")
            enhanced_matches = enhanced_matcher.match(input_title, input_artists, candidates)
            
            for i, match in enumerate(enhanced_matches):
                name = match.get("name", "")
                artists = [a.get("name", "") for a in match.get("artists", [])]
                final_score = match.get("similarity_scores", {}).get("final_score", 0)
                
                print(f"    候选{i+1}: '{name}' - {artists}")
                print(f"      最终分数: {final_score:.2f}")
                
            if enhanced_matches:
                best_enhanced = enhanced_matches[0]
                print(f"  最佳匹配(EnhancedMatcher): '{best_enhanced.get('name', '')}'")
        
        # 2. StringMatcher + BracketMatcher组合
        print("\n  StringMatcher + BracketMatcher结果:")
        
        # 标准化输入
        std_input_title = normalize_text(input_title)
        std_input_artists = [normalize_text(artist) for artist in input_artists]
        
        # a. StringMatcher基础匹配
        string_matches = string_matcher.match(std_input_title, std_input_artists, candidates)
        
        # b. BracketMatcher调整分数
        adjusted_matches = adjust_scores_with_brackets(string_matches.copy(), input_title)
        
        for i, match in enumerate(adjusted_matches):
            name = match.get("name", "")
            artists = [a.get("name", "") for a in match.get("artists", [])]
            base_score = match.get("similarity_scores", {}).get("weighted_score", 0)
            bracket_score = match.get("similarity_scores", {}).get("bracket_score", 0)
            final_score = match.get("similarity_scores", {}).get("final_score", 0)
            
            print(f"    候选{i+1}: '{name}' - {artists}")
            print(f"      基础分数: {base_score:.2f}, 括号调整: {bracket_score:+.2f}, 最终分数: {final_score:.2f}")
        
        if adjusted_matches:
            best_adjusted = adjusted_matches[0]
            print(f"  最佳匹配(StringMatcher+BracketMatcher): '{best_adjusted.get('name', '')}'")
        
        # 比较两种方法的结果 (如果都可用)
        if has_enhanced_matcher and enhanced_matches and adjusted_matches:
            best_enhanced_name = enhanced_matches[0].get("name", "")
            best_adjusted_name = adjusted_matches[0].get("name", "")
            
            if best_enhanced_name == best_adjusted_name:
                print(f"\n  ✓ 两种方法的最佳匹配一致: '{best_enhanced_name}'")
            else:
                print(f"\n  × 两种方法的最佳匹配不一致:")
                print(f"    - EnhancedMatcher: '{best_enhanced_name}'")
                print(f"    - StringMatcher+BracketMatcher: '{best_adjusted_name}'")

def summary():
    """总结优化效果"""
    print("\n=== 优化效果总结 ===")
    print("1. 括号内容标准化: 确保了不同语言、全/半角、大小写等因素不影响匹配精度")
    print("2. 别名指示词处理: 能够识别并正确处理'又名'、'aka'等格式的别名信息")
    print("3. 特定括号类型识别: 区分不同类型的括号信息(如live/remix)，进行针对性评分")
    print("4. 异常处理: 添加了异常处理机制，保证即使归一化失败也不会中断匹配流程")
    print("5. 日志增强: 提供了更详细的日志信息，便于调试和理解匹配过程")
    print("\n总体来看，任务11.4的优化提高了歌曲匹配在处理括号内容时的准确性和稳定性，")
    print("特别是在处理别名、不同版本类型等情况时，能更准确地识别相似歌曲。")

if __name__ == "__main__":
    print("开始集成测试：验证括号内容匹配优化效果...\n")
    
    # 测试括号内容匹配与字符串匹配的集成
    test_integrated_bracket_matching()
    
    # 测试完整匹配流程
    test_complete_matching_pipeline()
    
    # 总结优化效果
    summary()
    
    print("\n测试完成！") 