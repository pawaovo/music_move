#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
评估Spotify歌曲匹配算法性能

使用黄金标准数据集评估匹配算法的准确性，生成详细报告。
"""

import argparse
import json
import os
import sys
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

# 将项目根目录添加到PATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from spotify_playlist_importer.spotify.auth import get_spotify_client
from spotify_playlist_importer.spotify.client import search_song_on_spotify
from spotify_playlist_importer.core.models import ParsedSong


def evaluate_matching_algorithm(dataset_path: str, 
                               output_report_path: Optional[str] = None,
                               verbose: bool = False) -> Dict[str, Any]:
    """
    评估匹配算法性能
    
    Args:
        dataset_path: 黄金标准数据集路径
        output_report_path: 评估报告输出路径
        verbose: 是否输出详细信息
        
    Returns:
        Dict[str, Any]: 评估结果
    """
    # 加载黄金标准数据集
    try:
        with open(dataset_path, "r", encoding="utf-8") as f:
            dataset = json.load(f)
            print(f"已加载数据集，包含 {len(dataset)} 首歌曲")
    except Exception as e:
        print(f"加载数据集失败: {e}")
        return {"error": str(e)}
    
    # 获取Spotify客户端
    try:
        sp = get_spotify_client()
        print("成功获取Spotify客户端")
    except Exception as e:
        print(f"获取Spotify客户端失败: {e}")
        return {"error": str(e)}
    
    # 过滤掉没有预期匹配结果的条目
    valid_entries = [e for e in dataset if e.get("expected_match")]
    print(f"数据集中有 {len(valid_entries)}/{len(dataset)} 首歌曲包含预期匹配结果")
    
    # 性能统计
    total = len(valid_entries)
    matched = 0
    correct_match = 0
    failed = 0
    
    # 详细结果记录
    results = []
    
    # 开始时间
    start_time = time.time()
    
    # 评估每首歌曲的匹配
    for i, entry in enumerate(valid_entries):
        if verbose:
            print(f"评估 {i+1}/{total}: {entry['input']['original_line']}")
        
        # 创建ParsedSong
        parsed_song = ParsedSong(
            original_line=entry['input']['original_line'],
            title=entry['input']['title'],
            artists=entry['input']['artists']
        )
        
        # 记录这首歌的结果
        result = {
            "input": entry['input']['original_line'],
            "expected": {
                "name": entry['expected_match']['name'],
                "id": entry['expected_match']['spotify_id'],
                "artists": entry['expected_match']['artists'],
                "album": entry['expected_match'].get('album_name', 'N/A')
            }
        }
        
        # 运行匹配算法
        try:
            match_result = search_song_on_spotify(sp, parsed_song)
            
            if match_result:
                matched += 1
                result["actual"] = {
                    "name": match_result.name,
                    "id": match_result.spotify_id,
                    "artists": match_result.artists,
                    "album": match_result.album_name or 'N/A'
                }
                
                # 检查是否匹配到预期结果
                if match_result.spotify_id == entry['expected_match']['spotify_id']:
                    correct_match += 1
                    result["status"] = "CORRECT"
                    if verbose:
                        print(f"  ✓ 正确匹配: '{match_result.name}'")
                else:
                    result["status"] = "WRONG_MATCH"
                    if verbose:
                        print(f"  ✗ 错误匹配: 预期 '{entry['expected_match']['name']}', 实际 '{match_result.name}'")
            else:
                failed += 1
                result["status"] = "NO_MATCH"
                if verbose:
                    print(f"  ✗ 未找到匹配: 预期 '{entry['expected_match']['name']}'")
        except Exception as e:
            failed += 1
            result["status"] = "ERROR"
            result["error"] = str(e)
            if verbose:
                print(f"  ! 匹配过程出错: {e}")
        
        results.append(result)
    
    # 计算耗时
    duration = time.time() - start_time
    
    # 计算准确率
    accuracy = correct_match / total if total > 0 else 0
    match_rate = matched / total if total > 0 else 0
    
    # 生成评估报告
    report = {
        "timestamp": datetime.now().isoformat(),
        "dataset": dataset_path,
        "statistics": {
            "total_songs": total,
            "matched_songs": matched,
            "correct_matches": correct_match,
            "failed_matches": failed,
            "accuracy": accuracy,
            "match_rate": match_rate,
            "processing_time": duration,
            "average_time_per_song": duration / total if total > 0 else 0
        },
        "detailed_results": results
    }
    
    # 打印结果摘要
    print("\n===== 匹配算法评估结果 =====")
    print(f"总歌曲数: {total}")
    print(f"找到匹配数: {matched} ({match_rate:.2%})")
    print(f"正确匹配数: {correct_match} ({accuracy:.2%})")
    print(f"未匹配/错误: {failed} ({failed/total:.2%})")
    print(f"处理耗时: {duration:.2f}秒 (平均每首: {duration/total:.2f}秒)")
    print("=============================")
    
    # 输出结果状态统计
    status_counts = {}
    for r in results:
        status = r.get("status", "UNKNOWN")
        status_counts[status] = status_counts.get(status, 0) + 1
    
    print("\n状态统计:")
    for status, count in status_counts.items():
        print(f"{status}: {count} ({count/total:.2%})")
    
    # 保存评估报告
    if output_report_path:
        try:
            os.makedirs(os.path.dirname(os.path.abspath(output_report_path)) if os.path.dirname(output_report_path) else ".", exist_ok=True)
            with open(output_report_path, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"\n评估报告已保存至 {output_report_path}")
        except Exception as e:
            print(f"保存评估报告失败: {e}")
    
    return report


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="评估Spotify歌曲匹配算法性能")
    parser.add_argument("dataset_path", help="黄金标准数据集路径")
    parser.add_argument("--output", "-o", default=None, help="评估报告输出路径")
    parser.add_argument("--verbose", "-v", action="store_true", help="是否输出详细信息")
    
    args = parser.parse_args()
    
    # 如果没有指定输出路径，生成默认路径
    if not args.output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output = f"evaluation_report_{timestamp}.json"
    
    # 运行评估
    evaluate_matching_algorithm(args.dataset_path, args.output, args.verbose)


if __name__ == "__main__":
    main() 