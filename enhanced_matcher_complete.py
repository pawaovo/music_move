"""
A module for enhanced string matching between input songs and candidates.
"""

import logging
from typing import Dict, List, Any, Tuple

from spotify_playlist_importer.utils.string_matcher import StringMatcher
from spotify_playlist_importer.utils.bracket_matcher import BracketMatcher
from spotify_playlist_importer.utils.text_normalizer import normalize_text, split_text

class EnhancedMatcher:
    """
    增强歌曲匹配器，实现两阶段匹配：基础字符串匹配和括号内容感知匹配
    """
    
    def __init__(self, title_weight: float = 0.6, artist_weight: float = 0.4,
                 bracket_weight: float = 0.3, first_stage_threshold: float = 60.0, 
                 second_stage_threshold: float = 70.0, enable_detailed_logging: bool = True):
        """
        Initialize the EnhancedMatcher.
        
        Args:
            title_weight: Title similarity weight in the range [0.0, 1.0]
            artist_weight: Artist similarity weight in the range [0.0, 1.0]
            bracket_weight: Bracket content matching weight for stage 2
            first_stage_threshold: Minimum score threshold for first stage matching
            second_stage_threshold: Minimum score threshold for second stage matching
            enable_detailed_logging: Whether to enable detailed logging for each match
        """
        # Basic weights and thresholds
        self.title_weight = title_weight
        self.artist_weight = artist_weight
        self.bracket_weight = bracket_weight
        self.first_stage_threshold = first_stage_threshold
        self.second_stage_threshold = second_stage_threshold
        self.enable_detailed_logging = enable_detailed_logging
        
        # Create matcher instances
        self.string_matcher = StringMatcher(title_weight, artist_weight)
        self.bracket_matcher = BracketMatcher(weight=bracket_weight)
        
        # Original input (for logging)
        self._original_input_title = ""
        self._original_input_artists = []
        
        # Log initialization
        logging.info(f"[增强匹配] 初始化匹配器 - 权重: 标题={title_weight:.2f}, 艺术家={artist_weight:.2f}, 括号={bracket_weight:.2f}")
        logging.info(f"[增强匹配] 初始化匹配器 - 阈值: 第一阶段={first_stage_threshold:.2f}, 第二阶段={second_stage_threshold:.2f}")

    def standardize_texts(self, input_title: str, input_artists: List[str], 
                          candidates: List[Dict[str, Any]]) -> Tuple[str, List[str], List[Dict[str, Any]]]:
        """
        对输入歌曲和候选歌曲进行文本标准化处理
        
        Args:
            input_title: 输入歌曲标题
            input_artists: 输入歌曲艺术家列表
            candidates: 候选歌曲列表
            
        Returns:
            Tuple[str, List[str], List[Dict[str, Any]]]: 标准化后的标题、艺术家列表和候选歌曲
        """
        # 保存原始输入，以便在日志和调试中使用
        self._original_input_title = input_title
        self._original_input_artists = input_artists.copy() if input_artists else []
        
        # 记录原始输入
        logging.debug(f"开始统一文本标准化: 输入标题='{input_title}', 艺术家={input_artists}, 候选数量={len(candidates)}")
        
        # 标准化输入歌曲标题
        std_title = normalize_text(input_title, keep_brackets=True)
        if std_title != input_title:
            logging.debug(f"标准化输入标题: '{input_title}' -> '{std_title}'")
        
        # 标准化输入歌曲艺术家列表
        std_artists = [normalize_text(artist, keep_brackets=True) for artist in input_artists] if input_artists else []
        for i, (orig, std) in enumerate(zip(input_artists, std_artists)):
            if orig != std:
                logging.debug(f"标准化输入艺术家[{i}]: '{orig}' -> '{std}'")
        
        # 标准化候选歌曲信息
        std_candidates = []
        for candidate in candidates:
            # 复制原始候选歌曲数据
            std_candidate = candidate.copy()
            
            # 标准化候选歌曲标题
            title = candidate.get('name', '')
            std_title_candidate = normalize_text(title, keep_brackets=True)
            if std_title_candidate != title:
                logging.debug(f"标准化候选标题: '{title}' -> '{std_title_candidate}'")
                std_candidate['original_name'] = title  # 保存原始标题
                std_candidate['name'] = std_title_candidate  # 替换为标准化标题
            
            # 标准化候选歌曲艺术家
            std_artists_candidate = []
            for artist in candidate.get('artists', []):
                artist_name = artist.get('name', '')
                std_artist_name = normalize_text(artist_name, keep_brackets=True)
                
                # 复制艺术家数据并更新标准化名称
                std_artist = artist.copy()
                if std_artist_name != artist_name:
                    logging.debug(f"标准化候选艺术家: '{artist_name}' -> '{std_artist_name}'")
                    std_artist['original_name'] = artist_name  # 保存原始名称
                    std_artist['name'] = std_artist_name  # 替换为标准化名称
                
                std_artists_candidate.append(std_artist)
            
            # 更新候选歌曲的艺术家列表
            std_candidate['original_artists'] = candidate.get('artists', [])  # 保存原始艺术家列表
            std_candidate['artists'] = std_artists_candidate  # 替换为标准化艺术家列表
            
            std_candidates.append(std_candidate)
        
        logging.debug(f"完成统一文本标准化: 标准化后输入标题='{std_title}', 标准化后输入艺术家={std_artists}")
        
        return std_title, std_artists, std_candidates
        
    def match(self, input_title: str, input_artists: List[str],
              candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        执行歌曲匹配流程
        
        Args:
            input_title: 输入歌曲标题
            input_artists: 输入歌曲艺术家列表
            candidates: 候选歌曲列表
            
        Returns:
            List[Dict[str, Any]]: 匹配结果列表，按匹配分数降序排序
        """
        # 首先标准化所有文本
        std_title, std_artists, std_candidates = self.standardize_texts(input_title, input_artists, candidates)
        
        # 记录输入详情
        self.log_input_details(std_title, std_artists)
        
        # 第一阶段匹配：基于字符串相似度
        first_matches = self.first_stage_match(std_title, std_artists, std_candidates)
        
        # 如果第一阶段没有匹配，返回空列表
        if not first_matches:
            logging.debug(f"第一阶段未找到匹配，所有候选均低于阈值 {self.first_stage_threshold:.2f}")
            return []
        
        # 第二阶段匹配：考虑括号内容
        final_matches = self.second_stage_match(std_title, std_artists, first_matches)
        
        # 如果第二阶段没有匹配，返回空列表
        if not final_matches:
            logging.debug(f"第二阶段未找到匹配，所有候选均低于阈值 {self.second_stage_threshold:.2f}")
            return []
        
        # 记录最佳匹配的详细信息
        if final_matches:
            self._log_detailed_match_info(std_title, std_artists, final_matches[0])
        
        return final_matches

    def log_input_details(self, input_title: str, input_artists: List[str]) -> None:
        """
        Log input details for debugging.
        
        Args:
            input_title: Input song title
            input_artists: Input artists list
        """
        if not self.enable_detailed_logging:
            return
            
        logging.debug(f"[输入歌曲] 标题: '{input_title}'")
        if self._original_input_title != input_title:
            logging.debug(f"[输入歌曲] 原始标题: '{self._original_input_title}'")
            
        if input_artists:
            artist_str = ", ".join([f"'{a}'" for a in input_artists])
            logging.debug(f"[输入歌曲] 艺术家: {artist_str}")
            
            if any(a != b for a, b in zip(self._original_input_artists, input_artists)):
                orig_artist_str = ", ".join([f"'{a}'" for a in self._original_input_artists])
                logging.debug(f"[输入歌曲] 原始艺术家: {orig_artist_str}")
        else:
            logging.debug("[输入歌曲] 艺术家: 无")

    def log_candidate_details(self, candidate: Dict[str, Any], score: float) -> None:
        """
        Log candidate details for debugging.
        
        Args:
            candidate: Candidate song object
            score: Similarity score
        """
        if not self.enable_detailed_logging:
            return
            
        logging.debug(f"[候选歌曲] 标题: '{candidate.get('name', 'Unknown')}'")
        if 'original_name' in candidate:
            logging.debug(f"[候选歌曲] 原始标题: '{candidate['original_name']}'")
            
        artists = candidate.get('artists', [])
        if artists:
            artist_str = ", ".join([f"'{a.get('name', 'Unknown')}'" for a in artists])
            logging.debug(f"[候选歌曲] 艺术家: {artist_str}")
            
            if 'original_artists' in candidate:
                orig_artists = candidate['original_artists']
                if orig_artists:
                    orig_artist_str = ", ".join([f"'{a.get('name', 'Unknown')}'" for a in orig_artists])
                    logging.debug(f"[候选歌曲] 原始艺术家: {orig_artist_str}")
        else:
            logging.debug("[候选歌曲] 艺术家: 无")

        logging.debug(f"[候选歌曲] 匹配分数: {score:.2f}")

    def first_stage_match(self, input_title: str, input_artists: List[str], 
                         candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Execute first stage matching based on string similarity.
        
        Args:
            input_title: Input song title (standardized)
            input_artists: Input artists list (standardized)
            candidates: List of candidate songs
            
        Returns:
            List of matched candidates that exceed the first stage threshold
        """
        if not candidates:
            logging.debug("无候选歌曲可供匹配")
            return []
            
        logging.debug(f"\n=== 第一阶段匹配 - 基础字符串相似度 ===")
        
        # Calculate similarity scores for all candidates
        scored_candidates = []
        
        for candidate in candidates:
            # Extract data
            candidate_title = candidate.get('name', '')
            candidate_artists = [artist.get('name', '') for artist in candidate.get('artists', [])]
            
            # Calculate title and artist similarity
            title_similarity = self.string_matcher.calculate_title_similarity(input_title, candidate_title)
            artist_similarity = self.string_matcher.calculate_artist_similarity(input_artists, candidate_artists)
            
            # Calculate overall score
            score = self.string_matcher.calculate_combined_score(title_similarity, artist_similarity)
            
            # Store scores for later stages
            similarity_scores = {
                'title_similarity': title_similarity,
                'artist_similarity': artist_similarity,
                'first_stage_score': score,
                'is_low_confidence': score < self.second_stage_threshold
            }
            
            # Add to scored candidates
            scored_candidate = candidate.copy()
            scored_candidate['similarity_scores'] = similarity_scores
            scored_candidates.append(scored_candidate)
            
            # Detailed logging if enabled
            if self.enable_detailed_logging:
                logging.debug(f"\n[候选] {candidate_title} - {', '.join(candidate_artists)}")
                logging.debug(f"  标题相似度: {title_similarity:.2f}")
                logging.debug(f"  艺术家相似度: {artist_similarity:.2f}")
                logging.debug(f"  第一阶段得分: {score:.2f} {'(通过)' if score >= self.first_stage_threshold else '(未通过)'}")
        
        # Filter based on first stage threshold
        first_stage_matches = [c for c in scored_candidates if c['similarity_scores']['first_stage_score'] >= self.first_stage_threshold]
        
        # Sort by score
        first_stage_matches.sort(key=lambda c: c['similarity_scores']['first_stage_score'], reverse=True)
        
        logging.debug(f"\n第一阶段匹配结果: {len(first_stage_matches)}/{len(candidates)} 个候选通过阈值 {self.first_stage_threshold:.2f}")
        
        return first_stage_matches
        
    def second_stage_match(self, input_title: str, input_artists: List[str],
                          first_stage_matches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Execute second stage matching with bracket content awareness.
        
        Args:
            input_title: Input song title
            input_artists: Input artists list
            first_stage_matches: Candidates that passed first stage matching
            
        Returns:
            List of matched candidates that exceed the second stage threshold
        """
        if not first_stage_matches:
            return []
            
        logging.debug(f"\n=== 第二阶段匹配 - 括号内容处理 ===")
        
        # Process each first stage match
        second_stage_matches = []
        
        for candidate in first_stage_matches:
            # Extract data
            candidate_title = candidate.get('name', '')
            candidate_artists = [artist.get('name', '') for artist in candidate.get('artists', [])]
            first_stage_score = candidate['similarity_scores']['first_stage_score']
            
            # Calculate bracket score adjustment
            bracket_adjustment = self.bracket_matcher.calculate_bracket_adjustment(
                input_title, candidate_title, input_artists, candidate_artists
            )
            
            # Calculate final score
            final_score = first_stage_score + bracket_adjustment
            
            # Update similarity scores
            candidate['similarity_scores'].update({
                'bracket_adjustment': bracket_adjustment,
                'final_score': final_score,
                'is_low_confidence': final_score < self.second_stage_threshold
            })
            
            # Detailed logging if enabled
            if self.enable_detailed_logging:
                logging.debug(f"\n[候选] {candidate_title} - {', '.join(candidate_artists)}")
                logging.debug(f"  第一阶段得分: {first_stage_score:.2f}")
                logging.debug(f"  括号调整: {bracket_adjustment:+.2f}")
                logging.debug(f"  最终得分: {final_score:.2f} {'(通过)' if final_score >= self.second_stage_threshold else '(未通过)'}")
            
            # Add to second stage matches if it exceeds threshold
            if final_score >= self.second_stage_threshold:
                second_stage_matches.append(candidate)
        
        # Sort by final score
        second_stage_matches.sort(key=lambda c: c['similarity_scores']['final_score'], reverse=True)
        
        logging.debug(f"\n第二阶段匹配结果: {len(second_stage_matches)}/{len(first_stage_matches)} 个匹配")
        
        return second_stage_matches
        
    def get_best_match(self, input_title: str, input_artists: List[str],
                      candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get the best match from candidates.
        
        Args:
            input_title: Input song title
            input_artists: Input artists list
            candidates: List of candidate songs
            
        Returns:
            The best match or None if no match is found
        """
        matches = self.match(input_title, input_artists, candidates)
        return matches[0] if matches else None
        
    @property
    def original_input(self) -> Tuple[str, List[str]]:
        """
        Get the original input title and artists.
        
        Returns:
            Tuple of original title and artists
        """
        return self._original_input_title, self._original_input_artists
        
    def _log_detailed_match_info(self, input_title: str, input_artists: List[str], 
                               best_match: Dict[str, Any]) -> None:
        """
        Log detailed match information for the best match.
        
        Args:
            input_title: Input song title
            input_artists: Input artists list
            best_match: The best match
        """
        if not self.enable_detailed_logging:
            return
            
        scores = best_match['similarity_scores']
        match_title = best_match.get('name', 'Unknown')
        match_artists = [a.get('name', 'Unknown') for a in best_match.get('artists', [])]
        
        logging.debug("\n=== 最佳匹配详情 ===")
        logging.debug(f"[输入] 标题: '{input_title}'")
        if self._original_input_title != input_title:
            logging.debug(f"[输入] 原始标题: '{self._original_input_title}'")
            
        if input_artists:
            logging.debug(f"[输入] 艺术家: {input_artists}")
            if any(a != b for a, b in zip(self._original_input_artists, input_artists)):
                logging.debug(f"[输入] 原始艺术家: {self._original_input_artists}")
        
        logging.debug(f"[匹配] 标题: '{match_title}'")
        if 'original_name' in best_match:
            logging.debug(f"[匹配] 原始标题: '{best_match['original_name']}'")
            
        logging.debug(f"[匹配] 艺术家: {match_artists}")
        
        if 'original_artists' in best_match:
            orig_artists = [a.get('name', 'Unknown') for a in best_match['original_artists']]
            if any(a != b for a, b in zip(orig_artists, match_artists)):
                logging.debug(f"[匹配] 原始艺术家: {orig_artists}")
        
        logging.debug(f"[分数] 标题相似度: {scores.get('title_similarity', 0):.2f}")
        logging.debug(f"[分数] 艺术家相似度: {scores.get('artist_similarity', 0):.2f}")
        logging.debug(f"[分数] 第一阶段得分: {scores.get('first_stage_score', 0):.2f}")
        logging.debug(f"[分数] 括号调整: {scores.get('bracket_adjustment', 0):+.2f}")
        logging.debug(f"[分数] 最终得分: {scores.get('final_score', 0):.2f}")
        logging.debug(f"[分数] 低置信度: {scores.get('is_low_confidence', True)}")
        
def get_enhanced_match(input_title: str, input_artists: List[str], candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    使用增强匹配器获取最佳匹配结果
    
    Args:
        input_title: 输入歌曲标题
        input_artists: 输入歌曲艺术家列表
        candidates: 候选歌曲列表
        
    Returns:
        Dict[str, Any]: 最佳匹配结果，如果没有匹配则返回None
    """
    matcher = EnhancedMatcher()
    matches = matcher.match(input_title, input_artists, candidates)
    return matches[0] if matches else None 