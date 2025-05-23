"""测试括号内容匹配模块"""

import unittest
from typing import Dict, List, Any

from spotify_playlist_importer.utils.bracket_matcher import (
    BracketMatcher, 
    adjust_scores_with_brackets, 
    COMMON_BRACKETS_KEYWORDS
)
from spotify_playlist_importer.utils.text_normalizer import TextNormalizer


class TestBracketMatcher(unittest.TestCase):
    """测试BracketMatcher类"""

    def setUp(self):
        """测试前的设置"""
        self.matcher = BracketMatcher()
        self.normalizer = TextNormalizer()

    def test_extract_brackets(self):
        """测试括号内容提取功能"""
        test_cases = [
            ("Song Title (Live Version)", ("Song Title", ["Live Version"])),
            ("Song Title [Remix]", ("Song Title", ["Remix"])),
            ("Song Title (Live) [Remix]", ("Song Title", ["Live", "Remix"])),
            ("Song Title", ("Song Title", [])),
            ("", ("", [])),
        ]
        
        for title, expected in test_cases:
            clean_title, brackets = self.matcher.extract_brackets(title)
            # 使用strip()来忽略可能的尾随空格差异
            self.assertEqual((clean_title.strip(), brackets), expected)

    def test_normalize_bracket_content(self):
        """测试括号内容归一化功能"""
        test_cases = [
            ("Live Version", "live version"),
            ("REMIX", "remix"),
            ("Ｆｅａｔ．　Ａｒｔｉｓｔ", "feat. artist"),
            ("  Multiple   Spaces  ", "multiple spaces"),
            ("", ""),
        ]
        
        for content, expected in test_cases:
            normalized = self.matcher.normalize_bracket_content(content)
            self.assertEqual(normalized, expected)

    def test_extract_keywords(self):
        """测试关键词提取功能"""
        test_cases = [
            ("live version", {"live", "version"}),
            ("acoustic remix", {"acoustic", "remix"}),
            ("featuring artist", {"featuring", "feat"}),
            ("2022 remastered", {"remastered", "remaster"}),
            ("extended radio edit", {"extended", "radio", "edit"}),
            ("no keywords here", set()),
            ("", set()),
        ]
        
        for content, expected in test_cases:
            keywords = self.matcher.extract_keywords(content)
            self.assertEqual(keywords, expected)

    def test_calculate_brackets_similarity(self):
        """测试括号内容相似度计算"""
        test_cases = [
            # 完全匹配
            (["Live Version"], ["Live Version"], 90.0),
            # 关键词匹配
            (["Live Version"], ["Live Recording"], 55.0),
            # 部分匹配
            (["Remix"], ["Club Remix"], 50.0),
            # 无关键词匹配
            (["2022"], ["Acoustic"], 0.0),
            # 空列表
            ([], ["Live"], 0.0),
            (["Live"], [], 0.0),
            ([], [], 0.0),
        ]
        
        for input_brackets, candidate_brackets, expected_min_score in test_cases:
            score = self.matcher.calculate_brackets_similarity(input_brackets, candidate_brackets)
            self.assertGreaterEqual(
                score, expected_min_score,
                f"括号 {input_brackets} 和 {candidate_brackets} 的相似度 {score} 低于预期的 {expected_min_score}"
            )

    def test_calculate_keyword_bonus(self):
        """测试关键词加分计算"""
        # 修改matcher实例以使用可预测的keyword_bonus值
        self.matcher.keyword_bonus = 10.0
        
        test_cases = [
            # 单个关键词，权重高
            (["Remix"], ["Remix"], COMMON_BRACKETS_KEYWORDS["remix"]),
            # 多个关键词
            (["Live Version"], ["Live Recording"], COMMON_BRACKETS_KEYWORDS["live"]),
            # 多个关键词，匹配多个
            (["Live Remix"], ["Remix Live"], COMMON_BRACKETS_KEYWORDS["live"] + COMMON_BRACKETS_KEYWORDS["remix"]),
            # 无匹配关键词
            (["2022"], ["Studio"], 0.0),
            # 空列表
            ([], ["Live"], 0.0),
            (["Live"], [], 0.0),
            ([], [], 0.0),
        ]
        
        for input_brackets, candidate_brackets, expected_bonus in test_cases:
            bonus = self.matcher.calculate_keyword_bonus(input_brackets, candidate_brackets)
            self.assertAlmostEqual(
                bonus, min(expected_bonus, self.matcher.keyword_bonus),
                places=1,
                msg=f"括号 {input_brackets} 和 {candidate_brackets} 的关键词加分 {bonus} 不等于预期的 {expected_bonus}"
            )

    def test_adjust_score(self):
        """测试分数调整功能"""
        test_cases = [
            # 完全匹配的括号内容，应提高分数
            ("Song Title (Live)", "Song Title (Live)", 80.0, 85.0),
            # 完全不匹配的括号内容，应降低分数
            ("Song Title (Remix)", "Song Title (Acoustic)", 80.0, 75.0),
            # 没有括号内容，分数不变
            ("Song Title", "Song Title", 80.0, 80.0),
            # 一方有括号内容，一方没有，应降低分数
            ("Song Title (Remix)", "Song Title", 80.0, 75.0),
        ]
        
        for input_title, candidate_title, base_score, expected_min_score in test_cases:
            adjusted_score = self.matcher.adjust_score(base_score, input_title, candidate_title)
            if expected_min_score > base_score:
                # 如果期望分数高于基础分数，断言调整后分数也高于基础分数
                self.assertGreater(
                    adjusted_score, base_score,
                    f"标题 '{input_title}' 和 '{candidate_title}' 的调整后分数 {adjusted_score} 没有高于基础分数 {base_score}"
                )
            elif expected_min_score < base_score:
                # 如果期望分数低于基础分数，断言调整后分数也低于基础分数
                self.assertLess(
                    adjusted_score, base_score,
                    f"标题 '{input_title}' 和 '{candidate_title}' 的调整后分数 {adjusted_score} 没有低于基础分数 {base_score}"
                )
            else:
                # 期望分数等于基础分数，断言调整后分数也等于基础分数
                self.assertAlmostEqual(
                    adjusted_score, base_score,
                    places=1,
                    msg=f"标题 '{input_title}' 和 '{candidate_title}' 的调整后分数 {adjusted_score} 不等于基础分数 {base_score}"
                )

    def test_adjust_scores_with_brackets(self):
        """测试批量调整分数功能"""
        # 创建测试用的候选歌曲列表
        candidates = [
            {
                'name': 'Song Title (Live)',
                'similarity_scores': {'weighted_score': 80.0},
                'id': 'track1'
            },
            {
                'name': 'Song Title (Remix)',
                'similarity_scores': {'weighted_score': 75.0},
                'id': 'track2'
            },
            {
                'name': 'Different Song',
                'similarity_scores': {'weighted_score': 60.0},
                'id': 'track3'
            }
        ]
        
        input_title = "Song Title (Live)"
        adjusted_candidates = adjust_scores_with_brackets(candidates, input_title)
        
        # 检查是否所有候选歌曲都有final_score字段
        for candidate in adjusted_candidates:
            self.assertIn('final_score', candidate['similarity_scores'])
            self.assertIn('bracket_score', candidate['similarity_scores'])
        
        # 检查排序是否改变（Live版本应该排在Remix版本前面）
        self.assertEqual(adjusted_candidates[0]['id'], 'track1')
        
        # 检查带有相同括号的歌曲是否得分提高
        self.assertGreater(
            adjusted_candidates[0]['similarity_scores']['final_score'],
            candidates[0]['similarity_scores']['weighted_score']
        )


if __name__ == '__main__':
    unittest.main() 