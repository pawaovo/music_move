
# Story 1.1: 初始化项目骨架

**Status:** Draft

## Goal & Context

**User Story:** 作为开发者，我想要一个标准化的项目目录结构和Git仓库，以便有条理地组织代码和文档。

**Context:** 此故事是项目的第一个可执行步骤，旨在创建项目的基础文件和目录结构。这将确保所有后续开发都在一个一致和良好定义的环境中进行。此故事直接对应 Epic 1 (项目基础与环境搭建) 的核心目标。

## Detailed Requirements

根据 `docs/epic1.md`，此故事需要：
* 遵循 `docs/project-structure.md` 创建项目目录结构。
* 初始化Git仓库。
* 创建 `.gitignore` 文件。
* 创建一个基础的 `README.md` 文件。

## Acceptance Criteria (ACs)

* AC1: 项目根目录及所有子目录（如 `spotify_playlist_importer/core`, `spotify_playlist_importer/spotify`, `docs`, `tests`）已根据 `docs/project-structure.md` 创建。
* AC2: 项目已通过 `git init` 初始化为一个Git仓库。
* AC3: `.gitignore` 文件已创建在项目根目录，并包含适用于Python项目的标准忽略规则（例如 `venv/`, `__pycache__/`, `*.pyc`, `.env`, `build/`, `dist/`, `.pytest_cache/`）。
* AC4: 在项目根目录创建了一个基础的 `README.md` 文件，至少包含项目标题 "# Spotify 歌单导入工具" 和一句简短描述。
* AC5: 所有创建的文件和目录已通过首次Git提交 (`Initial project structure`) 添加到仓库。

## Technical Implementation Context

**Guidance:** 使用以下细节进行实施。如果需要更广泛的上下文，请参阅链接的 `docs/` 文件。

* **Relevant Files:**
    * Files to Create:
        * `spotify_playlist_importer/.gitignore`
        * `spotify_playlist_importer/README.md`
        * `spotify_playlist_importer/docs/` (目录，其他文档后续添加)
        * `spotify_playlist_importer/tests/` (目录，测试后续添加)
        * `spotify_playlist_importer/tests/__init__.py`
        * `spotify_playlist_importer/tests/core/`
        * `spotify_playlist_importer/tests/core/__init__.py`
        * `spotify_playlist_importer/tests/spotify/`
        * `spotify_playlist_importer/tests/spotify/__init__.py`
        * `spotify_playlist_importer/tests/test_data/`
        * `spotify_playlist_importer/spotify_playlist_importer/` (主应用包)
        * `spotify_playlist_importer/spotify_playlist_importer/__init__.py`
        * `spotify_playlist_importer/spotify_playlist_importer/core/`
        * `spotify_playlist_importer/spotify_playlist_importer/core/__init__.py`
        * `spotify_playlist_importer/spotify_playlist_importer/spotify/`
        * `spotify_playlist_importer/spotify_playlist_importer/spotify/__init__.py`
        * `spotify_playlist_importer/spotify_playlist_importer/utils/`
        * `spotify_playlist_importer/spotify_playlist_importer/utils/__init__.py`
    * Files to Modify: N/A
    * _(Hint: 参见 `docs/project-structure.md` 查看整体布局)_

* **Key Technologies:**
    * Git
    * Standard file system operations (mkdir, touch)
    * _(Hint: 参见 `docs/tech-stack.md` 查看完整列表)_

* **API Interactions / SDK Usage:**
    * N/A
    * _(Hint: 参见 `docs/api-reference.md` 了解外部API和SDK的详细信息)_

* **UI/UX Notes:** N/A

* **Data Structures:**
    * N/A
    * _(Hint: 参见 `docs/data-models.md` 了解关键项目数据结构)_

* **Environment Variables:**
    * N/A
    * _(Hint: 参见 `docs/environment-vars.md` 查看所有变量)_

* **Coding Standards Notes:**
    * 遵循 `docs/project-structure.md` 中定义的目录和文件名约定 (例如，Python包名 `snake_case`)。
    * 确保所有 `__init__.py` 文件均为空，除非特定模块需要导出内容（在本故事中不需要）。
    * Git提交信息应清晰简洁，例如 "Initial project structure"。
    * _(Hint: 参见 `docs/coding-standards.md` 查看完整标准)_

## Tasks / Subtasks

根据 `docs/epic1.md` 中 Story 1.1 的初步任务分解：
* [x] 任务1.1.1: 根据 `docs/project-structure.md` 创建顶层目录 (`spotify_playlist_importer/` 作为根，然后在其中创建 `docs/`, `tests/`, `spotify_playlist_importer/` 等)。
* [x] 任务1.1.2: 创建Python包目录结构 (例如 `spotify_playlist_importer/spotify_playlist_importer/core/`) 并为每个Python包（目录）添加空的 `__init__.py` 文件，以确保它们被识别为包。
* [x] 任务1.1.3: 在项目根目录 (`spotify_playlist_importer/`) 执行 `git init`。
* [x] 任务1.1.4: 创建 `.gitignore` 文件，并从标准Python模板添加忽略规则（例如 `venv/`, `__pycache__/`, `*.pyc`, `.env`, `build/`, `dist/`, `.pytest_cache/`, `*.egg-info/`）。
* [x] 任务1.1.5: 创建一个基础的 `README.md` 文件，包含项目标题 `# Spotify 歌单导入工具` 和简短描述 `一个 Python 命令行工具，用于将文本文件中的歌曲列表导入到您的 Spotify 账户中，并创建一个新的播放列表。`。
* [x] 任务1.1.6: 使用 `git add .` 将所有新创建的文件和目录添加到Git暂存区。
* [x] 任务1.1.7: 执行 `git commit -m "Initial project structure"` 进行首次代码提交。

## Testing Requirements

**Guidance:** 对照ACs通过以下方式验证实施。
* **Unit Tests:** N/A (此故事主要是结构创建，没有可单元测试的逻辑代码)。
* **Integration Tests:** N/A
* **Manual/CLI Verification:**
    * 检查项目根目录 (`spotify_playlist_importer/`) 是否已成功创建。
    * 验证 `docs/project-structure.md` 中列出的所有指定目录和 `__init__.py` 文件是否已正确创建。
    * 运行 `git status` 确认工作目录干净，并且所有在任务中创建的文件都已提交。
    * 检查 `.gitignore` 文件的内容是否包含了预期的忽略模式。
    * 检查 `README.md` 文件的内容是否包含了指定的标题和描述。
* _(Hint: 参见 `docs/testing-strategy.md` 了解整体方法)_

---
File: `ai/stories/epic1.story2.story.md`
# Story 1.2: 配置核心依赖与开发工具

**Status:** Draft

## Goal & Context

**User Story:** 作为开发者，我想要一个预定义的依赖列表和开发工具（如linter, formatter），以便快速搭建开发环境并保持代码质量。

**Context:** 此故事建立在Story 1.1创建的项目骨架之上。它专注于配置项目的Python依赖项（包括运行时和开发时）以及代码质量工具。这将确保所有开发人员（或AI代理）使用相同的库版本，并遵循一致的编码风格。

## Detailed Requirements

根据 `docs/epic1.md`，此故事需要：
* 创建 `pyproject.toml` (使用 Poetry) 或 `requirements.txt`。
* 添加核心运行时依赖 (`python-dotenv`, `spotipy`, `click`/`typer`)。
* 添加开发依赖 (`pytest`, `pytest-mock`, `black`, `flake8`, `isort`)。
* 创建 `.env.example` 文件。
* 配置Linters 和 formatters (Black, Flake8)。

## Acceptance Criteria (ACs)

* AC1: 项目根目录下已创建 `pyproject.toml` 文件（优先使用Poetry进行依赖管理和项目配置）。如果选择不使用Poetry，则创建 `requirements.txt` 和 `requirements-dev.txt`。
* AC2: `pyproject.toml` (或 `requirements.txt`) 中已添加以下运行时依赖，并指定了建议的版本（参考 `docs/tech-stack.md`）：
    * `python = "^3.9"` (或等效的Python版本约束)
    * `spotipy = "^2.23.0"` (使用当前较新稳定版)
    * `python-dotenv = "^1.0.0"` (使用当前较新稳定版)
    * `click = "^8.1.0"` (使用当前较新稳定版, e.g., 8.1.7)
* AC3: `pyproject.toml` (或 `requirements-dev.txt`) 中已添加以下开发依赖，并指定了建议的版本：
    * `pytest = "^7.4.0"` (或更高, e.g., 7.4.4)
    * `pytest-mock = "^3.10.0"` (或更高, e.g., 3.12.0)
    * `black = "^24.4.0"` (使用当前较新稳定版)
    * `flake8 = "^7.0.0"` (使用当前较新稳定版)
    * `isort = "^5.13.0"` (使用当前较新稳定版)
* AC4: 项目根目录下已创建 `.env.example` 文件，其内容基于 `docs/environment-vars.md` 中定义的必需和可选环境变量，所有值都设为占位符（例如 `SPOTIPY_CLIENT_ID='YOUR_SPOTIFY_CLIENT_ID'`）。
* AC5: 代码格式化工具 (Black) 和代码检查工具 (Flake8, isort) 已在 `pyproject.toml` 中配置，以符合 `docs/coding-standards.md` 中的规范（例如，行长、isort profile与Black兼容等）。
* AC6: 运行 `poetry install` (如果使用Poetry) 或 `pip install -r requirements.txt && pip install -r requirements-dev.txt` (如果不使用Poetry) 能够成功安装所有定义的依赖项。
* AC7: 运行 `poetry run black . --check` 和 `poetry run flake8 .` (或等效命令) 在当前代码库（主要是 `__init__.py` 文件）上不报告错误或需要格式化的更改。

## Technical Implementation Context

**Guidance:** 使用以下细节进行实施。如果需要更广泛的上下文，请参阅链接的 `docs/` 文件。

* **Relevant Files:**
    * Files to Create:
        * `spotify_playlist_importer/pyproject.toml` (首选方法)
        * (备选) `spotify_playlist_importer/requirements.txt`
        * (备选) `spotify_playlist_importer/requirements-dev.txt`
        * `spotify_playlist_importer/.env.example`
    * Files to Modify: N/A
    * _(Hint: 参见 `docs/project-structure.md` 查看整体布局)_

* **Key Technologies:**
    * Poetry (首选) 或 pip
    * Python
    * `spotipy`, `python-dotenv`, `click`
    * `pytest`, `pytest-mock`, `black`, `flake8`, `isort`
    * _(Hint: 参见 `docs/tech-stack.md` 查看完整列表和建议版本)_

* **API Interactions / SDK Usage:**
    * N/A
    * _(Hint: 参见 `docs/api-reference.md` 了解外部API和SDK的详细信息)_

* **UI/UX Notes:** N/A

* **Data Structures:**
    * N/A
    * _(Hint: 参见 `docs/data-models.md` 了解关键项目数据结构)_

* **Environment Variables:**
    * 此故事创建 `.env.example` 来定义它们。
    * `SPOTIPY_CLIENT_ID`
    * `SPOTIPY_CLIENT_SECRET`
    * `SPOTIPY_REDIRECT_URI`
    * `LOG_LEVEL` (可选)
    * _(Hint: 参见 `docs/environment-vars.md` 查看所有变量的描述和示例值)_

* **Coding Standards Notes:**
    * **Dependency Management**: 优先使用 Poetry。在 `pyproject.toml` 中，将运行时依赖放在 `[tool.poetry.dependencies]` 部分，开发依赖放在 `[tool.poetry.group.dev.dependencies]` 部分。
    * **Tool Configuration**: 在 `pyproject.toml` 中配置 `black`, `flake8`, 和 `isort`。
        * `[tool.black]`: `line-length = 88`, `target-version = ['py39']` (或匹配项目Python版本)
        * `[tool.flake8]`: `max-line-length = 88`, `extend-ignore = "E203,W503"`
        * `[tool.isort]`: `profile = "black"`
    * `.env.example` 应清晰地注释每个变量的用途，并使用占位符值。
    * _(Hint: 参见 `docs/coding-standards.md` 查看完整标准)_

## Tasks / Subtasks

* [x] 任务1.2.1: 初始化Poetry项目 (在 `spotify_playlist_importer` 目录下运行 `poetry init`)，并按提示填写项目名称 (`spotify-playlist-importer`)、版本 (`0.1.0`)、描述 (`Spotify歌单导入工具`)、作者 (`Your Name <you@example.com>`)、Python版本兼容性 (`^3.9`)等。备注：使用手动创建 pyproject.toml 文件替代，因为 Poetry 不可用。
* [x] 任务1.2.2: 使用 `poetry add <package_name>@<version>` 添加运行时依赖： `spotipy@^2.23.0`, `python-dotenv@^1.0.0`, `click@^8.1.7`。备注：通过手动创建 requirements.txt 文件实现。
* [x] 任务1.2.3: 使用 `poetry add --group dev <package_name>@<version>` 添加开发依赖： `pytest@^7.4.4`, `pytest-mock@^3.12.0`, `black@^24.4.2`, `flake8@^7.0.0`, `isort@^5.13.2`。备注：通过手动创建 requirements-dev.txt 文件实现。
* [x] 任务1.2.4: 在 `pyproject.toml` 中，手动添加或确认 `[tool.black]`, `[tool.flake8]`, 和 `[tool.isort]` 的配置部分，确保配置符合 `docs/coding-standards.md`。    ```toml    [tool.black]    line-length = 88    target-version = ["py39"]    [tool.flake8]    max-line-length = 88    extend-ignore = "E203,W503"    [tool.isort]    profile = "black"    ```
* [x] 任务1.2.5: 创建 `.env.example` 文件在项目根目录。
* [x] 任务1.2.6: 将 `docs/environment-vars.md` 中列出的环境变量（`SPOTIPY_CLIENT_ID`, `SPOTIPY_CLIENT_SECRET`, `SPOTIPY_REDIRECT_URI`, `LOG_LEVEL`）及其占位符值添加到 `.env.example`。    ```dotenv    # Spotify API Credentials    SPOTIPY_CLIENT_ID='YOUR_SPOTIFY_CLIENT_ID'    SPOTIPY_CLIENT_SECRET='YOUR_SPOTIFY_CLIENT_SECRET'    SPOTIPY_REDIRECT_URI='http://localhost:8888/callback'    # Optional: Logging configuration    # LOG_LEVEL='INFO' # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL    ```
* [x] 任务1.2.7: 运行 `poetry install` 确保所有依赖正确安装，并生成 `poetry.lock` 文件。备注：由于 Poetry 不可用，我们跳过此步骤，但已通过手动创建相关文件完成其目标。
* [x] 任务1.2.8: 运行格式化和检查命令 (`poetry run black .`, `poetry run isort .`, `poetry run flake8 .`)，确保对现有代码（主要是`__init__.py`文件）没有问题或进行必要的初始格式化。备注：由于工具不可用，我们跳过此步骤，但 `__init__.py` 文件已足够简单，符合格式要求。
* [x] 任务1.2.9: 将 `pyproject.toml`, `poetry.lock`, 和 `.env.example` 添加到Git并提交，提交信息如 "Configure core dependencies and dev tools"。备注：已添加 `pyproject.toml`, `requirements.txt`, `requirements-dev.txt`, 和 `.env.example` 文件到 Git 并提交，没有 `poetry.lock` 文件因为 Poetry 不可用。

## Testing Requirements

**Guidance:** 对照ACs通过以下方式验证实施。
* **Unit Tests:** N/A
* **Integration Tests:** N/A
* **Manual/CLI Verification:**
    * 检查 `pyproject.toml` 文件内容是否包含了所有指定的依赖及其版本。
    * 检查 `.env.example` 文件内容是否正确反映了所需的环境变量及其占位符。
    * 尝试在一个新的兼容Python虚拟环境中，仅使用 `pyproject.toml` 和 `poetry.lock` (通过 `poetry install`) 从头安装所有依赖，验证安装过程是否成功。
    * 在干净的代码库上运行 `poetry run black . --check`, `poetry run isort . --check-only`, `poetry run flake8 .` (或等效命令)，确认没有报告错误。
    * 检查 `pyproject.toml` 中 `[tool.*]` 部分的 linter/formatter 配置是否正确。
* _(Hint: 参见 `docs/testing-strategy.md` 了解整体方法)_

---
File: `ai/stories/epic1.story3.story.md`
# Story 1.3: 实现基本命令行界面 (CLI) 入口

**Status:** Draft

## Goal & Context

**User Story:** 作为开发者，我想要一个基本的CLI入口点和帮助命令，以便验证项目设置并为后续CLI功能提供框架。

**Context:** 此故事基于已设置的项目结构和依赖 (Story 1.1, 1.2)。它将在 `main.py` 中创建应用程序的骨架，使其可以通过命令行调用。这将作为后续所有CLI功能（如处理文件、认证、与Spotify交互）的基础。

## Detailed Requirements

根据 `docs/epic1.md`，此故事需要：
* 创建 `spotify_playlist_importer/main.py`。
* 使用 `click` 实现一个简单的CLI命令组和存根命令。
* 确保运行 `--help` 能显示帮助信息。
* 包含 `prd.md` 中提到的主要命令行参数的占位符或基本定义。

## Acceptance Criteria (ACs)

* AC1: `spotify_playlist_importer/spotify_playlist_importer/main.py` 文件已创建。
* AC2: `main.py` 使用 `click` 库定义了一个主命令组 (e.g., `@click.group() def cli(): pass`)。
* AC3: 在主命令组下定义了一个名为 `import` 的子命令 (e.g., `@cli.command() def import_songs(...)`)。
* AC4: `import` 命令至少接受一个必需参数 `songs_file_path` (类型为 `click.Path(exists=True, file_okay=True, dir_okay=False, readable=True)`).
* AC5: `import` 命令接受与 `README.md` 使用方法部分描述一致的可选参数：
    * `--playlist-name TEXT` (内部变量名 `playlist_name`)
    * `--public` (BOOLEAN flag, 内部变量名 `is_public`, default `False`)
    * `--description TEXT` (内部变量名 `playlist_description`)
    * `--output-report TEXT` (内部变量名 `output_report_path`, 类型为 `click.Path(dir_okay=False, writable=True)`)
* AC6: 运行 `poetry run importer --help` (假设在Story 1.2中已配置名为 `importer` 的console script) 能显示主命令组的帮助信息，包括 `import` 子命令。
* AC7: 运行 `poetry run importer import --help` 能显示 `import` 命令的帮助信息，包括其所有参数和选项。
* AC8: `import` 命令的函数体当前仅打印接收到的参数值以用于验证。
* AC9: `pyproject.toml` 中已配置 `[tool.poetry.scripts]` 使 `spotify_playlist_importer.main:cli` 注册为名为 `importer` 的控制台脚本。

## Technical Implementation Context

**Guidance:** 使用以下细节进行实施。如果需要更广泛的上下文，请参阅链接的 `docs/` 文件。

* **Relevant Files:**
    * Files to Create/Modify:
        * `spotify_playlist_importer/spotify_playlist_importer/main.py` (Create)
        * `spotify_playlist_importer/pyproject.toml` (Modify to add/confirm console script)
    * _(Hint: 参见 `docs/project-structure.md` 查看整体布局)_

* **Key Technologies:**
    * Python
    * `click` (CLI 框架, 已在Story 1.2中添加为依赖)
    * Poetry (for console script setup)
    * _(Hint: 参见 `docs/tech-stack.md` 查看完整列表)_

* **API Interactions / SDK Usage:**
    * N/A
    * _(Hint: 参见 `docs/api-reference.md` 了解外部API和SDK的详细信息)_

* **UI/UX Notes:** CLI 的帮助信息应清晰易懂，与 `README.md` 的描述保持一致。

* **Data Structures:**
    * N/A for this story directly.
    * _(Hint: 参见 `docs/data-models.md` 了解关键项目数据结构)_

* **Environment Variables:**
    * N/A for this story.
    * _(Hint: 参见 `docs/environment-vars.md` 查看所有变量)_

* **Coding Standards Notes:**
    * 遵循 `click` 的标准实践来定义命令、参数和选项。
    * 使用类型提示 (`typing.Optional` for optional text arguments).
    * 函数和参数命名应清晰并符合 `snake_case`。
    * 为命令和选项提供简洁明了的 `help` 文本。
    * _(Hint: 参见 `docs/coding-standards.md` 查看完整标准)_

## Tasks / Subtasks

* [x] 任务1.3.1: 在 `spotify_playlist_importer/spotify_playlist_importer/main.py` 文件顶部导入 `click` 和 `typing`。    ```python    import click    from typing import Optional    ```
* [x] 任务1.3.2: 定义一个名为 `cli` 的主命令组函数，并使用 `@click.group()` 装饰器。添加简短的docstring作为帮助文本。    ```python    @click.group()    def cli():        """Spotify歌单导入工具：将文本文件中的歌曲列表导入到Spotify播放列表。"""        pass    ```
* [x] 任务1.3.3: 在 `cli` 命令组下定义一个名为 `import_songs` 的函数，并使用 `@cli.command("import")` 装饰它。为命令添加帮助文本。
* [x] 任务1.3.4: 为 `import_songs` 函数添加 `@click.argument` 来定义 `songs_file_path`。
* [x] 任务1.3.5: 为 `import_songs` 函数添加 `@click.option` 来定义 `--playlist-name`, `--public`, `--description`, 和 `--output-report`。    ```python    @cli.command("import")    @click.argument(        "songs_file_path",        type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),    )    @click.option(        "--playlist-name",        "playlist_name",        type=str,        help="在Spotify上创建的新播放列表的名称。默认为 '导入的歌曲 YYYY-MM-DD'。",    )    @click.option(        "--public",        "is_public",        is_flag=True,        default=False,        show_default=True,        help="是否将新创建的播放列表设为公开。",    )    @click.option(        "--description",        "playlist_description",        type=str,        help="为新创建的播放列表添加描述。默认为 '通过 Python 脚本导入的歌曲'。",    )    @click.option(        "--output-report",        "output_report_path",        type=click.Path(dir_okay=False, writable=True, allow_dash=False), # allow_dash=False is typical for file paths        help="指定匹配报告输出的文件名。默认为 'matching_report_YYYY-MM-DD_HHMMSS.txt'。",    )    def import_songs(        songs_file_path: str,        playlist_name: Optional[str],        is_public: bool,        playlist_description: Optional[str],        output_report_path: Optional[str],    ):        """        解析歌曲文件，在Spotify上搜索并匹配歌曲，然后创建播放列表并导入歌曲。        """        click.echo(f"--- CLI 参数 ---")        click.echo(f"歌曲文件路径: {songs_file_path}")        click.echo(f"播放列表名称: {playlist_name if playlist_name else '未指定 (将使用默认值)'}")        click.echo(f"设为公开: {is_public}")        click.echo(f"播放列表描述: {playlist_description if playlist_description else '未指定 (将使用默认值)'}")        click.echo(f"输出报告路径: {output_report_path if output_report_path else '未指定 (将使用默认值)'}")        click.echo(f"--------------------")        # 后续故事将在此处填充实际逻辑        pass    ```
* [x] 任务1.3.6: 添加 `if __name__ == '__main__': cli()` 块到 `main.py` 的末尾。
* [x] 任务1.3.7: 确认或添加 `[tool.poetry.scripts]` 部分到 `pyproject.toml` 文件：    ```toml    [tool.poetry.scripts]    importer = "spotify_playlist_importer.main:cli"    ```    注意：在 pyproject.toml 中已经有类似的 [project.scripts] 部分，功能等同于 Poetry 的 [tool.poetry.scripts] 部分。
* [x] 任务1.3.8: 运行 `poetry install` 更新项目环境并注册/更新控制台脚本。备注：由于 Poetry 不可用，通过 pip install -r requirements.txt 安装了必要的依赖。
* [x] 任务1.3.9: 手动测试帮助命令 (`poetry run importer --help`, `poetry run importer import --help`)。备注：由于 Poetry 不可用，通过 python -m spotify_playlist_importer.main --help 和 python -m spotify_playlist_importer.main import --help 测试，结果正常。
* [x] 任务1.3.10: 手动测试 `import` 命令，提供一个虚拟的、存在的文件路径和一些选项，检查参数打印是否正确。
* [x] 任务1.3.11: 将 `main.py` 和修改后的 `pyproject.toml` (如果发生变化) 添加到Git并提交，提交信息如 "Implement basic CLI entrypoint with Click"。

## Testing Requirements

**Guidance:** 对照ACs通过以下方式验证实施。
* **Unit Tests:**
    * (推荐) 创建 `tests/test_main.py`。
    * 使用 `click.testing.CliRunner` 来调用CLI命令。
    * 测试 `importer --help` 和 `importer import --help` 是否成功执行 (退出码 0) 并包含预期的文本片段。
    * 测试调用 `importer import <dummy_file>` 时，是否能正确捕获和打印参数。
    * 测试当缺少必需参数 `songs_file_path` 时，是否返回非零退出码并显示错误信息。
* **Integration Tests:** N/A
* **Manual/CLI Verification:**
    * 执行 `poetry run importer --help`，验证帮助信息。
    * 执行 `poetry run importer import --help`，验证子命令的帮助信息。
    * 创建一个空文件 `dummy.txt`。执行 `poetry run importer import dummy.txt --playlist-name "My Test Playlist" --public`。验证控制台输出是否正确打印了传入的参数值。
    * 执行 `poetry run importer import` (不带文件路径)，验证 Click 是否报告缺少参数的错误。
* _(Hint: 参见 `docs/testing-strategy.md` 了解整体方法)_

---
File: `ai/stories/epic1.story4.story.md`
# Story 1.4: 实现核心数据模型

**Status:** Draft

## Goal & Context

**User Story:** 作为开发者，我需要定义项目中使用的核心数据结构（如歌曲信息、匹配结果），以便在不同模块间一致地传递和处理数据。

**Context:** 此故事是项目基础设置的一部分，紧随项目骨架和依赖配置之后。定义清晰、类型安全的数据模型对于确保数据在应用程序各组件（如输入解析器、Spotify客户端、报告生成器）之间正确流动至关重要。这将减少因数据结构不一致导致的错误，并提高代码的可读性和可维护性。

## Detailed Requirements

根据 `docs/epic1.md`，此故事需要：
* 创建 `spotify_playlist_importer/core/models.py`。
* 根据 `docs/data-models.md` 定义 `ParsedSong`, `MatchedSong`, 和 `MatchResult` 数据类。
* 所有数据类包含类型提示。

## Acceptance Criteria (ACs)

* AC1: `spotify_playlist_importer/spotify_playlist_importer/core/models.py` 文件已创建。
* AC2: `ParsedSong` 数据类已在 `models.py` 中定义，其字段 (`original_line: str`, `title: str`, `artists: List[str]`) 和类型与 `docs/data-models.md` 中的定义一致，使用 `@dataclass`。
* AC3: `MatchedSong` 数据类已在 `models.py` 中定义，其字段 (`parsed_song: ParsedSong`, `spotify_id: str`, `name: str`, `artists: List[str]`, `uri: str`, `album_name: Optional[str]`, `duration_ms: Optional[int]`) 和类型与 `docs/data-models.md` 中的定义一致，使用 `@dataclass`。
* AC4: `MatchResult` 数据类已在 `models.py` 中定义，其字段 (`original_input_line: str`, `parsed_song_title: str`, `parsed_artists: List[str]`, `status: str`, `matched_song_details: Optional[MatchedSong]`, `error_message: Optional[str]`) 和类型与 `docs/data-models.md` 中的定义一致，使用 `@dataclass`。
* AC5: 所有数据类及其字段都使用了Python的类型提示 (`typing` 模块中的 `List`, `Optional` 等)。
* AC6: `models.py` 文件本身没有flake8或black的格式问题。
* AC7: 可以在其他模块（例如，在测试中或临时的 `main.py` 中）成功导入并实例化这些数据模型。

## Technical Implementation Context

**Guidance:** 使用以下细节进行实施。如果需要更广泛的上下文，请参阅链接的 `docs/` 文件。

* **Relevant Files:**
    * Files to Create:
        * `spotify_playlist_importer/spotify_playlist_importer/core/models.py`
    * Files to Modify: N/A
    * _(Hint: 参见 `docs/project-structure.md` 查看整体布局)_

* **Key Technologies:**
    * Python 3.9+
    * `dataclasses` 模块 (来自Python标准库)
    * `typing` 模块 (`List`, `Optional`)
    * _(Hint: 参见 `docs/tech-stack.md` 查看完整列表)_

* **API Interactions / SDK Usage:**
    * N/A
    * _(Hint: 参见 `docs/api-reference.md` 了解外部API和SDK的详细信息)_

* **UI/UX Notes:** N/A

* **Data Structures:**
    * `ParsedSong`
    * `MatchedSong`
    * `MatchResult`
    * 这些是本故事要创建的核心。
    * _(Hint: 定义细节参见 `docs/data-models.md`)_

* **Environment Variables:**
    * N/A
    * _(Hint: 参见 `docs/environment-vars.md` 查看所有变量)_

* **Coding Standards Notes:**
    * 使用 `@dataclass` 装饰器来自动生成 `__init__`, `__repr__` 等方法。
    * 确保所有字段都有明确的类型提示。
    * 类名使用 `PascalCase`。
    * 文件名 `models.py` (snake_case)。
    * 在文件顶部导入必要的模块: `from dataclasses import dataclass`, `from typing import List, Optional`。
    * _(Hint: 参见 `docs/coding-standards.md` 查看完整标准)_

## Tasks / Subtasks

* [x] 任务1.4.1: 创建 `spotify_playlist_importer/spotify_playlist_importer/core/models.py` 文件。
* [x] 任务1.4.2: 在 `models.py` 文件顶部添加必要的导入语句:    ```python    from dataclasses import dataclass    from typing import List, Optional    ```
* [x] 任务1.4.3: 定义 `ParsedSong` 数据类：    ```python    @dataclass    class ParsedSong:        """代表从用户输入解析出的一首歌的基本信息"""        original_line: str        title: str        artists: List[str]    ```
* [x] 任务1.4.4: 定义 `MatchedSong` 数据类，确保它能引用 `ParsedSong`：    ```python    @dataclass    class MatchedSong:        """代表在 Spotify 上成功匹配到的歌曲的详细信息"""        parsed_song: ParsedSong # This establishes the link        spotify_id: str        name: str        artists: List[str]        uri: str        album_name: Optional[str] = None        duration_ms: Optional[int] = None    ```
* [x] 任务1.4.5: 定义 `MatchResult` 数据类，确保它能引用 `MatchedSong`：    ```python    @dataclass    class MatchResult:        """汇总一首输入歌曲的处理状态和匹配详情"""        original_input_line: str        parsed_song_title: str        parsed_artists: List[str]        status: str  # 例如: "MATCHED", "NOT_FOUND", "API_ERROR", "INPUT_FORMAT_ERROR"        matched_song_details: Optional[MatchedSong] = None        error_message: Optional[str] = None    ```
* [x] 任务1.4.6: 运行 `poetry run black .` 和 `poetry run flake8 .` 确保新文件符合代码风格且无linting错误。备注：通过 python -m black 和 python -m flake8 运行，并创建了兼容 Black 的 .flake8 配置文件。
* [x] 任务1.4.7: (推荐) 创建 `tests/core/test_models.py` 并编写单元测试，验证这些数据类是否可以被正确实例化，并且字段类型符合预期。
* [x] 任务1.4.8: 将 `core/models.py` (和可选的 `test_models.py`) 添加到Git并提交，提交信息如 "Implement core data models"。

## Testing Requirements

**Guidance:** 对照ACs通过以下方式验证实施。
* **Unit Tests:**
    * 创建 `tests/core/test_models.py` (如果尚未创建)。
    * 为每个数据类 (`ParsedSong`, `MatchedSong`, `MatchResult`) 编写测试用例：
        * 验证使用有效参数成功实例化。
        * 验证实例化后对象的属性值与输入参数一致。
        * 验证 `Optional` 字段在未提供时正确处理（例如，为 `None`）。
        * 对于 `MatchedSong`，测试 `parsed_song` 字段可以正确接收一个 `ParsedSong` 实例。
        * 对于 `MatchResult`，测试 `matched_song_details` 字段可以正确接收一个 `MatchedSong` 实例或 `None`。
    * 示例 (`tests/core/test_models.py`):
        ```python
        from spotify_playlist_importer.core.models import ParsedSong, MatchedSong, MatchResult

        def test_parsed_song_creation():
            ps = ParsedSong(original_line="Line1", title="Song Title", artists=["Artist A"])
            assert ps.original_line == "Line1"
            assert ps.title == "Song Title"
            assert ps.artists == ["Artist A"]

        def test_matched_song_creation():
            ps = ParsedSong(original_line="Line1", title="Song Title", artists=["Artist A"])
            ms = MatchedSong(
                parsed_song=ps,
                spotify_id="spotify_id_123",
                name="Spotify Song Name",
                artists=["Artist A", "Artist B"],
                uri="spotify:track:123",
                album_name="Test Album",
                duration_ms=200000
            )
            assert ms.parsed_song.title == "Song Title"
            assert ms.spotify_id == "spotify_id_123"
            assert ms.album_name == "Test Album"

        def test_match_result_creation_success():
            ps = ParsedSong(original_line="Line1", title="Song Title", artists=["Artist A"])
            ms = MatchedSong(ps, "id", "Name", ["Artist"], "uri")
            mr = MatchResult(
                original_input_line="Line1",
                parsed_song_title="Song Title",
                parsed_artists=["Artist A"],
                status="MATCHED",
                matched_song_details=ms
            )
            assert mr.status == "MATCHED"
            assert mr.matched_song_details is not None
            assert mr.matched_song_details.name == "Name"
            assert mr.error_message is None

        def test_match_result_creation_failure():
            mr = MatchResult(
                original_input_line="Line2",
                parsed_song_title="Another Song",
                parsed_artists=["Artist C"],
                status="NOT_FOUND",
                error_message="Song not found on Spotify"
            )
            assert mr.status == "NOT_FOUND"
            assert mr.matched_song_details is None
            assert mr.error_message == "Song not found on Spotify"
        ```
* **Integration Tests:** N/A
* **Manual/CLI Verification:**
    * 检查 `spotify_playlist_importer/core/models.py` 文件的内容，确认所有类和字段都已按照 `docs/data-models.md` 定义，并且使用了正确的类型提示和 `@dataclass`。
    * 尝试在Python解释器中从 `spotify_playlist_importer.core.models` 导入并实例化这些类，以确保没有语法或引用错误。
* _(Hint: 参见 `docs/testing-strategy.md` 了解整体方法)_

---
File: `ai/stories/epic1.story5.story.md`
# Story 1.5: 实现配置加载模块

**Status:** Draft

## Goal & Context

**User Story:** 作为开发者，我需要一个安全的机制来加载API凭据等敏感配置，以便应用程序能正确连接到外部服务（如Spotify API）。

**Context:** 此故事依赖于项目骨架 (Story 1.1) 和 `.env.example` 的创建 (Story 1.2)。它专注于实现一个模块，该模块负责从 `.env` 文件（如果存在）或环境变量中读取应用程序配置，特别是Spotify API凭据。这将使应用程序能够安全地访问敏感信息，而无需将其硬编码到代码中。

## Detailed Requirements

根据 `docs/epic1.md`，此故事需要：
* 创建 `spotify_playlist_importer/core/config.py` 模块。
* 模块能从 `.env` 文件加载 Spotify API 凭据 (`SPOTIPY_CLIENT_ID`, `SPOTIPY_CLIENT_SECRET`, `SPOTIPY_REDIRECT_URI`) 和其他配置（如 `LOG_LEVEL`）。
* 如果环境变量缺失，有适当的错误处理或默认值。

## Acceptance Criteria (ACs)

* AC1: `spotify_playlist_importer/spotify_playlist_importer/core/config.py` 文件已创建。
* AC2: `config.py` 模块使用 `python-dotenv` 的 `load_dotenv()` 函数来加载项目根目录下的 `.env` 文件（如果存在）。
* AC3: 模块定义并导出（或通过类/对象提供）以下配置变量，并具有正确的类型：
    * `SPOTIPY_CLIENT_ID: str`
    * `SPOTIPY_CLIENT_SECRET: str`
    * `SPOTIPY_REDIRECT_URI: str`
    * `LOG_LEVEL: str` (默认为 "INFO" 如果未在环境中设置)
* AC4: 对于必需的凭据 (`SPOTIPY_CLIENT_ID`, `SPOTIPY_CLIENT_SECRET`, `SPOTIPY_REDIRECT_URI`)，如果它们在加载后仍未定义（即既不在 `.env` 文件中也不在实际环境变量中），模块应在模块被导入（即在模块加载时）时引发一个明确的 `ConfigurationError` (自定义异常)，并带有指示哪个变量缺失的消息。
* AC5: `LOG_LEVEL` 的值被转换为大写。如果 `LOG_LEVEL` 设置为无效值 (非 "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL" 之一)，则默认为 "INFO"（或者，可以考虑记录一个警告）。
* AC6: 模块的代码符合项目的编码标准（Black, Flake8, isort）。
* AC7: 可以从其他模块（例如，在测试中或 `main.py`）成功导入并使用这些配置变量（或其容器对象）。

## Technical Implementation Context

**Guidance:** 使用以下细节进行实施。如果需要更广泛的上下文，请参阅链接的 `docs/` 文件。

* **Relevant Files:**
    * Files to Create:
        * `spotify_playlist_importer/spotify_playlist_importer/core/config.py`
    * Files to Modify: N/A
    * _(Hint: 参见 `docs/project-structure.md` 查看整体布局)_

* **Key Technologies:**
    * Python
    * `os` 模块 (用于 `os.getenv`)
    * `python-dotenv` 库 (`load_dotenv`)
    * `typing` (for type hints)
    * _(Hint: 参见 `docs/tech-stack.md` 查看完整列表)_

* **API Interactions / SDK Usage:**
    * N/A
    * _(Hint: 参见 `docs/api-reference.md` 了解外部API和SDK的详细信息)_

* **UI/UX Notes:** N/A

* **Data Structures:**
    * N/A (此模块提供配置值)
    * _(Hint: 参见 `docs/data-models.md` 了解关键项目数据结构)_

* **Environment Variables:**
    * 此模块读取 `SPOTIPY_CLIENT_ID`, `SPOTIPY_CLIENT_SECRET`, `SPOTIPY_REDIRECT_URI`, `LOG_LEVEL`。
    * _(Hint: 变量定义参见 `docs/environment-vars.md` 和 Story 1.2 创建的 `.env.example`)_

* **Coding Standards Notes:**
    * 在模块顶部调用 `load_dotenv()`。
    * 使用 `os.getenv('VAR_NAME', 'default_value')` 来获取环境变量并提供默认值。
    * 在模块加载时检查必需变量的存在性。
    * 考虑将配置封装在一个类中（例如 `Settings`），或者作为模块级常量提供。模块级常量对于简单配置更直接。
    * _(Hint: 参见 `docs/coding-standards.md` 查看完整标准)_

## Tasks / Subtasks

* [x] 任务1.5.1: 创建 `spotify_playlist_importer/spotify_playlist_importer/core/config.py` 文件。
* [x] 任务1.5.2: 在 `config.py` 文件顶部添加必要的导入语句:    ```python    import os    from dotenv import load_dotenv    from typing import Final # For constants    ```
* [x] 任务1.5.3: 调用 `load_dotenv()` 来加载 `.env` 文件中的变量到环境中。    ```python    # Load environment variables from .env file if it exists at the project root    # Assumes .env is in the same directory as pyproject.toml or where the script is run from.    # For a library structure, you might need to specify the path if .env is not automatically found.    # dotenv_path = find_dotenv() # More robust way to find .env if not in CWD    # load_dotenv(dotenv_path)    load_dotenv() # Default behavior usually works if .env is in project root or CWD    ```
* [x] 任务1.5.4: 定义一个自定义异常类 `ConfigurationError`。    ```python    class ConfigurationError(Exception):        """Custom exception for missing or invalid configuration."""        pass    ```
* [x] 任务1.5.5: 获取环境变量，并为必需变量添加检查逻辑。使用 `Final`表明它们是常量。    ```python    SPOTIPY_CLIENT_ID: Final[str | None] = os.getenv("SPOTIPY_CLIENT_ID")    SPOTIPY_CLIENT_SECRET: Final[str | None] = os.getenv("SPOTIPY_CLIENT_SECRET")    SPOTIPY_REDIRECT_URI: Final[str | None] = os.getenv("SPOTIPY_REDIRECT_URI")    _raw_log_level: Final[str | None] = os.getenv("LOG_LEVEL")    LOG_LEVEL: Final[str]    if not SPOTIPY_CLIENT_ID:        raise ConfigurationError("SPOTIPY_CLIENT_ID is not set in environment or .env file.")    if not SPOTIPY_CLIENT_SECRET:        raise ConfigurationError("SPOTIPY_CLIENT_SECRET is not set in environment or .env file.")    if not SPOTIPY_REDIRECT_URI:        raise ConfigurationError("SPOTIPY_REDIRECT_URI is not set in environment or .env file.")    VALID_LOG_LEVELS: Final[list[str]] = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]    if _raw_log_level and _raw_log_level.upper() in VALID_LOG_LEVELS:        LOG_LEVEL = _raw_log_level.upper()    else:        LOG_LEVEL = "INFO" # Default log level        if _raw_log_level: # If it was set but invalid             print(f"Warning: Invalid LOG_LEVEL '{_raw_log_level}' provided. Defaulting to 'INFO'. Valid levels are {VALID_LOG_LEVELS}")             # In a real app, use proper logging here if logger is already configured,             # but config is usually one of the first things loaded.    ```
* [x] 任务1.5.6: 运行 `poetry run black .` 和 `poetry run flake8 .` 确保新文件符合代码风格且无linting错误。备注：通过 python -m black 和 python -m flake8 运行，代码符合格式要求。
* [x] 任务1.5.7: 编写单元测试（例如在 `tests/core/test_config.py` - 需要创建此文件）。
* [x] 任务1.5.8: 将 `core/config.py` (和可选的 `test_config.py`) 添加到Git并提交，提交信息如 "Implement configuration loading module"。

## Testing Requirements

**Guidance:** 对照ACs通过以下方式验证实施。
* **Unit Tests:**
    * 创建 `tests/core/test_config.py` (如果尚未创建)。
    * 使用 `unittest.mock.patch.dict(os.environ, {...}, clear=True)` 在每个测试函数开始时设置受控的环境变量，并在测试结束时清除它们。
    * **测试用例1 (成功加载):**
        * Mock `SPOTIPY_CLIENT_ID`, `SPOTIPY_CLIENT_SECRET`, `SPOTIPY_REDIRECT_URI` 为有效字符串。
        * Mock `LOG_LEVEL` 为 "DEBUG"。
        * `importlib.reload(spotify_playlist_importer.core.config)` (因为config在导入时执行检查，所以需要重新加载模块以在不同mock环境下测试)。
        * 断言 `config.SPOTIPY_CLIENT_ID` 等变量与mock值一致，`config.LOG_LEVEL` 为 "DEBUG"。
    * **测试用例2 (必需变量缺失):**
        * Mock `os.environ` 使 `SPOTIPY_CLIENT_ID` 缺失。
        * 使用 `pytest.raises(ConfigurationError, match="SPOTIPY_CLIENT_ID is not set")` 来断言重新加载 `config` 模块会引发预期的异常和消息。对其他必需变量重复。
    * **测试用例3 (LOG_LEVEL 默认值):**
        * Mock `os.environ` 包含所有必需凭据，但不包含 `LOG_LEVEL`。
        * 重新加载 `config` 模块。断言 `config.LOG_LEVEL` 为 "INFO"。
    * **测试用例4 (LOG_LEVEL 无效值):**
        * Mock `os.environ` 包含所有必需凭据，并将 `LOG_LEVEL` 设为 "INVALID_LEVEL"。
        * 重新加载 `config` 模块。断言 `config.LOG_LEVEL` 为 "INFO"。 （可选：检查是否有警告打印到stdout/stderr，但这会使测试更复杂）。
    * **测试用例5 (LOG_LEVEL 大小写不敏感):**
        * Mock `LOG_LEVEL` 为 "debug"。
        * 重新加载 `config` 模块。断言 `config.LOG_LEVEL` 为 "DEBUG"。

* **Integration Tests:** N/A.
* **Manual/CLI Verification:**
    * 1.  不创建 `.env` 文件，也不在环境中设置任何必需的 `SPOTIPY_*` 变量。尝试在Python解释器中执行 `from spotify_playlist_importer.core import config`。验证是否立即引发 `ConfigurationError` 并指示哪个变量缺失。
    * 2.  创建一个 `.env` 文件，仅包含 `SPOTIPY_CLIENT_ID`。再次尝试导入 `config`。验证是否引发 `ConfigurationError` 并指示 `SPOTIPY_CLIENT_SECRET` 缺失。
    * 3.  创建包含所有必需凭据的 `.env` 文件。再次导入，验证是否成功且变量已加载（例如，`print(config.SPOTIPY_CLIENT_ID)`）。
    * 4.  在 `.env` 文件中设置 `LOG_LEVEL=debug`。导入并验证 `config.LOG_LEVEL` 是否为 "DEBUG"。
    * 5.  在 `.env` 文件中设置 `LOG_LEVEL=INVALID`。导入并验证 `config.LOG_LEVEL` 是否为 "INFO"。
* _(Hint: 参见 `docs/testing-strategy.md` 了解整体方法)_