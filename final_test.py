"""
测试EnhancedMatcher类的文本标准化功能
"""

import os
import sys
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

# 清除相关模块的缓存
for module in list(sys.modules.keys()):
    if 'spotify_playlist_importer' in module:
        del sys.modules[module]

# 导入EnhancedMatcher类
from spotify_playlist_importer.utils.enhanced_matcher import EnhancedMatcher

def test_standardize_texts():
    """测试文本标准化功能"""
    logging.info("=== 测试文本标准化功能 ===")
    
    # 创建EnhancedMatcher实例
    matcher = EnhancedMatcher()
    
    # 检查方法是否存在
    if not hasattr(matcher, 'standardize_texts'):
        logging.error("EnhancedMatcher类没有standardize_texts方法")
        return False
    
    logging.info("成功：EnhancedMatcher类拥有standardize_texts方法")
    
    # 准备测试数据：简繁体混合测试
    input_title = "测试歌曲（现场版）"  # 简体中文，全角括号
    input_artists = ["艺术家A", "艺術家B"]  # 混合简繁体
    
    candidates = [
        {
            'name': '測試歌曲 (Live)',  # 繁体中文，半角括号
            'artists': [{'name': '藝術家A'}, {'name': '藝術家B'}],  # 繁体
            'id': 'track1'
        }
    ]
    
    # 调用standardize_texts方法
    try:
        std_title, std_artists, std_candidates = matcher.standardize_texts(input_title, input_artists, candidates)
        
        # 检查标准化结果
        logging.info(f"输入标题: '{input_title}' -> 标准化: '{std_title}'")
        logging.info(f"输入艺术家: {input_artists} -> 标准化: {std_artists}")
        logging.info(f"候选标题: '{candidates[0]['name']}' -> 标准化: '{std_candidates[0]['name']}'")
        
        # 检查简繁体转换是否正确（应该都转为简体）
        if '测试' in std_title and '测试' in std_candidates[0]['name']:
            logging.info("成功：简繁体汉字转换正确")
        else:
            logging.error("失败：简繁体汉字转换有问题")
            return False
        
        # 检查括号标准化（全角括号应转为半角）
        if '(' in std_title and not '（' in std_title:
            logging.info("成功：括号标准化正确")
        else:
            logging.error("失败：括号标准化有问题")
            return False
        
        return True
    
    except Exception as e:
        logging.error(f"调用standardize_texts方法失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_match_with_standardization():
    """测试match方法中的标准化处理"""
    logging.info("\n=== 测试match方法标准化处理 ===")
    
    # 创建EnhancedMatcher实例
    matcher = EnhancedMatcher()
    
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
    
    # 调用match方法
    try:
        matches = matcher.match(input_title, input_artists, candidates)
        
        # 检查匹配结果
        if not matches:
            logging.error("匹配失败：未找到匹配结果")
            return False
        
        # 获取最佳匹配
        best_match = matches[0]
        logging.info(f"匹配成功: '{best_match['name']}' (ID: {best_match['id']})")
        
        # 验证匹配的是正确的歌曲
        if best_match['id'] == 'track1':
            logging.info("成功：匹配到了正确的歌曲")
        else:
            logging.error(f"失败：匹配到了错误的歌曲 ID: {best_match['id']}")
            return False
        
        # 检查匹配分数
        if 'similarity_scores' in best_match:
            score = best_match['similarity_scores'].get('final_score', 0)
            logging.info(f"匹配分数: {score:.2f}")
            
            # 验证匹配分数是否较高（简繁体标准化后应该有较高匹配分数）
            if score > 90:
                logging.info("成功：匹配分数较高，表明标准化正常工作")
            else:
                logging.warning(f"警告：匹配分数较低 ({score:.2f})，标准化可能未正常工作")
        
        return True
    
    except Exception as e:
        logging.error(f"调用match方法失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    logging.info("开始测试EnhancedMatcher的文本标准化功能...")
    
    # 测试standardize_texts方法
    if not test_standardize_texts():
        logging.error("standardize_texts方法测试失败")
        return False
    
    # 测试match方法中的标准化处理
    if not test_match_with_standardization():
        logging.error("match方法标准化处理测试失败")
        return False
    
    logging.info("\n所有测试通过！EnhancedMatcher的文本标准化功能正常工作")
    print("\n恭喜！标准化功能已成功实现，现在系统可以正确处理简繁体汉字和全半角符号差异")
    return True

if __name__ == "__main__":
    main() 