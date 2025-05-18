
# Spotify 歌单导入工具项目结构

本项目采用模块化的结构，以便于代码的组织、理解和维护。

```plaintext
spotify_playlist_importer/
├── .git/                     # Git 版本控制元数据 (自动生成)
├── .github/                  # (可选) GitHub Actions 工作流等
│   └── workflows/
│       └── python-app.yml    # (可选) CI/CD 配置文件示例
├── .vscode/                  # (可选) VSCode 编辑器特定配置
│   └── settings.json
├── docs/                     # 项目文档 (本文件所在目录)
│   ├── architecture.md       # 架构文档
│   ├── tech-stack.md         # 技术栈文档
│   ├── project-structure.md  # 项目结构文档 (本文)
│   ├── coding-standards.md   # 编码标准
│   ├── api-reference.md      # API 参考 (Spotify)
│   ├── data-models.md        # 数据模型
│   ├── environment-vars.md   # 环境变量说明
│   └── testing-strategy.md   # 测试策略
├── spotify_playlist_importer/  # Python 主应用包 (或 src/ 目录)
│   ├── __init__.py
│   ├── main.py               # CLI 应用程序入口点
│   ├── core/                 # 核心业务逻辑与数据模型
│   │   ├── __init__.py
│   │   ├── config.py         # 配置加载与管理
│   │   ├── input_parser.py   # 用户输入文件解析逻辑
│   │   └── models.py         # Pydantic 或 dataclass 定义的数据模型
│   ├── spotify/              # 与 Spotify API 交互相关模块
│   │   ├── __init__.py
│   │   ├── auth.py           # Spotify OAuth 认证处理
│   │   └── client.py         # Spotify API 客户端封装 (搜索、播放列表操作)
│   └── utils/                # 通用辅助工具模块
│       ├── __init__.py
│       └── cli_utils.py      # (可选) CLI 相关的辅助函数 (如进度条)
├── tests/                    # 自动化测试目录
│   ├── __init__.py
│   ├── conftest.py           # (可选) Pytest 共享 fixtures
│   ├── core/                 # core 模块的单元测试
│   │   └── test_input_parser.py
│   ├── spotify/              # spotify 模块的测试 (可能包含集成测试)
│   │   └── test_client.py
│   └── test_data/            # 测试用的示例输入文件或数据
│       └── sample_songs.txt
├── .env.example              # 环境变量配置文件示例
├── .gitignore                # 指定 Git 应忽略的文件和目录
├── LICENSE.txt               # (可选) 项目许可证文件
├── poetry.lock               # (可选) 如果使用 Poetry 管理依赖
├── pyproject.toml            # (可选) Python 项目配置文件 (例如使用 Poetry, Black, Flake8)
├── README.md                 # 项目概览、安装和使用指南
└── requirements.txt          # 项目依赖列表 (如果未使用 Poetry 等工具)
````

*(注意: `spotify_playlist_importer/` 也可以命名为 `src/`，这取决于个人或团队偏好。如果使用 `Poetry` 或其他现代 Python 项目管理工具，`requirements.txt` 可能会被 `pyproject.toml` 和 `poetry.lock`替代。)*

## 关键目录和文件说明

  * **`docs/`**: 包含所有项目相关的规划、设计和参考文档。
  * **`spotify_playlist_importer/` (或 `src/`)**: 应用程序的主要 Python 源代码包。
      * **`main.py`**: 整个命令行工具的入口和主控制流程。
      * **`core/`**: 存放不直接依赖于外部服务（如特定API客户端）的核心逻辑。
          * `config.py`: 负责加载和提供配置信息，如从 `.env` 文件读取 API 密钥。
          * `input_parser.py`: 专门处理用户提供的歌曲列表文件的解析。
          * `models.py`: 定义程序中使用的数据结构（例如，用 Pydantic 或 Python dataclasses 实现的 `ParsedSong`, `MatchedSong`）。
      * **`spotify/`**: 包含所有与 Spotify API 直接交互的代码。
          * `auth.py`: 处理 Spotify 的 OAuth 2.0 用户认证流程。
          * `client.py`: 封装对 Spotify API 端点的调用，如歌曲搜索、播放列表创建和歌曲添加。
      * **`utils/`**: 包含可在项目中复用的通用工具函数或类，例如特殊的日志记录配置、CLI 进度条等。
  * **`tests/`**: 包含所有自动化测试脚本。其内部结构通常会镜像源代码目录结构，以便清晰地组织单元测试和集成测试。
      * `test_data/`: 存放测试时使用的静态数据文件。
  * **`.env.example`**: 一个示例文件，展示了运行应用所需的环境变量格式。用户应复制此文件为 `.env` 并填入实际值。
  * **`.gitignore`**: 列出了应被 Git 忽略的文件和目录，例如 `venv/`, `__pycache__/`, `.env`, `build/`, `dist/` 等。
  * **`README.md`**: 提供项目的基本信息、安装步骤和使用说明，是用户和开发者首先接触的文档。
  * **`requirements.txt` / `pyproject.toml`**: 定义项目运行所需的 Python 依赖包及其版本。

## 注意事项

  * 建议使用虚拟环境 (`venv`) 来管理项目依赖，以避免与系统全局 Python 环境或其他项目的依赖产生冲突。
  * 代码组织应遵循高内聚、低耦合的原则，使得各个模块职责分明，易于独立测试和修改。

## 变更日志

| 变更描述             | 日期       | 版本 | 作者        |
| -------------------- | ---------- | ---- | ----------- |
| 初稿 - Spotify-only | 2025-05-17 | 0.1  | 3-Architect |
| ...                  | ...        | ...  | ...         |
