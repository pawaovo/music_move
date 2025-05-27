"""
测试 EnhancedMatcher 类的文本标准化功能，完全清除缓存
"""

import os
import sys
import importlib
import logging
import inspect

# 清除所有相关模块的缓存
for module in list(sys.modules.keys()):
    if 'spotify_playlist_importer' in module or 'enhanced_matcher' in module:
        del sys.modules[module]

# 设置日志级别
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s: %(message)s',
    stream=sys.stdout
)

# 添加项目根目录到系统路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def check_raw_file():
    """直接检查文件内容，不通过导入"""
    file_path = os.path.join(current_dir, 'spotify_playlist_importer', 'utils', 'enhanced_matcher.py')
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("\n=== 文件内容检查 ===")
    print(f"文件大小: {len(content)} 字节")
    
    has_method = "def standardize_texts" in content
    print(f"包含 standardize_texts 方法: {'是' if has_method else '否'}")
    
    if has_method:
        # 显示方法定义的上下文
        method_pos = content.find("def standardize_texts")
        context = content[max(0, method_pos-50):method_pos+200]
        print(f"方法定义上下文:\n{context}")

def test_method_existence():
    """测试 standardize_texts 方法是否存在"""
    # 完全清除 enhanced_matcher 缓存，重新导入
    if 'spotify_playlist_importer.utils.enhanced_matcher' in sys.modules:
        del sys.modules['spotify_playlist_importer.utils.enhanced_matcher']
    
    # 导入模块
    from spotify_playlist_importer.utils.enhanced_matcher import EnhancedMatcher
    
    # 获取类的所有方法
    all_methods = [name for name, _ in inspect.getmembers(EnhancedMatcher, predicate=inspect.isfunction)]
    print("\n=== 类方法检查 ===")
    print(f"EnhancedMatcher 类的所有方法: {all_methods}")
    
    # 实例化对象
    matcher = EnhancedMatcher()
    
    # 检查实例方法
    instance_methods = [name for name in dir(matcher) if not name.startswith('_') or name == '__init__']
    print(f"实例方法: {instance_methods}")
    
    # 检查标准化方法是否存在
    if hasattr(matcher, 'standardize_texts'):
        print("√ standardize_texts 方法已存在")
        return True
    else:
        print("× standardize_texts 方法不存在")
        return False

def test_standardization():
    """测试标准化功能"""
    if 'spotify_playlist_importer.utils.enhanced_matcher' in sys.modules:
        del sys.modules['spotify_playlist_importer.utils.enhanced_matcher']
    
    from spotify_playlist_importer.utils.enhanced_matcher import EnhancedMatcher
    
    matcher = EnhancedMatcher()
    
    # 检查方法是否存在
    if not hasattr(matcher, 'standardize_texts'):
        print("× 无法测试标准化功能：standardize_texts 方法不存在")
        return False
    
    print("\n=== 测试标准化功能 ===")
    
    # 准备测试数据
    input_title = "测试歌曲（现场版）"  # 简体中文，全角括号
    input_artists = ["艺术家A", "艺術家B"]  # 混合简繁体
    
    candidates = [
        {
            'name': '測試歌曲 (Live)',  # 繁体中文，半角括号
            'artists': [{'name': '藝術家A'}, {'name': '藝術家B'}],  # 繁体
            'id': 'track1'
        }
    ]
    
    print(f"输入标题: {input_title}")
    print(f"输入艺术家: {input_artists}")
    print(f"候选歌曲: {candidates[0]['name']}")
    
    # 执行标准化
    std_title, std_artists, std_candidates = matcher.standardize_texts(input_title, input_artists, candidates)
    
    # 检查结果
    print(f"标准化后标题: {std_title}")
    print(f"标准化后艺术家: {std_artists}")
    print(f"标准化后候选标题: {std_candidates[0]['name']}")
    print(f"标准化后候选艺术家: {[a['name'] for a in std_candidates[0]['artists']]}")
    
    return True

def test_match():
    """测试完整匹配流程"""
    if 'spotify_playlist_importer.utils.enhanced_matcher' in sys.modules:
        del sys.modules['spotify_playlist_importer.utils.enhanced_matcher']
    
    from spotify_playlist_importer.utils.enhanced_matcher import EnhancedMatcher, get_enhanced_match
    
    matcher = EnhancedMatcher()
    
    print("\n=== 测试匹配流程 ===")
    
    # 准备测试数据
    input_title = "测试歌曲（现场版）"  # 简体中文，全角括号
    input_artists = ["艺术家A", "艺術家B"]  # 混合简繁体
    
    candidates = [
        {
            'name': '測試歌曲 (Live)',  # 繁体中文，半角括号
            'artists': [{'name': '藝術家A'}, {'name': '藝術家B'}],  # 繁体
            'id': 'track1'
        },
        {
            'name': '另一首歌',
            'artists': [{'name': '其他艺术家'}],
            'id': 'track2'
        }
    ]
    
    print(f"执行匹配: {input_title} - {input_artists}")
    
    # 执行匹配
    matches = matcher.match(input_title, input_artists, candidates)
    
    # 检查结果
    if matches:
        best_match = matches[0]
        print(f"找到最佳匹配: {best_match['name']} (ID: {best_match['id']})")
        if 'similarity_scores' in best_match:
            scores = best_match['similarity_scores']
            print(f"匹配分数: {scores.get('final_score', 0):.2f}")
    else:
        print("未找到匹配")
    
    # 测试全局函数
    best_match = get_enhanced_match(input_title, input_artists, candidates)
    if best_match:
        print(f"全局函数结果: {best_match['name']} (ID: {best_match['id']})")
    else:
        print("全局函数未找到匹配")
    
    return True

def main():
    """主函数"""
    print("=== 开始全新测试 EnhancedMatcher 类的文本标准化功能 ===")
    
    # 直接检查文件内容
    check_raw_file()
    
    # 测试方法是否存在
    has_method = test_method_existence()
    
    if has_method:
        # 测试标准化功能
        test_standardization()
        
        # 测试匹配流程
        test_match()
        
        print("\n测试成功完成！")
    else:
        print("\n测试失败：standardize_texts 方法不存在")

if __name__ == "__main__":
    main() 