"""
直接测试 EnhancedMatcher 的 standardize_texts 方法
"""

import os
import sys
import importlib
import logging

# 清除相关模块的缓存
for module in list(sys.modules.keys()):
    if 'spotify_playlist_importer' in module:
        del sys.modules[module]

# 设置日志级别
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s',
    stream=sys.stdout
)

# 添加项目根目录到系统路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

print("导入 EnhancedMatcher 类...")
from spotify_playlist_importer.utils.enhanced_matcher import EnhancedMatcher

# 创建实例
print("创建 EnhancedMatcher 实例...")
matcher = EnhancedMatcher()

# 尝试直接调用 match 方法
print("准备测试数据...")
input_title = "测试歌曲"
input_artists = ["测试艺术家"]
candidates = [
    {
        'name': '测试歌曲',
        'artists': [{'name': '测试艺术家'}],
        'id': 'track1'
    }
]

print("调用 match 方法...")
try:
    results = matcher.match(input_title, input_artists, candidates)
    print(f"匹配结果: {results}")
    print("match 方法调用成功，说明 standardize_texts 方法正常工作")
except Exception as e:
    print(f"match 方法调用失败: {e}")

# 尝试直接调用 standardize_texts 方法
print("\n尝试直接调用 standardize_texts 方法...")
try:
    # 检查方法是否存在于实例中
    print(f"standardize_texts 存在于实例中: {hasattr(matcher, 'standardize_texts')}")
    
    # 获取类的方法列表
    class_methods = [m for m in dir(EnhancedMatcher) if callable(getattr(EnhancedMatcher, m)) and not m.startswith('_')]
    print(f"类的公开方法列表: {class_methods}")
    
    # 获取对象的方法列表
    instance_methods = [m for m in dir(matcher) if not m.startswith('_') or m == '__init__']
    print(f"实例的方法列表: {instance_methods}")
    
    # 直接调用方法
    logging.info("直接调用 standardize_texts 方法...")
    std_title, std_artists, std_candidates = matcher.standardize_texts(input_title, input_artists, candidates)
    print(f"标准化结果: {std_title}, {std_artists}, {len(std_candidates)} 个候选")
    print("standardize_texts 方法调用成功")
except AttributeError:
    print("AttributeError: standardize_texts 方法不存在")
except Exception as e:
    print(f"调用 standardize_texts 方法时出错: {e}")

# 尝试通过 getattr 调用
print("\n尝试通过 getattr 调用 standardize_texts 方法...")
try:
    if hasattr(EnhancedMatcher, 'standardize_texts'):
        std_method = getattr(EnhancedMatcher, 'standardize_texts')
        print(f"获取到方法: {std_method}")
        result = std_method(matcher, input_title, input_artists, candidates)
        print(f"调用成功，结果: {result}")
    else:
        print("getattr 无法找到 standardize_texts 方法")
except Exception as e:
    print(f"通过 getattr 调用失败: {e}")

# 解析类定义源代码
print("\n检查类定义源代码...")
try:
    import inspect
    source_code = inspect.getsource(EnhancedMatcher)
    print(f"类源代码长度: {len(source_code)} 字符")
    
    # 检查源代码中是否包含 standardize_texts 方法
    has_method = "def standardize_texts" in source_code
    print(f"源代码中包含 standardize_texts 方法定义: {has_method}")
    
    if has_method:
        # 找到方法定义的开始位置
        start_pos = source_code.find("def standardize_texts")
        if start_pos != -1:
            # 截取方法定义部分
            method_def = source_code[start_pos:start_pos+200]
            print(f"方法定义片段:\n{method_def}")
except Exception as e:
    print(f"解析源代码时出错: {e}")

print("\n尝试查看 __dict__ 内容...")
try:
    # 检查类的 __dict__
    class_dict = EnhancedMatcher.__dict__
    print(f"类的 __dict__ 键: {list(class_dict.keys())}")
    
    # 检查实例的 __dict__
    instance_dict = matcher.__dict__
    print(f"实例的 __dict__ 键: {list(instance_dict.keys())}")
except Exception as e:
    print(f"查看 __dict__ 时出错: {e}")

print("\n测试结束") 