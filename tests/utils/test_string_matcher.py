"""StringMatcher模块的单元测试"""

import unittest
from typing import Dict, List, Any

from spotify_playlist_importer.utils.string_matcher import StringMatcher, get_best_match


class TestStringMatcher(unittest.TestCase):
    """字符串相似度匹配模块的单元测试"""

    def setUp(self):
        """测试前的设置"""
        self.matcher = StringMatcher()

    def test_initialization(self):
        """测试初始化和参数验证"""
        # 测试默认参数
        matcher = StringMatcher()
        self.assertEqual(matcher.title_weight, 0.6)
        self.assertEqual(matcher.artist_weight, 0.4)
        self.assertEqual(matcher.threshold, 75.0)
        self.assertEqual(matcher.top_k, 3)

        # 测试自定义参数
        matcher = StringMatcher(
            title_weight=0.7,
            artist_weight=0.3,
            threshold=80.0,
            top_k=5
        )
        self.assertEqual(matcher.title_weight, 0.7)
        self.assertEqual(matcher.artist_weight, 0.3)
        self.assertEqual(matcher.threshold, 80.0)
        self.assertEqual(matcher.top_k, 5)

        # 测试无效权重
        with self.assertRaises(ValueError):
            StringMatcher(title_weight=1.1, artist_weight=0.4)

        with self.assertRaises(ValueError):
            StringMatcher(title_weight=-0.1, artist_weight=0.4)

        # 测试权重和不为1.0
        with self.assertRaises(ValueError):
            StringMatcher(title_weight=0.7, artist_weight=0.5)

    def test_normalize_for_matching(self):
        """测试文本归一化功能"""
        test_cases = [
            ("Song Title (Live Version)", "song title"),
            ("Artist Name [Remix]", "artist name"),
            ("UPPERCASE title", "uppercase title"),
            ("Ｆｕｌｌ　Ｗｉｄｔｈ", "full width"),
            ("Artist1 & Artist2", "artist1 artist2"),
        ]

        for input_text, expected_output in test_cases:
            self.assertEqual(self.matcher.normalize_for_matching(input_text), expected_output)

    def test_calculate_title_similarity(self):
        """测试标题相似度计算功能"""
        test_cases = [
            # 完全匹配
            ("Song Title", "Song Title", 90.0),
            # 大小写差异
            ("song title", "Song Title", 90.0),
            # 括号差异 (归一化后是相同的)
            ("Song Title", "Song Title (Live)", 90.0),
            # 小差异
            ("Song Title", "Song Titl", 80.0),
            # 词序不同
            ("Title of Song", "Song Title", 45.0),
            # 完全不同
            ("Song Title", "Different Music", 5.0),
        ]

        for input_title, candidate_title, expected_min_score in test_cases:
            score = self.matcher.calculate_title_similarity(input_title, candidate_title)
            self.assertGreaterEqual(
                score, expected_min_score,
                f"标题 '{input_title}' 和 '{candidate_title}' 的相似度 {score} 低于预期的 {expected_min_score}"
            )

    def test_calculate_artists_similarity(self):
        """测试艺术家相似度计算功能"""
        test_cases = [
            # 完全匹配
            (["Artist1"], ["Artist1"], 100.0),
            # 大小写和括号差异
            (["artist1"], ["Artist1 (Official)"], 100.0),
            # 多个艺术家，完全匹配
            (["Artist1", "Artist2"], ["Artist1", "Artist2"], 100.0),
            # 多个艺术家，部分匹配
            (["Artist1", "Artist2"], ["Artist1", "Artist3"], 50.0),
            # 多个艺术家，顺序不同
            (["Artist1", "Artist2"], ["Artist2", "Artist1"], 100.0),
            # 空列表
            ([], ["Artist1"], 0.0),
            (["Artist1"], [], 0.0),
        ]

        for input_artists, candidate_artists, expected_min_score in test_cases:
            score = self.matcher.calculate_artists_similarity(input_artists, candidate_artists)
            self.assertGreaterEqual(
                score, expected_min_score,
                f"艺术家 {input_artists} 和 {candidate_artists} 的相似度 {score} 低于预期的 {expected_min_score}"
            )

    def test_calculate_weighted_score(self):
        """测试加权分数计算功能"""
        test_cases = [
            # 标题和艺术家都是100分
            (100.0, 100.0, 100.0),
            # 标题是100分，艺术家是0分
            (100.0, 0.0, 60.0),  # 0.6 * 100 + 0.4 * 0
            # 标题是0分，艺术家是100分
            (0.0, 100.0, 40.0),  # 0.6 * 0 + 0.4 * 100
            # 标题和艺术家都是50分
            (50.0, 50.0, 50.0),  # 0.6 * 50 + 0.4 * 50
        ]

        for title_score, artist_score, expected_score in test_cases:
            score = self.matcher.calculate_weighted_score(title_score, artist_score)
            self.assertAlmostEqual(
                score, expected_score, places=1,
                msg=f"标题分数 {title_score} 和艺术家分数 {artist_score} 的加权分数 {score} 不等于预期的 {expected_score}"
            )

    def test_match(self):
        """测试匹配功能"""
        # 创建测试用候选歌曲
        candidates = [
            {
                'name': 'Perfect Match',
                'artists': [{'name': 'Artist1'}, {'name': 'Artist2'}],
                'id': 'track1'
            },
            {
                'name': 'Decent Match',
                'artists': [{'name': 'Artist1'}, {'name': 'Artist3'}],
                'id': 'track2'
            },
            {
                'name': 'Bad Match',
                'artists': [{'name': 'Artist4'}],
                'id': 'track3'
            },
            {
                'name': 'Not Match At All',
                'artists': [{'name': 'Artist5'}],
                'id': 'track4'
            }
        ]

        # 配置匹配器，阈值设为较低以便测试
        matcher = StringMatcher(threshold=60.0, top_k=2)
        
        # 测试完美匹配
        results = matcher.match('Perfect Match', ['Artist1', 'Artist2'], candidates)
        self.assertEqual(len(results), 2)  # 应该返回前2个结果
        self.assertEqual(results[0]['id'], 'track1')  # 最匹配的应该是track1
        self.assertTrue('similarity_scores' in results[0])
        self.assertTrue(results[0]['similarity_scores']['weighted_score'] > 90.0)

        # 测试部分匹配
        results = matcher.match('Perfect', ['Artist1'], candidates)
        self.assertGreaterEqual(len(results), 1)  # 至少应该有一个结果
        
        # 测试无匹配
        matcher_high_threshold = StringMatcher(threshold=95.0)
        results = matcher_high_threshold.match('No Such Song', ['No Such Artist'], candidates)
        self.assertEqual(len(results), 0)  # 应该没有结果

    def test_get_best_match(self):
        """测试便利函数get_best_match"""
        # 创建测试用候选歌曲
        candidates = [
            {
                'name': 'Perfect Match',
                'artists': [{'name': 'Artist1'}, {'name': 'Artist2'}],
                'id': 'track1'
            },
            {
                'name': 'Decent Match',
                'artists': [{'name': 'Artist1'}, {'name': 'Artist3'}],
                'id': 'track2'
            }
        ]
        
        # 测试找到最佳匹配
        best_match = get_best_match(
            'Perfect Match', ['Artist1', 'Artist2'], 
            candidates, threshold=60.0
        )
        self.assertIsNotNone(best_match)
        self.assertEqual(best_match['id'], 'track1')
        
        # 测试无匹配
        no_match = get_best_match(
            'No Such Song', ['No Such Artist'], 
            candidates, threshold=90.0
        )
        self.assertIsNone(no_match)


if __name__ == '__main__':
    unittest.main() 