"""
拼音处理工具模块。

此模块提供中文文本转拼音功能，以增强字符串匹配能力，特别是在比较中文艺术家名与可能的拼音或拉丁字母表示时。
"""

from typing import List, Set
import re
import logging

# 有条件导入pypinyin，如果导入失败则提供备用功能
try:
    from pypinyin import pinyin, Style
    PYPINYIN_AVAILABLE = True
except ImportError:
    PYPINYIN_AVAILABLE = False
    logging.warning("未安装pypinyin库，拼音转换功能将不可用")

from spotify_playlist_importer.utils.logger import get_logger

# 获取日志器
logger = get_logger(__name__)


def is_chinese_char(char: str) -> bool:
    """
    判断一个字符是否是中文字符
    
    Args:
        char: 要检查的单个字符
        
    Returns:
        bool: 如果是中文字符则为True，否则为False
    """
    if len(char) != 1:
        return False
    
    # 中文字符的Unicode范围
    return '\u4e00' <= char <= '\u9fff'


def contains_chinese(text: str) -> bool:
    """
    检查文本中是否包含中文字符
    
    Args:
        text: 要检查的文本
        
    Returns:
        bool: 如果包含中文字符则为True，否则为False
    """
    if not text:
        return False
    
    return any(is_chinese_char(char) for char in text)


def text_to_pinyin(text: str, style: str = 'default', separator: str = '') -> str:
    """
    将中文文本转换为拼音
    
    Args:
        text: 要转换的中文文本
        style: 拼音风格，可选值: 'default'(默认带声调), 'tone'(数字声调), 'normal'(不带声调)
        separator: 拼音之间的分隔符
        
    Returns:
        str: 转换后的拼音字符串。如果pypinyin不可用，则返回原文本
    """
    if not PYPINYIN_AVAILABLE:
        logger.warning("pypinyin库未安装，返回原始文本")
        return text
    
    if not text or not contains_chinese(text):
        return text
    
    try:
        # 根据style参数选择pypinyin风格
        if style == 'tone':
            py_style = Style.TONE3  # 数字声调，如 'ni3'
        elif style == 'normal':
            py_style = Style.NORMAL  # 不带声调，如 'ni'
        else:
            py_style = Style.TONE  # 默认带声调，如 'nǐ'
        
        # 转换为拼音列表
        py_list = pinyin(text, style=py_style)
        
        # 将拼音列表平铺并用分隔符连接
        result = separator.join([item[0] for item in py_list])
        
        logger.debug(f"文本 '{text}' 转换为拼音: '{result}'")
        return result
    except Exception as e:
        logger.error(f"拼音转换失败: {e}")
        return text


def get_pinyin_variants(text: str) -> Set[str]:
    """
    获取文本的多种拼音表示变体
    
    为提高匹配成功率，生成不同风格(带声调、数字声调、不带声调)的拼音表示
    
    Args:
        text: 要转换的文本
        
    Returns:
        Set[str]: 不同拼音表示的集合
    """
    if not PYPINYIN_AVAILABLE or not contains_chinese(text):
        return {text.lower()}
    
    variants = {text.lower()}  # 始终包含原始文本的小写形式
    
    # 添加不同风格的拼音变体
    variants.add(text_to_pinyin(text, style='normal', separator=''))  # 不带声调，无分隔符
    variants.add(text_to_pinyin(text, style='normal', separator=' '))  # 不带声调，空格分隔
    variants.add(text_to_pinyin(text, style='tone', separator=''))    # 数字声调，无分隔符
    
    # 移除空字符串
    variants.discard('')
    
    logger.debug(f"文本 '{text}' 的拼音变体: {variants}")
    return variants


def find_best_pinyin_match(chinese_text: str, candidates: List[str]) -> tuple:
    """
    在候选列表中找到与中文文本拼音最匹配的项
    
    首先检查直接的文本匹配，如果匹配度较低，则尝试拼音匹配
    
    Args:
        chinese_text: 中文文本
        candidates: 候选文本列表
        
    Returns:
        tuple: (最佳匹配的候选文本, 匹配分数, 是否使用了拼音匹配)
    """
    if not PYPINYIN_AVAILABLE or not contains_chinese(chinese_text) or not candidates:
        return None, 0, False
    
    from fuzzywuzzy import fuzz
    
    # 首先尝试直接文本匹配
    direct_match_scores = [(candidate, fuzz.ratio(chinese_text.lower(), candidate.lower())) 
                          for candidate in candidates]
    
    # 找到最高直接匹配分数
    best_direct_match, best_direct_score = max(direct_match_scores, key=lambda x: x[1])
    
    # 如果直接匹配分数足够高，直接返回
    if best_direct_score >= 75:
        logger.debug(f"文本 '{chinese_text}' 与 '{best_direct_match}' 直接匹配分数: {best_direct_score}")
        return best_direct_match, best_direct_score, False
    
    # 获取中文文本的拼音变体
    pinyin_variants = get_pinyin_variants(chinese_text)
    
    # 计算每个拼音变体与每个候选的匹配分数
    best_score = 0
    best_match = None
    used_pinyin = False
    
    for variant in pinyin_variants:
        for candidate in candidates:
            # 候选者转为小写
            candidate_lower = candidate.lower()
            
            # 计算相似度分数
            score = fuzz.ratio(variant, candidate_lower)
            
            # 更新最佳分数
            if score > best_score:
                best_score = score
                best_match = candidate
                used_pinyin = variant != chinese_text.lower()  # 检查是否使用了拼音变体
    
    logger.debug(f"文本 '{chinese_text}' 的最佳匹配: '{best_match}', " +
               f"分数: {best_score}, 使用拼音: {used_pinyin}")
    
    return best_match, best_score, used_pinyin 