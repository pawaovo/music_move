#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
简化的调试脚本，测试仅艺术家搜索匹配分设置为0分的功能
"""

import logging
import sys
import os
import traceback

# 添加项目根目录到路径
current_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, current_dir)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

def test_artist_only_search():
    """测试仅艺术家搜索匹配分设置为0分的功能"""
    print("\n=== 测试仅艺术家搜索匹配分设置为0分 ===")
    
    # 显示导入路径
    print("\n当前导入路径:")
    for p in sys.path:
        print(f"  - {p}")
    
    # 尝试从两个可能的位置导入
    print("\n尝试导入模块:")
    
    # 尝试从第一个位置导入
    try:
        print("\n1. 尝试从 spotify_playlist_importer.utils.enhanced_matcher 导入")
        from spotify_playlist_importer.utils.enhanced_matcher import get_enhanced_match as get_match1
        print("  - 成功导入 get_enhanced_match")
        
        # 测试导入的函数
        input_title = "告白气球"
        input_artists = ["周杰伦"]
        candidates = [
            {
                "name": "告白气球",
                "artists": [{"name": "周杰伦"}],
                "id": "123",
                "uri": "spotify:track:123"
            }
        ]
        
        print("\n  测试仅艺术家搜索:")
        try:
            result = get_match1(input_title, input_artists, candidates, is_artist_only_search=True)
            if result:
                score = result["similarity_scores"].get("final_score", 0)
                original_score = result["similarity_scores"].get("original_score", "未保存")
                print(f"  分数: {score}")
                print(f"  原始分数: {original_score}")
                print(f"  低置信度: {result['similarity_scores'].get('is_low_confidence', False)}")
                
                if score == 0:
                    print("  ✓ 验证通过: 分数已正确设置为0")
                else:
                    print(f"  ✗ 验证失败: 分数为 {score}，不为0")
            else:
                print("  未找到匹配项")
        except Exception as e:
            print(f"  测试函数时出错: {e}")
            traceback.print_exc()
    except ImportError as e:
        print(f"  导入失败: {e}")
    
    # 尝试从第二个位置导入
    try:
        print("\n2. 尝试从 utils.enhanced_matcher 导入")
        sys.path.append(os.path.join(current_dir, "spotify_playlist_importer"))
        from utils.enhanced_matcher import get_enhanced_match as get_match2
        print("  - 成功导入 get_enhanced_match")
        
        # 测试导入的函数
        input_title = "告白气球"
        input_artists = ["周杰伦"]
        candidates = [
            {
                "name": "告白气球",
                "artists": [{"name": "周杰伦"}],
                "id": "123",
                "uri": "spotify:track:123"
            }
        ]
        
        print("\n  测试仅艺术家搜索:")
        try:
            result = get_match2(input_title, input_artists, candidates, is_artist_only_search=True)
            if result:
                score = result["similarity_scores"].get("final_score", 0)
                original_score = result["similarity_scores"].get("original_score", "未保存")
                print(f"  分数: {score}")
                print(f"  原始分数: {original_score}")
                print(f"  低置信度: {result['similarity_scores'].get('is_low_confidence', False)}")
                
                if score == 0:
                    print("  ✓ 验证通过: 分数已正确设置为0")
                else:
                    print(f"  ✗ 验证失败: 分数为 {score}，不为0")
            else:
                print("  未找到匹配项")
        except Exception as e:
            print(f"  测试函数时出错: {e}")
            traceback.print_exc()
    except ImportError as e:
        print(f"  导入失败: {e}")
    
    # 尝试从第三个位置导入
    try:
        print("\n3. 尝试从 spotify_playlist_importer.spotify_playlist_importer.utils.enhanced_matcher 导入")
        from spotify_playlist_importer.spotify_playlist_importer.utils.enhanced_matcher import get_enhanced_match as get_match3
        print("  - 成功导入 get_enhanced_match")
        
        # 测试导入的函数
        input_title = "告白气球"
        input_artists = ["周杰伦"]
        candidates = [
            {
                "name": "告白气球",
                "artists": [{"name": "周杰伦"}],
                "id": "123",
                "uri": "spotify:track:123"
            }
        ]
        
        print("\n  测试仅艺术家搜索:")
        try:
            result = get_match3(input_title, input_artists, candidates, is_artist_only_search=True)
            if result:
                score = result["similarity_scores"].get("final_score", 0)
                original_score = result["similarity_scores"].get("original_score", "未保存")
                print(f"  分数: {score}")
                print(f"  原始分数: {original_score}")
                print(f"  低置信度: {result['similarity_scores'].get('is_low_confidence', False)}")
                
                if score == 0:
                    print("  ✓ 验证通过: 分数已正确设置为0")
                else:
                    print(f"  ✗ 验证失败: 分数为 {score}，不为0")
            else:
                print("  未找到匹配项")
        except Exception as e:
            print(f"  测试函数时出错: {e}")
            traceback.print_exc()
    except ImportError as e:
        print(f"  导入失败: {e}")

if __name__ == "__main__":
    try:
        test_artist_only_search()
    except Exception as e:
        print(f"测试过程中出错: {e}")
        traceback.print_exc() 