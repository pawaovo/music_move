"""
增强匹配器模块更新版本

添加standardize_texts方法，实现Stage 11.1中提到的文本标准化功能
"""

import logging
import sys
import os
from typing import Dict, List, Any, Optional, Tuple, Union
import shutil

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 设置日志级别
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s: %(message)s',
    stream=sys.stdout
)

# 导入必要的模块
from spotify_playlist_importer.utils.text_normalizer import normalize_text, split_text
from spotify_playlist_importer.utils.string_matcher import StringMatcher
from spotify_playlist_importer.utils.bracket_matcher import BracketMatcher

def update_enhanced_matcher_file():
    """
    更新EnhancedMatcher类，添加standardize_texts方法
    """
    # 源文件和目标文件路径
    source_file = 'spotify_playlist_importer/utils/enhanced_matcher.py'
    backup_file = 'spotify_playlist_importer/utils/enhanced_matcher.py.bak'
    
    # 备份原始文件
    if os.path.exists(source_file):
        shutil.copy2(source_file, backup_file)
        print(f"已备份原始文件到 {backup_file}")
    
    # 读取原始文件内容
    with open(source_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 定义要插入的standardize_texts方法
    standardize_texts_method = '''
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
        
        # 标准化输入歌曲标题
        std_title = normalize_text(input_title)
        
        # 标准化输入歌曲艺术家
        std_artists = [normalize_text(artist) for artist in input_artists] if input_artists else []
        
        # 标准化候选歌曲
        std_candidates = []
        for candidate in candidates:
            # 深拷贝候选歌曲，避免修改原始数据
            std_candidate = candidate.copy()
            
            # 保存原始标题和艺术家
            std_candidate['original_name'] = candidate.get('name', '')
            std_candidate['original_artists'] = candidate.get('artists', [])
            
            # 标准化标题
            std_candidate['name'] = normalize_text(candidate.get('name', ''))
            
            # 标准化艺术家
            std_artists_list = []
            for artist in candidate.get('artists', []):
                std_artist = artist.copy()
                std_artist['name'] = normalize_text(artist.get('name', ''))
                std_artists_list.append(std_artist)
            
            std_candidate['artists'] = std_artists_list
            std_candidates.append(std_candidate)
        
        return std_title, std_artists, std_candidates
    '''
    
    # 定义修改后的match方法
    modified_match_method = '''
    def match(self, input_title: str, input_artists: List[str],
              candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        执行歌曲匹配流程
        
        Args:
            input_title: 输入歌曲标题
            input_artists: 输入歌曲艺术家列表
            candidates: 候选歌曲列表
            
        Returns:
            List[Dict[str, Any]]: 匹配结果列表，按匹配分数降序排序
        """
        # 首先标准化所有文本
        std_title, std_artists, std_candidates = self.standardize_texts(input_title, input_artists, candidates)
        
        # 记录输入详情
        self.log_input_details(std_title, std_artists)
        
        # 第一阶段匹配：基于字符串相似度
        first_matches = self.first_stage_match(std_title, std_artists, std_candidates)
        
        # 如果第一阶段没有匹配，返回空列表
        if not first_matches:
            logging.debug(f"第一阶段未找到匹配，所有候选均低于阈值 {self.first_stage_threshold:.2f}")
            return []
        
        # 第二阶段匹配：考虑括号内容
        final_matches = self.second_stage_match(std_title, std_artists, first_matches)
        
        # 如果第二阶段没有匹配，返回空列表
        if not final_matches:
            logging.debug(f"第二阶段未找到匹配，所有候选均低于阈值 {self.low_confidence_threshold:.2f}")
            return []
        
        # 记录最佳匹配的详细信息
        if final_matches:
            self._log_detailed_match_info(std_title, std_artists, final_matches[0])
        
        return final_matches
    '''
    
    # 修改get_enhanced_match函数
    modified_get_enhanced_match = '''
def get_enhanced_match(input_title: str, input_artists: List[str],
                      candidates: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    使用增强匹配器获取最佳匹配
    
    Args:
        input_title: 输入歌曲标题
        input_artists: 输入歌曲艺术家列表
        candidates: 候选歌曲列表
        
    Returns:
        Optional[Dict[str, Any]]: 最佳匹配结果，如果没有匹配则返回None
    """
    matcher = EnhancedMatcher()
    matches = matcher.match(input_title, input_artists, candidates)
    return matches[0] if matches else None
'''
    
    # 查找插入standardize_texts方法的位置
    # 在__init__方法之后插入
    init_end_pattern = "        logging.info(f\"[增强匹配] 初始化匹配器 - 阈值: 第一阶段={first_stage_threshold:.2f}, 第二阶段={second_stage_threshold:.2f}\")"
    content = content.replace(init_end_pattern, init_end_pattern + standardize_texts_method)
    
    # 替换match方法
    match_start_pattern = "    def match(self, input_title: str, input_artists: List[str],"
    match_end_pattern = "        return final_matches"
    
    # 查找match方法的开始和结束
    match_start_index = content.find(match_start_pattern)
    if match_start_index != -1:
        # 查找match方法的结束
        match_end_index = content.find(match_end_pattern, match_start_index)
        if match_end_index != -1:
            # 找到方法的结束括号
            end_bracket_index = content.find("    ", match_end_index + len(match_end_pattern))
            if end_bracket_index != -1:
                # 替换整个方法
                old_match_method = content[match_start_index:end_bracket_index]
                content = content.replace(old_match_method, modified_match_method.strip())
    
    # 替换get_enhanced_match函数
    get_match_start_pattern = "def get_enhanced_match(input_title: str, input_artists: List[str],"
    get_match_end_pattern = "    return matches[0] if matches else None"
    
    # 查找get_enhanced_match函数的开始和结束
    get_match_start_index = content.find(get_match_start_pattern)
    if get_match_start_index != -1:
        # 查找函数的结束
        get_match_end_index = content.find(get_match_end_pattern, get_match_start_index)
        if get_match_end_index != -1:
            # 找到函数的结束括号
            end_bracket_index = content.find("\n", get_match_end_index + len(get_match_end_pattern))
            if end_bracket_index != -1:
                # 替换整个函数
                old_get_match_function = content[get_match_start_index:end_bracket_index]
                content = content.replace(old_get_match_function, modified_get_enhanced_match.strip())
    
    # 写入修改后的内容
    with open(source_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"已更新 {source_file}")
    print("添加了 standardize_texts 方法")
    print("修改了 match 方法以使用 standardize_texts")
    print("修改了 get_enhanced_match 函数")

if __name__ == "__main__":
    update_enhanced_matcher_file() 