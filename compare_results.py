#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

# 加载性能报告
with open('performance_report.json', 'r', encoding='utf-8') as f1:
    before = json.load(f1)

with open('performance_report_optimized.json', 'r', encoding='utf-8') as f2:
    after = json.load(f2)

# 提取结果
before_results = before['results']
after_results = after['results']

# 计算改进百分比
def calc_improvement(before_val, after_val):
    return (1 - after_val / before_val) * 100

# 比较关键指标
print("=== 性能优化比较报告 ===\n")

# 文本归一化性能
before_norm = before_results['text_normalization']['avg_time']
after_norm = after_results['text_normalization']['avg_time']
norm_improvement = calc_improvement(before_norm, after_norm)
print(f"文本归一化平均时间: {before_norm:.6f}s → {after_norm:.6f}s ({norm_improvement:.1f}% 改进)")

# 字符串匹配性能
before_str = before_results['string_matching']['avg_time']
after_str = after_results['string_matching']['avg_time']
str_improvement = calc_improvement(before_str, after_str)
print(f"字符串匹配平均时间: {before_str:.6f}s → {after_str:.6f}s ({str_improvement:.1f}% 改进)")

# 增强匹配性能
before_enhanced = before_results['enhanced_matching']['avg_time']
after_enhanced = after_results['enhanced_matching']['avg_time']
enhanced_improvement = calc_improvement(before_enhanced, after_enhanced)
print(f"增强匹配平均时间: {before_enhanced:.6f}s → {after_enhanced:.6f}s ({enhanced_improvement:.1f}% 改进)")

# 端到端性能
before_e2e = before_results['end_to_end']['avg_time_per_song']
after_e2e = after_results['end_to_end']['avg_time_per_song']
e2e_improvement = calc_improvement(before_e2e, after_e2e)
print(f"端到端匹配平均时间: {before_e2e:.6f}s → {after_e2e:.6f}s ({e2e_improvement:.1f}% 改进)")

# 批处理伸缩性
print("\n批处理伸缩性能:")
batch_sizes = [10, 50, 100, 200, 400]
for size in batch_sizes:
    size_str = str(size)
    before_batch = before_results['batch_scaling']['batch_times'][size_str]['avg_time_per_song']
    after_batch = after_results['batch_scaling']['batch_times'][size_str]['avg_time_per_song']
    batch_improvement = calc_improvement(before_batch, after_batch)
    print(f"  批次大小 {size}: {before_batch:.6f}s → {after_batch:.6f}s ({batch_improvement:.1f}% 改进)")

# 内存使用
before_mem_norm = before_results['text_normalization']['memory_usage_mb']
after_mem_norm = after_results['text_normalization']['memory_usage_mb']
before_mem_enhanced = before_results['enhanced_matching']['memory_usage_mb']
after_mem_enhanced = after_results['enhanced_matching']['memory_usage_mb']

print("\n内存使用:")
print(f"  文本归一化: {before_mem_norm:.2f}MB → {after_mem_norm:.2f}MB ({calc_improvement(before_mem_norm, after_mem_norm):.1f}% 改进)")
print(f"  增强匹配: {before_mem_enhanced:.2f}MB → {after_mem_enhanced:.2f}MB ({calc_improvement(before_mem_enhanced, after_mem_enhanced):.1f}% 改进)")

print("\n=== 总体改进 ===")
avg_improvement = (norm_improvement + str_improvement + enhanced_improvement + e2e_improvement) / 4
print(f"平均性能改进: {avg_improvement:.1f}%")
print(f"端到端性能改进: {e2e_improvement:.1f}%") 