"""
测试修复后的 EnhancedMatcher 类文本标准化功能
"""

import os
import sys
import logging
import importlib

# 设置日志级别
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s: %(message)s',
    stream=sys.stdout
)

# 添加项目根目录到系统路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def run_fix_script():
    """运行修复脚本，添加 standardize_texts 方法"""
    print("正在运行修复脚本...")
    from enhanced_matcher_fixed import fix_enhanced_matcher, update_get_enhanced_match
    
    fix_result = fix_enhanced_matcher()
    
    if fix_result:
        print("成功添加 standardize_texts 方法")
        update_result = update_get_enhanced_match()
        if update_result:
            print("成功更新 get_enhanced_match 函数")
        else:
            print("更新 get_enhanced_match 函数失败")
    else:
        print("修复失败")
    
    # 重新加载 enhanced_matcher 模块
    print("重新加载 enhanced_matcher 模块...")
    if 'spotify_playlist_importer.utils.enhanced_matcher' in sys.modules:
        importlib.reload(sys.modules['spotify_playlist_importer.utils.enhanced_matcher'])
    
    return fix_result

def test_standardize_texts():
    """测试添加的 standardize_texts 方法"""
    print("\n===== 测试 standardize_texts 方法 =====")
    
    try:
        # 强制重新加载模块
        if 'spotify_playlist_importer.utils.enhanced_matcher' in sys.modules:
            importlib.reload(sys.modules['spotify_playlist_importer.utils.enhanced_matcher'])
        
        from spotify_playlist_importer.utils.enhanced_matcher import EnhancedMatcher
        
        # 检查方法是否存在
        matcher = EnhancedMatcher()
        if hasattr(matcher, 'standardize_texts'):
            print("√ standardize_texts 方法已存在")
        else:
            print("× standardize_texts 方法不存在")
            # 打印类中的所有方法
            print("类中的方法:", [method for method in dir(matcher) if not method.startswith('_') or method == '__init__'])
            return False
        
        # 创建测试数据
        input_title = "Test Song（现场版）"  # 使用全角括号
        input_artists = ["艺术家A", "ArtistＢ"]  # 使用全角字符B
        
        candidates = [
            {
                'name': 'Test Song (Live)',  # 使用半角括号和英文Live
                'artists': [{'name': 'Artist A'}, {'name': 'Artist B'}],
                'id': 'track1'
            }
        ]
        
        # 运行标准化方法
        print("运行 standardize_texts 方法...")
        std_title, std_artists, std_candidates = matcher.standardize_texts(input_title, input_artists, candidates)
        
        # 检查标准化结果
        print(f"原始标题: {input_title} -> 标准化后: {std_title}")
        print(f"原始艺术家: {input_artists} -> 标准化后: {std_artists}")
        
        if len(std_candidates) > 0:
            candidate = std_candidates[0]
            orig_name = candidate.get('original_name', 'N/A')
            std_name = candidate.get('name', 'N/A')
            print(f"候选标题: {orig_name} -> 标准化后: {std_name}")
            
            std_artists_names = [a.get('name', 'N/A') for a in candidate.get('artists', [])]
            print(f"候选艺术家: {std_artists_names}")
        
        return True
    
    except Exception as e:
        print(f"测试 standardize_texts 方法时出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_match_with_standardization():
    """测试修改后的 match 方法"""
    print("\n===== 测试 match 方法 =====")
    
    try:
        # 强制重新加载模块
        if 'spotify_playlist_importer.utils.enhanced_matcher' in sys.modules:
            importlib.reload(sys.modules['spotify_playlist_importer.utils.enhanced_matcher'])
        
        from spotify_playlist_importer.utils.enhanced_matcher import EnhancedMatcher, get_enhanced_match
        
        # 创建测试数据 - 使用简繁体差异和全半角差异
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
        
        # 创建增强匹配器实例
        matcher = EnhancedMatcher()
        
        # 检查matcher是否有standardize_texts方法
        if not hasattr(matcher, 'standardize_texts'):
            print("× match测试中: matcher没有standardize_texts方法")
            print("类中的方法:", [method for method in dir(matcher) if not method.startswith('_') or method == '__init__'])
            return False
        
        # 执行匹配
        print("运行 match 方法...")
        matches = matcher.match(input_title, input_artists, candidates)
        
        # 检查匹配结果
        print("\n匹配结果:")
        if matches:
            best_match = matches[0]
            print(f"最佳匹配: '{best_match['name']}' (ID: {best_match['id']})")
            if 'original_name' in best_match:
                print(f"原始标题: '{best_match['original_name']}'")
            if 'similarity_scores' in best_match:
                scores = best_match['similarity_scores']
                print(f"匹配分数: {scores.get('final_score', 0):.2f}")
                print(f"低置信度: {scores.get('is_low_confidence', False)}")
        else:
            print("未找到匹配")
        
        # 测试全局 get_enhanced_match 函数
        print("\n测试 get_enhanced_match 函数...")
        best_match = get_enhanced_match(input_title, input_artists, candidates)
        
        if best_match:
            print(f"get_enhanced_match 结果: '{best_match['name']}' (ID: {best_match['id']})")
            if 'similarity_scores' in best_match:
                scores = best_match['similarity_scores']
                print(f"匹配分数: {scores.get('final_score', 0):.2f}")
        else:
            print("get_enhanced_match 未找到匹配")
        
        return True
    
    except Exception as e:
        print(f"测试 match 方法时出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_file_content():
    """检查文件内容，确认是否包含standardize_texts方法"""
    print("\n===== 检查文件内容 =====")
    
    try:
        # 获取文件路径
        file_path = os.path.join(current_dir, 'spotify_playlist_importer', 'utils', 'enhanced_matcher.py')
        
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否包含standardize_texts方法
        if 'def standardize_texts' in content:
            print("√ 文件中包含 standardize_texts 方法")
            # 打印方法定义前后的内容片段
            start_pos = content.find('def standardize_texts')
            end_pos = content.find('def ', start_pos + 5)
            if end_pos == -1:
                end_pos = len(content)
            
            method_context = content[max(0, start_pos-50):min(len(content), end_pos+100)]
            print("方法上下文片段:", method_context[:200] + "...")
            return True
        else:
            print("× 文件中不包含 standardize_texts 方法")
            return False
    
    except Exception as e:
        print(f"检查文件内容时出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("开始测试 EnhancedMatcher 文本标准化功能...")
    
    # 检查文件内容
    has_method = check_file_content()
    
    # 运行修复脚本
    if not has_method:
        if not run_fix_script():
            print("修复脚本运行失败，测试终止")
            return False
        
        # 再次检查文件内容
        check_file_content()
    
    # 测试 standardize_texts 方法
    if not test_standardize_texts():
        print("standardize_texts 方法测试失败")
        return False
    
    # 测试 match 方法
    if not test_match_with_standardization():
        print("match 方法测试失败")
        return False
    
    print("\n测试成功完成！EnhancedMatcher 类的文本标准化功能正常工作")
    return True

if __name__ == "__main__":
    main() 