"""
直接向EnhancedMatcher类添加standardize_texts方法
"""

import os
import sys
import logging
import types

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

# 导入EnhancedMatcher类
from spotify_playlist_importer.utils.enhanced_matcher import EnhancedMatcher
from spotify_playlist_importer.utils.text_normalizer import normalize_text

def standardize_texts(self, input_title, input_artists, candidates):
    """
    对输入歌曲和候选歌曲进行文本标准化处理
    
    Args:
        input_title: 输入歌曲标题
        input_artists: 输入歌曲艺术家列表
        candidates: 候选歌曲列表
        
    Returns:
        Tuple[str, List[str], List[Dict[str, Any]]]: 标准化后的标题、艺术家列表和候选歌曲
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

# 修补原始match方法，使用标准化处理
def patched_match(self, input_title, input_artists, candidates):
    """
    执行歌曲匹配流程，使用标准化文本处理
    
    Args:
        input_title: 输入歌曲标题
        input_artists: 输入歌曲艺术家列表
        candidates: 候选歌曲列表
        
    Returns:
        List[Dict[str, Any]]: 匹配结果列表，按匹配分数降序排序
    """
    # 首先标准化所有文本
    std_title, std_artists, std_candidates = self.standardize_texts(input_title, input_artists, candidates)
    
    # 调用原始match方法，但使用标准化后的文本
    # 保存原始match方法
    original_match = self.__class__._original_match
    
    # 临时移除standardize_texts，避免无限递归
    temp = self.standardize_texts
    self.standardize_texts = None
    
    try:
        # 使用原始方法处理标准化后的数据
        result = original_match(self, std_title, std_artists, std_candidates)
    finally:
        # 恢复standardize_texts方法
        self.standardize_texts = temp
    
    return result

def apply_monkey_patch():
    """
    将standardize_texts方法添加到EnhancedMatcher类
    """
    print("正在向EnhancedMatcher类添加standardize_texts方法...")
    
    # 检查是否已经应用了补丁
    if hasattr(EnhancedMatcher, '_original_match'):
        print("补丁已经应用，无需重复添加")
        return
    
    # 保存原始match方法
    EnhancedMatcher._original_match = EnhancedMatcher.match
    
    # 添加standardize_texts方法到EnhancedMatcher类
    EnhancedMatcher.standardize_texts = standardize_texts
    
    # 替换match方法
    EnhancedMatcher.match = patched_match
    
    # 检查方法是否已添加
    if hasattr(EnhancedMatcher, 'standardize_texts'):
        print("成功添加standardize_texts方法到EnhancedMatcher类")
    else:
        print("添加standardize_texts方法失败")
    
    # 检查match方法是否已替换
    if EnhancedMatcher.match == patched_match:
        print("成功替换match方法")
    else:
        print("替换match方法失败")

def test_patched_class():
    """
    测试补丁后的EnhancedMatcher类
    """
    print("\n===== 测试补丁后的EnhancedMatcher类 =====")
    
    # 创建实例
    matcher = EnhancedMatcher()
    
    # 检查方法是否存在
    has_method = hasattr(matcher, 'standardize_texts')
    print(f"实例拥有standardize_texts方法: {has_method}")
    
    if not has_method:
        return False
    
    # 准备测试数据
    input_title = "测试歌曲（现场版）"
    input_artists = ["艺术家A", "艺術家B"]
    
    candidates = [
        {
            'name': '測試歌曲 (Live)',
            'artists': [{'name': '藝術家A'}, {'name': '藝術家B'}],
            'id': 'track1'
        }
    ]
    
    try:
        # 测试单独调用standardize_texts方法
        print("\n测试standardize_texts方法...")
        std_title, std_artists, std_candidates = matcher.standardize_texts(input_title, input_artists, candidates)
        
        print(f"标准化结果:")
        print(f"- 原始标题: {input_title} -> 标准化后: {std_title}")
        print(f"- 原始艺术家: {input_artists} -> 标准化后: {std_artists}")
        print(f"- 候选标题: {candidates[0]['name']} -> 标准化后: {std_candidates[0]['name']}")
        
        # 测试match方法
        print("\n测试match方法...")
        matches = matcher.match(input_title, input_artists, candidates)
        
        if matches:
            print(f"匹配成功: {matches[0]['name']} (ID: {matches[0]['id']})")
            return True
        else:
            print("匹配失败: 未找到匹配")
            return False
        
    except Exception as e:
        print(f"测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # 应用monkey patch
    apply_monkey_patch()
    
    # 测试补丁后的类
    result = test_patched_class()
    
    if result:
        print("\n测试成功！EnhancedMatcher类现在可以正常使用standardize_texts方法")
    else:
        print("\n测试失败！请检查错误信息") 