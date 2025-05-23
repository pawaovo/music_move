# Spotify 歌曲匹配算法开发者文档

## 1. 算法概述

Spotify 歌曲匹配算法是一个两阶段的混合匹配系统，专为解决在线音乐匹配中的复杂场景设计。该算法通过综合文本标准化、字符串相似度计算和特殊信息提取等技术，实现高精度的歌曲匹配。

匹配流程主要分为以下几个步骤：

1. **文本预处理与归一化**：处理输入歌曲标题和艺术家，规范化文本格式
2. **API 查询构建**：基于归一化文本构建最优搜索查询
3. **第一阶段匹配**：基本字符串相似度匹配
4. **第二阶段匹配**：考虑括号内容及特殊信息的增强匹配
5. **最终匹配决策**：综合评分和阈值筛选

## 2. 核心组件

### 2.1 文本归一化器 (TextNormalizer)

负责文本预处理和标准化，支持多种文本处理功能。

**核心功能**：
- 中文简繁体转换
- 英文大小写统一
- 全角/半角字符转换
- 空白字符标准化
- 特殊模式处理（如 live、remix、feat 等）

**使用示例**：

```python
from spotify_playlist_importer.utils.text_normalizer import normalize_text

# 基本使用
normalized_text = normalize_text("Bohemian Rhapsody (Live)")
# 结果: "bohemian rhapsody"

# 带特定选项的使用
normalized_text = normalize_text(
    "Shape Of You (feat. Stormzy) [Remix]",
    remove_patterns=["feat", "remix"]
)
# 结果: "shape of you"

# 替换而非移除模式
normalized_text = normalize_text(
    "Hotel California (Live Version)",
    replacements={"live": "现场版"}
)
# 结果: "hotel california 现场版"
```

### 2.2 字符串匹配器 (StringMatcher)

实现基本的字符串相似度匹配，主要用于第一阶段匹配。

**核心功能**：
- 标题相似度计算
- 艺术家列表相似度计算
- 加权综合评分
- 早期剪枝优化

**使用示例**：

```python
from spotify_playlist_importer.utils.string_matcher import StringMatcher

# 创建匹配器实例
matcher = StringMatcher(
    title_weight=0.6,    # 标题权重
    artist_weight=0.4,   # 艺术家权重
    threshold=75.0,      # 匹配阈值 (0-100)
    top_k=3              # 返回前K个结果
)

# 进行匹配
matches = matcher.match(
    input_title="Bohemian Rhapsody",
    input_artists=["Queen"],
    candidates=spotify_search_results  # API搜索结果
)

# 获取最佳匹配
best_match = matches[0] if matches else None
```

### 2.3 括号匹配器 (BracketMatcher)

专门处理歌曲标题中括号内的特殊信息，用于第二阶段匹配。

**核心功能**：
- 括号内容提取
- 特殊关键词识别
- 括号内容相似度计算
- 基于括号内容的评分调整

**使用示例**：

```python
from spotify_playlist_importer.utils.bracket_matcher import BracketMatcher

# 创建匹配器实例
bracket_matcher = BracketMatcher(
    bracket_weight=0.3,      # 括号内容权重
    keyword_bonus=5.0,       # 关键词匹配加分
    threshold=70.0           # 括号内容匹配阈值
)

# 调整基础分数
base_score = 80.0  # 第一阶段得分
final_score = bracket_matcher.match(
    input_title="Shape of You (Acoustic)",
    candidate_title="Shape of You (Acoustic Version)",
    base_score=base_score
)
# final_score 会根据括号内容匹配情况调整
```

### 2.4 增强匹配器 (EnhancedMatcher)

集成字符串匹配和括号匹配，实现完整的两阶段匹配流程。

**核心功能**：
- 两阶段匹配流程编排
- 缓存机制
- 候选筛选
- 最终匹配决策

**使用示例**：

```python
from spotify_playlist_importer.utils.enhanced_matcher import EnhancedMatcher

# 创建增强匹配器
matcher = EnhancedMatcher(
    # 字符串匹配配置
    title_weight=0.6,
    artist_weight=0.4,
    string_threshold=75.0,
    top_k=3,
    # 括号匹配配置
    bracket_weight=0.3,
    keyword_bonus=5.0,
    bracket_threshold=70.0,
    # 两阶段阈值配置
    first_stage_threshold=60.0,
    second_stage_threshold=70.0
)

# 进行增强匹配
matches = matcher.match(
    input_title="Shape of You (Remix)",
    input_artists=["Ed Sheeran"],
    candidates=spotify_search_results
)

# 获取最佳匹配
best_match = matcher.get_best_match(
    input_title="Shape of You (Remix)",
    input_artists=["Ed Sheeran"],
    candidates=spotify_search_results
)
```

## 3. 配置参数详解

匹配算法的行为可通过配置参数进行调整。以下是关键配置参数及其作用：

| 参数名称 | 说明 | 默认值 | 推荐范围 |
|---------|------|-------|---------|
| `TITLE_WEIGHT` | 标题在匹配中的权重 | 0.6 | 0.5-0.7 |
| `ARTIST_WEIGHT` | 艺术家在匹配中的权重 | 0.4 | 0.3-0.5 |
| `MATCH_THRESHOLD` | 匹配阈值（满分100） | 75.0 | 70.0-80.0 |
| `SPOTIFY_SEARCH_LIMIT` | 每次搜索获取的结果数量 | 5 | 5-10 |
| `BRACKET_WEIGHT` | 括号内容在评分中的权重 | 0.3 | 0.2-0.4 |
| `FIRST_STAGE_THRESHOLD` | 第一阶段匹配阈值 | 60.0 | 50.0-70.0 |
| `SECOND_STAGE_THRESHOLD` | 第二阶段匹配阈值 | 70.0 | 65.0-80.0 |

## 4. 性能优化

匹配算法经过多项性能优化，以提高处理大型歌单的效率：

### 4.1 缓存机制

- **文本归一化缓存**：避免对相同文本的重复归一化
- **匹配结果缓存**：在处理相似歌曲时重用之前的匹配结果

### 4.2 早期剪枝

在进行详细相似度计算前，快速过滤掉明显不匹配的候选：
- 标题长度差异过大的过滤掉
- 艺术家完全不相关的过滤掉

### 4.3 正则表达式优化

使用预编译正则表达式处理括号内容，提高提取效率。

### 4.4 并行处理

通过多线程批量处理多首歌曲，充分利用系统资源。

## 5. 使用场景与最佳实践

### 5.1 基本使用场景

对于简单的匹配需求（少量歌曲，标准格式），可使用以下配置：

```python
from spotify_playlist_importer.utils.enhanced_matcher import get_best_enhanced_match

best_match = get_best_enhanced_match(
    input_title="Bohemian Rhapsody",
    input_artists=["Queen"],
    candidates=spotify_search_results
)
```

### 5.2 高精度匹配场景

对于需要高精度的场景，推荐调整以下参数：

```python
from spotify_playlist_importer.utils.enhanced_matcher import EnhancedMatcher

matcher = EnhancedMatcher(
    title_weight=0.7,               # 增加标题权重
    artist_weight=0.3,              # 减少艺术家权重
    string_threshold=80.0,          # 提高字符串匹配阈值
    second_stage_threshold=75.0     # 提高第二阶段阈值
)
```

### 5.3 批量处理场景

对于大型歌单（数百或数千首歌曲），推荐使用批处理模式：

```python
from spotify_playlist_importer.spotify.client import batch_search_songs_on_spotify

# 批量搜索匹配
matched_songs = batch_search_songs_on_spotify(
    sp=spotify_client,
    parsed_songs=song_list,
    batch_size=50  # 批次大小
)
```

### 5.4 匹配调优建议

- 对于电子音乐等remix版本较多的场景，可降低 `SECOND_STAGE_THRESHOLD` 以提高匹配率
- 对于古典音乐等曲目相似的场景，可提高 `TITLE_WEIGHT` 和阈值以减少误匹配
- 对于中文歌曲，启用简繁体转换可提高匹配率
- 对于特殊形式的歌曲（如现场版、翻唱版等），确保括号匹配的权重合理

## 6. 未来工作

匹配算法可能的改进方向：

- 集成机器学习技术，自动调整匹配参数
- 利用歌曲持续时间信息提高匹配准确性
- 添加更多特殊类型的检测（如"翻唱"、"混音"等中文形式）
- 实现基于流派的匹配策略调整
- 进一步优化批处理性能，支持更大规模的歌单处理 