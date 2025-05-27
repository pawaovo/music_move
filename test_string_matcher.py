"""
测试StringMatcher类的更新
"""
import os
import sys
import inspect
import logging

# 设置日志级别
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s: %(message)s',
    stream=sys.stdout
)

# 添加项目根目录到系统路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# 导入StringMatcher类
from spotify_playlist_importer.utils.string_matcher import StringMatcher

def test_string_matcher_methods():
    """测试StringMatcher类的方法"""
    # 创建StringMatcher实例
    matcher = StringMatcher()
    
    # 获取所有方法
    methods = inspect.getmembers(matcher, predicate=inspect.ismethod)
    method_names = [name for name, _ in methods]
    
    print("\n=== StringMatcher类的方法 ===")
    for name in sorted(method_names):
        print(f"- {name}")
    
    # 检查特定方法
    print("\n=== 特定方法检查 ===")
    has_get_pinyin = hasattr(matcher, "get_pinyin")
    print(f"get_pinyin 方法: {'✓ 存在' if has_get_pinyin else '× 不存在'}")
    
    has_calculate_artists_similarity = hasattr(matcher, "calculate_artists_similarity")
    print(f"calculate_artists_similarity 方法: {'✓ 存在' if has_calculate_artists_similarity else '× 不存在'}")
    
    has_calculate_combined_score = hasattr(matcher, "calculate_combined_score")
    print(f"calculate_combined_score 方法: {'✓ 存在' if has_calculate_combined_score else '× 不存在'}")
    
    # 如果get_pinyin存在，测试它
    if has_get_pinyin:
        print("\n=== 测试get_pinyin方法 ===")
        test_texts = ["周杰伦", "张三", "王力宏"]
        for text in test_texts:
            pinyin = matcher.get_pinyin(text)
            print(f"'{text}' -> '{pinyin}'")

if __name__ == "__main__":
    print("开始测试StringMatcher类...")
    test_string_matcher_methods()
    print("\n测试完成！") 