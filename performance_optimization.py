#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
性能优化与比较脚本

该脚本用于实施和验证性能优化措施的效果。
比较优化前后的性能差异，生成详细报告。
"""

import os
import sys
import time
import json
import gc
import tracemalloc
import argparse
from typing import List, Dict, Any, Tuple
from datetime import datetime
import statistics
import matplotlib.pyplot as plt
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), './')))

# 导入项目模块
from spotify_playlist_importer.core.models import ParsedSong
from spotify_playlist_importer.spotify.client import search_song_on_spotify
from spotify_playlist_importer.spotify.auth import get_spotify_client
from spotify_playlist_importer.utils.text_normalizer import normalize_text
from spotify_playlist_importer.utils.string_matcher import StringMatcher
from spotify_playlist_importer.utils.bracket_matcher import BracketMatcher
from spotify_playlist_importer.utils.enhanced_matcher import EnhancedMatcher, get_best_enhanced_match
from spotify_playlist_importer.utils.config_manager import set_config, get_config
from spotify_playlist_importer.utils.logger import get_logger, set_log_level

# 设置日志级别
set_log_level("WARNING")  # 性能测试时减少日志输出
logger = get_logger(__name__)

# 实现缓存机制
_normalize_cache = {}

def cached_normalize_text(text, **kwargs):
    """
    带缓存的文本归一化函数
    
    Args:
        text: 要归一化的文本
        **kwargs: 归一化参数
        
    Returns:
        str: 归一化后的文本
    """
    if not text:
        return text
        
    cache_key = (text, tuple(sorted(kwargs.items())))
    if cache_key not in _normalize_cache:
        _normalize_cache[cache_key] = normalize_text(text, **kwargs)
    return _normalize_cache[cache_key]


def parse_song_list(file_path: str) -> List[ParsedSong]:
    """
    解析歌曲列表文件
    
    Args:
        file_path: 歌曲列表文件路径
        
    Returns:
        List[ParsedSong]: 解析后的歌曲列表
    """
    songs = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
                
            # 分离标题和艺术家
            parts = line.split(" - ", 1)
            if len(parts) == 2:
                title, artists_str = parts
                artists = [a.strip() for a in artists_str.split("/")]
                
                songs.append(ParsedSong(
                    original_line=line,
                    title=title,
                    artists=artists
                ))
            else:
                print(f"警告: 无法解析行: '{line}'")
    
    return songs


def time_function(func, *args, **kwargs) -> Tuple[Any, float]:
    """
    测量函数执行时间
    
    Args:
        func: 要测量的函数
        *args, **kwargs: 函数的参数
        
    Returns:
        Tuple[Any, float]: (函数返回值, 执行时间(秒))
    """
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    return result, end_time - start_time


def measure_memory_usage(func, *args, **kwargs) -> Tuple[Any, float]:
    """
    测量函数执行期间的内存使用峰值
    
    Args:
        func: 要测量的函数
        *args, **kwargs: 函数的参数
        
    Returns:
        Tuple[Any, float]: (函数返回值, 内存使用峰值(MB))
    """
    gc.collect()  # 先进行垃圾回收
    tracemalloc.start()
    
    result = func(*args, **kwargs)
    
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    # 转换为MB
    peak_mb = peak / (1024 * 1024)
    
    return result, peak_mb


def compare_text_normalization(songs: List[ParsedSong]) -> Dict[str, Any]:
    """
    比较优化前后文本归一化的性能
    
    Args:
        songs: 歌曲列表
        
    Returns:
        Dict[str, Any]: 性能比较结果
    """
    print("\n--- 文本归一化性能比较 ---")
    
    # 标准文本归一化性能
    standard_times = []
    for song in songs[:100]:
        _, duration = time_function(normalize_text, song.title)
        standard_times.append(duration)
        
        for artist in song.artists:
            _, duration = time_function(normalize_text, artist)
            standard_times.append(duration)
    
    # 缓存优化后的文本归一化性能
    _normalize_cache.clear()  # 清空缓存，确保公平测试
    
    cached_times = []
    for song in songs[:100]:
        _, duration = time_function(cached_normalize_text, song.title)
        cached_times.append(duration)
        
        for artist in song.artists:
            _, duration = time_function(cached_normalize_text, artist)
            cached_times.append(duration)
    
    # 再次运行以测试缓存命中场景
    cached_hit_times = []
    for song in songs[:100]:
        _, duration = time_function(cached_normalize_text, song.title)
        cached_hit_times.append(duration)
        
        for artist in song.artists:
            _, duration = time_function(cached_normalize_text, artist)
            cached_hit_times.append(duration)
    
    # 测量内存使用
    _, standard_memory = measure_memory_usage(
        lambda: [normalize_text(song.title) for song in songs[:100]]
    )
    
    _normalize_cache.clear()
    _, cached_memory = measure_memory_usage(
        lambda: [cached_normalize_text(song.title) for song in songs[:100]]
    )
    
    # 统计结果
    result = {
        "standard": {
            "avg_time": statistics.mean(standard_times),
            "min_time": min(standard_times),
            "max_time": max(standard_times),
            "median_time": statistics.median(standard_times),
            "memory_usage_mb": standard_memory
        },
        "cached_first_run": {
            "avg_time": statistics.mean(cached_times),
            "min_time": min(cached_times),
            "max_time": max(cached_times),
            "median_time": statistics.median(cached_times)
        },
        "cached_hit": {
            "avg_time": statistics.mean(cached_hit_times),
            "min_time": min(cached_hit_times),
            "max_time": max(cached_hit_times),
            "median_time": statistics.median(cached_hit_times),
            "memory_usage_mb": cached_memory
        }
    }
    
    # 计算提升百分比
    improvement = (1 - result["cached_hit"]["avg_time"] / result["standard"]["avg_time"]) * 100
    
    print(f"标准归一化平均时间: {result['standard']['avg_time']:.6f} 秒")
    print(f"缓存首次运行平均时间: {result['cached_first_run']['avg_time']:.6f} 秒")
    print(f"缓存命中平均时间: {result['cached_hit']['avg_time']:.6f} 秒")
    print(f"性能提升: {improvement:.2f}%")
    print(f"标准内存使用: {result['standard']['memory_usage_mb']:.2f} MB")
    print(f"缓存内存使用: {result['cached_hit']['memory_usage_mb']:.2f} MB")
    
    return result


def compare_batch_processing(songs: List[ParsedSong]) -> Dict[str, Any]:
    """
    比较优化前后批处理的性能
    
    Args:
        songs: 歌曲列表
        
    Returns:
        Dict[str, Any]: 性能比较结果
    """
    print("\n--- 批处理性能比较 ---")
    
    batch_sizes = [10, 50, 100]
    if len(songs) >= 200:
        batch_sizes.append(200)
    
    # 创建模拟候选
    def create_mock_candidates(count: int):
        return [
            {
                'id': f'mock_id_{i}',
                'name': f'Mock Song {i}',
                'uri': f'spotify:track:mock_{i}',
                'artists': [{'name': f'Mock Artist {i % 3}'}],
                'album': {'name': f'Mock Album {i % 5}'},
                'duration_ms': 180000 + i * 1000
            }
            for i in range(count)
        ]
    
    candidates = create_mock_candidates(10)
    
    # 标准顺序处理
    sequential_times = {}
    
    for size in batch_sizes:
        if size > len(songs):
            continue
            
        batch = songs[:size]
        print(f"测试批次大小: {size}")
        
        start_time = time.time()
        
        for song in batch:
            # 模拟处理流程
            normalize_text(song.title)
            for artist in song.artists:
                normalize_text(artist)
            
            get_best_enhanced_match(
                input_title=song.title,
                input_artists=song.artists,
                candidates=candidates
            )
        
        duration = time.time() - start_time
        sequential_times[size] = duration
        print(f"  顺序处理耗时: {duration:.3f} 秒 (每首歌 {duration/size:.6f} 秒)")
    
    # 并行处理
    parallel_times = {}
    
    def process_song(song):
        # 模拟处理流程
        normalize_text(song.title)
        for artist in song.artists:
            normalize_text(artist)
        
        return get_best_enhanced_match(
            input_title=song.title,
            input_artists=song.artists,
            candidates=candidates
        )
    
    for size in batch_sizes:
        if size > len(songs):
            continue
            
        batch = songs[:size]
        print(f"测试并行批次大小: {size}")
        
        # 确定合适的线程数
        max_workers = min(os.cpu_count() or 4, size)
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(process_song, song) for song in batch]
            results = [future.result() for future in as_completed(futures)]
        
        duration = time.time() - start_time
        parallel_times[size] = duration
        print(f"  并行处理耗时: {duration:.3f} 秒 (每首歌 {duration/size:.6f} 秒)")
    
    # 计算加速比
    speedups = {}
    for size in batch_sizes:
        if size in sequential_times and size in parallel_times:
            speedups[size] = sequential_times[size] / parallel_times[size]
    
    # 统计结果
    result = {
        "batch_sizes": batch_sizes,
        "sequential_times": sequential_times,
        "parallel_times": parallel_times,
        "speedups": speedups
    }
    
    print("\n并行处理加速比:")
    for size, speedup in speedups.items():
        print(f"  批次大小 {size}: {speedup:.2f}x")
    
    return result


def compare_string_matching(songs: List[ParsedSong]) -> Dict[str, Any]:
    """
    比较优化前后字符串匹配的性能
    
    Args:
        songs: 歌曲列表
        
    Returns:
        Dict[str, Any]: 性能比较结果
    """
    print("\n--- 字符串匹配性能比较 ---")
    
    # 创建模拟候选
    def create_mock_candidates(count: int):
        return [
            {
                'id': f'mock_id_{i}',
                'name': f'Mock Song {i}',
                'uri': f'spotify:track:mock_{i}',
                'artists': [{'name': f'Mock Artist {i % 3}'}],
                'album': {'name': f'Mock Album {i % 5}'},
                'duration_ms': 180000 + i * 1000
            }
            for i in range(count)
        ]
    
    # 创建标准匹配器
    standard_matcher = StringMatcher(
        title_weight=0.6,
        artist_weight=0.4,
        threshold=70.0
    )
    
    # 创建优化匹配器（使用更高效的算法）
    class OptimizedStringMatcher(StringMatcher):
        def _calculate_artists_similarity(self, input_artists, candidate_artists):
            # 实现更高效的艺术家相似度计算
            if not input_artists or not candidate_artists:
                return 0.0
            
            # 使用集合操作，计算Jaccard相似度
            input_set = set(a.lower() for a in input_artists)
            candidate_set = set(a['name'].lower() for a in candidate_artists)
            
            intersection = len(input_set.intersection(candidate_set))
            union = len(input_set.union(candidate_set))
            
            return intersection / union if union > 0 else 0.0
    
    optimized_matcher = OptimizedStringMatcher(
        title_weight=0.6,
        artist_weight=0.4,
        threshold=70.0
    )
    
    # 测量标准匹配时间
    standard_times = []
    candidates = create_mock_candidates(20)
    
    for song in songs[:50]:  # 取前50首歌曲进行测试
        _, duration = time_function(
            standard_matcher.match,
            input_title=song.title,
            input_artists=song.artists,
            candidates=candidates
        )
        standard_times.append(duration)
    
    # 测量优化匹配时间
    optimized_times = []
    
    for song in songs[:50]:
        _, duration = time_function(
            optimized_matcher.match,
            input_title=song.title,
            input_artists=song.artists,
            candidates=candidates
        )
        optimized_times.append(duration)
    
    # 测量不同候选数量的性能影响
    candidate_counts = [5, 10, 20, 50]
    standard_count_times = {}
    optimized_count_times = {}
    
    for count in candidate_counts:
        test_candidates = create_mock_candidates(count)
        
        # 标准匹配
        durations = []
        for song in songs[:20]:
            _, duration = time_function(
                standard_matcher.match,
                input_title=song.title,
                input_artists=song.artists,
                candidates=test_candidates
            )
            durations.append(duration)
        standard_count_times[count] = statistics.mean(durations)
        
        # 优化匹配
        durations = []
        for song in songs[:20]:
            _, duration = time_function(
                optimized_matcher.match,
                input_title=song.title,
                input_artists=song.artists,
                candidates=test_candidates
            )
            durations.append(duration)
        optimized_count_times[count] = statistics.mean(durations)
    
    # 统计结果
    result = {
        "standard": {
            "avg_time": statistics.mean(standard_times),
            "min_time": min(standard_times),
            "max_time": max(standard_times),
            "median_time": statistics.median(standard_times),
            "count_times": standard_count_times
        },
        "optimized": {
            "avg_time": statistics.mean(optimized_times),
            "min_time": min(optimized_times),
            "max_time": max(optimized_times),
            "median_time": statistics.median(optimized_times),
            "count_times": optimized_count_times
        }
    }
    
    # 计算提升百分比
    improvement = (1 - result["optimized"]["avg_time"] / result["standard"]["avg_time"]) * 100
    
    print(f"标准匹配平均时间: {result['standard']['avg_time']:.6f} 秒")
    print(f"优化匹配平均时间: {result['optimized']['avg_time']:.6f} 秒")
    print(f"性能提升: {improvement:.2f}%")
    
    print("\n不同候选数量的性能比较:")
    for count in candidate_counts:
        std_time = standard_count_times[count]
        opt_time = optimized_count_times[count]
        local_improvement = (1 - opt_time / std_time) * 100
        print(f"  {count} 个候选: 标准 {std_time:.6f} 秒, 优化 {opt_time:.6f} 秒, 提升 {local_improvement:.2f}%")
    
    return result


def visualize_results(results: Dict[str, Dict[str, Any]], output_dir: str = "./"):
    """
    可视化性能比较结果
    
    Args:
        results: 性能比较结果
        output_dir: 输出目录
    """
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 绘制文本归一化性能
    if "text_normalization" in results:
        norm_result = results["text_normalization"]
        
        labels = ["标准", "缓存首次", "缓存命中"]
        times = [
            norm_result["standard"]["avg_time"],
            norm_result["cached_first_run"]["avg_time"],
            norm_result["cached_hit"]["avg_time"]
        ]
        
        plt.figure(figsize=(10, 6))
        plt.bar(labels, times, color=['blue', 'orange', 'green'])
        plt.title("文本归一化性能比较")
        plt.ylabel("平均执行时间 (秒)")
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        # 添加数据标签
        for i, v in enumerate(times):
            plt.text(i, v + 0.0001, f"{v:.6f}", ha='center')
        
        plt.savefig(os.path.join(output_dir, "text_normalization_comparison.png"), dpi=300, bbox_inches='tight')
        plt.close()
    
    # 绘制批处理性能
    if "batch_processing" in results:
        batch_result = results["batch_processing"]
        
        batch_sizes = list(batch_result["sequential_times"].keys())
        seq_times = [batch_result["sequential_times"][size] for size in batch_sizes]
        par_times = [batch_result["parallel_times"][size] for size in batch_sizes]
        
        plt.figure(figsize=(10, 6))
        width = 0.35
        x = np.arange(len(batch_sizes))
        
        plt.bar(x - width/2, seq_times, width, label='顺序处理')
        plt.bar(x + width/2, par_times, width, label='并行处理')
        
        plt.title("批处理性能比较")
        plt.xlabel("批次大小")
        plt.ylabel("执行时间 (秒)")
        plt.xticks(x, batch_sizes)
        plt.legend()
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        plt.savefig(os.path.join(output_dir, "batch_processing_comparison.png"), dpi=300, bbox_inches='tight')
        plt.close()
        
        # 绘制加速比
        speedups = [batch_result["speedups"][size] for size in batch_sizes]
        
        plt.figure(figsize=(10, 6))
        plt.plot(batch_sizes, speedups, marker='o', linestyle='-', linewidth=2)
        plt.title("并行处理加速比")
        plt.xlabel("批次大小")
        plt.ylabel("加速比")
        plt.grid(linestyle='--', alpha=0.7)
        
        # 添加数据标签
        for i, v in enumerate(speedups):
            plt.text(batch_sizes[i], v + 0.05, f"{v:.2f}x", ha='center')
        
        plt.savefig(os.path.join(output_dir, "batch_processing_speedup.png"), dpi=300, bbox_inches='tight')
        plt.close()
    
    # 绘制字符串匹配性能
    if "string_matching" in results:
        match_result = results["string_matching"]
        
        # 平均执行时间
        labels = ["标准匹配", "优化匹配"]
        times = [
            match_result["standard"]["avg_time"],
            match_result["optimized"]["avg_time"]
        ]
        
        plt.figure(figsize=(10, 6))
        plt.bar(labels, times, color=['blue', 'green'])
        plt.title("字符串匹配性能比较")
        plt.ylabel("平均执行时间 (秒)")
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        # 添加数据标签
        for i, v in enumerate(times):
            plt.text(i, v + 0.0001, f"{v:.6f}", ha='center')
        
        plt.savefig(os.path.join(output_dir, "string_matching_comparison.png"), dpi=300, bbox_inches='tight')
        plt.close()
        
        # 不同候选数量的性能
        counts = list(match_result["standard"]["count_times"].keys())
        std_times = [match_result["standard"]["count_times"][count] for count in counts]
        opt_times = [match_result["optimized"]["count_times"][count] for count in counts]
        
        plt.figure(figsize=(10, 6))
        plt.plot(counts, std_times, marker='o', linestyle='-', linewidth=2, label='标准匹配')
        plt.plot(counts, opt_times, marker='s', linestyle='-', linewidth=2, label='优化匹配')
        plt.title("不同候选数量的字符串匹配性能")
        plt.xlabel("候选数量")
        plt.ylabel("平均执行时间 (秒)")
        plt.legend()
        plt.grid(linestyle='--', alpha=0.7)
        
        plt.savefig(os.path.join(output_dir, "string_matching_candidates.png"), dpi=300, bbox_inches='tight')
        plt.close()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="对Spotify歌曲匹配算法进行性能优化分析")
    parser.add_argument("--input", "-i", default="yunmusic.txt", help="输入歌曲列表文件路径")
    parser.add_argument("--output", "-o", default="performance_optimization_results.json", help="性能分析报告输出路径")
    parser.add_argument("--plots", "-p", default="./plots", help="图表输出目录")
    parser.add_argument("--verbose", "-v", action="store_true", help="显示详细输出")
    
    args = parser.parse_args()
    
    # 加载歌曲数据
    print(f"正在从 {args.input} 加载歌曲数据...")
    songs = parse_song_list(args.input)
    print(f"已加载 {len(songs)} 首歌曲")
    
    # 执行性能比较
    results = {}
    
    print("\n=== 开始性能优化分析 ===")
    results["text_normalization"] = compare_text_normalization(songs)
    results["batch_processing"] = compare_batch_processing(songs)
    results["string_matching"] = compare_string_matching(songs)
    
    # 可视化结果
    print("\n=== 生成性能比较图表 ===")
    visualize_results(results, args.plots)
    
    # 保存分析报告
    if args.output:
        print(f"\n=== 保存性能报告到 {args.output} ===")
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "results": results,
                "metadata": {
                    "songs_count": len(songs),
                    "input_file": args.input
                }
            }, f, indent=2, ensure_ascii=False)
    
    print("\n=== 性能优化分析完成 ===")


if __name__ == "__main__":
    main() 