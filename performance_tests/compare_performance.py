import asyncio
import time
import logging
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from spotify_playlist_importer.utils.text_normalizer import TextNormalizer
from spotify_playlist_importer.core.batch_processor import process_song_list_file as original_process
from spotify_playlist_importer.core.optimized_batch_processor import process_song_list_file as optimized_process
from spotify_playlist_importer.core.models import ParsedSong, MatchedSong
from performance_tests.performance_analysis import mock_spotify_search, generate_test_data

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 性能比较函数
async def compare_performance(file_path, song_count=1000):
    """比较原始版本和优化版本的性能"""
    normalizer = TextNormalizer()
    
    # 确保测试文件存在
    if not os.path.exists(file_path):
        generate_test_data(file_path, num_songs=song_count)
    
    # 用于收集结果的回调函数
    async def dummy_callback(*args):
        pass
    
    # 测试原始版本
    logger.info("测试原始批处理模块...")
    start_time = time.time()
    total1, matched1, failed1 = await original_process(
        file_path,
        normalizer,
        mock_spotify_search,
        dummy_callback
    )
    original_time = time.time() - start_time
    logger.info(f"原始版本耗时: {original_time:.2f} 秒")
    logger.info(f"总计: {total1}, 成功: {matched1}, 失败: {failed1}")
    logger.info(f"平均每首歌曲处理时间: {(original_time / total1 if total1 else 0):.4f} 秒")
    
    # 测试优化版本
    logger.info("\n测试优化批处理模块...")
    start_time = time.time()
    total2, matched2, failed2 = await optimized_process(
        file_path,
        normalizer,
        mock_spotify_search,
        dummy_callback,
        batch_size=50,
        max_concurrency=10
    )
    optimized_time = time.time() - start_time
    logger.info(f"优化版本耗时: {optimized_time:.2f} 秒")
    logger.info(f"总计: {total2}, 成功: {matched2}, 失败: {failed2}")
    logger.info(f"平均每首歌曲处理时间: {(optimized_time / total2 if total2 else 0):.4f} 秒")
    
    # 计算性能提升
    if original_time > 0:
        improvement = (original_time - optimized_time) / original_time * 100
        logger.info(f"\n性能提升: {improvement:.2f}%")
    
    # 测试不同批处理大小和并发数的性能
    logger.info("\n测试不同批处理大小和并发数的性能...")
    
    batch_sizes = [10, 50, 100]
    concurrency_levels = [5, 10, 20]
    
    results = []
    
    for batch_size in batch_sizes:
        for concurrency in concurrency_levels:
            logger.info(f"\n测试批处理大小={batch_size}, 并发数={concurrency}...")
            start_time = time.time()
            total, matched, failed = await optimized_process(
                file_path,
                normalizer,
                mock_spotify_search,
                dummy_callback,
                batch_size=batch_size,
                max_concurrency=concurrency
            )
            elapsed_time = time.time() - start_time
            
            results.append({
                'batch_size': batch_size,
                'concurrency': concurrency,
                'time': elapsed_time,
                'songs_per_second': total / elapsed_time if elapsed_time > 0 else 0
            })
            
            logger.info(f"批处理大小={batch_size}, 并发数={concurrency} 耗时: {elapsed_time:.2f} 秒")
            logger.info(f"每秒处理歌曲数: {total / elapsed_time if elapsed_time > 0 else 0:.2f}")
    
    # 找出最佳配置
    best_config = max(results, key=lambda x: x['songs_per_second'])
    logger.info(f"\n最佳配置: 批处理大小={best_config['batch_size']}, 并发数={best_config['concurrency']}")
    logger.info(f"最佳性能: {best_config['time']:.2f} 秒, 每秒处理歌曲数: {best_config['songs_per_second']:.2f}")
    
    return {
        'original_time': original_time,
        'optimized_time': optimized_time,
        'improvement': improvement if original_time > 0 else 0,
        'best_config': best_config
    }

# 主函数
async def main():
    # 测试文件路径
    test_file = "performance_tests/large_songlist.txt"
    
    # 比较性能
    logger.info("开始性能比较测试...")
    results = await compare_performance(test_file, song_count=1000)
    
    logger.info("\n性能比较总结:")
    logger.info(f"原始版本耗时: {results['original_time']:.2f} 秒")
    logger.info(f"优化版本耗时: {results['optimized_time']:.2f} 秒")
    logger.info(f"性能提升: {results['improvement']:.2f}%")
    logger.info(f"最佳配置: 批处理大小={results['best_config']['batch_size']}, 并发数={results['best_config']['concurrency']}")
    logger.info(f"最佳性能: 每秒处理歌曲数: {results['best_config']['songs_per_second']:.2f}")
    
    logger.info("性能比较测试完成")

if __name__ == "__main__":
    asyncio.run(main()) 