"""
创建一个完整的 EnhancedMatcher 类文件，包含 standardize_texts 方法
用于在测试之后替换原始文件
"""

import os
import shutil
import logging
import traceback
import re

def fix_enhanced_matcher():
    """
    修复 EnhancedMatcher 类，添加 standardize_texts 方法
    """
    try:
        # 获取当前文件路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 获取 enhanced_matcher.py 文件路径
        source_path = os.path.join(current_dir, 'spotify_playlist_importer', 'utils', 'enhanced_matcher.py')
        backup_path = os.path.join(current_dir, 'spotify_playlist_importer', 'utils', 'enhanced_matcher.py.bak')
        
        if not os.path.exists(source_path):
            print(f"未找到 EnhancedMatcher 文件: {source_path}")
            return False
        
        print(f"找到 EnhancedMatcher 文件: {source_path}")
        
        # 备份原始文件
        print(f"备份原始文件到 {backup_path}")
        shutil.copy2(source_path, backup_path)
        
        # 读取原始文件内容
        with open(source_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查导入
        if "from typing import" in content and "Tuple" not in content:
            content = content.replace("from typing import", "from typing import Tuple, ")
        elif "from typing import" not in content:
            # 添加导入
            content = "from typing import Tuple, Dict, List, Any\n" + content
        
        # 使用正则表达式检查是否已添加 standardize_texts 方法
        if re.search(r'def\s+standardize_texts\s*\(', content):
            print("EnhancedMatcher 类已经包含 standardize_texts 方法，无需修改")
            return True
        
        # 使用正则表达式查找 class EnhancedMatcher 位置
        class_match = re.search(r'class\s+EnhancedMatcher', content)
        if not class_match:
            print("未找到 EnhancedMatcher 类定义")
            return False
        
        class_index = class_match.start()
        
        # 查找导入部分
        import_section = content[:class_index]
        
        # 查找类定义
        class_definition = content[class_index:]
        
        # 使用正则表达式在类中找到 __init__ 方法
        init_match = re.search(r'    def __init__\s*\(', class_definition)
        if not init_match:
            print("未找到 __init__ 方法")
            return False
        
        init_start = init_match.start()
        
        # 找到下一个方法开始的位置
        next_method_match = re.search(r'    def\s+', class_definition[init_start + 10:])
        if not next_method_match:
            print("未找到 __init__ 方法的结束位置")
            return False
        
        init_end = init_start + 10 + next_method_match.start()
        
        # 插入 standardize_texts 方法
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
        
        # 使用正则表达式查找原始 match 方法
        match_match = re.search(r'    def match\s*\(\s*self\s*,\s*input_title\s*:\s*str\s*,\s*input_artists\s*:\s*List\s*\[\s*str\s*\]\s*,', class_definition)
        if not match_match:
            print("未找到 match 方法，将只添加 standardize_texts 方法")
            # 构建新的类定义，只添加 standardize_texts 方法
            new_class_definition = class_definition[:init_end] + standardize_method + class_definition[init_end:]
        else:
            match_start = match_match.start()
            
            # 找到下一个方法开始的位置
            next_method_match = re.search(r'    def\s+', class_definition[match_start + 10:])
            if not next_method_match:
                # 可能是类的最后一个方法
                match_end = len(class_definition)
            else:
                match_end = match_start + 10 + next_method_match.start()
            
            # 修改后的 match 方法
            match_method = """
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
            
            # 构建新的类定义，添加 standardize_texts 方法并修改 match 方法
            new_class_definition = class_definition[:init_end] + standardize_method + class_definition[init_end:match_start] + match_method + class_definition[match_end:]
        
        # 确保 normalize_text 被正确导入
        if "from spotify_playlist_importer.utils.text_normalizer import normalize_text" not in import_section:
            import_section = import_section + "\nfrom spotify_playlist_importer.utils.text_normalizer import normalize_text, split_text\n"
        
        # 构建新的文件内容
        new_content = import_section + new_class_definition
        
        # 写入文件
        with open(source_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"已更新 {source_path}")
        print("已添加 standardize_texts 方法")
        
        if match_match:
            print("已修改 match 方法以使用标准化文本")
        
        return True
    
    except Exception as e:
        print(f"修复过程中出现错误: {e}")
        traceback.print_exc()
        return False

def update_get_enhanced_match():
    """
    更新 get_enhanced_match 函数以适配标准化文本
    """
    try:
        # 获取当前文件路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 获取 enhanced_matcher.py 文件路径
        source_path = os.path.join(current_dir, 'spotify_playlist_importer', 'utils', 'enhanced_matcher.py')
        
        if not os.path.exists(source_path):
            print(f"未找到 EnhancedMatcher 文件: {source_path}")
            return False
        
        # 读取文件内容
        with open(source_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找 get_enhanced_match 函数
        match = re.search(r'def get_enhanced_match\s*\(', content)
        if not match:
            print("未找到 get_enhanced_match 函数，跳过更新")
            return True
        
        # 查找函数体的起始和结束位置
        start_pos = match.start()
        
        # 查找下一个函数定义或类定义
        next_def = re.search(r'(def|class)\s+', content[start_pos + 10:])
        if next_def:
            end_pos = start_pos + 10 + next_def.start()
        else:
            end_pos = len(content)
        
        # 提取现有函数体
        func_body = content[start_pos:end_pos]
        
        # 更新后的函数体
        updated_func = """def get_enhanced_match(input_title: str, input_artists: List[str], candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    \"\"\"
    使用增强匹配器获取最佳匹配结果
    
    Args:
        input_title: 输入歌曲标题
        input_artists: 输入歌曲艺术家列表
        candidates: 候选歌曲列表
        
    Returns:
        Dict[str, Any]: 最佳匹配结果，如果没有匹配则返回None
    \"\"\"
    matcher = EnhancedMatcher()
    matches = matcher.match(input_title, input_artists, candidates)
    return matches[0] if matches else None
"""
        
        # 替换函数体
        new_content = content[:start_pos] + updated_func + content[end_pos:]
        
        # 写入文件
        with open(source_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("已更新 get_enhanced_match 函数")
        return True
    
    except Exception as e:
        print(f"更新 get_enhanced_match 函数时出现错误: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("开始修复 EnhancedMatcher 类...")
    success = fix_enhanced_matcher()
    
    if success:
        print("正在更新 get_enhanced_match 函数...")
        update_success = update_get_enhanced_match()
        if update_success:
            print("修复成功完成")
        else:
            print("更新 get_enhanced_match 函数失败")
    else:
        print("修复失败") 