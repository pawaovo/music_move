"""
调试脚本，测试文本标准化功能
"""

import logging
import sys
import os
import importlib.util
from typing import Dict, List, Any, Optional, Tuple

# 设置日志级别
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s: %(message)s',
    stream=sys.stdout
)

# 直接导入text_normalizer模块
text_normalizer_path = os.path.join('spotify_playlist_importer', 'utils', 'text_normalizer.py')
spec = importlib.util.spec_from_file_location("text_normalizer", text_normalizer_path)
text_normalizer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(text_normalizer)

# 获取normalize_text函数
normalize_text = text_normalizer.normalize_text
split_text = text_normalizer.split_text

def standardize_texts(input_title: str, input_artists: List[str], 
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
    original_input_title = input_title
    original_input_artists = input_artists.copy() if input_artists else []
    
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

def test_standardize_texts():
    """测试standardize_texts方法"""
    print("=== 测试文本标准化 ===")
    
    # 创建测试数据
    input_title = "Perfect Match (Live)"
    input_artists = ["Artist1", "Artist2"]
    
    candidates = [
        {
            'name': 'Perfect Match',
            'artists': [{'name': 'Artist1'}, {'name': 'Artist2'}],
            'id': 'track1'
        },
        {
            'name': 'Perfect Match (Live)',
            'artists': [{'name': 'Artist1'}, {'name': 'Artist2'}],
            'id': 'track2'
        }
    ]
    
    # 执行标准化
    std_title, std_artists, std_candidates = standardize_texts(input_title, input_artists, candidates)
    
    # 显示标准化结果
    print(f"\n原始输入: 标题='{input_title}', 艺术家={input_artists}")
    print(f"标准化结果: 标题='{std_title}', 艺术家={std_artists}")
    print("\n标准化后的候选歌曲:")
    for i, candidate in enumerate(std_candidates):
        print(f"  候选 #{i+1}: '{candidate['name']}' - {[a['name'] for a in candidate['artists']]}")
        if 'original_name' in candidate:
            print(f"    原始标题: '{candidate['original_name']}'")

def test_chinese_text_standardization():
    """测试中文文本标准化"""
    print("\n=== 测试中文文本标准化 ===")
    
    # 创建测试数据
    input_title = "完美匹配 (现场版)"
    input_artists = ["艺术家１", "艺术家２"]
    
    candidates = [
        {
            'name': '完美匹配',
            'artists': [{'name': '艺术家１'}, {'name': '艺术家２'}],
            'id': 'track1'
        },
        {
            'name': '完美匹配 (现场版)',
            'artists': [{'name': '艺术家１'}, {'name': '艺术家２'}],
            'id': 'track2'
        }
    ]
    
    # 执行标准化
    std_title, std_artists, std_candidates = standardize_texts(input_title, input_artists, candidates)
    
    # 显示标准化结果
    print(f"\n原始输入: 标题='{input_title}', 艺术家={input_artists}")
    print(f"标准化结果: 标题='{std_title}', 艺术家={std_artists}")
    print("\n标准化后的候选歌曲:")
    for i, candidate in enumerate(std_candidates):
        print(f"  候选 #{i+1}: '{candidate['name']}' - {[a['name'] for a in candidate['artists']]}")
        if 'original_name' in candidate:
            print(f"    原始标题: '{candidate['original_name']}'")

def test_text_split():
    """测试文本分割"""
    print("\n=== 测试文本分割 ===")
    
    # 创建测试数据
    titles = [
        "Perfect Match (Live)",
        "完美匹配 (现场版)",
        "Song Title (feat. Artist X) [Live]",
        "Song Title - Remix",
        "Song Title"
    ]
    
    # 测试分割
    for title in titles:
        main_title, brackets = split_text(title)
        print(f"原始标题: '{title}'")
        print(f"分割结果: 主要标题='{main_title}', 括号内容={brackets}")
        print()

if __name__ == "__main__":
    test_standardize_texts()
    test_chinese_text_standardization()
    test_text_split()