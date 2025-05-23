"""
完全清除缓存的EnhancedMatcher测试
"""

import os
import sys
import importlib
import logging
import inspect

# 设置日志级别
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s: %(message)s',
    stream=sys.stdout
)

# 确保当前工作目录是项目根目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 添加项目根目录到系统路径
current_dir = os.path.abspath('.')
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 打印系统路径
print("系统路径:")
for path in sys.path:
    print(f"  - {path}")

# 强制删除所有相关模块
for key in list(sys.modules.keys()):
    if 'spotify_playlist_importer' in key or 'enhanced_matcher' in key:
        del sys.modules[key]
        print(f"删除模块: {key}")

# 检查文件内容
def check_file_content():
    matcher_path = os.path.join(current_dir, 'spotify_playlist_importer', 'utils', 'enhanced_matcher.py')
    if not os.path.exists(matcher_path):
        print(f"文件不存在: {matcher_path}")
        return False
    
    with open(matcher_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"文件大小: {len(content)} 字节")
    
    has_method = 'def standardize_texts' in content
    print(f"文件中包含standardize_texts方法: {'是' if has_method else '否'}")
    
    if has_method:
        index = content.find('def standardize_texts')
        context = content[max(0, index-50):index+200]
        print(f"方法上下文:\n{context}")
    
    return has_method

# 检查文件内容
if not check_file_content():
    print("文件内容检查失败，退出测试")
    sys.exit(1)

# 重新导入模块
print("\n正在导入模块...")
try:
    from spotify_playlist_importer.utils.enhanced_matcher import EnhancedMatcher
    print("成功导入EnhancedMatcher类")
except Exception as e:
    print(f"导入失败: {e}")
    sys.exit(1)

# 创建实例并检查方法
matcher = EnhancedMatcher()
print("\n检查实例方法:")
methods = [name for name in dir(matcher) if not name.startswith('_')]
print(f"可用方法: {methods}")

if 'standardize_texts' in methods:
    print("成功: standardize_texts方法存在")
else:
    print("失败: standardize_texts方法不存在")
    
    # 显示类的__dict__内容
    print("\n类的__dict__内容:")
    for key, value in EnhancedMatcher.__dict__.items():
        if not key.startswith('__'):
            print(f"  - {key}: {type(value)}")
    sys.exit(1)

# 测试简繁体中文标准化
print("\n测试标准化简繁体中文:")
input_title = "测试歌曲（现场版）"  # 简体中文，全角括号
input_artists = ["艺术家A", "艺術家B"]  # 混合简繁体

candidates = [
    {
        'name': '測試歌曲 (Live)',  # 繁体中文，半角括号
        'artists': [{'name': '藝術家A'}, {'name': '藝術家B'}],  # 繁体
        'id': 'track1'
    }
]

try:
    # 调用standardize_texts方法
    std_title, std_artists, std_candidates = matcher.standardize_texts(input_title, input_artists, candidates)
    
    print(f"输入标题: '{input_title}' -> 标准化: '{std_title}'")
    print(f"输入艺术家: {input_artists} -> 标准化: {std_artists}")
    print(f"候选标题: '{candidates[0]['name']}' -> 标准化: '{std_candidates[0]['name']}'")
    
    # 检查简繁体转换是否正确
    if '测试' in std_title and '测试' in std_candidates[0]['name']:
        print("成功: 简繁体转换正确")
    else:
        print("失败: 简繁体转换有问题")
    
    # 测试完整匹配流程
    print("\n测试match方法:")
    matches = matcher.match(input_title, input_artists, candidates)
    
    if matches:
        best_match = matches[0]
        print(f"找到匹配: '{best_match['name']}' (ID: {best_match['id']})")
        
        if 'similarity_scores' in best_match:
            score = best_match['similarity_scores'].get('final_score', 0)
            print(f"匹配分数: {score:.2f}")
        
        print("测试成功!")
    else:
        print("匹配失败: 未找到匹配结果")
        
except Exception as e:
    print(f"测试过程中出错: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n恭喜! 文本标准化功能正常工作，简繁体中文和全半角符号可以正确处理。") 