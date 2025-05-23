"""
为EnhancedMatcher类添加文本标准化方法的monkey patching脚本
"""

import os
import sys
import logging
from typing import Dict, List, Any, Tuple

# 设置日志级别
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s: %(message)s',
    stream=sys.stdout
)

# 添加项目根目录到系统路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# 导入需要修补的类
from spotify_playlist_importer.utils.enhanced_matcher import EnhancedMatcher
from spotify_playlist_importer.utils.text_normalizer import normalize_text

def standardize_texts(self, input_title: str, input_artists: List[str], 
                      candidates: List[Dict[str, Any]]) -> Tuple[str, List[str], List[Dict[str, Any]]]:
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

def apply_monkey_patch():
    """
    应用monkey patch
    """
    # 添加standardize_texts方法到EnhancedMatcher类
    EnhancedMatcher.standardize_texts = standardize_texts
    
    print("已应用monkey patch，为EnhancedMatcher类添加standardize_texts方法")

if __name__ == "__main__":
    apply_monkey_patch()
    
    # 简单测试
    enhanced_matcher = EnhancedMatcher()
    print(f"EnhancedMatcher有standardize_texts方法: {'standardize_texts' in dir(enhanced_matcher)}") 