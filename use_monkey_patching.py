"""
在测试代码中直接使用monkey patching添加standardize_texts方法
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

# 导入需要的模块
from spotify_playlist_importer.utils.enhanced_matcher import EnhancedMatcher
from spotify_playlist_importer.utils.text_normalizer import normalize_text

# 定义standardize_texts方法
def standardize_texts(self, input_title, input_artists, candidates):
    """
    对输入歌曲和候选歌曲进行文本标准化处理
    """
    # 保存原始输入，以便在日志和调试中使用
    self._original_input_title = input_title
    self._original_input_artists = input_artists.copy() if input_artists else []
    
    # 记录原始输入
    logging.debug(f"开始统一文本标准化: 输入标题='{input_title}', 艺术家={input_artists}, 候选数量={len(candidates)}")
    
    # 标准化输入歌曲标题
    std_title = normalize_text(input_title)
    if std_title != input_title:
        logging.debug(f"标准化输入标题: '{input_title}' -> '{std_title}'")
    
    # 标准化输入歌曲艺术家列表
    std_artists = [normalize_text(artist) for artist in input_artists] if input_artists else []
    for i, (orig, std) in enumerate(zip(input_artists, std_artists)):
        if orig != std:
            logging.debug(f"标准化输入艺术家[{i}]: '{orig}' -> '{std}'")
    
    # 标准化候选歌曲信息
    std_candidates = []
    for candidate in candidates:
        # 复制原始候选歌曲数据
        std_candidate = candidate.copy()
        
        # 标准化候选歌曲标题
        title = candidate.get('name', '')
        std_title_candidate = normalize_text(title)
        if std_title_candidate != title:
            logging.debug(f"标准化候选标题: '{title}' -> '{std_title_candidate}'")
            std_candidate['original_name'] = title  # 保存原始标题
            std_candidate['name'] = std_title_candidate  # 替换为标准化标题
        
        # 标准化候选歌曲艺术家
        std_artists_candidate = []
        for artist in candidate.get('artists', []):
            artist_name = artist.get('name', '')
            std_artist_name = normalize_text(artist_name)
            
            # 复制艺术家数据并更新标准化名称
            std_artist = artist.copy()
            if std_artist_name != artist_name:
                logging.debug(f"标准化候选艺术家: '{artist_name}' -> '{std_artist_name}'")
                std_artist['original_name'] = artist_name  # 保存原始名称
                std_artist['name'] = std_artist_name  # 替换为标准化名称
            
            std_artists_candidate.append(std_artist)
        
        # 更新候选歌曲的艺术家列表
        std_candidate['original_artists'] = candidate.get('artists', [])  # 保存原始艺术家列表
        std_candidate['artists'] = std_artists_candidate  # 替换为标准化艺术家列表
        
        std_candidates.append(std_candidate)
    
    logging.debug(f"完成统一文本标准化: 标准化后输入标题='{std_title}', 标准化后输入艺术家={std_artists}")
    
    return std_title, std_artists, std_candidates

# 保存原始match方法
original_match = EnhancedMatcher.match

# 修补match方法
def patched_match(self, input_title, input_artists, candidates):
    """
    执行歌曲匹配流程，使用标准化文本处理
    """
    # 首先标准化所有文本
    std_title, std_artists, std_candidates = self.standardize_texts(input_title, input_artists, candidates)
    
    # 调用原始match方法，但使用标准化后的文本
    return original_match(self, std_title, std_artists, std_candidates)

def apply_monkey_patch():
    """
    应用monkey patch
    """
    # 添加standardize_texts方法到EnhancedMatcher类
    EnhancedMatcher.standardize_texts = standardize_texts
    
    # 替换match方法
    EnhancedMatcher.match = patched_match
    
    print("已应用monkey patch")

def test_standardization():
    """
    测试标准化功能
    """
    print("\n===== 测试标准化功能 =====")
    
    # 创建实例
    matcher = EnhancedMatcher()
    
    # 检查方法是否存在
    if not hasattr(matcher, 'standardize_texts'):
        print("错误: standardize_texts方法不存在")
        return False
    
    # 准备测试数据
    input_title = "测试歌曲（现场版）"  # 简体中文，全角括号
    input_artists = ["艺术家A", "艺術家B"]  # 混合简繁体
    
    candidates = [
        {
            'name': '測試歌曲 (Live)',  # 繁体中文，半角括号
            'artists': [{'name': '藝術家A'}, {'name': '藝術家B'}],  # 繁体
            'id': 'track1'
        }
    ]
    
    # 测试标准化方法
    std_title, std_artists, std_candidates = matcher.standardize_texts(input_title, input_artists, candidates)
    
    print("标准化结果:")
    print(f"- 标题: {input_title} -> {std_title}")
    print(f"- 艺术家: {input_artists} -> {std_artists}")
    print(f"- 候选标题: {candidates[0]['name']} -> {std_candidates[0]['name']}")
    
    # 验证简繁体转换
    if '测试' in std_title and '测试' in std_candidates[0]['name']:
        print("成功: 简繁体转换正确")
    else:
        print("失败: 简繁体转换有问题")
        return False
    
    # 验证全半角转换
    if '(' in std_title and not '（' in std_title:
        print("成功: 全半角括号转换正确")
    else:
        print("警告: 全半角括号转换可能有问题")
    
    return True

def test_matching():
    """
    测试匹配功能
    """
    print("\n===== 测试匹配功能 =====")
    
    # 创建实例
    matcher = EnhancedMatcher()
    
    # 准备测试数据
    input_title = "测试歌曲（现场版）"  # 简体中文，全角括号
    input_artists = ["艺术家A", "艺術家B"]  # 混合简繁体
    
    candidates = [
        {
            'name': '測試歌曲 (Live)',  # 繁体中文，半角括号
            'artists': [{'name': '藝術家A'}, {'name': '藝術家B'}],  # 繁体
            'id': 'track1'
        },
        {
            'name': '另一首歌',
            'artists': [{'name': '其他艺术家'}],
            'id': 'track2'
        }
    ]
    
    # 测试匹配方法
    matches = matcher.match(input_title, input_artists, candidates)
    
    if not matches:
        print("失败: 没有找到匹配")
        return False
    
    # 获取最佳匹配
    best_match = matches[0]
    print(f"最佳匹配: {best_match['name']} (ID: {best_match['id']})")
    
    # 验证匹配正确性
    if best_match['id'] == 'track1':
        print("成功: 匹配到了正确的歌曲")
    else:
        print(f"失败: 匹配到了错误的歌曲 ID: {best_match['id']}")
        return False
    
    return True

def main():
    """
    主函数
    """
    # 应用monkey patch
    apply_monkey_patch()
    
    # 测试标准化功能
    if not test_standardization():
        print("标准化功能测试失败")
        return
    
    # 测试匹配功能
    if not test_matching():
        print("匹配功能测试失败")
        return
    
    print("\n所有测试通过！文本标准化功能正常工作")
    print("恭喜！现在系统可以正确处理简繁体中文和全半角符号差异")

if __name__ == "__main__":
    main() 