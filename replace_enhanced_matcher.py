"""
替换 EnhancedMatcher 类文件
"""

import os
import shutil
import logging

def replace_enhanced_matcher():
    """
    用完整实现替换 EnhancedMatcher 类文件
    """
    # 获取当前文件路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 获取文件路径
    source_path = os.path.join(current_dir, 'enhanced_matcher_complete.py')
    target_path = os.path.join(current_dir, 'spotify_playlist_importer', 'utils', 'enhanced_matcher.py')
    backup_path = os.path.join(current_dir, 'spotify_playlist_importer', 'utils', 'enhanced_matcher.py.bak2')
    
    # 检查文件是否存在
    if not os.path.exists(source_path):
        print(f"完整实现文件不存在: {source_path}")
        return False
    
    if not os.path.exists(target_path):
        print(f"目标文件不存在: {target_path}")
        return False
    
    # 备份原始文件
    print(f"备份原始文件到 {backup_path}")
    shutil.copy2(target_path, backup_path)
    
    # 复制新文件
    print(f"复制完整实现到 {target_path}")
    shutil.copy2(source_path, target_path)
    
    print("替换成功！")
    return True

if __name__ == "__main__":
    replace_enhanced_matcher() 