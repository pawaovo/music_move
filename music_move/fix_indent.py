#!/usr/bin/env python
"""
修复sync_client.py中的缩进错误
"""

import re

# 定义文件路径
file_path = "spotify_playlist_importer/spotify_playlist_importer/spotify/sync_client.py"

# 读取文件内容
with open(file_path, 'r', encoding='utf-8') as file:
    content = file.read()

# 查找并修复缩进错误
pattern = r'return result, error\s+except Exception as e:'
replacement = 'return result, error\n    except Exception as e:'

new_content = re.sub(pattern, replacement, content)

# 保存修复后的文件
with open(file_path, 'w', encoding='utf-8') as file:
    file.write(new_content)

print(f"已修复 {file_path} 中的缩进错误") 