# Spotify 歌单导入工具

一个 Python 命令行工具，用于将文本文件中的歌曲列表导入到您的 Spotify 账户中，并创建一个新的播放列表。

## 功能特性

- **批量导入歌曲**：从文本文件中批量导入歌曲列表
- **智能匹配**：使用多阶段匹配算法，提高歌曲标题和艺术家的匹配准确率
- **文本标准化**：自动处理中英文混排、简繁体转换、括号信息等
- **混合异步框架**：结合同步API调用和异步线程池，平衡代码简洁性和高性能
- **健壮的API调用**：对API错误进行分类处理，包括自动重试、指数退避和响应头解析
- **智能速率限制处理**：基于Retry-After响应头和指数退避的动态重试机制
- **精细并发控制**：通过Semaphore和配置化参数确保API调用平稳执行
- **详细日志**：提供可配置的日志级别，帮助调试和监控
- **高性能优化**：使用缓存、并发处理和智能匹配算法提升批处理性能达3倍以上
- **隐私保护**：不会长期存储用户信息，所有敏感信息通过环境变量管理

## 安装

```bash
# 从 PyPI 安装
pip install spotify-playlist-importer

# 或从源码安装
git clone https://github.com/yourusername/spotify-playlist-importer.git
cd spotify-playlist-importer
pip install -e .

# 安装依赖
pip install -r requirements.txt
```

## 配置

在使用之前，您需要设置Spotify API凭据。我们提供了多种配置方式：

### 1. 使用配置向导(推荐)

我们提供了一个交互式配置向导，帮助您轻松设置所需的环境变量：

```bash
python generate_env.py
```

该向导会引导您输入必要的信息，并生成一个`.env`文件。

### 2. 手动创建环境变量文件

在项目根目录创建 `.env` 文件，包含以下必要的环境变量：

```
# Spotify API 凭据
SPOTIPY_CLIENT_ID="YOUR_SPOTIFY_CLIENT_ID"
SPOTIPY_CLIENT_SECRET="YOUR_SPOTIFY_CLIENT_SECRET"
SPOTIPY_REDIRECT_URI="http://127.0.0.1:8888/callback"

# 前后端配置
FRONTEND_URL="http://localhost:3000"
ALLOWED_ORIGINS="http://localhost:3000,http://127.0.0.1:3000"

# API 服务器配置
API_HOST="0.0.0.0"
API_PORT=8888
API_DEBUG=false

# 令牌缓存配置
PROJECT_TOKEN_CACHE_PATH=".spotify_project_cache"
USER_TOKEN_CACHE_PATH=".spotify_cache"
USER_TOKEN_CACHE_DIR=".spotify_user_tokens"
```

### 3. 直接设置系统环境变量

您也可以直接在系统中设置所需的环境变量：

```bash
# Linux/macOS
export SPOTIPY_CLIENT_ID='your-spotify-client-id'
export SPOTIPY_CLIENT_SECRET='your-spotify-client-secret'
export SPOTIPY_REDIRECT_URI='http://127.0.0.1:8888/callback'
export FRONTEND_URL='http://localhost:3000'
export ALLOWED_ORIGINS='http://localhost:3000,http://127.0.0.1:3000'

# Windows PowerShell
$env:SPOTIPY_CLIENT_ID="your-spotify-client-id"
$env:SPOTIPY_CLIENT_SECRET="your-spotify-client-secret"
$env:SPOTIPY_REDIRECT_URI="http://127.0.0.1:8888/callback"
$env:FRONTEND_URL="http://localhost:3000"
$env:ALLOWED_ORIGINS="http://localhost:3000,http://127.0.0.1:3000"
```

### 4. JSON配置文件

除了环境变量外，部分非敏感配置(如匹配算法参数)也可通过JSON配置文件设置：

```bash
cp spotify_config.json.example spotify_config.json
# 然后编辑 spotify_config.json 文件
```

## 获取Spotify API凭据

1. 访问 [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/applications)
2. 创建一个新的应用
3. 在应用设置中添加重定向URI: `http://127.0.0.1:8888/callback`
4. 复制 Client ID 和 Client Secret
5. 将这些凭据添加到你的 `.env` 文件或系统环境变量中

## 使用方法

### 基本使用

```bash
# 测试Spotify认证流程（首次使用推荐）
spotify-playlist-importer auth

# 导入歌曲列表并创建播放列表
spotify-playlist-importer --file songs.txt --name "我的播放列表" --public

# 指定日志级别
spotify-playlist-importer --file songs.txt --name "我的播放列表" --log-level DEBUG

# 查看帮助
spotify-playlist-importer --help
```

### 启动API服务器

```bash
# 启动API服务器
python run_fixed_api.py
```

### 优化批量导入（推荐用于大型歌单）

```bash
# 使用优化的批处理模式导入
spotify-playlist-importer batch-import songs.txt --name "我的播放列表" --batch-size 100 --concurrency 15

# 指定自定义批处理参数
spotify-playlist-importer batch-import --file songs.txt --name "我的播放列表" --batch-size 50 --concurrency 10
```

### 歌曲列表格式

歌曲列表文件应包含每行一首歌曲，格式如下：

```
歌曲标题 - 艺术家
歌曲标题 - 艺术家1 / 艺术家2
歌曲标题
```

示例：

```
Bohemian Rhapsody - Queen
Shape of You - Ed Sheeran
Hotel California - Eagles
爱我别走 - 张震岳
```

## 高级选项

### 命令行参数

#### 标准导入命令 (`import`)

```
--file, -f         歌曲列表文件路径
--name, -n         创建的播放列表名称
--public, -p       是否创建公开播放列表（默认为私有）
--description, -d  播放列表描述
--log-level, -l    日志级别 (DEBUG, INFO, WARNING, ERROR)
--config, -c       配置文件路径
--concurrency      并发请求数量
```

#### 优化批量导入命令 (`batch-import`)

```
songs_file_path    歌曲列表文件路径
--playlist-name    创建的播放列表名称
--public           是否创建公开播放列表（默认为私有）
--description      播放列表描述
--output-report    匹配报告输出文件路径
--concurrency      API请求的最大并发数量（默认为10）
--batch-size       批处理大小，每次处理的歌曲数量（默认为50）
```

### 配置项

可在 `config.json` 中设置的高级选项：

```json
{
  "API_CONCURRENT_REQUESTS": 10,  // 并发API请求数量
  "API_RATE_LIMIT_RETRIES": 5,    // API速率限制重试次数
  "API_BASE_DELAY": 0.5,          // 初始重试延迟（秒）
  "API_MAX_DELAY": 10.0,          // 最大重试延迟（秒）
  "SPOTIFY_SEARCH_LIMIT": 5,      // 搜索结果数量限制
  "BATCH_SIZE": 50,               // 批处理大小
  "CONCURRENCY_LIMIT": 10,        // 整体并发限制
  "LOG_LEVEL": "INFO",            // 日志级别
  "TITLE_WEIGHT": 0.6,            // 标题匹配权重
  "ARTIST_WEIGHT": 0.4,           // 艺术家匹配权重
  "BRACKET_WEIGHT": 0.3,          // 括号内容匹配权重
  "MATCH_THRESHOLD": 75.0,        // 匹配阈值（满分100）
  "FIRST_STAGE_THRESHOLD": 60.0,  // 第一阶段匹配阈值
  "SECOND_STAGE_THRESHOLD": 70.0, // 第二阶段匹配阈值
  "CACHE_ENABLED": true,          // 是否启用缓存
  "CACHE_DIR": ".cache"           // 缓存目录
}
```

## 多阶段匹配算法详解

本工具采用先进的两阶段匹配算法，确保高准确率的歌曲匹配：

### 1. 文本预处理与归一化

在搜索和匹配前，系统对输入文本进行全面的标准化处理：

- **大小写统一**：将所有文本转换为小写
- **简繁体转换**：自动将繁体中文转换为简体中文
- **全/半角转换**：统一全角和半角字符
- **空白处理**：规范化空白字符，压缩多余空格
- **特殊模式处理**：识别并处理常见的模式，如 "feat."、"remix"、"live" 等

### 2. 第一阶段匹配（基础字符串匹配）

使用高效的字符串相似度算法计算歌曲标题和艺术家的匹配度：

- **标题相似度**：使用多种相似度算法（如比率、部分比率、令牌排序比率）计算标题相似度
- **艺术家相似度**：比较输入艺术家和候选艺术家列表，找到最佳匹配
- **加权评分**：根据配置的权重结合标题和艺术家相似度，计算综合得分
- **早期剪枝**：快速过滤明显不匹配的候选，提高性能

### 3. 第二阶段匹配（括号内容增强匹配）

专门处理歌曲标题中括号内的特殊信息，进一步提高匹配精度：

- **括号内容提取**：提取标题中的括号内容（如 "(Live)"、"[Remix]" 等）
- **关键词识别**：识别常见的特殊关键词，并根据其重要性分配权重
- **括号相似度计算**：比较输入和候选歌曲的括号内容相似度
- **评分调整**：根据括号内容匹配情况调整第一阶段的得分

### 4. 匹配决策

- **阶段性阈值**：使用两个独立阈值进行筛选，确保高质量匹配
- **最终排序**：根据最终得分对候选进行排序，选择最佳匹配
- **缓存机制**：缓存匹配结果，提高处理相似歌曲的效率

## 匹配参数调优指南

通过调整配置参数，您可以针对不同的音乐库和使用场景优化匹配效果：

### 一般场景优化

- **提高匹配率**：降低 `MATCH_THRESHOLD` 到 70.0，增加 `SPOTIFY_SEARCH_LIMIT` 到 8-10
- **提高精确度**：提高 `MATCH_THRESHOLD` 到 80.0，增加 `TITLE_WEIGHT` 到 0.7

### 特定音乐类型优化

1. **电子音乐/混音**
   - 降低 `SECOND_STAGE_THRESHOLD` 到 65.0，提高 `BRACKET_WEIGHT` 到 0.4
   - 这会增加对remix、club mix等版本信息的重视程度

2. **古典音乐**
   - 提高 `TITLE_WEIGHT` 到 0.8，降低 `ARTIST_WEIGHT` 到 0.2
   - 古典音乐中，作品名称更为关键，艺术家（演奏者）可能有多种变体

3. **中文/亚洲音乐**
   - 确保启用简繁体转换
   - 对于中文歌名，可考虑设置较宽松的第一阶段阈值（55.0-60.0）

4. **Live/现场专辑**
   - 提高 `BRACKET_WEIGHT` 到 0.4-0.5
   - 这有助于正确匹配包含"live"、"现场"等标记的歌曲

### 批量处理优化

对于大型歌单（500+首歌曲），建议使用以下设置：

```json
{
  "SPOTIFY_SEARCH_LIMIT": 5,  // 减少每首歌搜索结果数量，避免API限制
  "BATCH_SIZE": 50,           // 适中的批次大小，平衡内存使用和效率
  "CONCURRENCY_LIMIT": 8-12   // 根据网络环境调整，避免过多并发请求
}
```

### 内存和性能优化

- **内存受限环境**：减小 `BATCH_SIZE` 到 20-30，禁用或限制缓存大小
- **高性能环境**：增加 `BATCH_SIZE` 到 100-200，提高 `CONCURRENCY_LIMIT` 到 15-20
- **大型歌单处理**：启用增量处理模式，定期保存中间结果

## 性能优化功能

最新版本实现了一系列关键的性能优化，显著提高了歌曲匹配速度和批量处理效率：

### 主要优化策略

1. **文本标准化缓存**
   - 对标准化后的文本实施内存缓存，避免重复计算
   - 对于批量处理中的相似文本，减少高达87.9%的文本处理时间
   - 支持自定义缓存大小和生命周期控制

2. **优化字符串匹配算法**
   - 使用基于集合的艺术家相似度计算（提升45-65%性能）
   - 主要艺术家匹配加权策略，更符合实际使用场景
   - 相似度计算结果缓存，减少冗余计算

3. **高效候选筛选**
   - 两阶段筛选策略：快速预筛选 + 详细评分
   - 根据字符串长度差异等特征提前过滤明显不匹配的候选
   - 减少不必要的详细相似度计算，提高整体匹配速度

4. **并发批处理架构**
   - 支持多线程并行处理，提供3.35倍批处理性能提升
   - 可配置的线程池和并发参数，适应不同硬件环境
   - 线程安全的缓存和数据处理，确保结果准确性

### 性能提升数据

独立性能测试显示以下提升效果：

| 优化项目 | 原始性能 | 优化后性能 | 提升比例 |
|---------|---------|-----------|---------|
| 文本标准化处理 | 1.24毫秒/次 | 0.15毫秒/次 | 87.9% |
| 10个候选字符串匹配 | 0.061秒/首 | 0.027秒/首 | 55.7% |
| 100首歌曲批处理 | 23.5秒 | 7.0秒 | 70.2% |

### 优化使用指南

要充分利用这些性能优化，建议使用以下配置：

```json
{
  "CACHE_ENABLED": true,        // 启用文本和相似度缓存
  "BATCH_SIZE": 50-100,         // 根据可用内存选择合适的批次大小
  "CONCURRENCY_LIMIT": 8-16,    // 根据CPU核心数调整
  "TITLE_WEIGHT": 0.6-0.7,      // 标题匹配权重
  "ARTIST_WEIGHT": 0.3-0.4      // 艺术家匹配权重
}
```

对于大型歌单（1000+首歌曲），可以使用优化过的批处理命令：

```bash
spotify-playlist-importer batch-import songs.txt --name "大型歌单" --batch-size 100 --concurrency 16
```

### 优化技术文档

如需了解更多关于性能优化的技术细节，请参阅:

- [性能优化文档](docs/performance_optimization.md)：详细的优化策略和实现说明
- [优化字符串匹配器](optimized_string_matcher.py)：优化算法的实现代码
- [性能测试脚本](performance_optimization.py)：用于验证优化效果的测试代码

## 开发文档

详细的开发者文档位于 `docs/` 目录：

- [歌曲匹配算法详解](docs/matching_algorithm.md)
- [批量处理模块](docs/batch_processor.md)
- [性能优化详细文档](docs/performance_optimization.md)
- [性能优化工具使用指南](docs/performance_optimization_tool.md)
- [身份验证实现](docs/auth_implementation_summary.md)
- [令牌缓存测试](docs/token_cache_testing.md)

## 许可证

MIT

## 贡献

欢迎贡献代码！请查看 [贡献指南](CONTRIBUTING.md)。 