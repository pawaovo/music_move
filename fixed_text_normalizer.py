#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
文本标准化工具模块。

此模块提供了文本预处理和标准化的功能，用于提高文本匹配精度。
主要功能包括:
1. 中英文文本标准化（大小写、全角半角、简繁体）
2. 特殊标记处理（括号、feat.等）
3. 空白字符和标点符号的标准化
"""

from typing import List, Optional, Dict, Pattern, Union
import re
import unicodedata
import json
import os
from pathlib import Path
import opencc

from spotify_playlist_importer.utils.logger import get_logger
from spotify_playlist_importer.utils.config_manager import ConfigManager

# 获取日志器
logger = get_logger(__name__)

# 配置管理器
config_manager = ConfigManager()

# 添加缓存字典
_normalize_cache = {}

class TextNormalizer:
    """
    文本标准化类，提供多种文本预处理和标准化方法。
    
    主要功能包括：
    - 大小写转换
    - 全角半角转换
    - 简繁体转换
    - 特殊标记处理
    - 空白和标点符号标准化
    """
    
    # 预定义的常用替换模式
    DEFAULT_PATTERNS = {
        "live": r"\(live\)|\[live\]|（live）|【live】|live版|现场版",
        "remix": r"\(remix\)|\[remix\]|（remix）|【remix】|remix版|重混版",
        "acoustic": r"\(acoustic\)|\[acoustic\]|（acoustic）|【acoustic】|acoustic版|原声版",
        "cover": r"\(cover\)|\[cover\]|（cover）|【cover】|cover版|翻唱版",
        "instrumental": r"\(instrumental\)|\[instrumental\]|（instrumental）|【instrumental】|instrumental版|器乐版",
        "remastered": r"\(remastered\)|\[remastered\]|（remastered）|【remastered】|remastered版|重制版",
        "feat": r"feat\.|\(feat\..*?\)|\[feat\..*?\]|ft\.|\(ft\..*?\)|\[ft\..*?\]|featuring",
        "version": r"\(.*?version\)|\[.*?version\]|（.*?version）|【.*?version】|.*?版",
        "demo": r"\(demo\)|\[demo\]|（demo）|【demo】|demo版|样本版",
        "single": r"\(single\)|\[single\]|（single）|【single】|single版|单曲版",
        "edited": r"\(edited\)|\[edited\]|（edited）|【edited】|edited版|编辑版",
        "extended": r"\(extended\)|\[extended\]|（extended）|【extended】|extended版|加长版",
        "radio": r"\(radio\)|\[radio\]|（radio）|【radio】|radio版|广播版|电台版",
        "bonus": r"\(bonus\)|\[bonus\]|（bonus）|【bonus】|bonus版|附赠版",
        "deluxe": r"\(deluxe\)|\[deluxe\]|（deluxe）|【deluxe】|deluxe版|豪华版",
        "explicit": r"\(explicit\)|\[explicit\]|（explicit）|【explicit】|explicit版|显式版",
        "clean": r"\(clean\)|\[clean\]|（clean）|【clean】|clean版|干净版",
        "anniversary": r"\(.*?anniversary.*?\)|\[.*?anniversary.*?\]|（.*?anniversary.*?）|【.*?anniversary.*?】|.*?周年.*?版",
        "years": r"\(\d+年\)|\[\d+年\]|（\d+年）|【\d+年】|\(\d+\)|\[\d+\]|（\d+）|【\d+】",
        "brackets": r"\(.*?\)|\[.*?\]|（.*?）|【.*?】"
    }
    
    def __init__(self, patterns_file: Optional[str] = None):
        """
        初始化标准化器
        
        Args:
            patterns_file: 替换模式配置文件路径，如果为None则使用默认模式
        """
        # 简繁体转换器
        self.converter = opencc.OpenCC('t2s')
        
        # 加载替换模式
        self.patterns = self._load_patterns(patterns_file)
        
        # 编译正则表达式
        self.compiled_patterns = {
            name: re.compile(pattern, re.IGNORECASE) 
            for name, pattern in self.patterns.items()
        }
        
        logger.debug(f"文本标准化器初始化完成，已加载 {len(self.patterns)} 个替换模式")
    
    def _load_patterns(self, patterns_file: Optional[str]) -> Dict[str, str]:
        """
        加载替换模式配置
        
        Args:
            patterns_file: 配置文件路径
            
        Returns:
            Dict[str, str]: 替换模式字典
        """
        # 首先使用默认模式
        patterns = self.DEFAULT_PATTERNS.copy()
        
        # 如果指定了配置文件，尝试加载
        if patterns_file and os.path.exists(patterns_file):
            try:
                with open(patterns_file, 'r', encoding='utf-8') as f:
                    custom_patterns = json.load(f)
                    patterns.update(custom_patterns)
                    logger.info(f"从 {patterns_file} 加载了自定义替换模式")
            except Exception as e:
                logger.warning(f"无法从 {patterns_file} 加载替换模式: {e}")
        
        # 尝试从配置管理器获取
        config_patterns = config_manager.get("TEXT_PATTERNS", {})
        if config_patterns:
            patterns.update(config_patterns)
            logger.info("从配置管理器加载了自定义替换模式")
            
        return patterns
    
    def to_simplified_chinese(self, text: str) -> str:
        """
        将繁体中文转换为简体中文
        
        Args:
            text: 输入文本
            
        Returns:
            str: 转换后的文本
        """
        return self.converter.convert(text)
    
    def to_lowercase(self, text: str) -> str:
        """
        将文本转换为小写
        
        Args:
            text: 输入文本
            
        Returns:
            str: 转换后的文本
        """
        return text.lower()
    
    def normalize_fullwidth(self, text: str) -> str:
        """
        将全角字符转换为半角字符
        
        Args:
            text: 输入文本
            
        Returns:
            str: 转换后的文本
        """
        # 全角字符Unicode范围: 0xFF01-0xFF5E
        # 半角字符Unicode范围: 0x0021-0x007E
        result = ""
        for char in text:
            code = ord(char)
            if 0xFF01 <= code <= 0xFF5E:
                # 转换全角字符到半角
                result += chr(code - 0xFF01 + 0x21)
            else:
                result += char
        return result
    
    def normalize_whitespace(self, text: str) -> str:
        """
        标准化空白字符
        - 去除开头和结尾的空白
        - 将连续的空白字符替换为单个空格
        
        Args:
            text: 输入文本
            
        Returns:
            str: 标准化后的文本
        """
        # 首先去除开头和结尾的空白
        text = text.strip()
        # 将连续的空白字符替换为单个空格
        text = re.sub(r'\s+', ' ', text)
        return text
    
    def normalize_separators(self, text: str) -> str:
        """
        标准化分隔符
        - 将各种连字符、斜杠、与号等标准化
        
        Args:
            text: 输入文本
            
        Returns:
            str: 标准化后的文本
        """
        # 标准化连字符：将各种连字符替换为标准连字符 "-"
        text = re.sub(r'[‐‑‒–—―]', '-', text)
        
        # 标准化斜杠：将全角斜杠替换为半角斜杠 "/"
        text = text.replace('／', '/')
        
        # 标准化与号：将各种与号替换为标准与号 "&"
        text = re.sub(r'[＆]', '&', text)
        
        # 标准化省略号：将连续的点替换为三个点 "..."
        text = re.sub(r'\.{2,}', '...', text)
        text = re.sub(r'。{2,}', '...', text)
        
        return text
    
    def remove_patterns(self, text: str, patterns: Optional[List[str]] = None) -> str:
        """
        去除特定模式的文本
        
        Args:
            text: 输入文本
            patterns: 要去除的模式名称列表，如果为None则使用所有模式
            
        Returns:
            str: 处理后的文本
        """
        if not patterns:
            return text
            
        result = text
        # 遍历指定的模式
        for pattern_name in patterns:
            if pattern_name in self.compiled_patterns:
                # 使用空字符串替换匹配到的内容
                result = self.compiled_patterns[pattern_name].sub('', result)
            else:
                logger.warning(f"未知的模式名称: {pattern_name}")
                
        # 去除可能出现的连续空格
        result = re.sub(r'\s+', ' ', result)
        result = result.strip()
        
        return result
    
    def replace_patterns(self, text: str, replacements: Dict[str, str]) -> str:
        """
        替换特定模式的文本
        
        Args:
            text: 输入文本
            replacements: 模式名称到替换字符串的映射
            
        Returns:
            str: 处理后的文本
        """
        if not replacements:
            return text
            
        result = text
        # 遍历指定的替换
        for pattern_name, replacement in replacements.items():
            if pattern_name in self.compiled_patterns:
                # 用指定的字符串替换匹配到的内容
                result = self.compiled_patterns[pattern_name].sub(replacement, result)
            else:
                logger.warning(f"未知的模式名称: {pattern_name}")
                
        return result
    
    def normalize(self, text: str, remove_patterns: Optional[List[str]] = None, 
                 replacements: Optional[Dict[str, str]] = None) -> str:
        """
        对文本应用所有标准化处理
        
        Args:
            text: 原始文本
            remove_patterns: 要去除的模式名称列表
            replacements: 要替换的模式和对应的替换字符串
            
        Returns:
            str: 标准化后的文本
        """
        if not text:
            return ""
            
        # 记录原始文本，用于日志
        original_text = text
        
        # 1. 转换为小写
        text = self.to_lowercase(text)
        
        # 2. 全角转半角
        text = self.normalize_fullwidth(text)
        
        # 3. 繁体转简体
        text = self.to_simplified_chinese(text)
        
        # 4. 标准化分隔符
        text = self.normalize_separators(text)
        
        # 5. 去除指定模式
        if remove_patterns:
            text = self.remove_patterns(text, remove_patterns)
        
        # 6. 替换指定模式
        if replacements:
            text = self.replace_patterns(text, replacements)
        
        # 7. 标准化空白字符
        text = self.normalize_whitespace(text)
        
        logger.debug(f"文本标准化: '{original_text}' -> '{text}'")
        return text

# 模块级别的便捷函数
def normalize_text(text: str, remove_patterns: Optional[List[str]] = None, 
                  replacements: Optional[Dict[str, str]] = None,
                  patterns_file: Optional[str] = None) -> str:
    """
    便捷函数：标准化文本
    
    Args:
        text: 原始文本
        remove_patterns: 要去除的模式名称列表
        replacements: 要替换的模式和对应的替换字符串
        patterns_file: 替换模式配置文件路径
        
    Returns:
        str: 标准化后的文本
    """
    if text is None:
        return ""
    
    # 使用缓存机制
    cache_key = (text, 
                tuple(sorted(remove_patterns)) if remove_patterns else None,
                tuple(sorted(replacements.items())) if replacements else None,
                patterns_file)
    if cache_key in _normalize_cache:
        return _normalize_cache[cache_key]
    
    # 创建归一化器实例
    normalizer = TextNormalizer(patterns_file)
    
    # 执行归一化
    normalized = normalizer.normalize(text, remove_patterns, replacements)
    
    # 存入缓存
    _normalize_cache[cache_key] = normalized
    
    return normalized

# 测试代码
if __name__ == "__main__":
    from spotify_playlist_importer.utils.logger import configure_root_logger, set_log_level
    
    # 配置日志
    configure_root_logger()
    set_log_level("DEBUG")
    
    # 创建标准化器
    normalizer = TextNormalizer()
    
    # 测试文本
    test_texts = [
        "Hello World",
        "  Extra Spaces  ",
        "UPPER CASE",
        "Mixed Case Text",
        "全角字符：ＡＢＣ１２３",
        "繁體中文測試",
        "My Favorite Song (Live Version)",
        "Artist feat. Guest",
        "Title [Remix] / Original",
        "Track   with   multiple    spaces",
        "Title（2021）- Special Edition",
    ]
    
    # 测试标准化
    print("文本标准化测试:")
    for text in test_texts:
        normalized = normalizer.normalize(text)
        print(f"原文本: '{text}'")
        print(f"标准化: '{normalized}'")
        print("-" * 40)
    
    # 测试去除模式
    print("\n去除特定模式测试:")
    test_text = "My Favorite Song (Live Version) [Remix] feat. Guest Artist"
    patterns_to_remove = ["live", "remix", "feat"]
    normalized = normalizer.normalize(test_text, remove_patterns=patterns_to_remove)
    print(f"原文本: '{test_text}'")
    print(f"标准化: '{normalized}'")
    print("-" * 40)
