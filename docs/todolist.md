# Spotify Playlist Importer - Upgrade Todolist

Based on `docs/project_upgrade_plan.md` (Version 1.2)

## I. 高优先级（基础与效率）

### 1.1 API 速率限制处理与并发执行框架 (同步API + 线程)
- [x] **1.1.1: 搭建同步API调用与并发执行环境:**
    - [x] 使用 `spotipy` (同步库) 进行核心Spotify API调用。
    - [x] 将 `spotipy` 的同步调用通过 `asyncio.to_thread` 在主异步框架的线程池中执行，以实现并发处理歌曲搜索等IO密集型任务。
- [x] **1.1.2: 实现并发控制:**
    - [x] 添加可配置的并发数量限制（例如，通过配置文件设置，用于控制并发线程数）。
    - [x] 使用 `asyncio.Semaphore` （或类似机制）管理提交到线程池的任务数量，确保并发行为符合预期且可控。
    - [x] (可选高级) 研究线程池大小与 `Semaphore` 限制的协同工作，优化资源利用。
- [x] **1.1.3: 实现健壮的API速率限制处理逻辑 (例如429错误):**
    - [x] 深入理解并验证 `spotipy` 库内置的错误处理和重试机制。
    - [x] 在API调用封装层面（如 `search_song_on_spotify_sync_wrapped`）添加更精细的异常捕获，以应对 `spotipy` 未处理或处理不充分的特定API错误。
    - [x] 如 `spotipy` 的默认处理不足，考虑实现基于 `Retry-After` 响应头（如果可获取）的等待或指数退避策略的封装层。
    - [x] 设置可配置的最大重试次数（如果实现自定义重试）。
- [x] **1.1.4: API模块的单元与集成测试:**
    - [x] Mock `spotipy` 的响应，测试错误处理、重试逻辑（自定义或 `spotipy` 内置的）。
    - [x] 在模拟负载下测试并发控制和线程池表现。

### 1.2 增强日志系统
- [x] **1.2.1: 集成 Python `logging` 模块:**
    - [x] 确保项目中所有错误/状态报告均通过 `logging` 调用。
- [x] **1.2.2: 配置日志级别:**
    - [x] 允许通过配置文件或环境变量设置日志级别 (DEBUG, INFO, WARNING, ERROR)。
- [x] **1.2.3: 实现详细的调试日志:**
    - [x] 为匹配过程的关键步骤（包括预处理、各阶段相似度计算、得分、决策过程）添加DEBUG级别的详细日志。

## II. 中高优先级（核心准确率提升）

### 2.1 文本预处理与归一化模块
- [x] **2.1.1: 实现核心的文本归一化功能:**
    - [x] 实现中文简繁体统一功能 (例如，使用 `opencc-python-reimplemented`)。
    - [x] 实现英文字母大小写统一功能 (转为小写)。
    - [x] 实现全角/半角字符统一功能。
- [x] **2.1.2: 实现特定模式的去除/替换:**
    - [x] 设计并实现一个可配置的机制（例如，通过JSON/YAML文件）来管理用于去除/替换的正则表达式或关键词列表 (例如 `(live)`, `[remastered]`, `(feat. ...)` 等)。
    - [x] 实现应用这些模式的逻辑。
- [x] **2.1.3: 实现空白字符与分隔符的标准化:**
    - [x] 标准化处理连字符 `-`、斜杠 `/`、与号 `&` 等。
    - [x] 去除首尾多余空格，并将连续的多个内部空格压缩为单个。
- [x] **2.1.4: 创建统一的归一化工具函数:**
    - [x] 将所有归一化步骤封装成一个易于调用的函数/类。
- [x] **2.1.5: 归一化模块的单元测试:**
    - [x] 针对每个归一化步骤编写测试用例，覆盖不同类型的输入。
    - [x] 测试统一的归一化工具函数/类。

### 2.2 歌曲搜索查询增强与候选获取
- [x] **2.2.1: 优化Spotify API搜索参数:**
    - [x] 将 `sp.search()` 调用中的 `limit` 参数设为动态可配置（例如通过配置文件，建议默认值为5-10），以获取足够的候选歌曲进行后续匹配。
- [x] **2.2.2: 增强查询构建逻辑:**
    - [x] 确保构建搜索查询字符串的逻辑能有效利用标准化后的歌曲标题和所有艺术家信息。
    - [x] (可选) 尝试不同的查询组合策略（例如，仅标题，标题+主艺术家，标题+所有艺术家）以应对不同情况。

### 2.3 实现第一阶段的基于字符串相似度的匹配 (核心匹配逻辑 - 忽略括号信息)
- [x] **2.3.1: 集成字符串相似度库:**
    - [x] 将选定的库 (如 `thefuzz` (fuzzywuzzy的新版) 或 `textdistance`) 添加到项目依赖中。
- [x] **2.3.2: 实现标题相似度评分:**
    - [x] 对每个从Spotify API获取的候选歌曲，计算其归一化标题与输入歌曲归一化标题之间的相似度得分（例如使用 `thefuzz.ratio` 或 `token_set_ratio`）。
- [x] **2.3.3: 实现艺术家列表相似度评分:**
    - [x] 对每个候选歌曲，计算其归一化艺术家列表与输入歌曲归一化艺术家列表之间的相似度得分（可考虑Jaccard相似度、平均最佳匹配、或将艺术家列表视为一个整体字符串用 `thefuzz` 计算）。
- [x] **2.3.4: 实现第一阶段的加权评分与候选筛选:**
    - [x] 使用可配置的权重 (`Wt_title`, `Wa_artist`) 组合标题相似度得分和艺术家相似度得分，得到第一阶段的综合评分 `score_stage1`。
    - [x] 应用可配置的初步阈值 (`T_stage1_min_score`) 过滤掉明显不相关的候选歌曲。
    - [x] (可选) 从通过初步阈值的候选中，选出得分最高的Top K个（例如K=3-5）进入下一阶段精细匹配，或全部进入。
- [x] **2.3.5: 第一阶段匹配的日志记录:**
    - [x] 添加DEBUG级别的日志，详细记录：输入歌曲信息、每个候选歌曲的原始信息、归一化后的文本、标题相似度、艺术家相似度、以及计算出的 `score_stage1`。

## III. 中优先级（精细化准确率）

### 3.1 实现第二阶段的匹配逻辑 (处理括号内特殊信息)
- [x] **3.1.1: 提取与归一化括号内/特殊标记信息:**
    - [x] 实现从用户输入歌曲名和候选歌曲名中提取括号内文本（如 `(Live)`, `(Remix)`, `(Acoustic)`）以及其他特殊标记（如 `feat.`, `- Version`）的逻辑。
    - [x] 对提取出的这些信息应用适当的（可能更宽松或特定的）归一化规则。
- [x] **3.1.2: 实现括号内/特殊标记信息的比较与评分调整:**
    - [x] **关键词匹配**: 检查提取信息中是否包含特定关键词 (如 "live", "acoustic", "remix", "instrumental", "cover", "demo" 等)。
    - [x] **特征匹配**: 比较 `feat.` 后面的艺术家是否与输入或候选中的艺术家有重合。
    - [x] **相似度计算**: 如果括号内容较长，可计算用户输入与候选歌曲括号内信息的文本相似度。
    - [x] **调整分数**: 根据上述比较结果，对第一阶段的 `score_stage1` 进行加分或减分调整。例如：
        - 输入含 `(Live)`，候选也含 `(Live)` -> 加分
        - 输入无 `(Live)`，候选含 `(Live)` -> 减分（或可配置为不减分，视策略而定）
        - 匹配到 `feat.` 艺术家 -> 加分
- [x] **3.1.3: 计算最终匹配得分与选择最佳匹配:**
    - [x] 得到调整后的最终匹配得分 `final_score`。
    - [x] 应用可配置的最终阈值 (`T_final_min_score`) 于 `final_score`。
    - [x] 从所有通过最终阈值的候选中，选择 `final_score` 最高的作为最佳匹配。如果最高分相同，可有其他决胜规则（如更短的标题、发布日期等，此为高级优化）。
- [x] **3.1.4: 第二阶段匹配的日志记录:**
    - [x] 添加DEBUG级别的日志，记录提取的括号/特殊信息、比较过程、分数调整细节及计算出的 `final_score`。

## IV. 持续进行

- [x] **4.1 配置文件管理:**
    - [x] 确保所有可配置参数（并发数、API凭据相关路径、归一化模式、相似度算法选择、各阶段匹配的权重和阈值、`limit` 参数等）都从统一的配置文件 (如YAML, JSON) 或环境变量加载。
    - [x] 提供一个包含所有可配置项及其默认值的示例配置文件。
- [x] **4.2 单元测试与集成测试 (持续进行):**
    - [x] 为所有新增或修改的函数和模块（特别是匹配算法的各个阶段）编写全面的单元测试。
    - [x] 开发针对端到端匹配流程的集成测试，使用多样化的输入数据。
    - [x] (推荐) 创建并维护一个"黄金标准数据集"，包含已知匹配和不匹配的歌曲对，用于回归测试和准确率评估。
- [x] **4.3 性能分析与优化:**
    - [x] 在实现新的匹配算法后，使用大型输入列表对应用进行性能分析。
    - [x] 识别并解决文本处理、相似度计算或并发执行中的性能瓶颈。
- [x] **4.4 文档更新:**
    - [x] 更新 `README.md`，详细说明新的匹配逻辑、所有可配置参数及其作用、以及如何优化匹配效果。
    - [x] 为新增的内部模块和复杂匹配逻辑撰写必要的开发者文档或代码注释。

## V. 优化与重构 (可选)

### 5.1 共享Spotify客户端实例
- [x] **5.1.1: 设计并实现Spotify客户端实例的共享机制:**
    - [x] 目标：避免在每次API调用时都创建新的 `spotipy.Spotify` 实例，以减少不必要的认证开销和潜在的性能瓶颈。
    - [x] 考虑方案：
        - 方案A: 在应用启动时初始化一个全局的 `spotipy.Spotify` 实例，并在需要时传递或引用它。
        - 方案B: 使用一个单例模式或工厂模式来管理和提供 `spotipy.Spotify` 实例。
    - [x] 确保所选方案的线程安全性，特别是在并发环境中（如 `main_async.py` 中的异步调用）。
- [x] **5.1.2: 更新现有代码以使用共享实例:**
    - [x] 修改 `spotify_playlist_importer/spotify/client.py` 中的 `search_song_on_spotify` 函数，使其接收或获取共享的 `spotipy` 客户端实例。
    - [x] 修改 `spotify_playlist_importer/main_async.py` 中的 `search_song_on_spotify_sync_wrapped` 函数，确保它通过 `asyncio.to_thread` 传递或使用了共享的客户端实例。
    - [x] 检查并更新其他可能直接或间接创建 `spotipy.Spotify` 实例的地方。
- [x] **5.1.3: 测试共享实例的有效性和稳定性:**
    - [x] 验证API调用是否仍然按预期工作。
    - [x] 在并发场景下测试，确保没有因实例共享引入新的问题（如状态冲突、认证失败等）。
    - [x] (可选) 比较共享实例前后在大量API调用时的性能差异。

## VI. 进一步优化匹配逻辑与报告 (Stage 6)

### 6.1 文本预处理与归一化模块 (`text_normalizer.py`)
- [x] **6.1.1: 调整归一化策略以保留括号内容:**
    - [x] 修改 `normalize_text` (或创建新变体) 以在主归一化过程中保留原始括号及其内部文本。例如，`Song Title (feat. Artist X) [Live]` 归一化后应大致为 `song title (feat. artist x) [live]`。
    - [x] 新增一个辅助函数，能够将归一化后的字符串分割成"主要部分"和"括号内含/特殊标记部分"。例如，`song title (feat. artist x) [live]` -> `("song title", ["(feat. artist x)", "[live]"])`。

### 6.2 歌曲搜索查询 (`client.py`)
- [x] **6.2.1: 优化Spotify API搜索查询构建:**
    - [x] 查询时使用歌曲的"主要部分"（即不含括号内文本）。
    - [x] 查询时默认仅使用输入的前两位艺术家（如果艺术家信息可用）。如果只有一位艺术家，则使用该艺术家。如果没有艺术家信息，则仅按主要标题搜索。
- [x] **6.2.2: 配置搜索结果数量:**
    - [x] 将 `SPOTIFY_SEARCH_LIMIT` 的默认值调整为3（通过 `spotify_config.json` 或环境变量配置）。

### 6.3 候选歌曲处理 (`client.py`)
- [x] **6.3.1: 归一化API返回的候选歌曲:**
    - [x] 对从Spotify API获取的每个候选歌曲的标题和艺术家进行与6.1.1中用户输入相似的归一化处理，保留其括号内容。
    - [x] 对每个归一化后的候选歌曲，也使用6.1.1中的辅助函数分割出"主要部分"和"括号内含/特殊标记部分"。

### 6.4 核心匹配逻辑 (`StringMatcher` 或相关部分在 `client.py`)
- [x] **6.4.1: 实现主要信息匹配:**
    - [x] 比较用户输入歌曲的"主要标题"与候选歌曲的"主要标题"的相似度。
    - [x] 比较用户输入歌曲的 *完整* 艺术家列表与候选歌曲的 *完整* 艺术家列表的相似度。
    - [x] 使用可配置的权重 (`TITLE_WEIGHT`, `ARTIST_WEIGHT`) 组合这两个相似度得分，得到主要匹配分数。
- [x] **6.4.2: 实现括号内/特殊标记信息的补充匹配:**
    - [x] 比较用户输入歌曲的"括号内含/特殊标记部分"列表与候选歌曲的相应列表。
    - [x] 这部分的比较可以更灵活，例如：
        - 检查关键词完全匹配 (e.g., `(live)` vs `(live)`)。
        - 检查是否存在 `feat.` 艺术家的重合。
        - 计算括号内文本的整体相似度。
    - [x] 根据匹配程度，对此主要匹配分数进行调整（例如，通过一个较低权重的 `BRACKET_WEIGHT` 或 `KEYWORD_BONUS`）。
- [x] **6.4.3: 计算最终匹配得分:**
    - [x] 结合主要匹配分数和补充匹配的调整，得到最终匹配得分。

### 6.5 低置信度匹配处理 (`client.py`)
- [x] **6.5.1: 实现低置信度回退逻辑:**
    - [x] 如果所有候选歌曲的最终匹配得分均未达到配置的 `MATCH_THRESHOLD`。
    - [x] 选择其中得分最高的那个候选歌曲作为匹配结果。
    - [x] 在匹配结果对象 (e.g., `MatchedSong`) 中增加一个标志，表明这是一个"低置信度匹配"。

### 6.6 报告生成 (例如在 `main_async.py` 或处理报告的模块)
- [x] **6.6.1: 调整报告格式:**
    - [x] 原始输入歌曲信息显示为单行: `Original Input: <完整原始歌曲字符串>`
    - [x] 匹配到的歌曲信息显示为单行: `Matched Song: <匹配到的歌曲标题 - 艺术家1, 艺术家2 ...>`
    - [x] 如果未找到匹配，则显示: `Matched Song: Not Found`
    - [x] 如果是低置信度匹配，在匹配结果后附加标记: `Matched Song: <匹配到的歌曲标题 - 艺术家1, 艺术家2 ...> [Low Confidence]`
- [x] **6.6.2: 在报告中明确标识低置信度匹配。**

### 6.7 配置参数调整 (`config_manager.py`, `spotify_config.json`)
- [x] **6.7.1: 更新默认配置:**
    - [x] 将 `SPOTIFY_SEARCH_LIMIT` 的默认值设为3。
- [x] **6.7.2: 审阅并调整权重和阈值:**
    - [x] 根据新的两阶段匹配逻辑（主要信息匹配 + 括号信息补充），重新评估并调整 `TITLE_WEIGHT`, `ARTIST_WEIGHT`, `BRACKET_WEIGHT` (或新引入的类似权重), `KEYWORD_BONUS` 以及 `MATCH_THRESHOLD` 的默认值。
    - [x] 确保这些参数在 `spotify_config.json.example` 中有清晰的文档说明。

## VII. 最大化API调用成功率以确保获取候选歌曲 (Stage 7)

**核心前提**: 假定一个功能正常的Spotify API在接收到有效的歌曲查询时，总会返回候选歌曲。因此，本阶段专注于通过极度稳健的API交互策略，确保最大限度地从Spotify获取这些候选数据。

**目标**: 实施一套极其稳健的API请求和重试机制，以确保对每首输入歌曲的Spotify查询都能成功执行并获取候选列表（无论候选内容多少或质量高低），随后由现有的匹配逻辑从中选择一个最终匹配。

### 7.1 极端API调用稳健性与高级重试策略 (`spotify/async_client.py` 或同步客户端的等效部分)

-   [x] **7.1.1: 实现高度持久化且智能的API请求重试机制:**
    -   [x] 在核心API请求函数（例如，封装 `spotipy` 调用的 `make_request`）中：
        -   [x] **自动重试的触发条件**: 针对特定的、通常被认为是瞬态的HTTP错误码（例如，`429 Too Many Requests`，`500 Internal Server Error`，`502 Bad Gateway`，`503 Service Unavailable`）以及常见的网络级错误（如请求超时、DNS解析失败、连接错误）进行自动重试。
        -   [x] **重试参数配置**:
            -   实现可配置的**最大重试次数** (`API_MAX_RETRIES`)，默认值设为一个较高的数字（例如 **10到15次**），以应对持续的瞬时网络波动或API繁忙。
            -   实现可配置的**基础重试延迟时间** (`API_RETRY_BASE_DELAY_SECONDS`)，默认值适当增加（例如 **3到5秒**）。
            -   采用**带抖动的指数退避 (Exponential Backoff with Jitter)** 策略计算每次重试的延迟时间，例如：`delay = min(API_RETRY_MAX_DELAY_SECONDS, API_RETRY_BASE_DELAY_SECONDS * (2 ** retry_count) * (0.5 + random.uniform(0, 1)))`。
            -   实现可配置的**最大重试总时长** (`API_TOTAL_TIMEOUT_PER_CALL_SECONDS`)，确保即使一个单一API调用（包括其所有重试）也不会无限期阻塞整个处理流程。

-   [x] **7.1.2: 加强日志和监控:**
    -   [x] 详细记录每次重试的原因、尝试次数、等待时间等，以便诊断和解决持续失败的原因。
    -   [x] 记录单个请求（包括其所有重试）的总处理时间，帮助识别潜在的性能瓶颈。

-   [x] **7.1.3: 改进报告处理:**
    -   [x] 在匹配报告中单独标记API彻底失败（所有重试后仍然失败）的情况，与未找到匹配进行区分。
    -   [x] 提供详细的API错误上下文，帮助用户理解API交互失败的原因。

### 7.2 处理最终无法恢复的API调用失败 (在所有重试之后)

-   [x] **7.2.1: 定义并处理API调用在极致努力后仍失败的场景:**
    -   [x] 如果一个对Spotify的API调用（例如 `search` 请求），在执行了7.1.1中定义的所有重试尝试、并可能已达到 `API_TOTAL_TIMEOUT_PER_CALL_SECONDS` 后，**仍然未能成功获取HTTP 2xx响应**（即，API通信层面持续失败）：
        -   负责获取候选歌曲的函数（如 `search_song_on_spotify_async`）应明确地将此情况报告为**该特定查询的API交互彻底失败**。
        -   在这种情况下，该函数应返回 `None` (或一个清晰指示API失败的特殊错误对象/元组) 给调用者，表示未能从Spotify获取任何数据（包括空的候选列表）。
        -   **关键点**: 这被视为程序无法与Spotify就该查询成功通信，而不是Spotify对一个成功的查询返回了"无候选"。

### 7.3 对匹配流程和报告的影响

-   [x] **7.3.1: 确保匹配逻辑仅在获取到API候选时执行:**
    -   [x] 只有当 `search_song_on_spotify_async` (或其同步版本) 成功地从Spotify API返回了一个（可能为空，但通常按您的前提是非空的）候选歌曲列表时，才会调用 `BracketAwareMatcher`。
    -   [x] 如果API调用最终成功并返回了候选歌曲（哪怕只有一个，质量再差），`BracketAwareMatcher` 现有的逻辑会从中选择一个。`MatchedSong.is_low_confidence` 和 `final_score` 会如实反映其匹配质量。

-   [x] **7.3.2: 报告中清晰区分不同结果:**
    -   [x] **成功获取候选并匹配**:
        -   若 `MatchedSong.is_low_confidence` 为 `True` (即 `final_score < MATCH_THRESHOLD`):
            `Matched Song: <Spotify歌曲名> - <Spotify艺术家> [Low Confidence - Score: <final_score>]`
        -   否则 (高置信度匹配):
            `Matched Song: <Spotify歌曲名> - <Spotify艺术家>`
    -   [x] **API调用在所有重试后最终失败 (来自7.2.1)**:
        -   报告为: `Match Status: API Call Failed for Input "<原始输入行>" - Reason: <具体的API错误信息或超时说明>`
        -   在最终的统计摘要中，这类情况应归类为 "API交互失败" 或 "处理错误"，不计入"未找到歌曲"（因为我们未能成功查询）。

### 7.4 配置参数更新 (`spotify_config.json`, `utils/config_manager.py`)

-   [x] **7.4.1: 新增或调整配置文件中的API重试参数:**
    -   [x] `API_MAX_RETRIES` (整数, 例如默认 12)
    -   [x] `API_RETRY_BASE_DELAY_SECONDS` (浮点数, 例如默认 3.0)
    -   [x] `API_RETRY_MAX_DELAY_SECONDS` (浮点数, 例如默认 60.0) (用于限制单次指数退避的最大延迟)
    -   [x] `API_TOTAL_TIMEOUT_PER_CALL_SECONDS` (整数, 例如默认 100) (单次API调用含所有重试的总时长上限)
    -   [x] 确保 `spotify_config.json.example` 文件和相关文档（如 `project_workflow.md` 或 `README.md`）清晰地解释这些参数及其默认值和影响。
    -   [x] `ConfigManager` 需要能正确加载和提供这些新的配置值。

### 7.5 强化测试

-   [x] **7.5.1: 针对API重试机制的专项单元测试:**
    -   [x] Mock Spotify API的响应，精确模拟各种需要重试的错误场景（429, 500, 502, 503, 网络超时等）。
    -   [x] 验证在不同错误序列下，重试次数、延迟计算（包括指数退避和抖动）、最大延迟上限和总超时是否符合预期。
    -   [x] 验证日志记录是否准确反映了重试过程。
    -   [x] 测试在达到最大重试次数或总超时后，API调用是否正确报告为最终失败。
-   [x] **7.5.2: 端到端集成测试下的表现评估:**
    -   [x] （如果可行）在可控环境中模拟API间歇性故障，观察整体流程是否能通过重试恢复。
    -   [x] 验证当某个歌曲的API查询在所有重试后仍失败时，报告是否准确反映为"API调用失败"，并且不影响其他歌曲的处理。
    -   [x] 确认当API调用（可能在重试后）成功返回候选时，即使候选质量差，匹配器也能选出一个，并在报告中以低置信度标记。
    -   [x] 评估启用这种强力重试策略后，对处理包含少量"问题API调用"的歌曲列表时的总处理时间影响。

## VIII. 进一步优化搜索与匹配逻辑 (Stage 8)

**核心目标**: 在现有成熟工作流程的基础上，通过采用单一高效的自由文本曲目名搜索策略，结合强化的多维度匹配评分系统，并重点优化对Spotify API返回结果中中文内容变体的处理，以提升匹配精准度和对中文歌曲的处理能力。

### 8.1 搜索策略调整 (`spotify/async_client.py` 或调用处)
-   [ ] **8.1.1: 切换到单一自由文本曲目名搜索:**
    -   [ ] 修改API查询构建逻辑，主要使用用户输入的原始歌曲标题（或初步清理后的标题）进行自由文本搜索。
    -   [ ] 移除或注释掉现有的多阶段降级搜索逻辑，除非评估后认为有必要保留可选的、基于艺术家提示的补充自由文本搜索作为极低置信度下的最终手段。

### 8.2 智能匹配评分与选择逻辑增强 (`utils/enhanced_matcher.py` 或新模块)
-   [x] **8.2.1: 重构或扩展 `select_best_match` (或等效) 函数:**
          -   [x] **核心评分因素实现**:
          -   [x] **标题相似度**: 实现基于 `fuzzywuzzy.fuzz.token_set_ratio` 或 `partial_ratio` 的标题相似度计算，并在计算前对输入和候选标题进行标准化和简体中文统一化。
          -   [x] **艺术家相似度**: 实现艺术家列表间的相似度计算。对每个输入艺术家，在候选艺术家列表中找最佳匹配。重点处理Spotify返回的中文名（简繁统一）和可能的拼音形式（与输入艺术家名的拼音形式对比）。
          -   [x] **括号内容相似度**: 复用或增强现有 `BracketMatcher` 逻辑，比较括号内容，并对关键词和 `feat.` 艺术家进行处理（艺术家名处理同上）。
      -   [x] **综合评分与选择**:
          -   [x] 实现基于上述三个核心因素的加权综合评分机制。
          -   [x] 确保权重 (`W_title`, `W_artist`, `W_bracket`) 可通过配置文件调整。
          -   [x] 应用 `MATCH_THRESHOLD` 和 `LOW_CONFIDENCE_THRESHOLD` 判断最终匹配状态。

### 8.3 中文内容处理优化 (集成到匹配评分逻辑中)
-   [x] **8.3.1: 文本预处理统一化:**
    -   [x] 确保在所有相似度计算前，对输入文本和从Spotify获取的候选文本都执行统一预处理：转小写、全角转半角、移除干扰标点、**统一到简体中文 (使用 `opencc-python-reimplemented`)**。
-   [x] **8.3.2: 艺术家名称匹配鲁棒性提升:**
    -   [x] **拼音处理集成**: 在艺术家相似度计算中，当直接中文名比较效果不佳时，尝试将输入的中文艺术家名转为拼音 (使用 `pypinyin`)
### 8.4 配置与日志调整
-   [x] **8.4.1: 配置文件更新 (`spotify_config.json`):**
    -   [x] 审阅并调整匹配评分权重 (`W_title`, `W_artist`, `W_bracket`) 和相关阈值的默认值。
    -   [x] 确保新增或修改的配置项在 `spotify_config.json.example` 中有清晰说明。
-   [x] **8.4.2: 日志记录增强:**
    -   [x] 记录采用的自由文本查询语句。
    -   [x] 详细记录每个主要候选歌曲的标题、艺术家、括号各项相似度得分及最终综合得分。
    -   [x] 在日志中高亮或明确指出中文简繁转换和拼音匹配步骤的执行情况。

### 8.5 测试与验证
-   [x] **8.5.1: 扩展测试用例:**
    -   [x] 针对新的匹配逻辑和中文处理机制，设计更多包含复杂中文歌名、艺术家名（含多音字、简繁、拼音变体）的测试用例。
-   [x] **8.5.2: 性能和准确率评估:**
    -   [x] 在标准测试集上评估新方案的匹配准确率和处理性能，与旧方案进行对比。
    -   [x] 重点分析先前匹配失败或匹配错误的中文歌曲案例，验证改进效果。 

    ## IX. 优化搜索策略以提高匹配召回率 (Stage 9)

**核心目标**: 实施一个多阶段的搜索策略，优先使用最精确的信息组合（歌名+艺术家），并在必要时逐步回退到更宽松的搜索条件，以最大限度地确保从Spotify API获取候选歌曲。对于通过仅艺术家名搜索到的歌曲，将其标记为低置信度。

### 9.1 搜索逻辑调整 (`spotify/sync_client.py` 中的 `_search_with_sync_client` 或等效函数)
-   [ ] **9.1.1: 实现多阶段搜索查询逻辑:**
    -   [ ] **阶段一 (主要搜索 - 歌名 + 前两位艺术家):**
        -   [ ] 从 `parsed_song_info` 获取标准化后的歌曲标题和艺术家列表。
        -   [ ] 如果艺术家列表不为空，提取前两位艺术家（如果只有一位则取一位）。
        -   [ ] 构建查询: `track:{标准化歌名} artist:{第一位艺术家} artist:{第二位艺术家}` (或仅一位艺术家)。
        -   [ ] 执行Spotify API搜索。如果返回结果，则使用这些结果进行后续匹配，并跳过后续搜索阶段。
    -   [ ] **阶段二 (第一次备用搜索 - 仅歌名):**
        -   [ ] 如果阶段一未返回结果（或最初就没有艺术家信息），构建查询: `track:{标准化歌名}`。
        -   [ ] 执行Spotify API搜索。如果返回结果，则使用这些结果进行后续匹配，并跳过后续搜索阶段。
    -   [ ] **阶段三 (第二次备用搜索 - 仅前两位艺术家):**
        -   [ ] 如果阶段二仍未返回结果（且最初有艺术家信息），构建查询: `artist:{第一位艺术家} artist:{第二位艺术家}` (或仅一位艺术家)。
        -   [ ] 执行Spotify API搜索。
-   [ ] **9.1.2: 处理艺术家搜索结果的特殊标记:**
    -   [ ] 如果搜索最终通过阶段三（仅艺术家名）获得了候选歌曲：
        -   [ ] 在传递给匹配器之前或在匹配器内部，将这些候选歌曲的潜在匹配分数强制设置为0。
        -   [ ] 确保匹配结果（如 `MatchedSong` 对象）被明确标记为低置信度 (例如，设置 `is_low_confidence = True` 并记录 `matched_score = 0.0`)，无论后续的字符串相似度匹配结果如何。
-   [ ] **9.1.3: 整合和返回搜索结果:**
    -   [ ] 无论哪个阶段成功获取了候选歌曲，都将这些结果返回给调用者（例如 `search_song_on_spotify_sync_wrapped`）。
    -   [ ] 如果所有阶段都未能获取结果，则返回空列表或适当的无结果指示。

### 9.2 日志记录增强
-   [ ] **9.2.1: 记录采用的搜索阶段和查询:**
    -   [ ] 在日志中明确指出当前歌曲是使用了哪个搜索阶段（歌名+艺术家, 仅歌名, 仅艺术家）以及具体的查询字符串。
-   [ ] **9.2.2: 记录艺术家搜索的特殊处理:**
    -   [ ] 如果匹配结果来源于仅艺术家名的搜索，在日志中高亮或明确指出其匹配分数被置为0且标记为低置信度。

### 9.3 配置参数 (可选，如果需要调整行为)
-   [ ] **9.3.1: 审阅是否需要为新策略添加配置:**
    -   [ ] 例如，是否允许禁用某个搜索阶段，或调整艺术家数量。目前看，按固定逻辑即可。

### 9.4 测试与验证
-   [ ] **9.4.1: 针对新搜索策略设计测试用例:**
    -   [ ] 包含仅能通过歌名匹配的歌曲。
    -   [ ] 包含仅能通过艺术家名匹配的歌曲。
    -   [ ] 包含能通过歌名+艺术家名精确匹配的歌曲。
    -   [ ] 包含即使通过所有阶段也无法找到任何候选的歌曲。
-   [ ] **9.4.2: 验证低置信度标记:**
    -   [ ] 确保通过仅艺术家名搜索匹配到的歌曲，在报告中正确显示为低置信度且分数为0。
-   [ ] **9.4.3: 回归测试:**
    -   [ ] 确保新的搜索策略没有对先前能够正确匹配的歌曲产生负面影响。

## X. 优化匹配器评分逻辑以提高准确性 (Stage 10)

**核心目标**: 改进 `EnhancedMatcher` (或 `BracketAwareMatcher`) 内部的评分逻辑，以更准确地处理因文本归一化（如简繁体差异）和括号内特殊标记（如 `(Live)`, `(Remix)`）导致的不完全匹配，从而提升整体匹配准确率，减少误判为0分或低分的情况。

**背景**: 当前匹配逻辑可能因对文本差异过于敏感，导致实际上匹配度很高的歌曲（例如仅简繁体不同，或一方多出 `(Live)` 标签）被评为0分或不合理低分。

### 10.1 文本归一化增强 (`utils/text_normalizer.py`)
-   [ ] **10.1.1: 确保 `normalize_text` 函数包含全面的归一化步骤:**
    -   [ ] **强制简体中文转换**: 确保所有参与比较的文本（输入、候选标题、艺术家、括号内容）统一转换为简体中文。使用 `opencc-python-reimplemented`。
    -   [ ] **大小写统一**: 转换为小写。
    -   [ ] **全角/半角统一**: 统一为半角。
    -   [ ] **移除或替换特定不影响语义的标点符号**: 定义一个可配置的标点符号处理规则。
    -   [ ] **处理多余空格**: 清理首尾空格，压缩连续空格。
-   [ ] **10.1.2: 审阅并确保归一化函数在匹配流程的关键节点被调用:**
    -   [ ] 在 `EnhancedMatcher` 或其依赖组件（`StringMatcher`, `BracketMatcher`）中，所有从输入和候选歌曲中提取的待比较文本片段，在送入相似度算法前，必须先调用此增强的归一化函数。

### 10.2 相似度算法与评分逻辑优化 (`utils/enhanced_matcher.py`, `utils/string_matcher.py`, `utils/bracket_matcher.py`)
-   [x] **10.2.1: 标题与艺术家名称相似度计算优化:**
    -   [x] **采用 `fuzzywuzzy.fuzz.token_set_ratio`**: 对于标题和艺术家列表的相似度计算，优先使用或确保使用的是 `token_set_ratio`。此算法对词序不敏感，且能更好地处理部分词语重叠及额外词语的情况。
    -   [x] **组件路径**: 主要关注 `EnhancedMatcher` (或 `BracketAwareMatcher`) 内的 `_calculate_main_title_similarity`, `_calculate_artists_similarity` (或 `StringMatcher` 内的等效方法)。
-   [x] **10.2.2: `BracketMatcher` 逻辑优化 (`utils/bracket_matcher.py`):**
    -   [x] **提取与归一化**: 确保从输入和候选标题中提取的括号内容，在比较前也经过10.1中定义的全面归一化处理。
    -   [x] **相似度计算**: 对比归一化后的括号内容时，可使用 `token_set_ratio` 或针对短语特点的其他模糊匹配方法。
    -   [x] **智能评分调整策略**: 
        -   **完全匹配/高度相似的括号内容**: 如双方都有 `(live)` 或 `(remix)`，则应给予显著加分（通过 `keyword_bonus` 或基于相似度得分调整）。
        -   **一方有括号内容，另一方没有** (例如，输入为 "歌名 (Live)"，候选为 "歌名"):
            -   **主要策略**: **不应直接判为0分或大幅扣分**。可以考虑不加分，或仅轻微调整分数（加分或减分，幅度可配置）。目标是识别出核心歌名匹配，并将括号内容视为一个次要区分特征。
            -   如果缺失的括号内容是重要区分性信息（如不同版本的 `remix` vs `acoustic`），则差异性应体现在最终得分上，但不至于直接导致0分（除非核心歌名也完全不匹配）。
        -   **双方都有括号内容但不匹配** (例如 "歌名 (Live)" vs "歌名 (Radio Edit)"):
            -   这种情况应根据括号内容的语义差异和相似度来调整分数，差异越大，负向调整或正向加分越少。
    -   [x] **feat. 艺术家处理**: 在比较括号内容时，特别关注 `(feat. ArtistX)` 这类信息。如果一方有而另一方没有，或 `feat.` 的艺术家不同，这通常是较强的差异信号，评分调整应能反映这一点。
-   [x] **10.2.3: 综合评分权重与阈值审阅:**
    -   [x] 在上述归一化和相似度算法调整后，重新评估 `EnhancedMatcher` 中的权重配置 (`TITLE_WEIGHT`, `ARTIST_WEIGHT`, `BRACKET_WEIGHT`, `KEYWORD_BONUS`) 和阈值 (`MATCH_THRESHOLD`, `LOW_CONFIDENCE_THRESHOLD`, `FIRST_STAGE_THRESHOLD`, `SECOND_STAGE_THRESHOLD`)。
    -   [x] 目标是让真正的匹配（即使有简繁、括号标签差异）能够获得合理的高分，而明显错误的匹配得分较低。

### 10.3 日志与调试增强
-   [x] **10.3.1: 详细记录归一化与评分过程:**
    -   [x] 在匹配相关的类的DEBUG日志中，清晰记录以下信息：
        -   原始输入文本片段。
        -   归一化后的文本片段。
        -   各部分（标题、艺术家、括号）计算出的具体相似度得分。
        -   评分调整的步骤和原因（例如，因括号内容匹配/不匹配而进行的加分/减分）。
        -   最终的综合得分。
    -   [x] 这有助于调试评分逻辑，并理解为何某些匹配得到特定分数。

### 10.4 测试与验证
-   [x] **10.4.1: 扩展测试用例集:**
    -   [x] 补充更多针对简繁体差异、不同括号内容（`Live`, `Remix`, `Acoustic`, `feat.` 等）、有无括号内容等情况的测试用例。
    -   [x] 包含正例（应高分匹配）和反例（应低分或不匹配）。
-   [x] **10.4.2: 回归测试与性能评估:**
    -   [x] 确保新的评分逻辑没有对原先能够正确高分匹配的简单案例产生负面影响。
    -   [x] 评估修改对整体匹配性能（准确率、召回率、处理时间）的影响。

## XI. 匹配评分逻辑优化 (Stage 11 - 聚焦评分阶段)

**核心前提**: API搜索返回候选数据的三个阶段逻辑（歌名+艺术家，仅歌名，仅艺术家）**保持不变**。所有优化都发生在获取到这些候选歌曲信息之后，在进行匹配评分的环节。

### 11.1 评分前置：统一文本标准化
-   [x] **11.1.1: 标准化输入歌曲信息:**
    -   [x] 在 `EnhancedMatcher` 内部，对用户输入的原始歌曲标题和艺术家列表，使用 `TextNormalizer` 进行一次全面的标准化（强制简体、大小写、全半角、标点、空格、括号格式）。
-   [x] **11.1.2: 标准化候选歌曲信息:**
    -   [x] 对从API返回的每一首候选歌曲，将其标题、艺术家列表也通过同一个 `TextNormalizer` 实例进行标准化。
-   [x] **11.1.3: 确保标准化覆盖所有比较文本:**
    -   [x] 验证括号内的文本在提取后也经过了同样的标准化流程。

### 11.2 标题相似度计算优化
-   [x ] **11.2.1: 使用标准化文本进行比较:**
    -   [x ] 确保标题相似度计算逻辑（如 `_calculate_title_similarity`）直接使用11.1中标准化的输入标题和候选标题。
    -   [ x] 核心相似度算法（如 `fuzzywuzzy.fuzz.token_set_ratio`）及权重保持不变。

### 11.3 艺术家相似度计算优化 (考虑拼音)
-   [x ] **11.3.1: 使用标准化艺术家列表:**
    -   [ x] 确保艺术家相似度计算逻辑（如 `_calculate_artists_similarity`）使用11.1中标准化的艺术家列表。
-   [x ] **11.3.2: 实现主要艺术家匹配保障:**
    -   [ x] 如果标准化后的输入主要艺术家完全存在于标准化后的候选艺术家列表中，则设定一个较高的基础艺术家得分（例如，保证至少80-85分）。
-   [x ] **11.3.3: 实现补充拼音比较逻辑:**
    -   [ x] 若初步基于文本的艺术家相似度较低（如低于60分）：
        -   [ x] 尝试将标准化的中文艺术家名转换为标准拼音。
        -   [ x] 尝试将候选的艺术家名（若为中文则转拼音，若像拼音则直接使用）与输入的拼音进行比较。
        -   [ x] 若拼音比较高度相似，则显著提升该候选的艺术家得分。
    -   [ x] 核心相似度算法及权重保持不变。

### 11.4 括号内内容匹配优化
- [x] **11.4.1: 使用标准化括号内容:**
    - [x] 确保从标准化标题中提取的括号内容，在比较前再次确认其自身的标准化。
- [x] **11.4.2: 优化常见别名指示词处理:**
    - [x] 对于如"(又名：...)"、"(aka...)"等模式，标准化处理后提取核心内容进行比较。
    - [x] 核心相似度算法及权重保持不变。

### 11.5 最终匹配分数计算与低分处理优化
-   [x] **11.5.1: 维持现有加权综合评分方式:**
    -   [x] 继续使用现有的 `TITLE_WEIGHT`, `ARTIST_WEIGHT`, `BRACKET_WEIGHT` 组合各部分得分。
-   [x] **11.5.2: 优化 `is_artist_only_search` 时的分数处理:**
    -   [x] 即使是仅艺术家搜索的候选，也应采用 `EnhancedMatcher` 计算的实际内容匹配分数。
    -   [ x] `is_low_confidence` 标志可保留，但不应强制将高实际匹配分覆盖为固定低分（如50分）。
-   [ x] **11.5.3: 优化 `final_score <= 5.0` (或极低分) 时的回退逻辑:**
    -   [ x] 如果某单项（如标准化后标题完全匹配，得100分）得分很高，即使总分因其他项过低而极低，最终分数也不应是固定的50分。
    -   [ x] 考虑动态下限，例如：如果标准化标题100%匹配，则最终分数不应低于一个特定值（例如70分），除非艺术家完全不相关。或者 `max(一个基础值, 0.6 * 最高单项分)`。
    -   [ x] 目标是减少不合理的硬编码低分，使分数更真实反映部分高质量匹配。

### 11.6 测试与验证
-   [ x] **11.6.1: 针对性设计测试用例:**
    -   [ x] 包含简繁体差异、拼音艺术家名、额外艺术家、不同括号格式等场景。
    -   [ x] 验证先前报告的低分问题（如"三十岁的女人 - 赵雷"，"给你呀 - 蒋小呢"）是否得到改善。
-   [ x] **11.6.2: 回归测试:**
    -   [ x] 确保优化没有对原先能够正确高分匹配的简单案例产生负面影响。
-   [ x] **11.6.3: 性能评估:**
    -   [ x] 确认上述调整未显著降低匹配流程的整体性能。

## XII. 前后端联调架构设计与实现 (Stage 12)

**核心目标**: 通过设计与实现一个高效的API中间层，将现有的Python后端Spotify歌曲搜索与匹配功能与Next.js前端页面进行整合，实现完整的歌曲导入与播放列表创建用户体验流程。

### 12.1 后端API设计与实现 (FastAPI)
- [ ] **12.1.1: 搭建FastAPI基础框架:**
    - [ ] 创建新的API模块，如 `api_server.py` 或 `api/` 目录结构。
    - [ ] 集成依赖项：FastAPI, Pydantic, uvicorn, CORS中间件。
    - [ ] 实现基础API服务器配置，包括CORS策略和错误处理。
- [ ] **12.1.2: 实现歌曲处理API端点:**
    - [ ] 创建 `POST /api/process-songs` 端点，接收歌曲列表文本。
    - [ ] 实现解析输入文本，调用现有的 `process_song_list_file` 和 `search_song_on_spotify` 函数处理歌曲。
    - [ ] 设计响应模型，包含总数、匹配歌曲、未匹配歌曲及其详细信息。
    - [ ] 实现异常处理与日志记录。
- [ ] **12.1.3: 实现播放列表创建API端点:**
    - [ ] 创建 `POST /api/create-playlist-and-add-songs` 端点，接收播放列表名称、描述、公开状态和歌曲URI列表。
    - [ ] 调用现有的 `create_spotify_playlist` 和 `add_tracks_to_spotify_playlist` 函数。
    - [ ] 设计响应模型，包含成功状态、播放列表ID和URL等信息。
- [x] **12.1.4: Spotify认证流程管理:**
    - [x] 设计API服务的Spotify认证策略，考虑：
        - [x] 实现基于现有授权流程的简化版，支持API服务器后台维护有效Token。
        - [x] 添加认证状态检查端点 `GET /api/auth-status`。
        - [x] 实现 `GET /api/auth-callback` 处理Spotify OAuth回调。
    - [x] 实现Token刷新机制，确保长时间运行时的有效性。

### 12.2 前端改造 (Next.js)
- [x] **12.2.1: 创建API服务层:**
    - [x] 在 `lib` 或新建 `services` 目录下创建 `api.ts` 文件。
    - [x] 实现 `processSongs` 函数，调用后端 `/api/process-songs` 端点。
    - [x] 实现 `createPlaylistAndAddSongs` 函数，调用后端 `/api/create-playlist-and-add-songs` 端点。
    - [x] 实现 `checkAuthStatus` 函数，调用后端 `/api/auth-status` 端点.
- [x] **12.2.2: 首页组件改造:**
    - [x] 将静态 HTML 转换为 React 受控组件，添加状态管理。
    - [x] 实现歌曲文本输入表单和验证逻辑。
    - [x] 将"转换歌曲列表"按钮的点击事件绑定到 `processSongs` API调用。
    - [x] 实现加载状态和错误提示UI组件。
    - [x] 成功后将数据传递到概要页面（使用状态管理或URL参数）。
- [x] **12.2.3: 概要页组件改造:**
    - [x] 实现接收和展示从首页传递的歌曲匹配信息。
    - [x] 添加显示匹配成功和失败歌曲的UI组件。
    - [x] 优化"开始转移"按钮，点击时收集播放列表信息，调用 `createPlaylistAndAddSongs`。
    - [x] 实现API调用过程中的加载状态和错误处理。
- [x] **12.2.4: 编辑页和完成页组件改造:**
    - [x] 根据流程需要，调整这些页面的逻辑和数据流。
    - [x] 编辑页：实现播放列表名称、描述等信息的表单。
    - [x] 完成页：展示从API返回的播放列表创建结果和链接。

### 12.3 状态管理与错误处理
- [x] **12.3.1: 实现前端状态管理:**
    - [x] 使用 React Context API 或轻量级状态管理库 (如 Zustand) 管理歌曲列表和匹配结果。
    - [x] 实现页面间数据传递的状态持久化（或通过URL参数）。
- [x] **12.3.2: 全面的错误处理:**
    - [x] 后端：实现结构化的错误响应格式，包含错误代码和详细信息。
    - [x] 前端：使用 Toast 组件展示API错误信息，提供用户友好的错误提示。
    - [x] 对常见错误场景（认证失败、API限流等）提供专门的处理逻辑。

### 12.4 部署与环境配置
- [x] **12.4.1: 环境变量配置:**
    - [x] 后端：整合现有配置系统，支持通过环境变量设置API服务器参数。
    - [x] 前端：在配置文件中设置 `API_BASE_URL` 等必要的环境变量。
- [x] **12.4.2: 启动脚本与文档:**
    - [x] 创建启动脚本，支持同时启动API服务器和Next.js开发服务器。
    - [x] 编写README，详细说明如何设置、启动和使用整合后的系统。

### 12.5 测试与验证
- [ x] **12.5.1: API端点测试:**
    - [ x] 编写单元测试，验证API端点的输入验证、处理逻辑和错误处理。
    - [ x] 使用 Postman 或类似工具创建API测试用例集。
- [ x] **12.5.2: 前后端集成测试:**
    - [ x] 设计端到端测试场景，验证从输入歌曲列表到创建播放列表的完整流程。
    - [ x] 测试不同的错误和边缘情况，确保系统的健壮性。
- [ x] **12.5.3: 性能评估:**
    - [ x] 对API服务进行负载测试，评估并发处理能力。
    - [ x] 优化响应时间和资源使用，特别是对于大量歌曲的处理。

## 阶段 13: 前端完整交互逻辑实现

### A. 前端状态管理方案

*   **选型**: 推荐使用 **Zustand** (或 Jotai/Valtio) 作为主要状态管理工具。
*   **配合**: 可选使用 `nuqs` 管理URL中的步骤状态。
*   **管理内容**:
    *   用户输入的原始歌曲列表。
    *   API调用加载状态 (`isLoading`, `error`)。
    *   `processSongs` API返回的匹配结果。
    *   用户在摘要页的歌曲选择。
    *   新播放列表的名称、描述、公开状态。
    *   `createPlaylistAndAddSongs` API的加载状态和结果。
    *   Spotify认证状态 (`isAuthenticated`, `userInfo`)。

### B. 页面与流程详细规划

#### B.0. 全局认证检查
*   **触发**: 应用加载时或关键操作前。
*   **API**: `checkAuthStatus`, `getAuthUrl`.
*   **UI**:
    *   未认证: 显示登录/授权按钮 -> Spotify授权页。
    *   已认证: 显示用户信息或允许操作。
    *   处理Spotify认证回调。
*   **状态**: `isAuthenticated`, `userInfo`.

#### B.1. 页面: 输入歌曲列表 (`/` 或 `/input`)
*   **目标**: 用户输入歌曲，调用API匹配。
*   **UI组件**:
    *   `<textarea>` (Shadcn UI Textarea) 用于歌曲输入。
    *   "转换歌曲列表"按钮 (Shadcn UI Button)。
*   **状态 (Zustand)**:
    *   `rawSongList`: string
    *   `isProcessingSongs`: boolean
    *   `processSongsError`: string | null
    *   `matchedSongsData`: ProcessSongsData | null
*   **逻辑**:
    1.  用户输入 -> 更新 `rawSongList`.
    2.  点击按钮:
        *   验证输入非空。
        *   设置加载状态 (`isProcessingSongs = true`).
        *   调用 `processSongs` API.
        *   成功: 存 `matchedSongsData`, `isProcessingSongs = false`, 导航到 `/summary`.
        *   失败: 存 `processSongsError`, `isProcessingSongs = false`, 显示错误.

#### B.2. 页面: 概要与编辑 (`/summary`)
*   **目标**: 展示匹配结果，用户编辑选择，输入新播放列表详情。
*   **UI组件**:
    *   统计信息 (总数、匹配数、未匹配数)。
    *   匹配歌曲列表 (Shadcn UI Table or Cards) 带复选框 (Shadcn UI Checkbox)。
    *   输入框: "播放列表名称" (Shadcn UI Input).
    *   文本区域: "播放列表描述" (Shadcn UI Textarea).
    *   切换开关: "是否公开" (Shadcn UI Switch).
    *   "创建播放列表"按钮.
*   **状态 (Zustand)**:
    *   `matchedSongsData` (来自上一步).
    *   `selectedSongUris`: string[] (用户选择的URI).
    *   `newPlaylistName`: string.
    *   `newPlaylistDescription`: string.
    *   `isPlaylistPublic`: boolean.
    *   `isCreatingPlaylist`: boolean.
    *   `createPlaylistError`: string | null.
    *   `createdPlaylistData`: CreatePlaylistData | null.
*   **逻辑**:
    1.  加载 `matchedSongsData`, 初始化 `selectedSongUris`.
    2.  用户编辑选择 -> 更新 `selectedSongUris`.
    3.  用户输入播放列表详情 -> 更新对应状态.
    4.  点击按钮:
        *   验证输入 (`newPlaylistName`, `selectedSongUris` 非空).
        *   设置加载状态 (`isCreatingPlaylist = true`).
        *   调用 `createPlaylistAndAddSongs` API.
        *   成功: 存 `createdPlaylistData`, `isCreatingPlaylist = false`, 导航到 `/completed`.
        *   失败: 存 `createPlaylistError`, `isCreatingPlaylist = false`, 显示错误.

#### B.3. 页面: 完成 (`/completed`)
*   **目标**: 显示成功信息和播放列表链接。
*   **UI组件**:
    *   成功提示信息。
    *   链接到Spotify播放列表 (使用 `createdPlaylistData.playlist_url`).
    *   "创建另一个播放列表"按钮.
*   **状态 (Zustand)**:
    *   `createdPlaylistData` (来自上一步).
*   **逻辑**:
    1.  加载 `createdPlaylistData`, 显示信息.
    2.  点击"创建另一个": 重置相关Zustand状态, 导航到 `/` 或 `/input`.

## 阶段 14: 前后端API联调与授权流程优化

**核心目标**: 解决当前前后端连接问题，并根据用户反馈优化Spotify授权流程，明确区分项目API凭证和用户授权令牌的使用。

### 14.1 后端API与连接问题修复
- [x] **14.1.1: 仔细检查并修复CORS配置:**
    - [x] 确保FastAPI后端已正确配置CORS中间件，允许来自前端Next.js应用源的请求。
    - [x] 验证允许的HTTP方法 (`GET`, `POST`, `OPTIONS`等) 和头部信息。
- [x] **14.1.2: 调查并解决后端日志中的重定向问题:**
    - [x] 分析FastAPI和uvicorn日志，确定是什么原因导致了重定向 (如果问题持续存在)。
    - [x] 确保所有API端点（尤其是认证回调 `/api/auth-callback`）能正确处理各种情况下的请求，避免不必要的重定向。
- [x] **14.1.3: 统一并验证URL配置的灵活性与正确性:**
    - [x] 确保前后端所有相关URL（API基地址、回调地址）通过环境变量进行配置，而不是硬编码。
    - [x] 开发环境下，验证这些环境变量配置（例如，前端指向 `http://localhost:8888`，Spotify回调指向 `http://localhost:3000/callback` 或相应的后端回调）能使本地联调正常工作。
    - [x] 规划生产环境的URL配置策略，确保部署时可以方便地将这些URL指向实际的服务器地址和域名。

### 14.2 Spotify授权流程优化与API调用分离
- [x] **14.2.1: 后端调整 - 用户授权与项目凭证分离:**
    - [x] **认证状态接口 (`/api/auth-status`):**
        - [x] 修改此接口，使其不仅返回用户是否通过本应用授权Spotify (`isAuthenticated`, `userInfo`)，还应尝试检测用户在浏览器中是否已登录Spotify主站（这可能需要前端辅助或不同的策略）。
        - [x] 如果可能，区分"用户已登录Spotify但未授权本应用"和"用户未登录Spotify"。
    - [x] **获取授权URL接口 (`/api/auth-url`):**
        - [x] 确保此接口生成的Spotify授权URL包含所有必要的`scope`，以支持后续代表用户创建播放列表和添加歌曲 (如 `playlist-modify-public`, `playlist-modify-private`等)。
    - [x] **歌曲处理接口 (`/api/process-songs`):**
        - [x] **重要**: 此接口的Spotify API调用（搜索歌曲）**必须**使用项目自身配置的Spotify API凭证（Client ID & Secret, 通过服务器到服务器的认证流程获取访问令牌），**而不是**用户的授权令牌。这意味着后端需要一套独立的机制来管理和刷新项目自身的Spotify访问令牌。
    - [x] **播放列表创建接口 (`/api/create-playlist` 或 `/api/create-playlist-and-add-songs`):**
        - [x] 此接口的Spotify API调用（创建播放列表、添加歌曲）**必须**使用用户通过前端OAuth流程授予的访问令牌。
        - [x] 后端需要能够安全地接收、存储（例如在session或安全cookie中）和使用这个用户特定的令牌。
- [x] **14.2.2: 前端调整 - 适配新的授权流程:**
    - [x] **`AuthCheck.tsx` 组件 (或等效全局认证逻辑):**
        - [x] 调用新的 `/api/auth-status`，根据返回结果处理UI：
            -   如果用户未登录Spotify：提示用户登录Spotify，然后引导授权本应用。
            -   如果用户已登录Spotify但未授权本应用：直接引导授权本应用。
            -   如果用户已授权本应用：显示用户信息。
        - [x] 授权按钮点击后，从 `/api/auth-url` 获取Spotify授权链接并引导用户跳转。
        - [x] 正确处理Spotify通过 `/callback` (前端Next.js路由) -> `/api/auth-callback` (后端API) 返回的授权码或错误。
    - [x] **歌曲搜索流程:**
        - [x] 用户在前端输入歌曲列表并点击"转换"后，前端调用后端的 `/api/process-songs`。此过程**不应**依赖用户是否已登录或授权Spotify，因为后端会使用项目凭证进行搜索。
    - [x] **播放列表创建流程:**
        - [x] 当用户在摘要页确认要创建播放列表时，前端**必须**确保用户已通过本应用授权Spotify。如果未授权，应先引导用户完成授权。
        - [x] 调用 `/api/create-playlist` 时，后端会使用先前存储的用户授权令牌。
- [x] **14.2.3: 后端Token管理:**
    - [x] 实现一个健壮的机制来管理项目自身的Spotify API访问令牌（用于歌曲搜索），包括自动刷新过期的令牌。
    - [x] 实现一个安全的机制来处理和临时存储用户授予的访问令牌（用于播放列表操作），确保令牌与用户会话关联。

### 14.3 用户体验与错误处理优化
- [x] **14.3.1: 优化授权提示信息:**
    - [x] 在前端授权流程的各个步骤中，提供清晰、准确的提示信息，告知用户为何需要授权以及授权的范围。
    - [x] 明确区分"登录Spotify"和"授权本应用访问您的Spotify数据"。
- [x] **14.3.2: 完善错误处理机制:**
    - [x] 对授权失败、API调用失败（无论是项目凭证调用还是用户令牌调用）等情况，在前端提供明确的错误提示和可能的解决建议。
    - [x] 后端API在返回错误时，应包含足够的信息供前端展示和调试。

### 14.4 测试与验证
- [ ] **14.4.1: 连接与CORS测试:**
    - [ ] 验证前端能够无障碍地调用所有后端API端点。
- [ ] **14.4.2: 授权流程端到端测试:**
    - [ ] 测试用户未登录Spotify的完整流程。
    - [ ] 测试用户已登录Spotify但未授权本应用的流程。
    - [ ] 测试用户已授权后的歌曲处理和播放列表创建流程。
    - [ ] 测试令牌刷新机制（项目令牌和用户令牌，如果可能）。
- [ ] **14.4.3: API调用权限验证:**
    - [ ] 确认歌曲搜索 (`/api/process-songs`) 确实使用的是项目凭证（例如，通过临时移除用户授权来测试）。
    - [ ] 确认播放列表创建 (`/api/create-playlist`) 确实使用的是用户授权令牌。

## 阶段15: 修正 Spotify OAuth 授权流程

**目标:** 解决用户授权 Spotify 后重定向错误的问题，确保前后端正确处理 OAuth 流程，实现用户授权、token 获取与存储、以及后续 API 的安全调用。

**核心问题定位:** 当前 Spotify OAuth 授权后的重定向逻辑混乱，前端可能错误地尝试处理本应由后端处理的回调。

**正确流程概述:**
1.  前端引导用户跳转至 Spotify 授权页面。
2.  用户授权后，Spotify 重定向至后端配置的 `/callback` URI，并附带授权码 (code)。
3.  后端 `/callback` 端点接收授权码，用其换取 access token 和 refresh token。
4.  后端安全存储用户 token。
5.  后端将用户重定向回前端指定页面（例如 `/auth-success` 或 `/auth-error`），并携带状态信息。
6.  前端根据后端重定向的状态更新 UI。
7.  后续所有代表用户的 Spotify API 调用均由后端发起，使用存储的 access token。

---

### 子任务与修改点:

#### 1. Spotify Developer Dashboard 配置核查

*   **负责人:** [待分配]
*   **任务:**
    *   [x] 确认在 Spotify Developer Dashboard 中配置的 **Redirect URI** 仍然是 `http://127.0.0.1:8888/callback` (后端 Python 服务的地址)。
    *   [x] (备注) 生产环境此 URI 应为 HTTPS 公网地址。

#### 2. 前端 (Next.js @merged) 修改

*   **负责人:** [待分配]
*   **任务:**
    *   [x] **发起 Spotify 授权请求逻辑调整:**
        *   [x] 构建指向 Spotify 授权端点 (`https://accounts.spotify.com/authorize`) 的 URL。
        *   [x] URL 参数包含:
            *   `client_id`: 你的 Spotify 应用 Client ID。
            *   `response_type`: `code`。
            *   `redirect_uri`: **必须是后端的回调地址** (`http://127.0.0.1:8888/callback`)。
            *   `scope`: 应用所需的权限 (例如 `playlist-modify-public`, `user-read-private`)。
            *   `state`: (推荐) 添加随机生成的字符串用于 CSRF 防护，可临时存储在前端。
        *   [x] 通过 `window.location.href` 重定向用户到 Spotify。
    *   [x] **处理授权后的流程 (等待后端重定向):**
        *   [x] 创建前端路由/页面用于接收后端处理完 OAuth 回调后的重定向，例如:
            *   `/spotify-auth-success`
            *   `/spotify-auth-error`
        *   [x] 在这些页面中，根据后端重定向时附加的 URL 参数 (如 `?status=success` 或 `?error=true`) 更新 UI，向用户展示授权结果。
        *   [x] 确保前端不再尝试直接处理 `http://127.0.0.1:8888/callback?code=...`。

#### 3. 后端 (Python @spotify_playlist_importer) 修改

*   **负责人:** [待分配]
*   **任务:**
    *   [x] **`/callback` 端点实现/增强 (例如，在 `run_fixed_api.py` 中):**
        *   [x] 能够接收 Spotify 回调 URL 中的 `code` 和 `state` 参数。
        *   [x] (如果使用 `state`) 验证 `state` 参数的有效性。
        *   [x] **实现 Token交换逻辑:**
            *   [x] 向 Spotify token 端点 (`https://accounts.spotify.com/api/token`) 发送 POST 请求。
            *   [x] 请求头: `Content-Type: application/x-www-form-urlencoded` 和 `Authorization: Basic <base64_encoded_client_id:client_secret>` (或在 body 中传递 client_id/secret)。
            *   [x] 请求体:
                *   `grant_type`: `authorization_code`
                *   `code`: 收到的授权码
                *   `redirect_uri`: `http://127.0.0.1:8888/callback` (必须与配置和请求时的一致)
        *   [x] **安全存储 Token:**
            *   [x] 将获取到的 `access_token` 和 `refresh_token` 与用户关联并安全存储（例如，加密后存入数据库）。
        *   [x] **重定向回前端:**
            *   [x] Token 处理成功后，将用户重定向回前端的成功页面 (如 `http://localhost:3000/spotify-auth-success?status=true`)。
            *   [x] 若处理失败，重定向回前端的错误页面 (如 `http://localhost:3000/spotify-auth-error?message=token_exchange_failed`)。
    *   [x] **后端调用 Spotify API 逻辑调整:**
        *   [x] **用户特定 API 调用:**
            *   [x] 从存储中检索对应用户的 `access_token`。
            *   [x] 在请求 Spotify API 时，于 `Authorization` 头中携带 `Bearer YOUR_USER_ACCESS_TOKEN`。
            *   [x] **实现 Token 刷新逻辑:** 如果 API 返回 401 (token 过期)，使用 `refresh_token` 向 Spotify token 端点请求新的 `access_token`。
                *   请求体: `grant_type: refresh_token`, `refresh_token: USER_REFRESH_TOKEN`。
                *   请求头同上。
                *   [x] 更新存储中的 token。
        *   [x] **应用级别 API 调用 (如果需要):**
            *   [x] 使用 Client Credentials Flow (`grant_type: client_credentials`) 获取应用级 access token。

#### 4. 前后端通信 (针对用户操作，如歌曲处理)

*   **负责人:** [待分配]
*   **任务:**
    *   [] 确认前端将用户输入（如歌曲文本）发送到后端专用 API 端点。
    *   [] 后端在该端点:
        *   [] 验证用户身份。
        *   [] 获取该用户的 Spotify `access_token`。
        *   [] 使用 token 调用 Spotify API。
        *   [] 返回处理结果给前端。

---
**验收标准:**
*   用户可以从前端发起 Spotify 登录。
*   用户在 Spotify 成功授权后，被正确重定向回前端应用，并看到授权成功的提示。
*   后端成功获取并存储了用户的 access token 和 refresh token。
*   后续用户在前端进行需要 Spotify API 的操作（如搜索、添加歌曲）时，后端能够使用正确的用户 token 代表用户执行操作。
*   Access token 过期后，后端能够自动使用 refresh token 刷新。

---

## XVI. 修复 MatchedSong 初始化与兼容性问题 (Stage 16)

**核心目标**: 解决 `MatchedSong.__init__() got an unexpected keyword argument 'original_line'` 的 `TypeError`，并确保 `MatchedSong` 模型能够存储原始输入行信息，以兼容纯后端脚本的报告生成需求及增强前后端联调后的信息展示。

### 16.1 修改 `MatchedSong` 模型类 (`spotify_playlist_importer/core/models.py` 或类似路径)
- [ ] **16.1.1: 定位 `MatchedSong` 类定义。**
- [ ] **16.1.2: 在 `__init__` 方法参数列表中添加 `original_line`:**
    - [ ] 参数定义为 `original_line: Optional[str] = None`，使其成为可选参数并提供默认值，以保证向后兼容性。
- [ ] **16.1.3: 在 `__init__` 方法内部赋值:**
    - [ ] 添加 `self.original_line: Optional[str] = original_line`，将传入的参数保存为实例属性。
- [ ] **16.1.4: 确认类型提示已更新 (如使用 `typing.Optional`)。**

### 16.2 验证调用点 (无需修改，仅验证)
- [ ] **16.2.1: 验证 `spotify_playlist_importer/spotify/sync_client.py` (约 L469):**
    - [ ] 确认 `create_matched_song(best_match, parsed_song.original_line)` 的调用方式保持不变。
- [ ] **16.2.2: 验证 `spotify_playlist_importer/spotify/matcher.py` (约 L214):**
    - [ ] 确认 `return MatchedSong(...)` 在实例化时传递了 `original_line`（或其对应变量）。

### 16.3 兼容性与影响评估
- [ ] **16.3.1: 评估对纯后端脚本（如果仍在使用）的影响:**
    - [ ] 确认旧的、可能不传递 `original_line` 的 `MatchedSong` 实例化代码路径不会因本次修改而报错。
- [ ] **16.3.2: 评估对当前前后端结合版本的影响:**
    - [ ] 确认 `TypeError` 已解决。
    - [ ] 确认 `/api/process-songs` 的响应（如果包含 `MatchedSong` 序列化对象）现在可以包含 `original_line` 字段。
    - [ ] 评估前端是否可以利用此新增字段来改进用户界面展示。

### 16.4 (可选) 更新Pydantic模型/TypeScript接口
- [ ] **16.4.1: 如果API响应基于Pydantic模型，更新相关模型以包含 `original_line: Optional[str]`。**
- [ ] **16.4.2: 如果前端有对应的TypeScript接口定义，同步更新这些接口。**

### 16.5 测试与验证
- [ ] **16.5.1: 重新运行导致 `TypeError` 的测试场景:**
    - [ ] 确认错误已消失，歌曲匹配流程可以完整执行。
- [ ] **16.5.2: 检查匹配报告/API响应:**
    - [ ] 确认 `original_line` 信息已正确包含在 `MatchedSong` 对象及相关的输出中。
- [ ] **16.5.3: 回归测试:**
    - [ ] 确保此修改未对其他匹配逻辑或功能产生负面影响。

---

## XVII. 用户信息与敏感信息处理优化 (Stage 17)

**核心目标**: 调整项目以符合网页服务的要求，不长期存储用户信息，并通过配置文件管理敏感信息，为项目开源做准备。

### 17.1 用户信息存储优化
- [ ] **17.1.1: 审阅后端代码，识别用户信息持久化存储点:**
    - [ ] 检查 `spotify_playlist_importer/spotify/auth_manager.py` (或相关认证管理模块) 中 OAuth 令牌的缓存机制。
    - [ ] 确认令牌缓存路径 (例如 `auth_manager.cache_handler.cache_path`) 指向的是临时存储还是持久化存储。
- [ ] **17.1.2: 修改令牌缓存策略:**
    - [ ] **方案A (推荐 - 内存缓存):** 将令牌缓存从文件系统迁移到内存缓存 (例如，使用简单的字典或更健壮的内存缓存库如 `cachetools`)。
        - [ ] 为内存缓存中的令牌设置合理的、较短的过期时间 (例如，与Spotify令牌有效期一致或略短，如1小时)。
    - [ ] **方案B (临时文件缓存优化):** 如果暂时保留文件缓存，实现会话结束或令牌过期后自动清理缓存文件的逻辑。
        - [ ] 确保缓存文件权限安全。
- [ ] **17.1.3: 审阅会话管理机制 (`spotify_playlist_importer/api/routes_fixed.py`):**
    - [ ] 确认 `SESSION_COOKIE_NAME` (`spotify_session_id`) 的 `max_age` (当前为30天) 是否符合"不长期存储用户信息"的要求。用户接受了30天有效期，此项可标记为已确认。
    - [x] (已确认) 用户接受 Cookie 有效期为30天。
    - [ ] 评估是否需要更短的会话有效期，或在用户登出时强制清除会话及关联的令牌缓存（如果已实现登出功能）。
- [ ] **17.1.4: 优化临时文件处理:**
    - [ ] 检查 `spotify_playlist_importer/api/routes_fixed.py` 中 `/api/process-songs` 端点使用 `tempfile.NamedTemporaryFile` 的逻辑。
    - [ ] 确保临时文件在使用完毕后被可靠删除 (目前通过 `try...finally` 和 `os.unlink` 实现，是良好实践)。
    - [ ] 考虑是否可以将此处的歌曲列表处理完全在内存中进行，以避免创建临时文件（取决于歌曲列表大小和内存限制）。

### 17.2 敏感信息配置化 (为开源准备)
- [ ] **17.2.1: 识别项目中的硬编码敏感信息:**
    - [ ] **Spotify API 凭证**: 检查 `spotify_playlist_importer/spotify/client_manager.py` (或 `auth.py`) 中 `SpotifyOAuth` 或 `SpotifyClientCredentials` 初始化时 `client_id` 和 `client_secret` 的来源。
    - [ ] **后端重定向 URI**: 检查 `spotify_playlist_importer/spotify/client_manager.py` (或 `auth.py`) 中 `SpotifyOAuth` 初始化时 `redirect_uri` 的来源。
    - [ ] **前端 API 基地址**: `music_move/merged/services/api.ts` 中的 `API_BASE_URL` 已使用环境变量，是良好实践。
    - [ ] **其他可能的密钥或配置**: 全局搜索项目中类似密码、API Key、特定URL等字符串。
- [ ] **17.2.2: 实现通过环境变量加载敏感信息:**
    - [ ] **后端 Python:**
        - [ ] 使用 `python-dotenv` 库在开发环境加载 `.env` 文件中的环境变量。
        - [ ] 修改相关代码 (如 `client_manager.py`)，使其从 `os.environ.get()` 读取 `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET`, `SPOTIFY_REDIRECT_URI` 等。
    - [ ] **前端 Next.js:**
        - [ ] `NEXT_PUBLIC_API_BASE_URL` 已按规范处理。
- [ ] **17.2.3: 创建配置文件模板:**
    - [ ] 在项目根目录或配置目录下创建 `.env.example` 文件。
    - [ ] 列出所有必需的环境变量及其用途说明，例如:
      ```env
      # Spotify App Credentials
      SPOTIFY_CLIENT_ID="YOUR_SPOTIFY_CLIENT_ID"
      SPOTIFY_CLIENT_SECRET="YOUR_SPOTIFY_CLIENT_SECRET"
      SPOTIFY_REDIRECT_URI="http://127.0.0.1:8888/callback" # For backend API

      # Frontend Configuration (if any beyond API URL)
      # NEXT_PUBLIC_API_BASE_URL="http://localhost:8888" # Already handled

      # Backend API Server Configuration
      # FRONTEND_URL="http://localhost:3000" # Used by backend for redirects
      ```
- [ ] **17.2.4: 更新 `.gitignore`:
    - [ ] 确保 `.env` (以及可能的其他本地配置文件如 `spotify_config.local.json` 如果有的话) 被添加到 `.gitignore` 文件中，防止敏感信息提交到版本库。
- [ ] **17.2.5: 更新项目文档 (README.md, 部署文档):**
    - [ ] 详细说明项目依赖的环境变量。
    - [ ] 指导用户如何创建和配置他们自己的 `.env` 文件或在部署环境中设置这些变量。

### 17.3 测试与验证
- [ ] **17.3.1: 测试用户信息非持久化存储:**
    - [ ] 验证令牌缓存是否按预期工作（例如，在内存中且有过期时间，或临时文件被正确清理）。
    - [ ] 验证会话管理是否符合预期。
- [ ] **17.3.2: 测试敏感信息配置化:**
    - [ ] 在本地开发环境中，通过设置不同的 `.env` 文件值，验证应用是否能正确读取和使用这些配置。
    - [ ] 确认移除硬编码值后，应用依然能够正常认证和运行。
    - [ ] 检查Git提交，确保 `.env` 文件未被追踪。

---