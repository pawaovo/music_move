"""
将monkey patching添加到包的__init__.py中
"""

import os
import sys
import shutil

def install_patch():
    """
    将monkey patching代码添加到包的__init__.py文件中
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 获取文件路径
    utils_init_path = os.path.join(current_dir, 'spotify_playlist_importer', 'utils', '__init__.py')
    backup_path = os.path.join(current_dir, 'spotify_playlist_importer', 'utils', '__init__.py.bak')
    
    # 检查文件是否存在
    if not os.path.exists(utils_init_path):
        print(f"文件不存在: {utils_init_path}")
        return False
    
    # 备份原始文件
    print(f"备份原始文件到 {backup_path}")
    shutil.copy2(utils_init_path, backup_path)
    
    # 读取原始内容
    with open(utils_init_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 构造要添加的代码
    patch_code = '''
# 添加文本标准化功能
import logging
from typing import Dict, List, Any, Tuple
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

# 保存原始match方法
original_match = EnhancedMatcher.match

# 修补match方法
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
    return original_match(self, std_title, std_artists, std_candidates)

# 应用monkey patch
EnhancedMatcher.standardize_texts = standardize_texts
EnhancedMatcher.match = patched_match

print("已添加文本标准化功能到EnhancedMatcher类")
'''
    
    # 添加补丁代码到文件末尾
    if patch_code not in content:
        new_content = content + "\n" + patch_code
        
        # 写入文件
        with open(utils_init_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"补丁已安装到 {utils_init_path}")
        return True
    else:
        print("补丁已经存在，无需重复安装")
        return True

if __name__ == "__main__":
    if install_patch():
        print("安装成功！")
    else:
        print("安装失败！") 