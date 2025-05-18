# Spotify 歌单导入工具编码标准与规范

本文档旨在为 "Spotify 歌单导入工具" 项目建立一套统一的编码标准和开发规范，以提高代码质量、可读性、可维护性，并促进团队协作（即使目前是单人开发，良好的规范也有助于未来的扩展和交接）。

## 架构/设计模式采纳

* **模块化设计 (Modular Design)**: 如 `docs/architecture.md` 中所述，项目代码按功能划分为核心模块 (`core/`) 和 Spotify 交互模块 (`spotify/`)，每个模块有明确的职责。
    * *理由/参考*: 提高代码组织性，降低耦合度，便于独立开发和测试。
* **单体命令行应用 (Monolithic CLI Application)**: 应用整体作为一个单独的命令行程序运行。
    * *理由/参考*: 对于当前功能范围，这是最简单直接且易于管理的架构。
* **配置外部化 (Externalized Configuration)**: API 密钥等敏感信息通过 `.env` 文件管理，不由代码硬编码。
    * *理由/参考*: 提高安全性，方便不同环境的配置切换。

## 编码标准

* **主要编程语言**: Python 3.9 或更高版本。
* **主要运行时**: Python 3.9+。
* **代码风格指南与检查/格式化工具**:
    * **Black**: 用于代码自动格式化，确保风格统一。建议在代码提交前运行。
        * *配置*: 通常使用 Black 的默认配置。可以在 `pyproject.toml` 中配置，例如：
            ```toml
            [tool.black]
            line-length = 88 # 或根据团队喜好调整，但建议与PEP 8的79字符有所区分，88是Black的默认值
            target-version = ['py39']
            ```
    * **Flake8**: 用于代码风格检查和潜在错误检测。
        * *配置*: 可以在 `pyproject.toml` 或 `.flake8` 文件中配置。例如，在 `pyproject.toml` 中：
            ```toml
            [tool.flake8]
            max-line-length = 88 # 与Black保持一致
            extend-ignore = "E203,W503" # 忽略与Black冲突的规则
            # E203: whitespace before ':' (Black会处理)
            # W503: line break before binary operator (Black风格是after)
            ```
    * **isort**: 用于自动排序 import 语句。
        * *配置*: 可以在 `pyproject.toml` 中配置，使其与 Black 兼容。
            ```toml
            [tool.isort]
            profile = "black"
            ```
* **命名约定**:
    * 模块名 (文件名): `snake_case.py` (例如: `input_parser.py`)。
    * 包名 (目录名): `snake_case` (例如: `core`, `spotify`)。
    * 类名: `PascalCase` (例如: `SpotifyClient`, `ParsedSong`)。
    * 函数名: `snake_case` (例如: `parse_song_list`, `get_spotify_client`)。
    * 方法名: `snake_case` (例如: `search_and_match_song`)。
    * 变量名: `snake_case` (例如: `parsed_songs`, `playlist_id`)。
    * 常量名: `UPPER_SNAKE_CASE` (例如: `SPOTIPY_CLIENT_ID`, `DEFAULT_PLAYLIST_NAME`)。
* **文件结构**: 遵循 `docs/project-structure.md` 中定义的布局。
* **异步操作**: 本项目主要为同步操作。如果未来引入需要大量并发I/O的操作，可以考虑使用 `asyncio`。
* **类型提示 (Type Hinting)**:
    * **强烈推荐**对所有函数和方法的参数及返回值使用类型提示 (PEP 484)。
    * 使用 Python 内置的 `typing` 模块。
    * 例如: `def parse_song_list(file_path: str) -> List[ParsedSong]:`
    * *类型定义*: 复杂类型或共享类型可以在 `core/models.py` 中定义，或在各自模块的开头。
* **注释与文档字符串 (Docstrings)**:
    * **模块**: 每个模块文件应在开头包含一个简短的文档字符串，说明模块的功能。
    * **类**: 每个类应有文档字符串，描述其用途、主要属性和方法。
    * **函数/方法**:
        * 所有公开的 (public) 函数和方法必须有文档字符串。
        * 文档字符串应遵循 Google Python Style Guide 或 reStructuredText 格式 (Numpy/Sphinx 兼容的格式更佳，如果未来考虑自动生成文档)。
        * 简述函数功能、参数 (名称、类型、含义) 和返回值 (类型、含义)。
        * 例如:
            ```python
            def get_spotify_client(client_id: str, client_secret: str, redirect_uri: str) -> spotipy.Spotify:
                """
                Initializes and returns an authenticated Spotipy client.

                Handles OAuth 2.0 authentication flow.

                Args:
                    client_id: The Spotify application client ID.
                    client_secret: The Spotify application client secret.
                    redirect_uri: The redirect URI configured in Spotify Dashboard.

                Returns:
                    An authenticated spotipy.Spotify instance.
                
                Raises:
                    SpotipyException: If authentication fails.
                """
                # ... implementation ...
            ```
    * **行内注释**: 对于复杂或不直观的代码逻辑，应添加必要的行内注释 (#)。
* **依赖管理**:
    * 使用 `requirements.txt` 文件列出所有项目依赖及其版本。
    * (可选) 考虑使用 `Poetry` 或 `PDM` 等现代 Python 包管理工具，它们可以更好地管理依赖关系和项目打包，并将依赖信息存储在 `pyproject.toml` 中。
    * 添加新依赖前，应评估其必要性、稳定性和社区支持。

## 错误处理策略

* **通用方法**:
    * 优先使用 Python 的异常处理机制 (`try...except...finally`)。
    * 定义清晰的自定义异常类 (如果需要)，继承自内置的 `Exception` 或更具体的异常类型。例如，`InputFileError`, `SongParsingError`。
    * 避免使用空的 `except:` 或 `except Exception:` 来捕获所有异常，应尽可能捕获具体的异常类型。
* **日志记录**:
    * 使用 Python 内置的 `logging` 模块进行日志记录。
    * 在 `main.py` 或一个集中的配置模块中配置日志记录器（级别、格式、处理器）。
    * 日志级别:
        * `DEBUG`: 用于详细的诊断信息，主要在开发和调试时使用。
        * `INFO`: 用于报告程序正常运行过程中的关键事件 (例如，“开始处理文件X”，“成功创建播放列表Y”)。
        * `WARNING`: 用于指示可能出现的问题或非严重错误，程序仍可继续运行。
        * `ERROR`: 用于指示导致操作失败的严重错误，但程序可能仍能继续处理其他任务或安全退出。
        * `CRITICAL`: 用于指示导致程序无法继续运行的致命错误。
    * 日志格式: 建议包含时间戳, 日志级别, 模块名 (或函数名), 和具体消息。
        `%(asctime)s - %(levelname)s - %(name)s - %(message)s`
    * 上下文信息: 在记录错误时，尽可能包含相关的上下文信息，如失败的文件名、歌曲名、API 端点等。
* **特定场景处理**:
    * **外部 API 调用 (Spotify)**:
        * 捕获 `spotipy.exceptions.SpotifyException` 及其子类。
        * 检查响应状态码，对常见的错误（如 401 未授权, 403 禁止, 404 未找到, 429 速率限制）进行特定处理。
        * 对于可重试的错误 (如 429 速率限制，或临时网络问题 5xx)，可以实现带指数退避的重试逻辑 (或者依赖 `spotipy` 的内置重试，如果它提供)。
    * **文件输入/输出**:
        * 使用 `try...except FileNotFoundError, PermissionError, IOError` 等处理文件操作相关的异常。
        * 确保文件在使用后被正确关闭 (推荐使用 `with open(...) as f:` 语句)。
    * **输入验证**:
        * 在 `core/input_parser.py` 中验证用户提供的歌曲行格式。
        * 对于命令行参数，`Click` 或 `Typer` 等库通常会提供内置的验证机制。
* **用户反馈**:
    * 将重要的错误信息清晰地呈现给用户，避免直接暴露原始的 Traceback (除非在 DEBUG 模式下)。
    * 对于可操作的错误，向用户提供可能的解决建议。

## 安全最佳实践

* **密钥管理**:
    * Spotify API 凭据 (`SPOTIPY_CLIENT_ID`, `SPOTIPY_CLIENT_SECRET`) 必须通过环境变量或 `.env` 文件加载，绝不能硬编码到代码中。参考 `docs/environment-vars.md`。
    * `.env` 文件必须添加到 `.gitignore`。
    * `spotipy` 缓存的认证令牌应存储在用户特定的安全位置，并具有适当的文件权限。
* **输入处理**:
    * 虽然本项目不直接处理高度敏感的用户输入用于生成代码或数据库查询，但对文件路径等输入仍需谨慎处理，防止路径遍历等问题 (尽管Python标准库通常有保护)。
* **依赖安全**:
    * 定期检查项目依赖 (通过 `requirements.txt` 或 `pyproject.toml` 管理的包) 是否存在已知的安全漏洞。可以使用 `pip-audit` 或 GitHub 的 Dependabot 等工具。
    * 仅从可信来源获取依赖包。
* **API 通信**:
    * `spotipy` 默认使用 HTTPS 与 Spotify API 通信，确保数据传输的加密。

## 变更日志

| 变更描述             | 日期       | 版本 | 作者        |
| -------------------- | ---------- | ---- | ----------- |
| 初稿 - Spotify-only | 2025-05-17 | 0.1  | 3-Architect |
| ...                  | ...        | ...  | ...         |