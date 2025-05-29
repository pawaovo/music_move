"""
字符串相似度匹配模块

提供歌曲标题和艺术家名称的相似度计算功能，用于匹配Spotify搜索结果。
"""

import logging
from typing import Dict, List, Optional, Tuple, Union, Any

import fuzzywuzzy.fuzz as fuzz
from fuzzywuzzy import process

from spotify_playlist_importer.utils.text_normalizer import normalize_text


class StringMatcher:
    """
    字符串相似度匹配类，用于计算文本相似度并排序匹配结果
    
    该类实现了歌曲匹配算法的第一阶段，主要基于标题和艺术家的字符串相似度，
    通过多维度的文本比较（包括比率得分、部分比率、令牌排序等）计算相似度，
    并应用可配置的权重进行综合评分。
    
    核心算法特性:
    1. 多种相似度算法组合，提高匹配准确性
    2. 可配置的权重系统，适应不同音乐类型的匹配需求
    3. 早期剪枝策略，提高处理大量候选时的性能
    4. 详细的相似度分解，便于调试和优化
    """

    def __init__(self, title_weight: float = 0.6, artist_weight: float = 0.4,
                 threshold: float = 75.0, top_k: int = 3):
        """
        初始化StringMatcher
        
        参数权重决定了匹配过程中各因素的重要性。通常，标题权重应略高于艺术家权重，
        但对于某些特定音乐类型可能需要调整（如古典音乐可能需要更高的标题权重）。

        Args:
            title_weight: 标题相似度在总得分中的权重，默认0.6
            artist_weight: 艺术家相似度在总得分中的权重，默认0.4
            threshold: 最小匹配阈值，默认75（满分100）
            top_k: 返回的最佳匹配数量，默认3
        """
        # 验证权重参数
        if not (0 <= title_weight <= 1) or not (0 <= artist_weight <= 1):
            raise ValueError("权重必须在0到1之间")
        if abs((title_weight + artist_weight) - 1.0) > 0.001:  # 允许浮点误差
            raise ValueError(f"权重之和应为1.0，当前为{title_weight + artist_weight}")

        self.title_weight = title_weight
        self.artist_weight = artist_weight
        self.threshold = threshold
        self.top_k = top_k

    def normalize_for_matching(self, text: str) -> str:
        """
        为匹配准备文本，进行归一化处理
        
        此处使用文本归一化模块处理输入文本，并特别移除括号内容，
        因为括号信息将在第二阶段匹配中单独处理。

        Args:
            text: 要归一化的文本

        Returns:
            str: 归一化后的文本
        """
        # 使用文本归一化模块进行处理，并移除括号内容
        return normalize_text(text, remove_patterns=["brackets"])

    def calculate_title_similarity(self, input_title: str, candidate_title: str) -> float:
        """
        计算两个标题的相似度分数
        
        使用多种相似度算法计算标题相似度，并综合加权得到最终分数。
        这种多算法组合的方法可以处理各种标题变体，如词序不同、部分匹配等情况。

        Args:
            input_title: 输入的歌曲标题
            candidate_title: 候选歌曲标题

        Returns:
            float: 相似度分数（0-100）
        """
        # 归一化标题
        norm_input = self.normalize_for_matching(input_title)
        norm_candidate = self.normalize_for_matching(candidate_title)

        logging.debug(f"标题比较: '{norm_input}' vs '{norm_candidate}'")

        # 计算比率得分 - 标准编辑距离相似度
        ratio_score = fuzz.ratio(norm_input, norm_candidate)
        # 计算部分比率（处理部分匹配，如子字符串）
        partial_ratio_score = fuzz.partial_ratio(norm_input, norm_candidate)
        # 计算标记排序比率（处理词序不同的情况）
        token_sort_ratio_score = fuzz.token_sort_ratio(norm_input, norm_candidate)

        # 综合三种得分，可以调整权重
        # 标准比率和部分比率各占40%，词序比率占20%
        # 这个权重分配适合大多数流行音乐标题，可根据需求调整
        final_score = (ratio_score * 0.4 + 
                      partial_ratio_score * 0.4 + 
                      token_sort_ratio_score * 0.2)

        logging.debug(f"标题相似度分数: {final_score:.2f} [ratio={ratio_score}, " +
                     f"partial={partial_ratio_score}, token_sort={token_sort_ratio_score}]")

        return final_score

    def contains_chinese(self, text: str) -> bool:
        """
        检查文本是否包含中文字符

        Args:
            text: 要检查的文本

        Returns:
            bool: 是否包含中文字符
        """
        return any('\u4e00' <= c <= '\u9fff' for c in text)
    
    def get_pinyin(self, text: str) -> str:
        """
        获取文本的拼音表示，用于中文文本的匹配
        
        Args:
            text: 输入文本
            
        Returns:
            str: 拼音表示
        """
        try:
            # 如果pypinyin库可用，使用它进行拼音转换
            import pypinyin
            pinyin_list = pypinyin.lazy_pinyin(text)
            return ' '.join(pinyin_list)
        except ImportError:
            logging.warning("未找到pypinyin库，将返回原始文本")
            return text
        except Exception as e:
            logging.warning(f"拼音转换失败: {e}")
            return text

    def calculate_artists_similarity(self, input_artists: List[str], candidate_artists: List[str]) -> float:
        """
        计算艺术家列表的相似度分数

        Args:
            input_artists: 输入的艺术家列表
            candidate_artists: 候选歌曲的艺术家列表

        Returns:
            float: 相似度分数（0-100）
        """
        # 处理空列表情况
        if not input_artists and not candidate_artists:
            # 两个都为空，认为是完全匹配
            return 100.0
        if not input_artists or not candidate_artists:
            # 一个为空，另一个不为空，基本不匹配
            return 0.0

        # 日志记录
        logging.debug(f"艺术家比较: {input_artists} vs {candidate_artists}")
        
        # 检查主要艺术家是否完全存在于候选艺术家列表中
        if input_artists and len(input_artists) > 0:
            main_artist = input_artists[0]  # 第一位艺术家视为主要艺术家
            
            # 检查主要艺术家是否完全匹配
            main_artist_highest_match = max(
                fuzz.token_set_ratio(main_artist, cand_artist) 
                for cand_artist in candidate_artists
            )
            
            if main_artist_highest_match >= 90:
                logging.debug(f"主要艺术家高度匹配: {main_artist}")
                artist_similarity = max(85.0, main_artist_highest_match)  # 保证至少85分
                logging.debug(f"艺术家相似度结果(主要艺术家匹配): {artist_similarity:.2f}")
                return artist_similarity

        # 计算每个输入艺术家与候选艺术家的最高匹配度
        best_matches = []
        for input_artist in input_artists:
            # 计算与每个候选艺术家的匹配度，选择最高的
            best_match = max(fuzz.token_set_ratio(input_artist, cand_artist) for cand_artist in candidate_artists)
            best_matches.append(best_match)

        # 如果所有艺术家的匹配度都很高，那么给予高分
        avg_match = sum(best_matches) / len(best_matches) if best_matches else 0
        
        # 如果艺术家相似度较低（低于60分），尝试拼音比较
        if avg_match < 60.0 and self.contains_chinese(''.join(input_artists + candidate_artists)):
            logging.debug("艺术家相似度较低，尝试拼音比较")
            
            # 将输入艺术家转换为拼音
            input_pinyin_artists = []
            for artist in input_artists:
                if self.contains_chinese(artist):
                    pinyin = self.get_pinyin(artist)
                    input_pinyin_artists.append(pinyin)
                    logging.debug(f"输入艺术家拼音: {artist} -> {pinyin}")
                else:
                    input_pinyin_artists.append(artist)
            
            # 将候选艺术家转换为拼音
            candidate_pinyin_artists = []
            for artist in candidate_artists:
                if self.contains_chinese(artist):
                    pinyin = self.get_pinyin(artist)
                    candidate_pinyin_artists.append(pinyin)
                    logging.debug(f"候选艺术家拼音: {artist} -> {pinyin}")
                else:
                    candidate_pinyin_artists.append(artist)

            # 计算拼音相似度
            pinyin_best_matches = []
            for input_pinyin in input_pinyin_artists:
                best_match = max(fuzz.token_set_ratio(input_pinyin, cand_pinyin) 
                                 for cand_pinyin in candidate_pinyin_artists)
                pinyin_best_matches.append(best_match)
            
            pinyin_avg_match = sum(pinyin_best_matches) / len(pinyin_best_matches) if pinyin_best_matches else 0
            
            logging.debug(f"拼音相似度: {pinyin_avg_match:.2f}")
            
            # 如果拼音相似度较高，使用拼音相似度替代原始相似度
            if pinyin_avg_match > avg_match:
                avg_match = pinyin_avg_match
                logging.debug(f"艺术家相似度更新为拼音相似度: {avg_match:.2f}")

        # 记录结果
        logging.debug(f"艺术家相似度分数: {avg_match:.2f}, 最佳匹配: {best_matches}")

        return avg_match

    def calculate_weighted_score(self, title_score: float, artist_score: float) -> float:
        """
        计算标题和艺术家相似度的加权总分

        Args:
            title_score: 标题相似度分数（0-100）
            artist_score: 艺术家相似度分数（0-100）

        Returns:
            float: 加权总分（0-100）
        """
        return self.title_weight * title_score + self.artist_weight * artist_score
    
    def calculate_combined_score(self, title_score: float, artist_score: float) -> float:
        """
        计算标题和艺术家相似度的加权总分（与calculate_weighted_score功能相同，为兼容性添加）

        Args:
            title_score: 标题相似度分数（0-100）
            artist_score: 艺术家相似度分数（0-100）

        Returns:
            float: 加权总分（0-100）
        """
        return self.calculate_weighted_score(title_score, artist_score)

    def _quick_check(self, input_title: str, input_artists: List[str], candidate: Dict[str, Any]) -> bool:
        """
        快速检查候选是否有可能匹配，用于早期剪枝
        
        此方法是性能优化的关键部分，通过简单但高效的启发式规则，
        在进行详细（计算密集型）相似度计算前过滤掉明显不匹配的候选。
        
        优化策略:
        1. 检查标题长度差异 - 差异过大说明可能不是同一首歌
        2. 检查艺术家交集 - 完全无交集的艺术家很可能不是同一首歌
        
        Args:
            input_title: 输入歌曲标题
            input_artists: 输入艺术家列表
            candidate: 候选歌曲
            
        Returns:
            bool: 如果候选可能匹配则返回True，否则返回False
        """
        # 获取候选标题和艺术家
        candidate_title = candidate.get("name", "")
        candidate_artists = [artist.get("name", "") for artist in candidate.get("artists", [])]
        
        # 转换为小写以进行快速比较
        input_title_lower = input_title.lower()
        candidate_title_lower = candidate_title.lower()
        
        # 如果标题长度差异太大，可能不匹配
        # 此启发式规则基于观察：真实匹配的歌曲标题长度通常不会相差太多
        if abs(len(input_title_lower) - len(candidate_title_lower)) > len(input_title_lower) * 0.5:
            return False
            
        # 检查艺术家是否有交集
        if input_artists and candidate_artists:
            input_artists_lower = [a.lower() for a in input_artists]
            candidate_artists_lower = [a.lower() for a in candidate_artists]
            
            # 如果没有任何艺术家名称部分匹配，可能不匹配
            # 这里使用部分包含而非完全匹配，因为艺术家名称可能有变体
            has_artist_match = False
            for input_artist in input_artists_lower:
                for candidate_artist in candidate_artists_lower:
                    if input_artist in candidate_artist or candidate_artist in input_artist:
                        has_artist_match = True
                        break
                if has_artist_match:
                    break
                    
            if not has_artist_match:
                return False
        
        return True
        
    def match(self, input_title: str, input_artists: List[str], 
             candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        匹配输入歌曲与候选列表
        
        这是匹配算法的主要入口，执行完整的第一阶段匹配流程:
        1. 对每个候选进行早期剪枝检查
        2. 对通过检查的候选计算详细相似度
        3. 过滤低于阈值的结果
        4. 排序并返回最佳匹配
        
        Args:
            input_title: 输入歌曲标题
            input_artists: 输入艺术家列表
            candidates: 候选歌曲列表
            
        Returns:
            List[Dict[str, Any]]: 匹配结果列表，按相似度降序排序
        """
        if not candidates:
            logging.debug("没有候选歌曲，返回空列表")
            return []
            
        matches = []
        
        for candidate in candidates:
            # 快速检查，早期剪枝
            if not self._quick_check(input_title, input_artists, candidate):
                continue
                
            # 计算相似度
            similarity_scores = self.calculate_similarity(input_title, input_artists, candidate)
            weighted_score = similarity_scores["weighted_score"]
            
            # 如果相似度超过阈值，添加到匹配结果
            if weighted_score >= self.threshold:
                # 复制候选，避免修改原始数据
                match = candidate.copy()
                # 添加相似度信息
                match["similarity_scores"] = similarity_scores
                matches.append(match)
        
        # 按相似度降序排序
        matches.sort(key=lambda x: x["similarity_scores"]["weighted_score"], reverse=True)
        
        # 如果指定了top_k，只返回前k个结果
        if self.top_k > 0 and len(matches) > self.top_k:
            matches = matches[:self.top_k]
            
        return matches

    def calculate_similarity(self, input_title: str, input_artists: List[str],
                        candidate: Dict[str, Any]) -> Dict[str, float]:
        """
        计算输入歌曲与候选歌曲的相似度
        
        综合计算标题和艺术家的相似度，并返回详细的评分数据。
        此方法将整个相似度计算过程封装为一个简单调用，方便外部使用。
        
        Args:
            input_title: 输入歌曲标题
            input_artists: 输入艺术家列表
            candidate: 候选歌曲
            
        Returns:
            Dict[str, float]: 包含标题相似度、艺术家相似度和加权总分的字典
        """
        candidate_title = candidate.get('name', '')
        candidate_artists = [artist.get('name', '') for artist in candidate.get('artists', [])]
        
        title_score = self.calculate_title_similarity(input_title, candidate_title)
        artist_score = self.calculate_artists_similarity(input_artists, candidate_artists)
        weighted_score = self.calculate_weighted_score(title_score, artist_score)
        
        return {
            'title_score': title_score,
            'artist_score': artist_score,
            'weighted_score': weighted_score
        }


def get_best_match(input_title: str, input_artists: List[str],
                 candidates: List[Dict[str, Any]],
                 title_weight: float = 0.6, artist_weight: float = 0.4,
                 threshold: float = 75.0) -> Optional[Dict[str, Any]]:
    """
    便利函数，获取最佳匹配的候选歌曲
    
    这是一个简化的接口，适用于只需要最佳匹配结果的场景。
    内部使用StringMatcher进行计算，但简化了调用过程。

    Args:
        input_title: 输入的歌曲标题
        input_artists: 输入的艺术家列表
        candidates: 候选歌曲列表
        title_weight: 标题相似度权重
        artist_weight: 艺术家相似度权重
        threshold: 最小匹配阈值

    Returns:
        Optional[Dict[str, Any]]: 最佳匹配的候选歌曲，如果没有匹配则返回None
    """
    matcher = StringMatcher(
        title_weight=title_weight,
        artist_weight=artist_weight,
        threshold=threshold,
        top_k=1
    )
    
    matches = matcher.match(input_title, input_artists, candidates)
    return matches[0] if matches else None 