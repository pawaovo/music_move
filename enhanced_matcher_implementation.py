"""
EnhancedMatcher 文本标准化功能实现

该文件包含对文本标准化的实现，可以与原有的 EnhancedMatcher 类集成。
用于实现 Stage 11.1 中提到的在评分前对所有文本进行统一标准化处理的功能。
"""

import logging
import sys
import os
from typing import Dict, List, Any, Tuple

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
    std_title = normalize_text(input_title, keep_brackets=True)
    if std_title != input_title:
        logging.debug(f"标准化输入标题: '{input_title}' -> '{std_title}'")
    
    # 标准化输入歌曲艺术家列表
    std_artists = [normalize_text(artist, keep_brackets=True) for artist in input_artists] if input_artists else []
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
        std_title_candidate = normalize_text(title, keep_brackets=True)
        if std_title_candidate != title:
            logging.debug(f"标准化候选标题: '{title}' -> '{std_title_candidate}'")
            std_candidate['original_name'] = title  # 保存原始标题
            std_candidate['name'] = std_title_candidate  # 替换为标准化标题
        
        # 标准化候选歌曲艺术家
        std_artists_candidate = []
        for artist in candidate.get('artists', []):
            artist_name = artist.get('name', '')
            std_artist_name = normalize_text(artist_name, keep_brackets=True)
            
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


def enhanced_match(self, input_title: str, input_artists: List[str],
                   candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    执行完整的两阶段匹配流程，使用标准化文本
    
    Args:
        input_title: 输入歌曲标题
        input_artists: 输入歌曲艺术家列表
        candidates: 候选歌曲列表
        
    Returns:
        List[Dict[str, Any]]: 最佳匹配结果
    """
    # 记录匹配开始
    logging.debug(f"\n===================================================")
    logging.debug(f"开始增强匹配流程: '{input_title}' - {input_artists}")
    logging.debug(f"===================================================")
    
    # 保存原始输入，供日志使用
    self._original_input_title = input_title
    self._original_input_artists = input_artists
    
    # 记录候选数量
    logging.debug(f"待匹配候选: {len(candidates)} 个")
    
    # 首先标准化所有文本
    std_title, std_artists, std_candidates = self.standardize_texts(input_title, input_artists, candidates)
    
    # 记录输入详情
    self.log_input_details(std_title, std_artists)
    
    # 第一阶段：基本字符串匹配
    first_matches = self.first_stage_match(std_title, std_artists, std_candidates)
    
    if not first_matches:
        logging.debug("\n未找到匹配：第一阶段没有候选歌曲通过阈值")
        return []
    
    # 第二阶段：考虑括号内容
    second_matches = self.second_stage_match(std_title, std_artists, first_matches)
    
    if not second_matches:
        logging.debug("\n第二阶段未找到匹配，返回第一阶段最佳结果（标记为低置信度）")
        # 标记为低置信度
        first_matches[0]["similarity_scores"]["is_low_confidence"] = True
        # 返回第一阶段中得分最高的结果
        return [first_matches[0]]
    
    # 记录最终选择的匹配
    if second_matches:
        self._log_detailed_match_info(std_title, std_artists, second_matches[0])
    
    logging.debug(f"===================================================\n")
    return second_matches


def add_standardization_to_enhanced_matcher():
    """
    将文本标准化功能添加到 EnhancedMatcher 类
    
    这个函数修改 EnhancedMatcher 类，添加 standardize_texts 方法，
    并更新 match 方法以使用标准化文本
    """
    import os
    import importlib.util
    
    # 获取当前文件路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 获取 enhanced_matcher.py 文件路径
    enhanced_matcher_path = os.path.join(current_dir, 'spotify_playlist_importer', 'utils', 'enhanced_matcher.py')
    
    try:
        # 修改原始文件
        if os.path.exists(enhanced_matcher_path):
            print(f"找到 EnhancedMatcher 文件: {enhanced_matcher_path}")
            print("准备添加文本标准化功能...")
            
            with open(enhanced_matcher_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否已包含标准化方法
            if "def standardize_texts(" in content:
                print("EnhancedMatcher 类已经包含 standardize_texts 方法，无需修改")
                return True
            
            # 找到插入位置 (在类的__init__方法之后)
            init_pattern = "    def __init__"
            init_pos = content.find(init_pattern)
            if init_pos == -1:
                print("无法找到__init__方法，添加失败")
                return False
                
            # 找到__init__方法的结束位置
            init_end = content.find("    def ", init_pos + len(init_pattern))
            if init_end == -1:
                print("无法找到__init__方法的结束位置，添加失败")
                return False
            
            # 获取standardize_texts方法的代码
            std_func_str = "\n" + inspect.getsource(standardize_texts).replace("def standardize_texts(self", "    def standardize_texts(self")
            
            # 插入standardize_texts方法
            new_content = content[:init_end] + std_func_str + content[init_end:]
            
            # 查找match方法是否需要修改
            match_pattern = "    def match(self, input_title: str, input_artists: List[str],"
            match_pos = new_content.find(match_pattern)
            
            if match_pos == -1:
                print("无法找到match方法，不进行修改")
            else:
                # 查找match方法内是否已包含文本标准化调用
                match_content = new_content[match_pos:new_content.find("    def ", match_pos + len(match_pattern))]
                
                if "standardize_texts" not in match_content:
                    print("检测到match方法未使用标准化，准备修改...")
                    # 获取enhanced_match方法的代码
                    enhanced_match_str = inspect.getsource(enhanced_match).replace("def enhanced_match(self", "    def match(self")
                    
                    # 替换match方法
                    new_content = new_content[:match_pos] + enhanced_match_str + new_content[match_pos + len(match_content):]
            
            # 写入修改后的内容
            print("写入修改后的文件...")
            with open(enhanced_matcher_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
                
            print("文本标准化功能已成功添加到 EnhancedMatcher 类")
            return True
            
        else:
            print(f"未找到 EnhancedMatcher 文件: {enhanced_matcher_path}")
            return False
    
    except Exception as e:
        print(f"添加文本标准化功能失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def direct_edit_enhanced_matcher():
    """
    直接编辑 EnhancedMatcher 文件，添加 standardize_texts 方法
    """
    import os
    
    # 获取当前文件路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 获取 enhanced_matcher.py 文件路径
    enhanced_matcher_path = os.path.join(current_dir, 'spotify_playlist_importer', 'utils', 'enhanced_matcher.py')
    
    if not os.path.exists(enhanced_matcher_path):
        print(f"未找到 EnhancedMatcher 文件: {enhanced_matcher_path}")
        return False
        
    print(f"找到 EnhancedMatcher 文件: {enhanced_matcher_path}")
    print("准备添加文本标准化功能...")
    
    # 读取文件内容
    with open(enhanced_matcher_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已包含标准化方法
    if "def standardize_texts(" in content:
        print("EnhancedMatcher 类已经包含 standardize_texts 方法，无需修改")
        return True
    
    # 添加standardize_texts方法
    standardize_method = """
    def standardize_texts(self, input_title: str, input_artists: List[str], 
                          candidates: List[Dict[str, Any]]) -> Tuple[str, List[str], List[Dict[str, Any]]]:
        \"\"\"
        对输入歌曲和候选歌曲进行文本标准化处理
        
        Args:
            input_title: 输入歌曲标题
            input_artists: 输入歌曲艺术家列表
            candidates: 候选歌曲列表
            
        Returns:
            Tuple[str, List[str], List[Dict[str, Any]]]: 标准化后的标题、艺术家列表和候选歌曲
        \"\"\"
        # 保存原始输入，以便在日志和调试中使用
        self._original_input_title = input_title
        self._original_input_artists = input_artists.copy() if input_artists else []
        
        # 记录原始输入
        logging.debug(f"开始统一文本标准化: 输入标题='{input_title}', 艺术家={input_artists}, 候选数量={len(candidates)}")
        
        # 标准化输入歌曲标题
        std_title = normalize_text(input_title, keep_brackets=True)
        if std_title != input_title:
            logging.debug(f"标准化输入标题: '{input_title}' -> '{std_title}'")
        
        # 标准化输入歌曲艺术家列表
        std_artists = [normalize_text(artist, keep_brackets=True) for artist in input_artists] if input_artists else []
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
            std_title_candidate = normalize_text(title, keep_brackets=True)
            if std_title_candidate != title:
                logging.debug(f"标准化候选标题: '{title}' -> '{std_title_candidate}'")
                std_candidate['original_name'] = title  # 保存原始标题
                std_candidate['name'] = std_title_candidate  # 替换为标准化标题
            
            # 标准化候选歌曲艺术家
            std_artists_candidate = []
            for artist in candidate.get('artists', []):
                artist_name = artist.get('name', '')
                std_artist_name = normalize_text(artist_name, keep_brackets=True)
                
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
    """
    
    # 定义修改后的match方法
    modified_match = """
    def match(self, input_title: str, input_artists: List[str],
              candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        \"\"\"
        执行歌曲匹配流程
        
        Args:
            input_title: 输入歌曲标题
            input_artists: 输入歌曲艺术家列表
            candidates: 候选歌曲列表
            
        Returns:
            List[Dict[str, Any]]: 匹配结果列表，按匹配分数降序排序
        \"\"\"
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
    """
    
    # 查找位置插入 standardize_texts 方法
    # 在类的__init__方法之后
    init_pattern = "    def __init__"
    init_pos = content.find(init_pattern)
    if init_pos == -1:
        print("无法找到__init__方法，添加失败")
        return False
        
    # 找到__init__方法的结束位置
    init_end = content.find("    def ", init_pos + len(init_pattern))
    if init_end == -1:
        print("无法找到__init__方法的结束位置，添加失败")
        return False
    
    # 插入standardize_texts方法
    new_content = content[:init_end] + standardize_method + content[init_end:]
    
    # 查找并替换match方法
    match_pattern = "    def match(self, input_title: str, input_artists: List[str],"
    match_pos = new_content.find(match_pattern)
    
    if match_pos == -1:
        print("无法找到match方法，不进行修改")
    else:
        # 查找match方法的结束位置
        next_method = new_content.find("    def ", match_pos + len(match_pattern))
        if next_method == -1:
            print("无法找到match方法的结束位置，不进行修改")
        else:
            # 替换match方法
            match_content = new_content[match_pos:next_method]
            new_content = new_content[:match_pos] + modified_match + new_content[next_method:]
    
    # 写入文件
    print("写入修改后的文件...")
    with open(enhanced_matcher_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("文本标准化功能已成功添加到 EnhancedMatcher 类")
    return True


if __name__ == "__main__":
    # 添加文本标准化功能到 EnhancedMatcher 类
    print("开始向 EnhancedMatcher 添加文本标准化功能...")
    
    try:
        import inspect
        success = add_standardization_to_enhanced_matcher()
    except Exception as e:
        print(f"使用动态方法添加失败，尝试直接编辑文件: {e}")
        success = direct_edit_enhanced_matcher()
    
    if success:
        print("文本标准化功能已成功添加到 EnhancedMatcher 类")
    else:
        print("文本标准化功能添加失败")
    
    print("完成") 