"""
括号内容匹配模块

提供歌曲标题中括号内容的处理和匹配功能，用于增强Spotify搜索结果匹配准确性。
"""

import re
import logging
from typing import Dict, List, Optional, Set, Tuple, Union, Any

import fuzzywuzzy.fuzz as fuzz

from spotify_playlist_importer.utils.text_normalizer import normalize_text, TextNormalizer


class BracketMatcher:
    """
    括号内容匹配类，用于处理和比较歌曲标题中的括号内容
    
    该类专门处理歌曲标题中的括号内容，如(Live)、[Remix]、（现场版）等，
    这些内容通常表示歌曲的特殊版本信息，对于准确匹配特别重要。
    
    核心功能：
    1. 从标题中提取各种类型的括号内容
    2. 识别常见特殊关键词（如live、remix、acoustic等）
    3. 计算括号内容的相似度
    4. 根据括号内容匹配情况调整基础匹配分数
    
    此模块是两阶段匹配算法中的第二阶段的核心组件。
    """

    # 预编译正则表达式，匹配小括号、中括号、全角括号等
    BRACKET_PATTERN = re.compile(r'\(([^)]*)\)|\[([^]]*)\]|（([^）]*)）|【([^】]*)】')

    def __init__(self, bracket_weight: float = 0.3, keyword_bonus: float = 5.0,
                 threshold: float = 70.0):
        """
        初始化BracketMatcher
        
        参数配置决定了括号内容对最终匹配分数的影响程度。
        通常，对于包含大量特殊版本的音乐类型（如电子音乐、现场专辑），
        可以考虑提高bracket_weight和keyword_bonus。

        Args:
            bracket_weight: 括号内容在最终得分中的权重，默认0.3
            keyword_bonus: 关键词匹配时的额外加分，默认5.0
            threshold: 最小匹配阈值，默认70（满分100）
        """
        self.bracket_weight = bracket_weight
        self.keyword_bonus = keyword_bonus
        self.threshold = threshold
        
        # 括号内常见关键词及其权重
        # 权重值反映了关键词的重要性和特异性
        # 例如，"remix"和"instrumental"权重较高，因为它们明确定义了歌曲版本
        # 而"version"和"edit"权重较低，因为它们较为通用
        self.keywords = {
            "live": 6.0,           # 现场版本
            "现场": 6.0,           # 现场版本(中文)
            "現場": 6.0,           # 现场版本(繁体)
            "现场版": 6.0,         # 现场版本(中文)
            "現場版": 6.0,         # 现场版本(繁体)
            "acoustic": 6.0,       # 原声版本
            "原声": 6.0,           # 原声版本(中文)
            "原聲": 6.0,           # 原声版本(繁体)
            "remix": 8.0,          # 混音版本（高权重，因为混音版本差异通常很大）
            "重混": 8.0,           # 混音版本(中文)
            "重混版": 8.0,         # 混音版本(中文)
            "piano": 5.0,          # 钢琴版本
            "钢琴": 5.0,           # 钢琴版本(中文)
            "鋼琴": 5.0,           # 钢琴版本(繁体)
            "instrumental": 7.0,   # 器乐版本（无人声）
            "器乐": 7.0,           # 器乐版本(中文)
            "器樂": 7.0,           # 器乐版本(繁体)
            "karaoke": 7.0,        # 卡拉OK版本
            "卡拉OK": 7.0,         # 卡拉OK版本(中文)
            "cover": 4.0,          # 翻唱版本
            "翻唱": 4.0,           # 翻唱版本(中文)
            "翻唱版": 4.0,         # 翻唱版本(中文)
            "version": 2.0,        # 一般版本标记（低权重，因为不够具体）
            "版": 2.0,             # 一般版本标记(中文)
            "版本": 2.0,           # 一般版本标记(中文)
            "remaster": 3.0,       # 重制版本
            "remastered": 3.0,     # 重制版本（另一种写法）
            "重制": 3.0,           # 重制版本(中文)
            "重制版": 3.0,         # 重制版本(中文)
            "deluxe": 2.0,         # 豪华版本
            "豪华": 2.0,           # 豪华版本(中文)
            "豪华版": 2.0,         # 豪华版本(中文)
            "single": 3.0,         # 单曲版本
            "单曲": 3.0,           # 单曲版本(中文)
            "單曲": 3.0,           # 单曲版本(繁体)
            "album": 2.0,          # 专辑版本
            "专辑": 2.0,           # 专辑版本(中文)
            "專輯": 2.0,           # 专辑版本(繁体)
            "ep": 2.0,             # EP版本
            "original": 2.0,       # 原版
            "原版": 2.0,           # 原版(中文)
            "feat": 5.0,           # 合作艺术家标记
            "featuring": 5.0,      # 合作艺术家标记（完整形式）
            "ft": 5.0,             # 合作艺术家标记（缩写）
            "合作": 5.0,           # 合作艺术家标记(中文)
            "合作版": 5.0,         # 合作艺术家标记(中文)
            "extended": 2.0,       # 扩展版本
            "加长": 2.0,           # 扩展版本(中文)
            "加长版": 2.0,         # 扩展版本(中文)
            "edit": 1.0,           # 编辑版本（低权重，因为变化通常较小）
            "编辑": 1.0,           # 编辑版本(中文)
            "編輯": 1.0,           # 编辑版本(繁体)
            "radio": 1.5,          # 广播版本
            "广播": 1.5,           # 广播版本(中文)
            "廣播": 1.5,           # 广播版本(繁体)
            "电台": 1.5,           # 电台版本(中文)
            "電臺": 1.5,           # 电台版本(繁体)
            "explicit": 1.0,       # 显式内容标记
            "clean": 1.0,          # 清洁版本（无不良用语）
            "bonus": 1.0,          # 额外曲目标记
            "track": 1.0,          # 音轨标记
        }
        
        # 特殊关键词映射，用于处理相似概念的不同表达
        self.keyword_mappings = {
            "live": ["现场", "演唱会", "音乐会", "concert", "live", "live version", "live recording", "在线", "現場"],
            "remix": ["remix", "mix", "重混", "重制", "混音", "dj", "club", "extended"],
            "acoustic": ["acoustic", "原声", "原聲", "钢琴", "吉他", "unplugged", "piano", "guitar"],
            "remaster": ["remaster", "remastered", "重制", "修复", "高清", "hd", "高音质"],
            "version": ["version", "版本", "版", "ver", "mix"],
            "feat": ["feat", "ft", "featuring", "with", "和", "合作", "協作"],
            "alias": ["又名", "别名", "aka", "also known as", "原名", "原名为", "原名是"],
        }
        
        # 初始化文本归一化器
        self.text_normalizer = TextNormalizer()
        
        # 定义括号类型权重 - 用于确定不同类型的括号在相似度计算中的重要性
        self.bracket_type_weights = {
            "feat": 0.9,  # 特殊艺术家相关信息，非常重要
            "remix": 0.85,  # 混音版本，明显不同的版本，很重要
            "live": 0.80,  # 现场版本，与录音室版本有区别，很重要
            "acoustic": 0.75,  # 原声版本，与标准版本有区别，较重要
            "version": 0.70,  # 特殊版本，有一定区别，较重要
            "alias": 0.60,  # 别名信息，中等重要性
            "remaster": 0.40,  # 重制版，与原版相似，影响较小
            "release": 0.35,  # 发行信息，影响较小
            "year": 0.30,  # 年份信息，影响较小
            "other": 0.40,  # 其他信息，默认中低重要性
        }
        
        # 记录初始化参数
        logging.info(f"[括号匹配] 初始化BracketMatcher - 权重={bracket_weight:.2f}, 关键词加分={keyword_bonus:.2f}, 阈值={threshold:.2f}")

    def extract_brackets(self, text: str) -> List[str]:
        """
        从文本中提取括号内容
        
        使用预编译的正则表达式提取各种类型的括号内容，
        包括小括号()、中括号[]、全角括号（）和【】。
        
        性能优化：使用预编译的正则表达式，而不是每次调用时重新编译。

        Args:
            text: 输入文本

        Returns:
            List[str]: 括号内容列表
        """
        if not text:
            return []
        
        # 使用预编译正则表达式匹配所有类型的括号
        matches = self.BRACKET_PATTERN.findall(text)
        
        # 处理结果
        result = []
        for match_groups in matches:
            # findall返回的是元组，每个元组对应多个模式分组
            # 每个元组中只有一个分组会有内容，其他为空字符串
            content = next((group for group in match_groups if group), "")
            if content.strip():  # 忽略空内容
                result.append(content)
                
        logging.info(f"[括号提取] 从文本 '{text}' 提取到括号内容: {result if result else '无'}")
        return result

    def normalize_bracket_content(self, bracket_content: str) -> str:
        """
        归一化括号内容，应用特定的归一化规则

        Args:
            bracket_content: 括号内容

        Returns:
            str: 归一化后的括号内容
        """
        # 使用增强的文本归一化，确保完整的标准化流程
        # 包括全角转半角、简繁体转换、大小写标准化等
        
        # 记录原始内容
        original_content = bracket_content
        logging.debug(f"归一化括号内容: 原始='{original_content}'")
        
        # 应用全面的归一化处理
        try:
            # 使用TextNormalizer中的normalize_text方法进行全面标准化
            content = normalize_text(bracket_content)
        
            # 处理多余空格，确保只有一个空格
            content = re.sub(r'\s+', ' ', content).strip()
            
            logging.debug(f"归一化括号内容: 结果='{content}'")
            
            return content
        except Exception as e:
            logging.error(f"括号内容归一化失败: {e}")
            # 出现异常时返回原始内容，避免影响正常流程
            return bracket_content

    def extract_alias(self, bracket_content: str) -> str:
        """
        从括号内容中提取别名
        
        处理格式如 "(又名：XXX)", "(aka XXX)", "(别称 XXX)" 等
        
        Args:
            bracket_content: 括号内容
            
        Returns:
            str: 提取的别名，如果没有识别到别名模式则返回None
        """
        # 首先标准化括号内容
        content = self.normalize_bracket_content(bracket_content)
        
        # 匹配中文常见别名指示词
        chinese_indicators = ["又名", "别名", "别称", "原名"]
        for indicator in chinese_indicators:
            if indicator in content:
                # 尝试各种分隔方式（冒号、空格或直接连接）
                parts = None
                # 尝试"又名："形式
                if f"{indicator}:" in content:
                    parts = content.split(f"{indicator}:", 1)
                # 尝试"又名 "形式
                elif f"{indicator} " in content:
                    parts = content.split(f"{indicator} ", 1)
                # 尝试直接相连的形式"又名XXX"
                elif indicator in content:
                    parts = content.split(indicator, 1)
                    
                if parts and len(parts) > 1:
                    alias = parts[1].strip()
                    logging.debug(f"从'{content}'中提取到中文别名: '{alias}'")
                    return alias
        
        # 匹配英文常见别名指示词
        english_indicators = ["aka", "also known as", "alternate title", "original"]
        for indicator in english_indicators:
            if indicator in content:
                parts = content.split(indicator, 1)
                if len(parts) > 1:
                    alias = parts[1].strip()
                    logging.debug(f"从'{content}'中提取到英文别名: '{alias}'")
                    return alias
        
        # 未识别到别名模式
        return None

    def detect_keywords(self, bracket_contents: List[str]) -> Dict[str, float]:
        """
        在括号内容中检测关键词
        
        搜索预定义的关键词列表，识别括号内容中包含的特殊关键词，
        并根据关键词的重要性分配权重。
        
        这一步对于识别歌曲的特殊版本（如现场版、混音版等）至关重要。

        Args:
            bracket_contents: 括号内容列表

        Returns:
            Dict[str, float]: 检测到的关键词及其权重字典
        """
        detected_keywords = {}
        
        for content in bracket_contents:
            normalized = self.normalize_bracket_content(content).lower()
            
            for keyword, weight in self.keywords.items():
                if keyword.lower() in normalized:
                    detected_keywords[keyword] = weight
                    logging.info(f"[关键词检测] 在 '{content}' 中检测到关键词 '{keyword}'，权重 {weight:.2f}")
                    
        if not detected_keywords:
            logging.debug(f"[关键词检测] 在括号内容 {bracket_contents} 中未检测到关键词")
        else:
            logging.info(f"[关键词检测] 检测到的关键词: {list(detected_keywords.keys())}")
                    
        return detected_keywords

    def calculate_bracket_similarity(self, input_brackets: List[str], 
                                     candidate_brackets: List[str]) -> float:
        """
        计算两组括号内容的相似度
        
        使用字符串相似度算法计算输入和候选歌曲的括号内容相似度。
        采用"最佳匹配"策略，为每个输入括号找到最匹配的候选括号，
        然后计算平均相似度。

        Args:
            input_brackets: 输入歌曲的括号内容列表
            candidate_brackets: 候选歌曲的括号内容列表

        Returns:
            float: 相似度分数（0-100）
        """
        if not input_brackets and not candidate_brackets:
            # 如果两者都没有括号内容，返回满分以不影响基本得分
            logging.debug("输入和候选均无括号内容，返回满分以不影响基础得分")
            return 100.0
        
        if not input_brackets or not candidate_brackets:
            # 如果一方有括号内容，另一方没有，计算智能的调整分数
            # 分析括号内容的类型和重要性
            brackets_to_analyze = input_brackets if input_brackets else candidate_brackets
            bracket_types = [self.classify_bracket_type(b) for b in brackets_to_analyze]
            
            # 计算平均重要性权重
            importance_weights = [self.bracket_type_weights.get(t, 0.4) for t in bracket_types]
            avg_importance = sum(importance_weights) / len(importance_weights) if importance_weights else 0.4
            
            # 根据重要性调整基础分数
            # 重要性高的括号（如feat/remix）缺失会给予较低的分数
            # 重要性低的括号（如remaster）缺失影响较小
            base_score = 75  # 中等基础分
            adjustment = (1 - avg_importance) * 25  # 根据重要性调整，重要性越高，加分越少
            adjusted_score = base_score + adjustment
            
            # 详细日志记录不平衡情况
            missing_side = "输入" if not input_brackets else "候选"
            present_side = "候选" if not input_brackets else "输入"
            
            logging.debug(f"括号内容不平衡: {missing_side}无括号，{present_side}有括号")
            logging.debug(f"括号类型分析: {bracket_types}")
            for i, (br_type, weight) in enumerate(zip(bracket_types, importance_weights)):
                br_content = brackets_to_analyze[i]
                logging.debug(f"  括号内容[{i}]: '{br_content}' (类型={br_type}, 重要性={weight:.2f})")
            
            logging.debug(f"平均重要性: {avg_importance:.2f}, 基础分={base_score}, 调整={adjustment:+.2f}")
            logging.debug(f"最终括号相似度分数: {adjusted_score:.2f}")
            
            return adjusted_score
            
        # 归一化所有括号内容
        normalized_inputs = [self.normalize_bracket_content(b) for b in input_brackets]
        normalized_candidates = [self.normalize_bracket_content(b) for b in candidate_brackets]
        
        logging.debug(f"括号内容比较:")
        logging.debug(f"  输入括号: {normalized_inputs}")
        logging.debug(f"  候选括号: {normalized_candidates}")
        
        # 检查是否有别名指示词
        input_aliases = {}
        for i, input_bracket in enumerate(input_brackets):
            alias = self.extract_alias(input_bracket)
            if alias:
                input_aliases[i] = alias
        
        candidate_aliases = {}
        for i, candidate_bracket in enumerate(candidate_brackets):
            alias = self.extract_alias(candidate_bracket)
            if alias:
                candidate_aliases[i] = alias
        
        # 记录找到的别名
        if input_aliases:
            logging.debug(f"  输入括号中的别名: {input_aliases}")
        if candidate_aliases:
            logging.debug(f"  候选括号中的别名: {candidate_aliases}")
        
        # 为每个输入括号找到最佳匹配的候选括号
        overall_scores = []
        for i, input_bracket in enumerate(normalized_inputs):
            if not input_bracket.strip():
                continue

            # 分类当前括号类型
            input_type = self.classify_bracket_type(input_bracket)
            input_importance = self.bracket_type_weights.get(input_type, 0.4)
            
            logging.debug(f"\n  输入括号[{i}]: '{input_bracket}' (类型={input_type}, 重要性={input_importance:.2f})")
            
            # 检查是否是别名括号
            is_input_alias = i in input_aliases
            input_alias = input_aliases.get(i)
            
            best_score = 0
            best_candidate_idx = -1
            best_candidate_type = ""
            comparison_details = []
            
            for j, candidate in enumerate(normalized_candidates):
                if not candidate.strip():
                    continue
                    
                # 分类候选括号类型
                candidate_type = self.classify_bracket_type(candidate)
                
                # 检查是否是别名括号
                is_candidate_alias = j in candidate_aliases
                candidate_alias = candidate_aliases.get(j)
                
                # 标准相似度计算
                token_set_score = fuzz.token_set_ratio(input_bracket, candidate)
                ratio_score = fuzz.ratio(input_bracket, candidate)
                partial_score = fuzz.partial_ratio(input_bracket, candidate)
                
                # 标准相似度分数
                score = max(token_set_score, ratio_score, partial_score)
                score_detail = f"基础分={score:.2f}"
                
                # 类型匹配加分
                type_bonus = 0
                if input_type == candidate_type:
                    type_bonus = 10
                    score += type_bonus
                    score_detail += f", 类型匹配加分={type_bonus:+.2f}"
                
                # 别名处理 - 如果双方都是别名指示符格式
                alias_score_detail = ""
                if is_input_alias and is_candidate_alias:
                    # 比较两个别名的相似度
                    alias_score = fuzz.token_set_ratio(input_alias, candidate_alias)
                    old_score = score
                    # 别名相似度高则提升总分，用加权平均
                    if alias_score > 70:  # 别名有一定相似度
                        score = score * 0.3 + alias_score * 0.7  # 更重视别名匹配
                        alias_score_detail = f", 别名相似度={alias_score:.2f}, 调整={score-old_score:+.2f}"
                
                # 特殊处理feat艺术家
                feat_score_detail = ""
                if input_type == "feat" and candidate_type == "feat":
                    input_artists = self.extract_feat_artists(input_brackets[i])
                    candidate_artists = self.extract_feat_artists(candidate_brackets[j])
                    feat_score = self.calculate_feat_artist_similarity(input_artists, candidate_artists)
                    
                    # 根据feat艺术家相似度调整分数
                    if feat_score > 0:
                        old_score = score
                        score = score * 0.3 + feat_score * 0.7  # 更重视艺术家匹配
                        feat_score_detail = f", feat艺术家分={feat_score:.2f}, 调整={score-old_score:+.2f}"
                
                # 记录每次比较的详情
                comparison_details.append(
                    f"    与候选[{j}] '{candidate}' (类型={candidate_type}): " +
                    f"分数={score:.2f} [{score_detail}{feat_score_detail}{alias_score_detail}]"
                )
                
                if score > best_score:
                    best_score = score
                    best_candidate_idx = j
                    best_candidate_type = candidate_type
            
            # 记录为当前输入括号找到的最佳匹配
            if comparison_details:
                for detail in comparison_details:
                    logging.debug(detail)
                
                if best_candidate_idx >= 0:
                    logging.debug(f"  最佳匹配: 候选括号[{best_candidate_idx}] " +
                                 f"'{normalized_candidates[best_candidate_idx]}' " +
                                 f"(类型={best_candidate_type}), 分数={best_score:.2f}")
                else:
                    logging.debug(f"  未找到匹配")

            if best_score > 0:  # 只添加有效的分数
                # 根据括号重要性加权
                overall_scores.append((best_score, input_importance))
        
        # 如果没有有效的分数，返回中等分数，避免过度惩罚
        if not overall_scores:
            logging.debug(f"没有有效的括号匹配，返回默认分数70.0")
            return 70.0
            
        # 计算加权平均分数 - 重要性高的括号获得更高权重
        total_weight = sum(weight for _, weight in overall_scores)
        weighted_avg = sum(score * weight for score, weight in overall_scores) / total_weight
        
        # 记录最终的加权计算过程
        logging.debug(f"\n括号得分汇总:")
        for i, (score, weight) in enumerate(overall_scores):
            logging.debug(f"  括号[{i}]: 分数={score:.2f}, 重要性权重={weight:.2f}, 贡献={score*weight/total_weight:.2f}")
        
        logging.debug(f"括号内容加权相似度最终分数: {weighted_avg:.2f} (总权重={total_weight:.2f})")
        
        return weighted_avg

    def calculate_keyword_bonus(self, input_brackets: List[str], 
                               candidate_brackets: List[str]) -> float:
        """
        根据关键词匹配计算额外加分
        
        在匹配过程中对特殊关键词（如"live"、"remix"等）给予额外加分。
        当输入和候选歌曲都包含相同的特殊关键词时，这一点尤为重要，
        因为它强烈暗示了两首歌曲是同一版本。

        Args:
            input_brackets: 输入歌曲的括号内容列表
            candidate_brackets: 候选歌曲的括号内容列表

        Returns:
            float: 额外加分（0+）
        """
        # 检测关键词
        input_keywords = self.detect_keywords(input_brackets)
        candidate_keywords = self.detect_keywords(candidate_brackets)
        
        # 如果没有关键词，返回0
        if not input_keywords or not candidate_keywords:
            logging.info("[关键词加分] 输入或候选没有检测到关键词，不加分")
            return 0.0
            
        # 准备关键词映射，用于匹配相似概念
        extended_input_keywords = {}
        for keyword, weight in input_keywords.items():
            extended_input_keywords[keyword] = weight
            # 添加同义词
            if keyword in self.keyword_mappings:
                for variant in self.keyword_mappings[keyword]:
                    if variant not in extended_input_keywords:
                        extended_input_keywords[variant] = weight
            
        extended_candidate_keywords = {}
        for keyword, weight in candidate_keywords.items():
            extended_candidate_keywords[keyword] = weight
            # 添加同义词
            if keyword in self.keyword_mappings:
                for variant in self.keyword_mappings[keyword]:
                    if variant not in extended_candidate_keywords:
                        extended_candidate_keywords[variant] = weight
                        
        # 计算匹配关键词的额外加分
        bonus = 0.0
        for keyword, weight in extended_input_keywords.items():
            if keyword in extended_candidate_keywords:
                match_bonus = min(weight, extended_candidate_keywords[keyword]) * self.keyword_bonus
                bonus += match_bonus
                logging.info(f"[关键词加分] 关键词 '{keyword}' 匹配成功，加分 {match_bonus:.2f}")
            else:
                logging.debug(f"[关键词加分] 关键词 '{keyword}' 在候选中未找到")
                
        if bonus == 0.0:
            logging.info("[关键词加分] 没有找到匹配的关键词，不加分")
        else:
            logging.info(f"[关键词加分] 总加分: {bonus:.2f}")
                
        return bonus

    def calculate_final_score(self, base_score: float, bracket_score: float, 
                             keyword_bonus: float) -> float:
        """
        计算最终得分，整合基本得分、括号内容得分和关键词额外加分
        
        这是括号匹配器的核心算法，将第一阶段的基本得分与括号内容匹配
        和关键词匹配结果相结合，计算最终的匹配得分。
        
        得分计算公式：
        final_score = base_score + (bracket_score * bracket_weight) + keyword_bonus

        Args:
            base_score: 基本得分（如字符串匹配得分）
            bracket_score: 括号内容相似度得分
            keyword_bonus: 关键词额外加分

        Returns:
            float: 最终得分（0-100+）
        """
        # 括号内容得分需要超过阈值才会被计入
        # 这确保了只有高质量的括号内容匹配才会影响最终分数
        bracket_contribution = 0.0
        if bracket_score >= self.threshold:
            bracket_contribution = bracket_score * self.bracket_weight
            logging.info(f"[最终得分] 括号得分 {bracket_score:.2f} 超过阈值 {self.threshold:.2f}，贡献为 {bracket_contribution:.2f}")
        else:
            logging.info(f"[最终得分] 括号得分 {bracket_score:.2f} 未超过阈值 {self.threshold:.2f}，不计入")
            
        # 计算最终得分
        final_score = base_score + bracket_contribution + keyword_bonus
        
        # 记录得分组成
        logging.info(f"[最终得分] {final_score:.2f} = {base_score:.2f}(基础) + " +
                     f"{bracket_contribution:.2f}(括号) + {keyword_bonus:.2f}(关键词)")
        
        return min(final_score, 100.0)  # 最高分为100

    def match(self, input_title: str, candidate_title: str, base_score: float) -> float:
        """
        计算考虑括号内容后的最终匹配分数
        
        这是BracketMatcher类的主要入口点，提供了一个简单的接口来调整匹配分数。
        它协调整个括号匹配过程，从提取括号内容到计算最终得分。

        Args:
            input_title: 输入歌曲标题
            candidate_title: 候选歌曲标题
            base_score: 基本字符串匹配得分

        Returns:
            float: 最终匹配分数（0-100+，可能超过100，但一般会在使用前限制）
        """
        logging.info(f"[括号匹配] 开始匹配: 输入 '{input_title}' vs 候选 '{candidate_title}', 基础分数: {base_score:.2f}")
        
        # 提取括号内容
        input_brackets = self.extract_brackets(input_title)
        candidate_brackets = self.extract_brackets(candidate_title)
        
        # 如果两者都没有括号内容，直接返回基础分数
        if not input_brackets and not candidate_brackets:
            logging.info(f"[括号匹配] 输入和候选均无括号内容，保持基础分数 {base_score:.2f}")
            return base_score
            
        # 计算括号内容相似度
        bracket_score = self.calculate_bracket_similarity(input_brackets, candidate_brackets)
        
        # 计算关键词额外加分
        keyword_bonus = self.calculate_keyword_bonus(input_brackets, candidate_brackets)
        
        # 计算最终分数
        final_score = self.calculate_final_score(base_score, bracket_score, keyword_bonus)
        
        logging.info(f"[括号匹配] 完成匹配: 输入 '{input_title}' vs 候选 '{candidate_title}', 最终分数: {final_score:.2f}")
        
        return final_score 

    def classify_bracket_type(self, bracket_content: str) -> str:
        """
        根据括号内容识别其类型
        
        Args:
            bracket_content: 标准化后的括号内容
            
        Returns:
            str: 括号类型，如"live"、"remix"、"feat"等
        """
        if not bracket_content:
            return "other"
        
        content = bracket_content.lower()
        
        # 检查是否包含合作艺术家信息
        if any(k in content for k in ["feat", "ft", "featuring", "with"]):
            return "feat"
        
        # 检查是否是remix版本
        if any(k in content for k in ["remix", "mix", "dj", "club", "extended"]):
            return "remix"
        
        # 检查是否是现场版本
        if any(k in content for k in ["live", "现场", "演唱会", "concert"]):
            return "live"
        
        # 检查是否是原声版本
        if any(k in content for k in ["acoustic", "原声", "钢琴", "吉他", "piano", "guitar"]):
            return "acoustic"
        
        # 检查是否是重制版
        if any(k in content for k in ["remaster", "重制", "修复", "高清", "hd"]):
            return "remaster"
        
        # 检查是否包含版本信息
        if any(k in content for k in ["version", "版本", "ver", "special", "deluxe"]):
            return "version"
        
        # 检查是否是别名信息
        if any(k in content for k in ["又名", "别名", "aka", "also known as", "原名"]):
            return "alias"
        
        # 检查是否包含年份 - 四位数字可能是年份
        if re.search(r'\b(19|20)\d{2}\b', content):
            return "year"
        
        # 默认为其他类型
        return "other"

def adjust_scores_with_brackets(matches: List[Dict[str, Any]], input_title: str) -> List[Dict[str, Any]]:
    """
    使用括号匹配调整字符串匹配的分数
    
    Args:
        matches: StringMatcher计算的基础匹配结果列表
        input_title: 原始输入标题（未标准化）
        
    Returns:
        List[Dict[str, Any]]: 调整后的匹配结果列表
    """
    # 创建BracketMatcher实例
    bracket_matcher = BracketMatcher()
    
    # 复制匹配结果，避免修改原始数据
    adjusted_matches = []
    
    logging.debug(f"使用括号匹配调整分数: 输入标题='{input_title}', 匹配数量={len(matches)}")
    
    for match in matches:
        # 复制匹配项，避免修改原始数据
        adjusted_match = match.copy()
        
        # 获取候选标题
        candidate_title = match.get("name", "")
        
        # 获取基础分数
        base_score = match.get("similarity_scores", {}).get("weighted_score", 0)
        
        # 应用括号匹配调整分数
        bracket_score = bracket_matcher.match(input_title, candidate_title, base_score)
        
        # 重新计算最终分数 - 确保不超过100
        final_score = min(bracket_score, 100.0)
        
        # 更新匹配项的分数信息
        if "similarity_scores" not in adjusted_match:
            adjusted_match["similarity_scores"] = {}
            
        adjusted_match["similarity_scores"]["bracket_score"] = bracket_score - base_score
        adjusted_match["similarity_scores"]["final_score"] = final_score
        
        # 记录调整过程
        logging.debug(f"标题匹配调整: '{candidate_title}', 基础分={base_score:.2f}, " + 
                     f"括号调整={bracket_score-base_score:+.2f}, 最终分={final_score:.2f}")
        
        adjusted_matches.append(adjusted_match)
    
    # 重新按最终得分排序
    adjusted_matches.sort(
        key=lambda x: x.get("similarity_scores", {}).get("final_score", 0),
        reverse=True
    )
    
    return adjusted_matches 