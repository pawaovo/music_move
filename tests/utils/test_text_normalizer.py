"""文本归一化模块的测试"""

import unittest
import os
import tempfile
import json
from pathlib import Path

from spotify_playlist_importer.utils.text_normalizer import (
    TextNormalizer,
    normalize_text,
    load_patterns,
    DEFAULT_PATTERNS,
    split_text
)


class TestTextNormalizer(unittest.TestCase):
    """文本归一化模块单元测试"""
    
    def setUp(self):
        self.normalizer = TextNormalizer()
    
    def test_normalize_case(self):
        """测试英文大小写统一功能"""
        test_cases = [
            ("Hello World", "hello world"),
            ("SPOTIFY", "spotify"),
            ("jAzZ", "jazz"),
            ("中文ABC混合", "中文abc混合"),
            ("", ""),
            (None, None),
        ]
        
        for input_text, expected_output in test_cases:
            self.assertEqual(self.normalizer.normalize_case(input_text), expected_output)
    
    def test_normalize_fullwidth(self):
        """测试全角/半角字符统一功能"""
        test_cases = [
            ("Ｈｅｌｌｏ　Ｗｏｒｌｄ", "Hello World"),
            ("１２３４５", "12345"),
            ("ａｂｃＡＢＣ", "abcABC"),
            ("中文混合Ａｂｃ１２３", "中文混合Abc123"),
            ("", ""),
            (None, None),
        ]
        
        for input_text, expected_output in test_cases:
            self.assertEqual(self.normalizer.normalize_fullwidth(input_text), expected_output)
    
    def test_normalize_separators(self):
        """测试空白字符与分隔符的标准化"""
        test_cases = [
            ("hello-world", "hello world"),
            ("artist1/artist2", "artist1 artist2"),
            ("artist1 & artist2", "artist1 artist2"),
            ("  multiple   spaces  ", "multiple spaces"),
            ("tab\tand\nnewline", "tab and newline"),
            ("", ""),
            (None, None),
        ]
        
        for input_text, expected_output in test_cases:
            self.assertEqual(self.normalizer.normalize_separators(input_text), expected_output)
    
    def test_remove_patterns_from_text(self):
        """测试模式去除功能"""
        test_cases = [
            ("Song Title (live)", "Song Title "),
            ("Song Title [remastered]", "Song Title "),
            ("Song Title (Bonus Track)", "Song Title "),
            ("Song Title (remastered) (live version)", "Song Title  "),
            ("Song Title", "Song Title"),
            ("", ""),
            (None, None),
        ]
        
        for input_text, expected_output in test_cases:
            self.assertEqual(self.normalizer.remove_patterns_from_text(input_text), expected_output)
    
    def test_replace_patterns_in_text(self):
        """测试模式替换功能"""
        test_cases = [
            ("Artist1 feat. Artist2", "Artist1 feat Artist2"),
            ("Artist1 ft. Artist2", "Artist1 feat Artist2"),
            ("Artist1 featuring Artist2", "Artist1 feat Artist2"),
            ("Artist1 ft Artist2", "Artist1 feat Artist2"),
            ("Artist1 feat Artist2", "Artist1 feat Artist2"),
            ("", ""),
            (None, None),
        ]
        
        for input_text, expected_output in test_cases:
            self.assertEqual(self.normalizer.replace_patterns_in_text(input_text), expected_output)
    
    def test_extract_bracketed_content(self):
        """测试括号内容提取功能"""
        test_cases = [
            ("Song Title (live version)", ("Song Title ", ["live version"])),
            ("Song Title [remastered] (2022)", ("Song Title  ", ["remastered", "2022"])),
            ("Song Title", ("Song Title", [])),
            ("Song Title (live) (remix)", ("Song Title  ", ["live", "remix"])),
            ("Song Title {deluxe}", ("Song Title ", ["deluxe"])),
            ("", ("", [])),
            (None, (None, [])),
        ]
        
        for input_text, expected_output in test_cases:
            self.assertEqual(self.normalizer.extract_bracketed_content(input_text), expected_output)
    
    def test_normalize(self):
        """测试综合归一化功能"""
        test_cases = [
            # 大小写统一 + 全角半角 + 模式去除 + 模式替换 + 分隔符标准化
            (
                "Ｓｏｎｇ　Ｔｉｔｌｅ (Live Version) feat. Artist1/Artist2",
                "song title feat artist1 artist2"
            ),
            # 大小写统一 + 分隔符标准化
            (
                "ARTIST1 & ARTIST2 - SONG",
                "artist1 artist2 song"
            ),
            # 只保留括号内容
            (
                "Song Title (Live Version)",
                "song title live version",
                True  # keep_brackets=True
            ),
            # 移除括号内容
            (
                "Song Title (Live Version)",
                "song title",
                False  # keep_brackets=False
            ),
            # 空输入
            ("", "", True),
            (None, None, True),
        ]
        
        for test_case in test_cases:
            if len(test_case) == 2:
                input_text, expected_output = test_case
                keep_brackets = True
            else:
                input_text, expected_output, keep_brackets = test_case
            
            # 测试实例方法
            self.assertEqual(
                self.normalizer.normalize(input_text, keep_brackets=keep_brackets),
                expected_output
            )
            
            # 测试工具函数
            self.assertEqual(
                normalize_text(input_text, keep_brackets=keep_brackets),
                expected_output
            )
    
    def test_custom_patterns_from_file(self):
        """测试从配置文件加载自定义模式"""
        # 创建临时配置文件
        custom_patterns = {
            "remove": [r"\(demo\)", r"\(test\)"],
            "replace": {r"cover by": "remix by"}
        }
        
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as temp_file:
            json.dump(custom_patterns, temp_file)
            temp_file_name = temp_file.name
        
        try:
            # 测试加载自定义模式
            loaded_patterns = load_patterns(temp_file_name)
            self.assertEqual(loaded_patterns, custom_patterns)
            
            # 测试使用自定义模式的归一化器
            custom_normalizer = TextNormalizer(config_file=temp_file_name)
            
            # 测试模式去除
            self.assertEqual(
                custom_normalizer.remove_patterns_from_text("Song (demo)"),
                "Song "
            )
            
            # 测试模式替换
            self.assertEqual(
                custom_normalizer.replace_patterns_in_text("Song cover by Artist"),
                "Song remix by Artist"
            )
        finally:
            # 清理临时文件
            os.unlink(temp_file_name)
    
    def test_load_default_patterns_on_invalid_file(self):
        """测试在无效配置文件情况下加载默认模式"""
        # 测试不存在的文件
        loaded_patterns = load_patterns("non_existent_file.json")
        self.assertEqual(loaded_patterns, DEFAULT_PATTERNS)
        
        # 测试无效的JSON文件
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as temp_file:
            temp_file.write("This is not valid JSON")
            temp_file_name = temp_file.name
        
        try:
            loaded_patterns = load_patterns(temp_file_name)
            self.assertEqual(loaded_patterns, DEFAULT_PATTERNS)
        finally:
            os.unlink(temp_file_name)

    def test_normalize_with_preserved_brackets(self):
        """测试保留括号内容的归一化功能"""
        test_cases = [
            (
                "Song Title (Live Version)",
                "song title (live version)"
            ),
            (
                "Song Title [Remastered 2022]",
                "song title (remastered 2022)"
            ),
            (
                "Song Title (Remix) feat. Artist",
                "song title (remix) feat artist"
            ),
            (
                "Song Title (feat. Artist1) (Acoustic Version)",
                "song title (feat artist1) (acoustic version)"
            ),
            (
                "ARTIST NAME - SONG {Deluxe Edition}",
                "artist name song (deluxe edition)"
            ),
        ]
        
        for input_text, expected_output in test_cases:
            result = normalize_text(input_text, keep_brackets=True)
            self.assertEqual(result, expected_output)
    
    def test_split_text(self):
        """测试将文本分割成主要部分和括号部分的功能"""
        test_cases = [
            (
                "song title (live version)",
                ("song title", ["(live version)"])
            ),
            (
                "song title (remix) (feat artist)",
                ("song title", ["(remix)", "(feat artist)"])
            ),
            (
                "song title",
                ("song title", [])
            ),
            (
                "song title (feat artist1) [remastered]",
                ("song title", ["(feat artist1)", "[remastered]"])
            ),
            (
                "song title (feat artist1 & artist2)",
                ("song title", ["(feat artist1 & artist2)"])
            ),
            (
                "",
                ("", [])
            ),
            (
                None,
                (None, [])
            ),
        ]
        
        for input_text, expected_output in test_cases:
            self.assertEqual(split_text(input_text), expected_output)


if __name__ == '__main__':
    unittest.main() 