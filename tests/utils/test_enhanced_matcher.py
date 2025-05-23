"""测试增强匹配模块"""

import unittest
from typing import Dict, List, Any

from spotify_playlist_importer.utils.enhanced_matcher import (
    EnhancedMatcher,
    get_best_enhanced_match
)


class TestEnhancedMatcher(unittest.TestCase):
    """测试EnhancedMatcher类"""

    def setUp(self):
        """测试前的设置"""
        self.matcher = EnhancedMatcher()
        
        # 创建测试用的候选歌曲
        self.candidates = [
            {
                'name': 'Perfect Match',
                'artists': [{'name': 'Artist1'}, {'name': 'Artist2'}],
                'id': 'track1'
            },
            {
                'name': 'Perfect Match (Live)',
                'artists': [{'name': 'Artist1'}, {'name': 'Artist2'}],
                'id': 'track2'
            },
            {
                'name': 'Perfect Match (Remix)',
                'artists': [{'name': 'Artist1'}, {'name': 'Artist2'}],
                'id': 'track3'
            },
            {
                'name': 'Close Match',
                'artists': [{'name': 'Artist1'}],
                'id': 'track4'
            },
            {
                'name': 'Different Song',
                'artists': [{'name': 'Artist3'}],
                'id': 'track5'
            }
        ]

    def test_initialization(self):
        """测试初始化和参数设置"""
        matcher = EnhancedMatcher(
            title_weight=0.7,
            artist_weight=0.3,
            bracket_weight=0.4,
            first_stage_threshold=65.0,
            second_stage_threshold=75.0,
            top_k=5
        )
        
        # 验证参数是否正确设置
        self.assertEqual(matcher.title_weight, 0.7)
        self.assertEqual(matcher.artist_weight, 0.3)
        self.assertEqual(matcher.bracket_weight, 0.4)
        self.assertEqual(matcher.first_stage_threshold, 65.0)
        self.assertEqual(matcher.second_stage_threshold, 75.0)
        self.assertEqual(matcher.top_k, 5)
        
        # 验证内部匹配器是否正确配置
        self.assertEqual(matcher.string_matcher.title_weight, 0.7)
        self.assertEqual(matcher.string_matcher.artist_weight, 0.3)
        self.assertEqual(matcher.string_matcher.threshold, 65.0)
        self.assertEqual(matcher.bracket_matcher.bracket_weight, 0.4)
        self.assertEqual(matcher.bracket_matcher.threshold, 75.0)

    def test_match_exact_title(self):
        """测试完全匹配标题的情况"""
        input_title = "Perfect Match"
        input_artists = ["Artist1", "Artist2"]
        
        results = self.matcher.match(input_title, input_artists, self.candidates)
        
        # 检查是否返回结果
        self.assertGreater(len(results), 0)
        
        # 检查最匹配的结果是否正确
        self.assertEqual(results[0]['id'], 'track1')
        
        # 检查分数是否存在
        self.assertIn('similarity_scores', results[0])
        self.assertIn('final_score', results[0]['similarity_scores'])

    def test_match_with_brackets(self):
        """测试带括号的匹配情况"""
        input_title = "Perfect Match (Live)"
        input_artists = ["Artist1", "Artist2"]
        
        results = self.matcher.match(input_title, input_artists, self.candidates)
        
        # 检查是否返回结果
        self.assertGreater(len(results), 0)
        
        # 检查最匹配的结果是否正确（应该是Live版本）
        self.assertEqual(results[0]['id'], 'track2')
        
        # 检查括号分数是否存在并且为正值
        self.assertIn('bracket_score', results[0]['similarity_scores'])
        self.assertGreaterEqual(results[0]['similarity_scores']['bracket_score'], 0)

    def test_match_partial(self):
        """测试部分匹配的情况"""
        input_title = "Perfect"  # 只有部分标题
        input_artists = ["Artist1"]  # 只有部分艺术家
        
        results = self.matcher.match(input_title, input_artists, self.candidates)
        
        # 检查是否返回结果
        self.assertGreater(len(results), 0)
        
        # 任何包含"Perfect"的歌曲都应该匹配
        self.assertTrue(any(r['id'] in ['track1', 'track2', 'track3'] for r in results))

    def test_match_no_results(self):
        """测试无匹配结果的情况"""
        input_title = "Completely Different Song"
        input_artists = ["Unknown Artist"]
        
        # 创建一个高阈值的匹配器
        high_threshold_matcher = EnhancedMatcher(
            first_stage_threshold=95.0,  # 设置非常高的阈值
            second_stage_threshold=95.0
        )
        
        results = high_threshold_matcher.match(input_title, input_artists, self.candidates)
        
        # 检查是否没有返回结果
        self.assertEqual(len(results), 0)

    def test_bracket_improves_score(self):
        """测试括号内容如何提高匹配分数"""
        # 准备特殊的候选歌曲，具有相同的基本标题但不同的括号内容
        special_candidates = [
            {
                'name': 'Same Title',
                'artists': [{'name': 'Artist1'}],
                'id': 'track1'
            },
            {
                'name': 'Same Title (Live)',
                'artists': [{'name': 'Artist1'}],
                'id': 'track2'
            }
        ]
        
        # 匹配带括号的输入
        input_title = "Same Title (Live)"
        input_artists = ["Artist1"]
        
        results = self.matcher.match(input_title, input_artists, special_candidates)
        
        # 确保有结果返回
        self.assertGreater(len(results), 0)
        
        # 检查最匹配的结果是否正确（应该是带括号的版本）
        self.assertEqual(results[0]['id'], 'track2')
        
        # 检查是否有括号分数字段
        self.assertIn('bracket_score', results[0]['similarity_scores'])

    def test_get_best_enhanced_match(self):
        """测试获取最佳匹配的便利函数"""
        # 测试标准匹配
        best_match = get_best_enhanced_match(
            "Perfect Match",
            ["Artist1", "Artist2"],
            self.candidates
        )
        self.assertIsNotNone(best_match)
        self.assertEqual(best_match['id'], 'track1')
        
        # 测试带括号的精确匹配
        best_match = get_best_enhanced_match(
            "Perfect Match (Live)",
            ["Artist1", "Artist2"],
            self.candidates
        )
        self.assertIsNotNone(best_match)
        self.assertEqual(best_match['id'], 'track2')
        
        # 测试无匹配的情况
        no_match = get_best_enhanced_match(
            "No Match At All",
            ["Unknown"],
            self.candidates,
            first_stage_threshold=90.0  # 设置高阈值以确保没有匹配
        )
        self.assertIsNone(no_match)


if __name__ == '__main__':
    unittest.main() 