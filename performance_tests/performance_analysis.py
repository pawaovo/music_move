import asyncio
import time
import logging
import cProfile
import pstats
import io
import os
import sys
import random
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from spotify_playlist_importer.utils.text_normalizer import TextNormalizer
from spotify_playlist_importer.core.batch_processor import process_song_list_file
from spotify_playlist_importer.core.models import ParsedSong, MatchedSong

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建一个模拟的Spotify搜索函数
async def mock_spotify_search(parsed_song):
    """模拟Spotify搜索，随机返回成功或失败结果"""
    # 模拟API延迟
    await asyncio.sleep(random.uniform(0.05, 0.2))
    
    # 80%的概率返回成功结果
    if random.random() < 0.8:
        matched_song = MatchedSong(
            id=f"spotify:track:{random.randint(10000, 99999)}",
            name=f"Matched: {parsed_song.title}",
            artists=[f"Artist{i}" for i in range(random.randint(1, 3))],
            album="Some Album",
            uri=f"spotify:track:{random.randint(10000, 99999)}",
            duration_ms=random.randint(180000, 300000),
            popularity=random.randint(0, 100)
        )
        return matched_song, None
    else:
        return None, "未找到匹配"

# 创建测试数据
def generate_test_data(filename, num_songs=1000):
    """生成大量测试数据"""
    artists = [
        "周杰伦", "林俊杰", "Taylor Swift", "Ed Sheeran", "Adele", 
        "Beyoncé", "Jay-Z", "Eminem", "Rihanna", "Drake", "Ariana Grande",
        "Bruno Mars", "Lady Gaga", "Justin Bieber", "Katy Perry"
    ]
    
    titles = [
        "爱在西元前", "告白气球", "不能说的秘密", "Shake It Off", "Shape of You",
        "Hello", "Formation", "Lose Yourself", "Umbrella", "God's Plan",
        "Thank U, Next", "Uptown Funk", "Bad Romance", "Sorry", "Roar",
        "晴天", "江南", "可惜没如果", "Perfect", "Rolling in the Deep"
    ]
    
    with open(filename, 'w', encoding='utf-8') as f:
        for _ in range(num_songs):
            title = random.choice(titles)
            
            # 随机选择1-3个艺术家
            num_artists = random.randint(1, 3)
            selected_artists = random.sample(artists, num_artists)
            
            # 随机选择格式
            format_type = random.randint(1, 4)
            if format_type == 1:  # 只有标题
                line = title
            elif format_type == 2:  # 标准格式 "Title - Artist"
                line = f"{title} - {selected_artists[0]}"
            elif format_type == 3:  # 多艺术家 "Title - Artist1 / Artist2"
                line = f"{title} - {' / '.join(selected_artists)}"
            else:  # 特殊格式 " - Artist"
                line = f" - {selected_artists[0]}"
            
            f.write(f"{line}\n")
    
    logger.info(f"已生成 {num_songs} 首歌曲到 {filename}")

# 性能测试函数
async def run_performance_test(file_path, batch_size=None):
    """运行性能测试"""
    normalizer = TextNormalizer()
    
    # 用于收集结果的回调函数
    results = []
    async def result_callback(original_line, title, artists, norm_title, norm_artists, search_result):
        results.append((original_line, search_result))
    
    # 使用cProfile进行性能分析
    pr = cProfile.Profile()
    pr.enable()
    
    start_time = time.time()
    
    # 处理文件
    total, matched, failed = await process_song_list_file(
        file_path,
        normalizer,
        mock_spotify_search,
        result_callback
    )
    
    elapsed_time = time.time() - start_time
    pr.disable()
    
    # 输出性能统计
    logger.info(f"处理完成! 总计: {total}, 成功: {matched}, 失败: {failed}")
    logger.info(f"总耗时: {elapsed_time:.2f} 秒")
    logger.info(f"平均每首歌曲处理时间: {(elapsed_time / total if total else 0):.4f} 秒")
    
    # 输出详细的性能分析
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats(20)  # 打印前20个最耗时的函数
    logger.info(f"性能分析结果:\n{s.getvalue()}")
    
    return elapsed_time, total, matched, failed

# 主函数
async def main():
    # 测试文件路径
    test_file = "performance_tests/large_songlist.txt"
    
    # 生成测试数据
    if not os.path.exists(test_file):
        generate_test_data(test_file, num_songs=1000)
    
    logger.info("开始性能测试...")
    await run_performance_test(test_file)
    
    logger.info("性能测试完成")

if __name__ == "__main__":
    asyncio.run(main()) 