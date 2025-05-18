# Story 2.1: 实现 Spotify OAuth 2.0 认证流程

**Status:** Completed

## Goal & Context

**User Story:** 作为应用程序，我需要能够引导用户完成 Spotify OAuth 2.0 授权，并获取一个有效的 `spotipy.Spotify` 客户端实例，以便后续进行 API 调用。

**Context:** 此故事是 Epic 2 (Spotify 用户认证) 的核心。它依赖于 Epic 1 中创建的配置加载模块 (Story 1.5) 来获取 API 凭据。成功实现此故事将使应用程序能够代表用户执行操作。这是与 Spotify API 进行任何有意义交互的先决条件。

## Detailed Requirements

根据 `docs/epic2.md`，此故事的关键需求包括：

  * 创建 `spotify_playlist_importer/spotify/auth.py` 模块。
  * 使用 `spotipy.SpotifyOAuth` 和从 `core.config` 加载的凭据处理 OAuth 2.0 授权码流程 (PKCE)。
  * 模块提供一个函数，该函数在需要时能触发用户授权流程，并返回一个已认证的 `spotipy.Spotify` 客户端实例。
  * 请求正确的 Scopes。

## Acceptance Criteria (ACs)

  * AC1: `spotify_playlist_importer/spotify_playlist_importer/spotify/auth.py` 文件已创建。
  * AC2: `auth.py` 中定义了一个函数（例如 `get_spotify_client()`)，该函数不接受参数，但能从 `spotify_playlist_importer.core.config` 模块获取 `SPOTIPY_CLIENT_ID`, `SPOTIPY_CLIENT_SECRET`, `SPOTIPY_REDIRECT_URI`。
  * AC3: `get_spotify_client()` 函数正确配置并实例化 `spotipy.SpotifyOAuth`，使用的 scopes 为 `["user-read-private", "playlist-modify-public", "playlist-modify-private"]` (参考 `docs/api-reference.md`)。
  * AC4: 调用 `get_spotify_client()` 函数时：
      * 如果本地没有有效的缓存令牌，它应能通过 `spotipy` 的机制自动尝试打开用户的默认浏览器以进行 Spotify 授权。
      * 成功授权（并在本地服务器接收回调）后，函数应返回一个已认证的 `spotipy.Spotify` 客户端实例。
  * AC5: 如果由于任何原因（例如，凭据无效，用户拒绝授权）导致 `spotipy.SpotifyOAuth` 或 `spotipy.Spotify` 实例化失败，函数应捕获相关的 `spotipy.SpotifyOauthError` 或 `spotipy.SpotifyException`，打印一条用户友好的错误消息到 `stderr` (例如，提示检查凭据和回调URI配置)，然后程序应以非零状态码退出 (例如 `sys.exit(1)`)。
  * AC6: `auth.py` 模块的代码符合项目的编码标准。

## Technical Implementation Context

**Guidance:** 使用以下细节进行实施。如果需要更广泛的上下文，请参阅链接的 `docs/` 文件。

  * **Relevant Files:**

      * Files to Create:
          * `spotify_playlist_importer/spotify_playlist_importer/spotify/auth.py`
      * Files to Modify: N/A (但 `main.py` 后续会调用此模块)
      * *(Hint: 参见 `docs/project-structure.md` 查看整体布局)*

  * **Key Technologies:**

      * Python
      * `spotipy` (特别是 `spotipy.SpotifyOAuth` 和 `spotipy.Spotify`)
      * `spotify_playlist_importer.core.config` (用于获取凭据)
      * `sys` (用于 `sys.exit`)
      * `webbrowser` (spotipy 可能会在内部使用它来打开浏览器)
      * *(Hint: 参见 `docs/tech-stack.md` 查看完整列表)*

  * **API Interactions / SDK Usage:**

      * **`spotipy.SpotifyOAuth`**:
          * `client_id`, `client_secret`, `redirect_uri` 从 `core.config` 获取。
          * `scope` 参数应设置为: `"user-read-private playlist-modify-public playlist-modify-private"`。
          * `cache_path` 可以使用 `spotipy` 的默认值 (通常是项目根目录下的 `.cache` 或 `.cache-username`)。
      * **`spotipy.Spotify`**:
          * 使用 `auth_manager=SpotifyOAuth_instance` 进行实例化。
      * *(Hint: 参见 `docs/api-reference.md` (认证部分) 和 `spotipy` 文档)*

  * **UI/UX Notes:**

      * 错误消息应清晰，指导用户可能的问题（例如，不正确的 `.env` 配置，Spotify Dashboard 中的 redirect URI 不匹配）。
      * `spotipy` 会在需要授权时自动启动一个本地Web服务器来接收回调，并在控制台打印URL让用户在浏览器中打开（如果自动打开失败）。

  * **Data Structures:**

      * N/A (此模块返回 `spotipy.Spotify` 实例)
      * *(Hint: 参见 `docs/data-models.md` 了解关键项目数据结构)*

  * **Environment Variables:**

      * 间接依赖 (通过 `core.config`): `SPOTIPY_CLIENT_ID`, `SPOTIPY_CLIENT_SECRET`, `SPOTIPY_REDIRECT_URI`。
      * *(Hint: 参见 `docs/environment-vars.md` 查看所有变量)*

  * **Coding Standards Notes:**

      * 函数应包含类型提示。
      * 错误处理应使用 `try-except` 块，捕获特定的 `spotipy` 异常。
      * *(Hint: 参见 `docs/coding-standards.md` 查看完整标准)*

## Tasks / Subtasks

根据 `docs/epic2.md` 中 Story 2.1 的初步任务分解进行细化：

  * [ ] 任务2.1.1: 创建 `spotify_playlist_importer/spotify_playlist_importer/spotify/auth.py` 文件。
  * [ ] 任务2.1.2: 在 `auth.py` 中导入必要的模块:
    ```python
    import spotipy
    from spotipy.oauth2 import SpotifyOAuth, SpotifyOauthError
    import sys
    from spotify_playlist_importer.core import config # Assuming config raises error if vars not set
    ```
  * [ ] 任务2.1.3: 定义 `get_spotify_client() -> spotipy.Spotify:` 函数。
  * [ ] 任务2.1.4: 在函数内部，定义 `SPOTIFY_SCOPES` 列表/字符串。
    ```python
    SPOTIFY_SCOPES = "user-read-private playlist-modify-public playlist-modify-private"
    ```
  * [ ] 任务2.1.5: 在 `try-except` 块中，实例化 `spotipy.SpotifyOAuth`，使用从 `config` 模块获取的凭据和定义的 `SPOTIFY_SCOPES`。
    ```python
    try:
        auth_manager = SpotifyOAuth(
            client_id=config.SPOTIPY_CLIENT_ID,
            client_secret=config.SPOTIPY_CLIENT_SECRET,
            redirect_uri=config.SPOTIPY_REDIRECT_URI,
            scope=SPOTIFY_SCOPES,
            # open_browser=True by default, cache_handler can be default
        )
        # The following line will attempt to get a token, potentially opening the browser
        # if no valid cached token is found.
        sp = spotipy.Spotify(auth_manager=auth_manager)
        
        # Verify authentication by making a simple call
        sp.me() # This will raise SpotifyException if auth failed or token is invalid
        
        return sp

    except SpotifyOauthError as e:
        print(f"Spotify Authentication Error: {e}", file=sys.stderr)
        print("Please check your Spotify API credentials and redirect URI in your .env file and Spotify Developer Dashboard.", file=sys.stderr)
        sys.exit(1)
    except spotipy.SpotifyException as e: # Catch errors from sp.me() or other initial calls
        print(f"Spotify API Error after authentication: {e}", file=sys.stderr)
        print("There might be an issue with your token or permissions. Try removing the .cache file and re-authenticating.", file=sys.stderr)
        sys.exit(1)
    except Exception as e: # Catch any other unexpected errors during auth setup
        print(f"An unexpected error occurred during Spotify authentication: {e}", file=sys.stderr)
        sys.exit(1)
    ```
  * [ ] 任务2.1.6: （可选，但推荐）在 `main.py` 中临时添加代码以调用 `get_spotify_client()` 并打印 `sp.me()` 的结果，以手动测试认证流程。确保在提交前移除或注释掉此测试代码。
  * [ ] 任务2.1.7: 运行 `poetry run black .` 和 `poetry run flake8 .` 确保新文件符合代码风格且无linting错误。
  * [ ] 任务2.1.8: 将 `spotify/auth.py` 添加到Git并提交，提交信息如 "Implement Spotify OAuth 2.0 authentication flow"。

## Testing Requirements

**Guidance:** 对照ACs通过以下方式验证实施。

  * **Unit Tests:**

      * 创建 `tests/spotify/test_auth.py`。
      * **测试场景1 (成功认证 - 模拟 `spotipy`):**
          * 使用 `pytest-mock` 来 mock `spotipy.SpotifyOAuth` 和 `spotipy.Spotify`。
          * Mock `config` 模块变量。
          * 断言 `get_spotify_client` 在模拟的成功路径下返回一个 mock 的 `spotipy.Spotify` 实例。
          * 断言 `SpotifyOAuth` 被以正确的参数（client\_id, client\_secret, redirect\_uri, scope）实例化。
      * **测试场景2 (认证失败 - `SpotifyOauthError`):**
          * Mock `SpotifyOAuth` 的实例化或其获取token的方法以引发 `SpotifyOauthError`。
          * 使用 `pytest.raises(SystemExit)` 来断言 `get_spotify_client` 调用 `sys.exit(1)`。
          * （可选）捕获 `stderr` 并验证错误消息。
      * **测试场景3 (API调用失败 - `SpotifyException` after auth):**
          * Mock `SpotifyOAuth` to succeed but mock the `sp.me()` call within `get_spotify_client` to raise `spotipy.SpotifyException`.
          * 使用 `pytest.raises(SystemExit)` 来断言 `get_spotify_client` 调用 `sys.exit(1)`。
          * （可选）捕获 `stderr` 并验证错误消息。
      * **注意:** 单元测试真实的OAuth流程（打开浏览器等）很困难且不可靠。单元测试应专注于模块的逻辑和对`spotipy`库的正确使用（通过mocking）。

  * **Integration Tests:** N/A for this story in isolation, as it depends on external service and user interaction. Full auth flow is better tested manually or as part of E2E.

  * **Manual/CLI Verification:**

      * **首次运行 / 无缓存:**
          * 确保 `.env` 文件已正确配置了有效的Spotify API凭据和在Spotify Developer Dashboard中完全匹配的回调URI (e.g., `http://localhost:8888/callback`).
          * 删除任何现有的 `.cache*` 文件。
          * 在Python解释器或一个简单脚本中，导入并调用 `get_spotify_client()`。
          * 验证浏览器是否自动打开Spotify授权页面。
          * 完成授权流程。
          * 验证函数是否返回一个 `spotipy.Spotify` 实例，并且可以成功调用一个简单的方法，例如 `sp.me()`，并打印用户信息。
          * 验证是否在项目根目录生成了 `.cache` 文件 (文件名可能包含用户名)。
      * **后续运行 / 有缓存:**
          * 再次调用 `get_spotify_client()`。
          * 验证浏览器是否**没有**再次打开，并且函数直接返回了有效的 `spotipy.Spotify` 实例 (通过调用 `sp.me()` 验证)。
      * **无效凭据测试:**
          * 修改 `.env` 中的 `SPOTIPY_CLIENT_ID` 为无效值。
          * 调用 `get_spotify_client()`。验证是否打印了预期的错误消息并以非零状态码退出。
      * **用户拒绝授权 (模拟):**
          * 在浏览器打开授权页面时，选择"取消"或不授权。Spotipy应该能够处理此情况，并可能在其本地服务器上显示错误，或最终导致 `get_spotify_client` 中的异常。验证程序是否按AC5处理。

  * *(Hint: 参见 `docs/testing-strategy.md` 了解整体方法)*

-----

File: `ai/stories/epic2.story2.story.md`

# Story 2.2: 实现认证令牌的缓存与复用

**Status:** Completed

## Goal & Context

**User Story:** 作为应用程序，我应该缓存已获取的认证令牌，以便用户在后续运行应用时无需每次都重新授权，除非令牌过期或授权范围变更，从而提升用户体验。

**Context:** 此故事直接关联 Story 2.1。`spotipy` 库本身提供了默认的令牌缓存处理机制。本故事的重点是确保这个默认机制被正确利用和验证，而不是实现一个新的缓存系统。一个顺畅的、不需要每次都重新登录的用户体验对于CLI工具至关重要。

## Detailed Requirements

根据 `docs/epic2.md`：

  * `spotipy` 默认行为，需确保其正常工作。
  * 用户在令牌有效期内再次运行脚本时无需重新授权。

## Acceptance Criteria (ACs)

  * AC1: 当 Story 2.1 中的 `get_spotify_client()` 首次成功执行后，一个包含认证令牌信息的 `.cache` 文件（文件名通常为 `.cache` 或 `.cache-你的用户名`，具体取决于 `spotipy.SpotifyOAuth` 的 `cache_path` 或 `username` 参数，如果提供了的话；若未提供，则通常为 `.cache`）被创建在项目根目录（或 `spotipy` 决定的默认位置）。
  * AC2: 在 `.cache` 文件有效且未过期的情况下，后续调用 `get_spotify_client()` 时，不会提示用户重新进行浏览器授权。
  * AC3: 使用缓存令牌初始化的 `spotipy.Spotify` 客户端实例能够成功执行需要认证的API调用（例如 `sp.me()`）。
  * AC4: 如果手动删除 `.cache` 文件，下一次调用 `get_spotify_client()` 时会触发完整的浏览器授权流程（如 Story 2.1 中所定义）。

## Technical Implementation Context

**Guidance:** 使用以下细节进行实施。如果需要更广泛的上下文，请参阅链接的 `docs/` 文件。

  * **Relevant Files:**

      * Files to Create/Modify: N/A (主要是验证 Story 2.1 中 `spotify/auth.py` 的行为)
      * *(Hint: 参见 `docs/project-structure.md` 查看整体布局)*

  * **Key Technologies:**

      * `spotipy` (特别是 `spotipy.SpotifyOAuth` 的默认缓存行为)
      * File system (for verifying `.cache` file presence/absence)
      * *(Hint: 参见 `docs/tech-stack.md` 查看完整列表)*

  * **API Interactions / SDK Usage:**

      * `spotipy.SpotifyOAuth` 的 `cache_handler` 参数。默认情况下，`spotipy` 使用 `CacheFileHandler`，它会将令牌信息存储在本地文件中。本故事依赖此默认行为。我们不需要显式配置 `cache_path`，除非想改变默认位置。
      * `get_cached_token()` 方法是 `SpotifyOAuth` 的一部分，`spotipy.Spotify(auth_manager=...)` 会自动利用它。
      * *(Hint: 参见 `spotipy` 文档了解 `CacheFileHandler` 和令牌管理)*

  * **UI/UX Notes:** 用户体验的关键在于"无缝"的后续执行，无需重复授权。

  * **Data Structures:**

      * N/A
      * *(Hint: 参见 `docs/data-models.md` 了解关键项目数据结构)*

  * **Environment Variables:**

      * N/A for this story directly, but relies on `core.config` providing credentials to `SpotifyOAuth`.
      * *(Hint: 参见 `docs/environment-vars.md` 查看所有变量)*

  * **Coding Standards Notes:**

      * 无特定于此故事的代码，但验证步骤很重要。
      * *(Hint: 参见 `docs/coding-standards.md` 查看完整标准)*

## Tasks / Subtasks

此故事主要是验证性的，确保 Story 2.1 中实现的 `spotipy.SpotifyOAuth` 的默认行为符合预期。

  * [x] 任务2.2.1: (接续 Story 2.1 的手动测试) 首次成功运行 `get_spotify_client()` 并完成浏览器授权后，定位并确认在项目根目录（或用户主目录下的 `.config/spotipy/` 等，取决于spotipy版本和环境）生成了 `.cache` 文件（文件名可能是 `.cache` 或 `.cache-<username>`）。
  * [x] 任务2.2.2: 记录此 `.cache` 文件的时间戳。
  * [x] 任务2.2.3: 在短时间内（确保令牌未过期，通常Spotify令牌有效期为1小时）再次执行调用 `get_spotify_client()` 的脚本。
  * [x] 任务2.2.4: 验证此次调用**没有**打开浏览器进行授权。
  * [x] 任务2.2.5: 验证返回的 `spotipy.Spotify` 实例仍然可以成功执行API调用（如 `sp.me()`）。
  * [x] 任务2.2.6: 手动删除已生成的 `.cache` 文件。
  * [x] 任务2.2.7: 再次执行调用 `get_spotify_client()` 的脚本。
  * [x] 任务2.2.8: 验证此次调用**重新**触发了浏览器授权流程。
  * [x] 任务2.2.9: (文档化) 在 `spotify/auth.py` 的模块级文档字符串或相关函数的文档字符串中，简要说明 `spotipy` 的默认缓存行为及其对用户体验的影响。

## Testing Requirements

**Guidance:** 对照ACs通过以下方式验证实施。

  * **Unit Tests:**
      * 单元测试很难直接验证文件系统缓存的创建和复用，因为这涉及到 `spotipy` 的内部实现和外部状态。
      * 可以通过mock `CacheFileHandler` 的 `get_cached_token` 和 `save_token_to_cache` 方法来模拟缓存命中和缓存未命中的场景，从而测试 `SpotifyOAuth` 的逻辑分支，但这更多是测试 `spotipy` 自身，而非我们应用代码的直接逻辑，除非我们自定义了 `CacheHandler`。对于依赖默认行为，手动验证更直接。
  * **Integration Tests:** N/A for direct cache file testing.
  * **Manual/CLI Verification:**
      * **AC1 Verification:**
          * 执行 Story 2.1 的手动验证步骤，确保首次授权后 `.cache` 文件被创建。记下其位置。
      * **AC2 & AC3 Verification:**
          * 在 `.cache` 文件存在且有效（例如，授权后几分钟内）的情况下，重新运行调用 `get_spotify_client()` 的测试脚本。
          * **期望:** 不会弹出浏览器，脚本直接获得认证的 `sp` 对象，并且 `sp.me()` 调用成功。
      * **AC4 Verification:**
          * 手动从文件系统中删除 `.cache` 文件。
          * 再次运行调用 `get_spotify_client()` 的测试脚本。
          * **期望:** 浏览器重新弹出，要求用户进行Spotify授权。
  * *(Hint: 参见 `docs/testing-strategy.md` 了解整体方法)*

-----

File: `ai/stories/epic2.story3.story.md`

# Story 2.3: 处理认证错误与用户取消

**Status:** Completed

## Goal & Context

**User Story:** 作为应用程序，当用户认证失败（例如，拒绝授权、无效凭据）或在认证过程中取消操作时，我需要能够优雅地处理这些情况，并向用户提供清晰的反馈或退出程序。

**Context:** 此故事是 Story 2.1 (实现 Spotify OAuth 2.0 认证流程) 的扩展和健壮性增强。在实际的用户交互中，认证过程可能由于多种原因失败。应用程序需要能够识别这些失败，向用户提供有用的信息，并以可控的方式终止，而不是意外崩溃。

## Detailed Requirements

根据 `docs/epic2.md`：

  * 应用程序需要优雅处理认证失败。
  * 向用户提供清晰的反馈。
  * 在认证失败时退出程序。
  * Story 2.1 的 AC5 已经初步覆盖了此需求，本故事确保其被充分测试和考虑。

## Acceptance Criteria (ACs)

  * AC1: (扩展/验证 Story 2.1 AC5) 当 `spotipy.SpotifyOAuth` 在获取令牌时因用户在Spotify授权页面明确点击"取消"或关闭授权窗口而导致失败时，`get_spotify_client()` 函数能捕获相应的 `spotipy.SpotifyOauthError` (或类似错误)，向 `stderr` 打印一条指明用户已取消授权的特定消息，并以状态码 1 退出程序。
  * AC2: (扩展/验证 Story 2.1 AC5) 当提供的Spotify API凭据 (`SPOTIPY_CLIENT_ID`, `SPOTIPY_CLIENT_SECRET`) 无效，或 `SPOTIPY_REDIRECT_URI` 与Spotify Developer Dashboard中的配置不匹配，导致 `spotipy.SpotifyOAuth` 认证失败时，`get_spotify_client()` 函数能捕获 `spotipy.SpotifyOauthError`，向 `stderr` 打印一条指示凭据或回调URI可能存在问题的错误消息，并以状态码 1 退出程序。
  * AC3: 如果在认证流程中发生其他意外的 `spotipy` 相关异常（例如，网络问题导致无法连接到Spotify认证服务器），`get_spotify_client()` 函数能捕获通用的 `spotipy.SpotifyException` 或特定的网络异常，打印相关的错误信息，并以状态码 1 退出程序。
  * AC4: 所有打印到 `stderr` 的用户反馈错误消息都应清晰、易懂，并尽可能提供解决问题的建议（例如，"请检查您的 .env 文件中的 Spotify API 凭据和 Spotify Developer Dashboard 中的回调 URI 配置是否正确且匹配。"）。

## Technical Implementation Context

**Guidance:** 使用以下细节进行实施。如果需要更广泛的上下文，请参阅链接的 `docs/` 文件。

  * **Relevant Files:**

      * Files to Create/Modify:
          * `spotify_playlist_importer/spotify_playlist_importer/spotify/auth.py` (主要修改和增强错误处理逻辑)
      * *(Hint: 参见 `docs/project-structure.md` 查看整体布局)*

  * **Key Technologies:**

      * Python (`try-except` blocks, `sys.exit`, `print` to `sys.stderr`)
      * `spotipy` (异常类如 `SpotifyOauthError`, `SpotifyException`)
      * *(Hint: 参见 `docs/tech-stack.md` 查看完整列表)*

  * **API Interactions / SDK Usage:**

      * 重点在于捕获 `spotipy.SpotifyOAuth` 在尝试获取令牌时可能抛出的各种异常。
      * `spotipy.oauth2.SpotifyOauthError`: 通常用于指示OAuth流程本身的问题，如无效的客户端、无效的grant、回调错误等。
      * `spotipy.exceptions.SpotifyException`: 更通用的 `spotipy` 异常。
      * *(Hint: 查阅 `spotipy` 文档以了解其异常层次结构和何时可能抛出它们)*

  * **UI/UX Notes:** 错误消息对用户至关重要。它们应该是指导性的，而不是技术性的堆栈跟踪（除非在DEBUG模式下）。

  * **Data Structures:**

      * N/A
      * *(Hint: 参见 `docs/data-models.md` 了解关键项目数据结构)*

  * **Environment Variables:**

      * 验证时需要操控这些变量来触发错误场景。
      * *(Hint: 参见 `docs/environment-vars.md` 查看所有变量)*

  * **Coding Standards Notes:**

      * 在 `get_spotify_client()` 函数中使用更细致的 `except` 块来捕获不同类型的 `spotipy` 异常，以便提供更具体的错误消息。
      * 确保 `sys.exit(1)` 在所有预期的错误路径上被调用。
      * *(Hint: 参见 `docs/coding-standards.md` 查看完整标准和错误处理策略)*

## Tasks / Subtasks

大部分实现已在 Story 2.1 的任务 T2.1.5 中初步完成。此故事的任务主要是完善和验证这些错误处理路径。

  * [x] 任务2.3.1: 回顾并细化 `spotify/auth.py` 中 `get_spotify_client()` 函数的 `try-except` 块，确保：
      * `SpotifyOauthError` 被优先捕获。
      * 针对不同原因的 `SpotifyOauthError` (如果 `spotipy` 提供了区分方式，例如通过错误消息内容)，可以打印略有不同的提示。例如，如果错误消息中包含 "redirect\_uri\_mismatch"，则特别提示检查回调URI。
      * 通用的 `spotipy.SpotifyException` 在之后被捕获。
      * 一个最终的 `except Exception` 块用于捕获任何其他未预料到的错误，并打印通用错误消息。
  * [x] 任务2.3.2: 为每种预期的错误情况（无效客户端ID/密钥，不匹配的回调URI，用户取消）设计清晰的用户友好错误消息。
      * 例如，对于凭据/回调问题: `"Spotify Authentication Failed: Could not get access token. Please verify that SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, and SPOTIPY_REDIRECT_URI in your .env file are correct and match the settings in your Spotify Developer Dashboard. Error details: {e}"`
      * 例如，对于用户取消 (可能需要从错误消息 `e` 中推断): `"Spotify Authorization Cancelled: User did not grant permission or cancelled the authorization process."`
  * [x] 任务2.3.3: 确保在所有捕获到这些认证相关异常的路径中，程序都使用 `sys.exit(1)` 退出。
  * [x] 任务2.3.4: 对 `spotify/auth.py` 运行 linting 和 formatting 工具。
  * [x] 任务2.3.5: 更新或添加Git提交，如果对 `auth.py` 进行了显著的错误处理逻辑修改，提交信息如 "Refine Spotify authentication error handling"。