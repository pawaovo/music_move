"""
永久更新EnhancedMatcher类文件，添加standardize_texts方法
"""

import os
import re
import shutil
import logging

# 设置日志级别
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)

def update_enhanced_matcher():
    """
    更新EnhancedMatcher类文件，添加standardize_texts方法
    """
    # 获取当前文件路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 定义文件路径
    matcher_path = os.path.join(current_dir, 'spotify_playlist_importer', 'utils', 'enhanced_matcher.py')
    backup_path = os.path.join(current_dir, 'spotify_playlist_importer', 'utils', 'enhanced_matcher.py.bak')
    
    # 检查文件是否存在
    if not os.path.exists(matcher_path):
        logging.error(f"找不到EnhancedMatcher文件: {matcher_path}")
        return False
    
    # 创建备份
    logging.info(f"创建备份: {backup_path}")
    shutil.copy2(matcher_path, backup_path)
    
    # 读取文件内容
    with open(matcher_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已经包含standardize_texts方法
    if 'def standardize_texts' in content:
        logging.info("EnhancedMatcher已经包含standardize_texts方法，无需更新")
        return True
    
    # 检查导入部分
    if 'from spotify_playlist_importer.utils.text_normalizer import normalize_text' not in content:
        # 添加normalize_text导入
        import_match = re.search(r'import\s+[^\n]+\n\n', content)
        if import_match:
            insert_pos = import_match.end()
            content = content[:insert_pos] + 'from spotify_playlist_importer.utils.text_normalizer import normalize_text\n' + content[insert_pos:]
            logging.info("添加了normalize_text导入")
        else:
            logging.warning("无法找到适合插入导入语句的位置")
    
    # 查找位置插入standardize_texts方法
    # 通常在__init__方法之后，match方法之前
    match_method_match = re.search(r'def\s+match\s*\(', content)
    if not match_method_match:
        logging.error("无法找到match方法，无法添加standardize_texts方法")
        return False
    
    # 查找match方法之前的位置
    insert_pos = match_method_match.start()
    
    # 构造standardize_texts方法
    standardize_method = '''
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
    '''
    
    # 插入standardize_texts方法
    content = content[:insert_pos] + standardize_method + content[insert_pos:]
    logging.info("添加了standardize_texts方法")
    
    # 修改原始match方法以使用标准化文本
    # 找到match方法开始位置
    match_def_start = match_method_match.start()
    
    # 找到match方法的函数体开始位置（左大括号之后）
    match_body_start_match = re.search(r'def\s+match\s*\([^)]*\).*?:', content[match_def_start:])
    if not match_body_start_match:
        logging.error("无法找到match方法的函数体开始位置")
        return False
    
    match_body_start = match_def_start + match_body_start_match.end()
    
    # 查找记录日志的第一条语句
    log_match = re.search(r'\s+self\.log_input_details', content[match_body_start:])
    if not log_match:
        logging.warning("无法找到match方法中的log_input_details调用，可能已经修改过")
    else:
        # 找到插入标准化调用的位置（在log_input_details之前）
        insert_pos = match_body_start + log_match.start()
        
        # 构造标准化调用代码
        standardize_call = '''
        # 首先标准化所有文本
        std_title, std_artists, std_candidates = self.standardize_texts(input_title, input_artists, candidates)
        
'''
        
        # 修改match方法以使用标准化文本
        updated_content = content[:insert_pos] + standardize_call + content[insert_pos:]
        
        # 替换input_title, input_artists, candidates为std_version
        updated_content = updated_content.replace("self.log_input_details(input_title, input_artists)",
                                           "self.log_input_details(std_title, std_artists)")
        
        # 替换第一阶段匹配调用参数
        updated_content = re.sub(
            r'self\.first_stage_match\(input_title, input_artists, candidates\)',
            r'self.first_stage_match(std_title, std_artists, std_candidates)',
            updated_content
        )
        
        content = updated_content
        logging.info("修改了match方法以使用standardize_texts")
    
    # 写入更新后的文件
    with open(matcher_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    logging.info(f"成功更新EnhancedMatcher文件: {matcher_path}")
    return True

if __name__ == "__main__":
    if update_enhanced_matcher():
        print("成功更新EnhancedMatcher类，添加了standardize_texts方法")
    else:
        print("更新EnhancedMatcher类失败") 