#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
修复enhanced_matcher.py文件中的缩进问题
"""

def fix_indentation_in_file():
    input_file = "spotify_playlist_importer/utils/enhanced_matcher.py"
    output_file = "spotify_playlist_importer/utils/enhanced_matcher_fixed.py"
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 找到并修复第224行附近的问题
    for i in range(len(lines)):
        # 检查第224行的问题
        if i >= 220 and i <= 225 and "else:" in lines[i] and "logging.debug" in lines[i+1]:
            print(f"检测到问题行: {i+1}")
            indent = " " * 12  # 正确的缩进级别
            # 修复else行的缩进
            lines[i] = f"{indent}else:\n"
            # 修复下一行的缩进
            lines[i+1] = f"{indent}    logging.debug(\"[输入歌曲] 艺术家: 无\")\n"
    
    # 写入新文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"已修复文件并保存为: {output_file}")

if __name__ == "__main__":
    fix_indentation_in_file() 