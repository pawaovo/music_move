import sys
import os

# 打印Python搜索路径
print("Python 搜索路径:")
for path in sys.path:
    print(f"  {path}")

# 打印相关模块
try:
    from spotify_playlist_importer.utils.enhanced_matcher import get_enhanced_match
    module_path = os.path.abspath(get_enhanced_match.__module__)
    print(f"\n导入的get_enhanced_match函数来自模块: {get_enhanced_match.__module__}")
    print(f"函数定义: {get_enhanced_match}")
    
    # 检查模块源文件
    import inspect
    if hasattr(get_enhanced_match, "__code__"):
        code = get_enhanced_match.__code__
        print(f"函数源文件: {code.co_filename}")
    else:
        print("无法获取函数源文件")
        
except ImportError as e:
    print(f"导入错误: {e}")
except Exception as e:
    print(f"其他错误: {e}") 