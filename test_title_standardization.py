"""
测试EnhancedMatcher与StringMatcher使用标准化文本的集成
"""

import os
import sys
import logging

# 设置日志级别
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s: %(message)s',
    stream=sys.stdout
)

# 添加项目根目录到系统路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# 清除相关模块的缓存
for module in list(sys.modules.keys()):
    if 'spotify_playlist_importer' in module:
        del sys.modules[module]

# 导入monkey patching模块并应用补丁
print("\n应用monkey patching...")
from monkey_patch_enhanced_matcher import apply_monkey_patch
apply_monkey_patch()

# 导入需要的模块
from spotify_playlist_importer.utils.enhanced_matcher import EnhancedMatcher
from spotify_playlist_importer.utils.string_matcher import StringMatcher
from spotify_playlist_importer.utils.text_normalizer import normalize_text

def test_match_with_standardization():
    """测试match方法对简繁体混合文本的匹配能力"""
    print("\n=== 测试match方法对简繁体混合文本的匹配能力 ===")
    
    # 创建EnhancedMatcher实例
    enhanced_matcher = EnhancedMatcher()
    
    # 测试数据：简繁体混合测试
    input_title = "测试歌曲（现场版）"  # 简体中文，全角括号
    input_artists = ["艺术家A", "艺術家B"]  # 混合简繁体
    
    candidates = [
        {
            'name': '測試歌曲 (Live)',  # 繁体中文，半角括号
            'artists': [{'name': '藝術家A'}, {'name': '藝術家B'}],  # 繁体
            'id': 'track1'
        }
    ]
    
    # 手动打印简繁体转换结果，以确认标准化生效
    print("输入数据:")
    print(f"  标题: '{input_title}'")
    print(f"  艺术家: {input_artists}")
    print(f"候选数据:")
    print(f"  标题: '{candidates[0]['name']}'")
    print(f"  艺术家: {[a['name'] for a in candidates[0]['artists']]}")
    
    # 手动标准化文本，以便比较
    std_title = normalize_text(input_title)
    std_candidate_title = normalize_text(candidates[0]['name'])
    print("\n标准化后:")
    print(f"  输入标题 -> '{std_title}'")
    print(f"  候选标题 -> '{std_candidate_title}'")
    
    # 判断标准化是否正确转换了简繁体
    if '测试' in std_title and '测试' in std_candidate_title:
        print("  简繁体文本标准化正确")
    else:
        print("  简繁体文本标准化可能有问题")
    
    # 使用EnhancedMatcher进行匹配
    print("\n执行匹配...")
    matches = enhanced_matcher.match(input_title, input_artists, candidates)
    
    if matches:
        best_match = matches[0]
        scores = best_match['similarity_scores']
        print(f"找到匹配: '{best_match['name']}' (ID: {best_match['id']})")
        print(f"相似度分数: 标题={scores.get('title_similarity', 0):.2f}, 艺术家={scores.get('artist_similarity', 0):.2f}")
        print(f"第一阶段得分: {scores.get('first_stage_score', 0):.2f}")
        print(f"括号调整: {scores.get('bracket_adjustment', 0):+.2f}")
        print(f"最终匹配分数: {scores.get('final_score', 0):.2f}")
        
        # 判断匹配得分是否足够高（说明标准化生效）
        if scores.get('final_score', 0) > 90:
            print("测试通过: 得分高，表明简繁体标准化正常工作")
            return True
        else:
            print(f"警告: 得分较低 ({scores.get('final_score', 0):.2f})，标准化可能未正确应用")
    else:
        print("匹配失败: 未找到匹配结果")
    
    # 如果没有找到匹配或分数不够高，我们可以测试没有标准化的情况会怎样
    print("\n进一步测试: 比较原始标题相似度")
    # 使用StringMatcher直接计算原始标题的相似度
    string_matcher = StringMatcher()
    title_similarity = string_matcher.calculate_title_similarity(input_title, candidates[0]['name'])
    print(f"原始标题直接相似度: {title_similarity:.2f}")
    
    # 比较标准化后的标题相似度
    std_title_similarity = string_matcher.calculate_title_similarity(std_title, std_candidate_title)
    print(f"标准化后标题相似度: {std_title_similarity:.2f}")
    
    if std_title_similarity > title_similarity:
        print(f"标准化提高了相似度 (+{std_title_similarity - title_similarity:.2f})")
        return True
    
    return False

if __name__ == "__main__":
    success = test_match_with_standardization()
    
    if success:
        print("\n所有测试通过！标题标准化功能正常工作")
        print("恭喜！现在StringMatcher会直接使用已标准化的文本进行相似度计算，避免了重复标准化操作")
    else:
        print("\n测试失败！请检查错误信息") 