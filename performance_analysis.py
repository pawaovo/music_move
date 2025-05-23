#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
性能分析脚本

该脚本用于测试Spotify歌曲匹配算法在处理大规模输入时的性能表现。
主要分析:
1. 各匹配阶段的执行时间
2. 内存使用情况
3. 文本处理和相似度计算的性能瓶颈
4. 可能的优化点
"""

import os
import sys
import time
import cProfile
import pstats
import io
import gc
import tracemalloc
from typing import List, Dict, Any, Tuple
from datetime import datetime
import statistics

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


def profile_function(func, *args, **kwargs) -> Tuple[Any, str]:
    """
    使用cProfile分析函数性能
    
    Args:
        func: 要分析的函数
        *args, **kwargs: 函数的参数
        
    Returns:
        Tuple[Any, str]: (函数返回值, 分析结果)
    """
    profiler = cProfile.Profile()
    profiler.enable()
    result = func(*args, **kwargs)
    profiler.disable()
    
    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
    ps.print_stats(20)  # 只打印前20个最耗时的函数
    
    return result, s.getvalue()


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


def analyze_text_normalization_performance(songs: List[ParsedSong]) -> Dict[str, Any]:
    """
    分析文本归一化的性能
    
    Args:
        songs: 歌曲列表
        
    Returns:
        Dict[str, Any]: 性能分析结果
    """
    print("\n--- 文本归一化性能分析 ---")
    
    # 测量整体执行时间
    times = []
    for song in songs:
        _, duration = time_function(normalize_text, song.title)
        times.append(duration)
        
        # 对艺术家名称也进行测量
        for artist in song.artists:
            _, duration = time_function(normalize_text, artist)
            times.append(duration)
    
    # 分析cProfile结果
    sample_song = songs[0]
    _, profile_result = profile_function(normalize_text, sample_song.title)
    
    # 测量内存使用
    _, memory_usage = measure_memory_usage(
        lambda: [normalize_text(song.title) for song in songs[:100]]
    )
    
    # 统计结果
    result = {
        "total_samples": len(times),
        "avg_time": statistics.mean(times),
        "min_time": min(times),
        "max_time": max(times),
        "median_time": statistics.median(times),
        "memory_usage_mb": memory_usage,
        "profile_result": profile_result
    }
    
    print(f"平均执行时间: {result['avg_time']:.6f} 秒")
    print(f"执行时间中位数: {result['median_time']:.6f} 秒")
    print(f"最长执行时间: {result['max_time']:.6f} 秒")
    print(f"内存使用峰值: {result['memory_usage_mb']:.2f} MB")
    
    return result


def analyze_string_matching_performance(songs: List[ParsedSong], num_candidates: int = 10) -> Dict[str, Any]:
    """
    分析字符串匹配的性能
    
    Args:
        songs: 歌曲列表
        num_candidates: 每首歌曲生成的候选数量
        
    Returns:
        Dict[str, Any]: 性能分析结果
    """
    print("\n--- 字符串匹配性能分析 ---")
    
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
    
    # 创建匹配器
    matcher = StringMatcher(
        title_weight=0.6,
        artist_weight=0.4,
        threshold=70.0
    )
    
    # 测量匹配时间
    times = []
    candidates = create_mock_candidates(num_candidates)
    
    for song in songs[:100]:  # 取前100首歌曲进行测试
        _, duration = time_function(
            matcher.match,
            input_title=song.title,
            input_artists=song.artists,
            candidates=candidates
        )
        times.append(duration)
    
    # 分析cProfile结果
    sample_song = songs[0]
    _, profile_result = profile_function(
        matcher.match,
        input_title=sample_song.title,
        input_artists=sample_song.artists,
        candidates=candidates
    )
    
    # 测量内存使用
    _, memory_usage = measure_memory_usage(
        lambda: [matcher.match(
            input_title=song.title,
            input_artists=song.artists,
            candidates=candidates
        ) for song in songs[:20]]
    )
    
    # 测试不同候选数量的性能
    candidate_counts = [5, 10, 20, 50]
    count_times = {}
    
    for count in candidate_counts:
        test_candidates = create_mock_candidates(count)
        durations = []
        
        for song in songs[:20]:  # 取少量歌曲测试不同候选数量
            _, duration = time_function(
                matcher.match,
                input_title=song.title,
                input_artists=song.artists,
                candidates=test_candidates
            )
            durations.append(duration)
        
        count_times[count] = statistics.mean(durations)
    
    # 统计结果
    result = {
        "total_samples": len(times),
        "avg_time": statistics.mean(times),
        "min_time": min(times),
        "max_time": max(times),
        "median_time": statistics.median(times),
        "memory_usage_mb": memory_usage,
        "candidate_count_times": count_times,
        "profile_result": profile_result
    }
    
    print(f"平均执行时间: {result['avg_time']:.6f} 秒")
    print(f"执行时间中位数: {result['median_time']:.6f} 秒")
    print(f"最长执行时间: {result['max_time']:.6f} 秒")
    print(f"内存使用峰值: {result['memory_usage_mb']:.2f} MB")
    
    print("\n不同候选数量的性能:")
    for count, avg_time in count_times.items():
        print(f"  {count} 个候选: {avg_time:.6f} 秒")
    
    return result


def analyze_enhanced_matching_performance(songs: List[ParsedSong], num_candidates: int = 10) -> Dict[str, Any]:
    """
    分析增强匹配算法的性能
    
    Args:
        songs: 歌曲列表
        num_candidates: 每首歌曲生成的候选数量
        
    Returns:
        Dict[str, Any]: 性能分析结果
    """
    print("\n--- 增强匹配算法性能分析 ---")
    
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
    
    # 测量匹配时间
    times = []
    candidates = create_mock_candidates(num_candidates)
    
    for song in songs[:100]:  # 取前100首歌曲进行测试
        _, duration = time_function(
            get_best_enhanced_match,
            input_title=song.title,
            input_artists=song.artists,
            candidates=candidates
        )
        times.append(duration)
    
    # 分析cProfile结果
    sample_song = songs[0]
    _, profile_result = profile_function(
        get_best_enhanced_match,
        input_title=sample_song.title,
        input_artists=sample_song.artists,
        candidates=candidates
    )
    
    # 测量内存使用
    _, memory_usage = measure_memory_usage(
        lambda: [get_best_enhanced_match(
            input_title=song.title,
            input_artists=song.artists,
            candidates=candidates
        ) for song in songs[:20]]
    )
    
    # 测试不同阈值的性能影响
    thresholds = [(50, 60), (60, 70), (70, 80), (80, 90)]
    threshold_times = {}
    
    for first_stage, second_stage in thresholds:
        durations = []
        
        for song in songs[:20]:  # 取少量歌曲测试不同阈值
            _, duration = time_function(
                get_best_enhanced_match,
                input_title=song.title,
                input_artists=song.artists,
                candidates=candidates,
                first_stage_threshold=first_stage,
                second_stage_threshold=second_stage
            )
            durations.append(duration)
        
        threshold_times[(first_stage, second_stage)] = statistics.mean(durations)
    
    # 统计结果
    result = {
        "total_samples": len(times),
        "avg_time": statistics.mean(times),
        "min_time": min(times),
        "max_time": max(times),
        "median_time": statistics.median(times),
        "memory_usage_mb": memory_usage,
        "threshold_times": threshold_times,
        "profile_result": profile_result
    }
    
    print(f"平均执行时间: {result['avg_time']:.6f} 秒")
    print(f"执行时间中位数: {result['median_time']:.6f} 秒")
    print(f"最长执行时间: {result['max_time']:.6f} 秒")
    print(f"内存使用峰值: {result['memory_usage_mb']:.2f} MB")
    
    print("\n不同阈值的性能:")
    for threshold, avg_time in threshold_times.items():
        print(f"  一阶段阈值 {threshold[0]}, 二阶段阈值 {threshold[1]}: {avg_time:.6f} 秒")
    
    return result


def analyze_end_to_end_performance(songs: List[ParsedSong], sample_size: int = 50) -> Dict[str, Any]:
    """
    分析端到端的匹配性能
    
    Args:
        songs: 歌曲列表
        sample_size: 样本大小
        
    Returns:
        Dict[str, Any]: 性能分析结果
    """
    print(f"\n--- 端到端匹配性能分析 (样本大小: {sample_size}) ---")
    
    # 由于端到端测试需要Spotify API调用，可能受到API限制影响
    # 此处使用模拟函数替代实际API调用
    # 实际测试中，应小心API调用频率，避免触发限制
    
    test_songs = songs[:sample_size]
    total_start_time = time.time()
    
    # 设置相关配置
    set_config("SPOTIFY_SEARCH_LIMIT", 10)
    set_config("TITLE_WEIGHT", 0.6)
    set_config("ARTIST_WEIGHT", 0.4)
    set_config("MATCH_THRESHOLD", 70.0)
    
    # 模拟Spotify API结果
    def mock_search_spotify(parsed_song):
        # 创建一个模拟的Spotify搜索结果
        # 实际测试中应使用真实的API调用
        import random
        
        # 模拟搜索延迟
        time.sleep(0.1 + random.random() * 0.1)
        
        # 模拟返回的候选列表
        candidates = [
            {
                'id': f'mock_id_{i}_{hash(parsed_song.title) % 1000}',
                'name': f'{parsed_song.title}{" (Live)" if random.random() > 0.8 else ""}',
                'uri': f'spotify:track:mock_{i}_{hash(parsed_song.title) % 1000}',
                'artists': [{'name': artist} for artist in parsed_song.artists],
                'album': {'name': f'Album for {parsed_song.title}'},
                'duration_ms': 180000 + i * 1000
            }
            for i in range(10)
        ]
        
        # 为候选添加一些变体，增加测试多样性
        for i in range(3):
            candidates.append({
                'id': f'variant_id_{i}_{hash(parsed_song.title) % 1000}',
                'name': f'{parsed_song.title} {"(Remix)" if i==0 else "(Acoustic)" if i==1 else "(Cover)"}',
                'uri': f'spotify:track:variant_{i}_{hash(parsed_song.title) % 1000}',
                'artists': [{'name': f'Different Artist {i}'}],
                'album': {'name': f'Different Album {i}'},
                'duration_ms': 180000 + i * 1000
            })
        
        # 混合候选顺序，使测试更真实
        import random
        random.shuffle(candidates)
        
        # 使用增强匹配算法选择最佳匹配
        best_match = get_best_enhanced_match(
            input_title=parsed_song.title,
            input_artists=parsed_song.artists,
            candidates=candidates
        )
        
        return best_match
    
    # 执行端到端匹配测试
    results = []
    
    for song in test_songs:
        start_time = time.time()
        
        # 步骤1: 文本归一化
        norm_title = normalize_text(song.title)
        norm_artists = [normalize_text(artist) for artist in song.artists]
        
        # 步骤2: 搜索匹配
        match_result = mock_search_spotify(song)
        
        # 记录结果
        duration = time.time() - start_time
        results.append({
            "song": song.original_line,
            "duration": duration,
            "match_found": match_result is not None
        })
    
    total_duration = time.time() - total_start_time
    match_rate = len([r for r in results if r["match_found"]]) / len(results)
    
    # 统计结果
    durations = [r["duration"] for r in results]
    result = {
        "total_songs": len(test_songs),
        "total_duration": total_duration,
        "avg_time_per_song": total_duration / len(test_songs),
        "song_times": {
            "avg": statistics.mean(durations),
            "min": min(durations),
            "max": max(durations),
            "median": statistics.median(durations)
        },
        "match_rate": match_rate
    }
    
    print(f"总执行时间: {result['total_duration']:.3f} 秒")
    print(f"每首歌曲平均耗时: {result['avg_time_per_song']:.3f} 秒")
    print(f"匹配成功率: {result['match_rate']:.2%}")
    print(f"单首歌曲执行时间 - 平均: {result['song_times']['avg']:.3f} 秒, "
          f"最短: {result['song_times']['min']:.3f} 秒, "
          f"最长: {result['song_times']['max']:.3f} 秒, "
          f"中位数: {result['song_times']['median']:.3f} 秒")
    
    return result


def analyze_batch_scaling(songs: List[ParsedSong]) -> Dict[str, Any]:
    """
    分析批处理伸缩性能
    
    Args:
        songs: 歌曲列表
        
    Returns:
        Dict[str, Any]: 性能分析结果
    """
    print("\n--- 批处理伸缩性能分析 ---")
    
    # 测试不同批次大小的处理性能
    batch_sizes = [10, 50, 100, 200]
    if len(songs) >= 400:
        batch_sizes.append(400)
    
    times = {}
    
    for size in batch_sizes:
        if size > len(songs):
            continue
            
        batch = songs[:size]
        print(f"测试批次大小: {size}")
        
        start_time = time.time()
        
        # 执行文本归一化
        for song in batch:
            normalize_text(song.title)
            for artist in song.artists:
                normalize_text(artist)
        
        # 创建模拟候选
        candidates = [
            {
                'id': f'mock_id_{i}',
                'name': f'Mock Song {i}',
                'uri': f'spotify:track:mock_{i}',
                'artists': [{'name': f'Mock Artist {i % 3}'}],
                'album': {'name': f'Mock Album {i % 5}'},
                'duration_ms': 180000 + i * 1000
            }
            for i in range(10)
        ]
        
        # 执行增强匹配
        for song in batch:
            get_best_enhanced_match(
                input_title=song.title,
                input_artists=song.artists,
                candidates=candidates
            )
        
        duration = time.time() - start_time
        times[size] = {
            "total_time": duration,
            "avg_time_per_song": duration / size
        }
        
        print(f"  总耗时: {duration:.3f} 秒")
        print(f"  每首歌平均耗时: {duration/size:.6f} 秒")
    
    # 分析伸缩性
    scaling_factors = {}
    base_size = batch_sizes[0]
    base_time = times[base_size]["total_time"]
    
    for size in batch_sizes[1:]:
        if size in times:
            # 计算理想线性伸缩因子
            ideal_factor = size / base_size
            # 计算实际伸缩因子
            actual_factor = times[size]["total_time"] / base_time
            # 计算伸缩效率 (理想情况下为1.0)
            efficiency = ideal_factor / actual_factor
            
            scaling_factors[size] = {
                "ideal_factor": ideal_factor,
                "actual_factor": actual_factor,
                "efficiency": efficiency
            }
    
    print("\n伸缩效率分析:")
    for size, factors in scaling_factors.items():
        print(f"  从 {base_size} 到 {size}: 效率 = {factors['efficiency']:.2f} "
              f"(理想因子: {factors['ideal_factor']:.2f}, 实际因子: {factors['actual_factor']:.2f})")
    
    return {
        "batch_times": times,
        "scaling_factors": scaling_factors
    }


def generate_optimization_suggestions(results: Dict[str, Any]) -> List[str]:
    """
    根据性能分析结果生成优化建议
    
    Args:
        results: 性能分析结果
        
    Returns:
        List[str]: 优化建议列表
    """
    suggestions = []
    
    # 文本归一化优化建议
    norm_result = results.get("text_normalization", {})
    if norm_result:
        if norm_result.get("avg_time", 0) > 0.001:
            suggestions.append("考虑对文本归一化函数进行缓存，避免对相同输入重复处理")
        
        if "profile_result" in norm_result:
            # 分析profile结果，查找可能的瓶颈
            if "opencc" in norm_result["profile_result"] and norm_result.get("avg_time", 0) > 0.002:
                suggestions.append("简繁体转换是文本归一化的性能瓶颈之一，考虑仅在必要时启用此功能，或使用更高效的实现")
    
    # 字符串匹配优化建议
    str_result = results.get("string_matching", {})
    if str_result:
        if str_result.get("avg_time", 0) > 0.005:
            suggestions.append("字符串匹配算法性能可以进一步优化，考虑使用更高效的相似度计算方法")
        
        # 分析候选数量对性能的影响
        candidate_times = str_result.get("candidate_count_times", {})
        if candidate_times and 50 in candidate_times and 10 in candidate_times:
            if candidate_times[50] > 3 * candidate_times[10]:
                suggestions.append("候选数量显著影响匹配性能，建议限制初始候选数量，或实施早期剪枝策略")
    
    # 增强匹配优化建议
    enhanced_result = results.get("enhanced_matching", {})
    if enhanced_result:
        if enhanced_result.get("avg_time", 0) > 0.01:
            suggestions.append("增强匹配算法执行时间较长，考虑优化或简化计算逻辑")
        
        # 分析阈值对性能的影响
        threshold_times = enhanced_result.get("threshold_times", {})
        if threshold_times and (50, 60) in threshold_times and (80, 90) in threshold_times:
            low_time = threshold_times[(50, 60)]
            high_time = threshold_times[(80, 90)]
            if low_time < 0.7 * high_time:
                suggestions.append("降低匹配阈值可以提高处理速度，但可能降低匹配质量，建议根据实际需求调整阈值")
    
    # 批处理伸缩性优化建议
    batch_result = results.get("batch_scaling", {})
    if batch_result:
        scaling_factors = batch_result.get("scaling_factors", {})
        for size, factors in scaling_factors.items():
            if factors.get("efficiency", 1.0) < 0.7:
                suggestions.append(f"批处理伸缩效率在处理{size}首歌曲时下降明显，可能存在内存压力或其他资源瓶颈，建议进一步优化")
    
    # 端到端性能优化建议
    e2e_result = results.get("end_to_end", {})
    if e2e_result:
        if e2e_result.get("avg_time_per_song", 0) > 0.5:
            suggestions.append("端到端匹配时间较长，考虑增加并发处理或使用缓存机制")
    
    # 一般性优化建议
    suggestions.extend([
        "考虑使用并行处理同时处理多首歌曲，特别是在批量导入场景",
        "对于常见的艺术家和歌曲名称组合，可以实现结果缓存以减少计算",
        "考虑使用更精细的日志级别控制，在生产环境中减少不必要的日志输出",
        "评估是否可以使用更高效的字符串相似度算法，如使用编辑距离的近似算法",
        "在用户界面中显示进度指示器，改善用户体验"
    ])
    
    return suggestions


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="对Spotify歌曲匹配算法进行性能分析")
    parser.add_argument("--input", "-i", default="yunmusic.txt", help="输入歌曲列表文件路径")
    parser.add_argument("--output", "-o", default=None, help="性能分析报告输出路径")
    parser.add_argument("--verbose", "-v", action="store_true", help="显示详细输出")
    
    args = parser.parse_args()
    
    # 加载歌曲数据
    print(f"正在从 {args.input} 加载歌曲数据...")
    songs = parse_song_list(args.input)
    print(f"已加载 {len(songs)} 首歌曲")
    
    # 执行性能分析
    results = {}
    
    print("\n=== 开始性能分析 ===")
    results["text_normalization"] = analyze_text_normalization_performance(songs)
    results["string_matching"] = analyze_string_matching_performance(songs)
    results["enhanced_matching"] = analyze_enhanced_matching_performance(songs)
    results["batch_scaling"] = analyze_batch_scaling(songs)
    results["end_to_end"] = analyze_end_to_end_performance(songs)
    
    # 生成优化建议
    suggestions = generate_optimization_suggestions(results)
    
    # 输出性能分析报告
    print("\n=== 性能优化建议 ===")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"{i}. {suggestion}")
    
    # 保存分析报告
    if args.output:
        import json
        
        # 移除无法JSON序列化的内容
        for key in results:
            if "profile_result" in results[key]:
                results[key]["profile_result"] = str(results[key]["profile_result"])
            
            # 处理元组键的问题
            if "threshold_times" in results[key]:
                threshold_times = results[key]["threshold_times"]
                string_threshold_times = {}
                for threshold_tuple, value in threshold_times.items():
                    string_key = f"{threshold_tuple[0]}_{threshold_tuple[1]}"
                    string_threshold_times[string_key] = value
                results[key]["threshold_times"] = string_threshold_times
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "input_file": args.input,
            "song_count": len(songs),
            "results": results,
            "optimization_suggestions": suggestions
        }
        
        try:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"\n性能分析报告已保存至 {args.output}")
        except Exception as e:
            print(f"保存性能分析报告失败: {e}")
    
    print("\n=== 性能分析完成 ===")


if __name__ == "__main__":
    import argparse
    main() 