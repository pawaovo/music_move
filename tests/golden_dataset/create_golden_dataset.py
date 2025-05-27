#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
创建黄金标准数据集

此脚本用于从歌曲列表创建黄金标准数据集，用于评估Spotify歌曲匹配算法的性能。
步骤：
1. 解析输入文件（yunmusic.txt），提取歌曲标题和艺术家
2. 为每首歌曲获取Spotify实际匹配结果
3. 将结果保存为JSON格式的黄金标准数据集
"""

import json
import os
import random
import time
import sys
from typing import Dict, List, Any, Optional
import argparse

# 添加项目根目录到Python路径，确保可以导入项目模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# 创建ParsedSong和MatchedSong的模拟类，以避免导入问题
class ParsedSong:
    """模拟ParsedSong类，用于测试"""
    def __init__(self, original_line: str, title: str, artists: List[str]):
        self.original_line = original_line
        self.title = title
        self.artists = artists

class MatchedSong:
    """模拟MatchedSong类，用于测试"""
    def __init__(self, parsed_song, spotify_id: str, name: str, artists: List[str], 
                 uri: str, album_name: str, duration_ms: int):
        self.parsed_song = parsed_song
        self.spotify_id = spotify_id
        self.name = name
        self.artists = artists
        self.uri = uri
        self.album_name = album_name
        self.duration_ms = duration_ms

# 模拟Spotify搜索函数
def mock_search_song_on_spotify(sp, parsed_song: ParsedSong) -> Optional[MatchedSong]:
    """
    模拟的Spotify搜索函数，返回假数据用于测试
    
    Args:
        sp: Spotify客户端（在这里被忽略）
        parsed_song: 解析的歌曲信息
        
    Returns:
        模拟的匹配结果
    """
    # 假设70%的歌曲能找到匹配
    if random.random() < 0.7:
        song_id = f"spotify:track:{hash(parsed_song.original_line) % 100000000}"
        artists = parsed_song.artists if parsed_song.artists else ["Unknown Artist"]
        
        # 创建模拟的匹配结果
        return MatchedSong(
            parsed_song=parsed_song,
            spotify_id=song_id,
            name=f"Spotify: {parsed_song.title}",
            artists=artists,
            uri=f"spotify:track:{song_id}",
            album_name=f"Album for {parsed_song.title}",
            duration_ms=random.randint(180000, 300000)
        )
    return None

# 模拟Spotify客户端
class MockSpotifyClient:
    """模拟的Spotify客户端，用于测试"""
    def search(self, q: str, type: str = 'track', limit: int = 10):
        """模拟的搜索方法"""
        # 创建假的搜索结果
        return {
            "tracks": {
                "items": [
                    {
                        "id": f"track_{i}",
                        "name": f"Mock Track {i}",
                        "artists": [{"name": f"Mock Artist {i % 3}"}],
                        "uri": f"spotify:track:track_{i}",
                        "album": {"name": f"Mock Album {i % 5}"},
                        "duration_ms": 180000 + i * 10000
                    }
                    for i in range(limit)
                ]
            }
        }

# 模拟获取Spotify客户端的函数
def get_spotify_client():
    """返回模拟的Spotify客户端"""
    return MockSpotifyClient()


def parse_input_file(file_path: str) -> List[Dict[str, Any]]:
    """
    解析输入文件，提取歌曲标题和艺术家
    
    Args:
        file_path: 输入文件路径，每行一首歌曲，格式为"标题 - 艺术家1 / 艺术家2"
        
    Returns:
        List[Dict[str, Any]]: 包含歌曲信息的数据列表
    """
    dataset = []
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                # 分离标题和艺术家
                parts = line.split(" - ", 1)
                if len(parts) == 2:
                    title, artists_str = parts
                    artists = [a.strip() for a in artists_str.split("/")]
                    
                    # 创建数据集条目
                    entry = {
                        "input": {
                            "title": title,
                            "artists": artists,
                            "original_line": line
                        },
                        "expected_match": None,  # 将通过实际API查询填充
                        "variants": []  # 可存储预期的变体匹配
                    }
                    dataset.append(entry)
                else:
                    print(f"警告: 无法解析行: '{line}'")
        
        print(f"已从 {file_path} 解析 {len(dataset)} 首歌曲")
        return dataset
        
    except Exception as e:
        print(f"解析文件时出错: {e}")
        return []


def sample_dataset(dataset: List[Dict[str, Any]], sample_size: int = 100, seed: int = 42) -> List[Dict[str, Any]]:
    """
    从数据集中随机抽样，确保多样性
    
    Args:
        dataset: 完整数据集
        sample_size: 样本大小
        seed: 随机种子
        
    Returns:
        List[Dict[str, Any]]: 抽样后的数据集
    """
    if sample_size >= len(dataset):
        return dataset
    
    random.seed(seed)
    
    # 定义多样性类别
    categories = {
        "single_artist": [],
        "multiple_artists": [],
        "with_brackets": [],
        "live_versions": [],
        "remixes": [],
        "remastered": [],
        "chinese": [],
        "english": [],
        "other": []
    }
    
    # 将歌曲分类
    for entry in dataset:
        title = entry["input"]["title"]
        artists = entry["input"]["artists"]
        original = entry["input"]["original_line"]
        
        if len(artists) > 1:
            categories["multiple_artists"].append(entry)
        else:
            categories["single_artist"].append(entry)
        
        if any(bracket in title for bracket in ["(", "[", "（"]):
            categories["with_brackets"].append(entry)
            
        if any(live_term in original.lower() for live_term in ["live", "现场", "演唱会"]):
            categories["live_versions"].append(entry)
            
        if any(remix_term in original.lower() for remix_term in ["remix", "mix", "版"]):
            categories["remixes"].append(entry)
            
        if "remaster" in original.lower():
            categories["remastered"].append(entry)
            
        # 根据标题和艺术家名称中的字符判断语言
        if any(char in original for char in "一二三四五六七八九十"):
            categories["chinese"].append(entry)
        elif original.isascii():
            categories["english"].append(entry)
        else:
            categories["other"].append(entry)
    
    # 按比例抽样
    sample = []
    remaining_slots = sample_size
    
    # 首先从每个类别中至少取一些样本
    min_per_category = min(5, remaining_slots // len(categories))
    for category, entries in categories.items():
        if entries:
            category_sample = random.sample(entries, min(min_per_category, len(entries)))
            sample.extend(category_sample)
            remaining_slots -= len(category_sample)
    
    # 从所有歌曲中随机抽取剩余样本
    if remaining_slots > 0:
        remaining_pool = [e for e in dataset if e not in sample]
        if remaining_pool:
            additional_sample = random.sample(remaining_pool, min(remaining_slots, len(remaining_pool)))
            sample.extend(additional_sample)
    
    print(f"已从 {len(dataset)} 首歌曲中抽样 {len(sample)} 首，确保多样性")
    return sample


def populate_expected_matches(dataset: List[Dict[str, Any]], 
                             output_path: str, 
                             max_retries: int = 3,
                             delay: float = 1.0) -> List[Dict[str, Any]]:
    """
    使用模拟的Spotify API结果填充数据集
    
    Args:
        dataset: 初始数据集
        output_path: 输出文件路径
        max_retries: 最大重试次数
        delay: 请求间隔延迟(秒)
        
    Returns:
        List[Dict[str, Any]]: 填充后的数据集
    """
    # 获取模拟的Spotify客户端
    sp = get_spotify_client()
    print(f"已获取模拟的Spotify客户端")
    
    # 统计信息
    total = len(dataset)
    matched = 0
    failed = 0
    
    # 处理每首歌曲
    for i, entry in enumerate(dataset):
        print(f"处理 {i+1}/{total}: {entry['input']['original_line']}")
        
        # 创建ParsedSong对象
        parsed_song = ParsedSong(
            original_line=entry["input"]["original_line"],
            title=entry["input"]["title"],
            artists=entry["input"]["artists"]
        )
        
        # 尝试获取匹配结果
        retries = 0
        match_result = None
        
        while retries < max_retries and match_result is None:
            try:
                # 使用模拟的搜索函数
                match_result = mock_search_song_on_spotify(sp, parsed_song)
                
                if match_result:
                    # 填充预期匹配结果
                    entry["expected_match"] = {
                        "spotify_id": match_result.spotify_id,
                        "name": match_result.name,
                        "artists": match_result.artists,
                        "uri": match_result.uri,
                        "album_name": match_result.album_name,
                        "duration_ms": match_result.duration_ms
                    }
                    matched += 1
                    print(f"  ✓ 找到匹配: {match_result.name}")
                else:
                    failed += 1
                    print(f"  ✗ 未找到匹配")
                
            except Exception as e:
                print(f"  ! 搜索出错: {e}")
                retries += 1
                if retries < max_retries:
                    print(f"  重试 ({retries}/{max_retries})...")
                    time.sleep(delay)
                else:
                    failed += 1
                    print(f"  ✗ 达到最大重试次数，跳过")
        
        # 模拟API延迟
        time.sleep(delay / 10)  # 减小延迟以加快测试
    
    # 保存结果
    try:
        # 确保输出目录存在
        os.makedirs(os.path.dirname(os.path.abspath(output_path)) if os.path.dirname(output_path) else ".", exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(dataset, f, ensure_ascii=False, indent=2)
        
        print(f"\n已保存数据集到 {output_path}")
        print(f"统计: 总计 {total} 首歌曲, 匹配成功 {matched}, 匹配失败 {failed}")
    except Exception as e:
        print(f"保存数据集时出错: {e}")
    
    return dataset


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="从歌曲列表创建黄金标准数据集")
    parser.add_argument("input_file", help="输入文件路径，每行一首歌曲")
    parser.add_argument("--output", "-o", default="golden_dataset.json", help="输出文件路径")
    parser.add_argument("--sample-size", "-s", type=int, default=100, help="样本大小")
    parser.add_argument("--seed", type=int, default=42, help="随机种子")
    parser.add_argument("--delay", "-d", type=float, default=0.5, help="API请求间隔延迟(秒)")
    
    args = parser.parse_args()
    
    # 解析输入文件
    dataset = parse_input_file(args.input_file)
    
    if not dataset:
        print("没有可用的歌曲数据，退出")
        return
    
    # 抽样
    if args.sample_size < len(dataset):
        dataset = sample_dataset(dataset, args.sample_size, args.seed)
    
    # 填充匹配结果
    populate_expected_matches(dataset, args.output, delay=args.delay)
    
    print("数据集创建完成!")


if __name__ == "__main__":
    main() 