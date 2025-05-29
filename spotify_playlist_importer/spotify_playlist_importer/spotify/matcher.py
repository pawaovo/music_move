"""
Spotify歌曲匹配模块

提供歌曲匹配和处理相关的功能，用于在Spotify搜索结果中选择最佳匹配。
"""

import logging
import re
from typing import Dict, List, Optional, Any, Tuple

from spotify_playlist_importer.core.models import ParsedSong, MatchedSong
from spotify_playlist_importer.utils.enhanced_matcher import EnhancedMatcher, get_enhanced_match
from spotify_playlist_importer.utils.config_manager import get_all_config

# 配置日志
logger = logging.getLogger(__name__)

def build_search_query(parsed_song: ParsedSong) -> str:
    """
    构建Spotify搜索查询
    
    Args:
        parsed_song: 已解析的歌曲信息
        
    Returns:
        str: 搜索查询字符串
    """
    if not parsed_song.title:
        raise ValueError("无法从原始文本构建有效查询：缺少标题")
        
    # 使用标准化后的标题，确保已处理过括号等内容
    title = parsed_song.title
    
    # 如果仍有括号内容，进一步清理
    clean_title = re.sub(r'\([^)]*\)|\[[^\]]*\]|\{[^}]*\}', '', title).strip()
    
    # 记录标题转换过程
    logger.debug(
        f"标题标准化: 原标题='{parsed_song.original_line}', 标准化标题='{title}', 最终搜索标题='{clean_title}'")
    
    # 默认使用歌名+艺术家搜索
    if parsed_song.artists and len(parsed_song.artists) > 0:
        # 获取前两位艺术家（如果有）
        artists_to_use = parsed_song.artists[:min(2, len(parsed_song.artists))]
        artists_query = " ".join(
            f"artist:{artist}" for artist in artists_to_use)
        query = f"track:{clean_title} {artists_query}"
    else:
        # 仅歌名搜索
        query = f"track:{clean_title}"
    
    return query

def select_best_match(parsed_song: ParsedSong, candidates: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    从候选歌曲中选择最佳匹配
    
    使用增强匹配器评估每个候选歌曲，选择得分最高的作为最佳匹配。
    
    Args:
        parsed_song: 已解析的歌曲信息
        candidates: 候选歌曲列表
        
    Returns:
        Optional[Dict[str, Any]]: 最佳匹配的候选歌曲，如果没有符合条件的则返回None
    """
    if not candidates:
        return None
        
    # [诊断日志] 详细记录所有候选歌曲
    logger.info(
        f"===== 诊断信息：歌曲 '{parsed_song.original_line}' 的API候选列表 =====")
    for idx, candidate in enumerate(candidates):
        artists_str = ', '.join([artist['name']
                                for artist in candidate['artists']])
        logger.info(f"  候选[{idx+1}]: {candidate['name']} - {artists_str}")
    logger.info(f"===== API候选列表结束 =====")
    
    try:
        # 获取匹配配置
        config = get_all_config()
        title_weight = config.get("TITLE_WEIGHT", 0.6)
        artist_weight = config.get("ARTIST_WEIGHT", 0.4)
        bracket_weight = config.get("BRACKET_WEIGHT", 0.3)
        keyword_bonus = config.get("KEYWORD_BONUS", 5.0)
        match_threshold = config.get("MATCH_THRESHOLD", 75.0)
        bracket_threshold = config.get("BRACKET_THRESHOLD", 70.0)
        first_stage_threshold = config.get("FIRST_STAGE_THRESHOLD", 60.0)
        second_stage_threshold = config.get("SECOND_STAGE_THRESHOLD", 70.0)
        
        # 创建增强匹配器实例
        enhanced_matcher = EnhancedMatcher(
            title_weight=title_weight,
            artist_weight=artist_weight,
            bracket_weight=bracket_weight,
            keyword_bonus=keyword_bonus,
            string_threshold=match_threshold,
            bracket_threshold=bracket_threshold,
            first_stage_threshold=first_stage_threshold,
            second_stage_threshold=second_stage_threshold
        )
        
        # [诊断日志] 开启增强匹配器的详细日志模式
        enhanced_matcher.enable_detailed_logging = True
        enhanced_matcher.original_input = parsed_song.original_line
        
        # 执行两阶段匹配
        clean_title = re.sub(r'\([^)]*\)|\[[^\]]*\]|\{[^}]*\}', '', parsed_song.title).strip()
        matches = enhanced_matcher.match(
            input_title=clean_title,
            input_artists=parsed_song.artists,
            candidates=candidates
        )
        
        # 核对结果状态
        if not matches and len(candidates) > 0:
            # 如果没有匹配结果但有候选歌曲，使用第一阶段最高分或直接使用第一个候选
            logger.info(f"在候选结果中没有匹配分数超过阈值的歌曲，采用分数最高的候选")
            
            # 尝试使用第一阶段匹配获取最高分候选
            first_stage_matches = enhanced_matcher.first_stage_match(
                input_title=clean_title,
                input_artists=parsed_song.artists,
                candidates=candidates
            )
            
            if first_stage_matches:
                best_match = first_stage_matches[0]  # 分数最高的候选
            else:
                # 如果第一阶段也没有结果，直接使用第一个候选
                best_match = candidates[0]
            
            # 标记为低置信度匹配
            best_match['is_low_confidence'] = True
            
            # 获取匹配分数（如果有）
            similarity_scores = best_match.get('similarity_scores', {})
            title_score = similarity_scores.get('title_similarity', 0.0)
            artist_score = similarity_scores.get('artist_similarity', 0.0)
            final_score = similarity_scores.get('final_score', 0.0) or title_score
            
            # 将分数添加到匹配结果中
            best_match['similarity_scores'] = {
                'title_similarity': title_score,
                'artist_similarity': artist_score,
                'final_score': final_score
            }
            
            logger.debug(f"低置信度匹配 - 标题分数: {title_score:.2f}, " + 
                        f"艺术家分数: {artist_score:.2f}, " + 
                        f"最终分数: {final_score:.2f}")
                        
            return best_match
            
        elif matches:
            # 有匹配结果（通过两阶段匹配找到的）
            best_match = matches[0]
            
            # 记录匹配分数
            similarity_scores = best_match.get('similarity_scores', {})
            title_score = similarity_scores.get('title_similarity', 0.0)
            artist_score = similarity_scores.get('artist_similarity', 0.0)
            final_score = similarity_scores.get('final_score', 0.0)
            
            # 判断是否为低置信度匹配
            is_low_confidence = final_score < match_threshold
            best_match['is_low_confidence'] = is_low_confidence
            
            logger.debug(f"相似度匹配结果 - 标题分数: {title_score:.2f}, " + 
                        f"艺术家分数: {artist_score:.2f}, " + 
                        f"最终分数: {final_score:.2f}, " + 
                        f"低置信度: {is_low_confidence}")
                        
            return best_match
        else:
            # 没有候选歌曲
            return None
            
    except ImportError as ie:
        logger.warning(f"无法导入增强匹配器: {ie}，回退到直接使用第一个结果")
        # 回退到使用第一个结果
        best_match = candidates[0]
        
        # 标记为低置信度
        best_match['is_low_confidence'] = True
        best_match['similarity_scores'] = {
            'title_similarity': 50.0,
            'artist_similarity': 50.0,
            'final_score': 50.0
        }
        
        return best_match
    except Exception as e:
        logger.exception(f"匹配过程中出现未预期的错误: {e}")
        return None

def create_matched_song(track: Dict[str, Any], original_line: str) -> MatchedSong:
    """
    从Spotify搜索结果创建MatchedSong对象
    
    Args:
        track: Spotify搜索结果中的曲目信息
        original_line: 原始输入文本
        
    Returns:
        MatchedSong: 创建的匹配歌曲对象
    """
    # 提取匹配分数和低置信度标志
    similarity_scores = track.get('similarity_scores', {})
    final_score = similarity_scores.get('final_score', 50.0)
    is_low_confidence = track.get('is_low_confidence', final_score < 75.0)
    
    # 创建一个简化的ParsedSong对象
    artists_list = [artist['name'] for artist in track['artists']]
    parsed_song = ParsedSong(original_line=original_line, title=track['name'], artists=artists_list)
    
    # 提取专辑图片URL
    album_image_urls = None
    if 'album' in track and 'images' in track['album'] and track['album']['images']:
        album_image_urls = [image['url'] for image in track['album']['images']]
    
    # 创建MatchedSong对象
    return MatchedSong(
        parsed_song=parsed_song,
        spotify_id=track['id'],
        name=track['name'],
        uri=track['uri'],
        artists=[artist['name'] for artist in track['artists']],
        album_name=track['album']['name'] if 'album' in track else None,
        album_image_urls=album_image_urls,  # 设置专辑图片URL列表
        duration_ms=track.get('duration_ms', 0),
        is_low_confidence=is_low_confidence,
        matched_score=final_score,
        original_line=original_line  # 保留original_line参数以兼容修改后的MatchedSong类
    ) 