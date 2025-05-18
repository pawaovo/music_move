# Spotify 歌单导入工具

一个 Python 命令行工具，用于将文本文件中的歌曲列表导入到您的 Spotify 账户中，并创建一个新的播放列表。

## 功能特性

* **歌曲列表解析**: 支持解析特定格式的文本文件，每行包含“歌曲名称 - 艺人1 / 艺人2”。
* **Spotify 歌曲搜索**: 在 Spotify 庞大的曲库中搜索您提供的歌曲。
* **自动匹配**: 默认选择 Spotify 搜索结果中的第一个作为匹配项。
* **播放列表创建**: 在您的 Spotify 账户中自动创建一个新的播放列表。
* **歌曲导入**: 将所有成功匹配的歌曲添加到新创建的播放列表中。
* **详细报告**: 提供一个清晰的报告，列出哪些歌曲成功匹配并导入，哪些未能找到。

## 安装指南

### 先决条件

* Python 3.9 或更高版本。您可以从 [python.org](https://www.python.org/downloads/) 下载并安装。
* pip (Python 包安装器)，通常随 Python 一起安装。
* 一个有效的 Spotify 账户 (免费或 Premium 均可)。

### 步骤

1.  **克隆或下载项目**:
    ```bash
    git clone https://your-repository-url/spotify-playlist-importer.git # 替换为您的仓库URL
    cd spotify-playlist-importer
    ```
    如果您不是通过 git 克隆，而是下载的 ZIP 文件，请解压到您选择的目录。

2.  **创建并激活虚拟环境 (推荐)**:
    在项目根目录下执行：
    ```bash
    python -m venv venv
    ```
    激活虚拟环境：
    * Windows: `venv\Scripts\activate`
    * macOS/Linux: `source venv/bin/activate`

3.  **安装依赖**:
    在项目根目录下 (确保虚拟环境已激活) 执行：
    ```bash
    pip install -r requirements.txt
    ```
    (`requirements.txt` 文件将在后续步骤中创建，主要包含 `spotipy`, `python-dotenv`, 以及您选择的CLI库如 `click` 或 `typer`)

4.  **设置 Spotify API 凭据**:
    a.  访问 Spotify Developer Dashboard: [https://developer.spotify.com/dashboard/](https://developer.spotify.com/dashboard/)
    b.  登录您的 Spotify 账户。
    c.  创建一个新的应用程序 (App)。
        * 给您的应用取一个名字 (例如："我的歌单导入工具") 和描述。
        * 在应用设置中，找到 `Client ID` 和 `Client Secret`。
        * **重要**: 设置 `Redirect URIs`。对于本地运行的 CLI 工具，一个常用的回调 URI 是 `http://localhost:8888/callback` 或 `http://localhost/callback`。您在此处设置的 URI **必须**与您在下一步 `.env` 文件中配置的 `SPOTIPY_REDIRECT_URI` 完全一致。
    d.  在项目根目录下，复制 `.env.example` 文件并重命名为 `.env`。
        ```bash
        cp .env.example .env
        ```
    e.  编辑 `.env` 文件，填入您的 Spotify 应用凭据：
        ```dotenv
        SPOTIPY_CLIENT_ID='您的Client_ID'
        SPOTIPY_CLIENT_SECRET='您的Client_Secret'
        SPOTIPY_REDIRECT_URI='您在Spotify Dashboard设置的回调URI'
        ```
        **注意**: `.env` 文件包含敏感信息，已默认添加到 `.gitignore` 中，请勿将其提交到公共代码库。

## 使用方法

在项目根目录下，激活虚拟环境后，使用以下命令运行脚本：

```bash
python main.py [选项] <歌曲文件路径>
````

### 命令行参数和选项

  * `<歌曲文件路径>`: (必需) 包含歌曲列表的文本文件的路径。文件格式要求：
      * 每行一首歌。
      * 歌曲格式为: `歌曲名称 - 艺人1 / 艺人2` (例如: `Bohemian Rhapsody - Queen` 或 `Stairway to Heaven - Led Zeppelin / Jimmy Page`)。
      * 注意 " - " (空格-连字符-空格) 是歌曲名和艺人名之间的分隔符。
      * 多个艺人用 " / " (空格/空格) 分隔。
  * `--playlist-name TEXT`: (可选) 指定在 Spotify 上创建的新播放列表的名称。默认为 "导入的歌曲 YYYY-MM-DD"。
  * `--public BOOLEAN`: (可选) 是否将新创建的播放列表设为公开。默认为 `False` (即私有播放列表)。
  * `--description TEXT`: (可选) 为新创建的播放列表添加描述。默认为 "通过 Python 脚本导入的歌曲"。
  * `--output-report TEXT`: (可选) 指定匹配报告输出的文件名。默认为 `matching_report_YYYY-MM-DD_HHMMSS.txt`。

### 示例

```bash
python main.py my_song_list.txt
```

```bash
python main.py "/path/to/my songs.txt" --playlist-name "我的经典收藏" --public True
```

### 首次运行

首次运行脚本时，或者当认证令牌过期后，脚本会自动打开您的默认浏览器，引导您登录 Spotify 并授权应用程序访问您的账户。成功授权后，浏览器可能会显示一个成功页面或重定向到一个本地 URL (您在 Spotify Dashboard 设置的回调 URI)。之后您可以关闭浏览器窗口，脚本将继续执行。

## 输出

脚本执行完毕后，会在控制台输出总结信息，并生成一个详细的匹配报告文件，内容包括：

  * 原始输入的每一行歌曲。
  * 解析出的歌曲名和艺人。
  * 匹配状态 (已匹配 / 未找到 / 搜索出错)。
  * 如果匹配成功，会显示 Spotify 上的歌曲名称、艺人、ID 和 URI。
  * 如果播放列表创建成功，会显示新播放列表的链接。

## 常见问题与故障排除

  * **认证失败/回调URI错误**:
      * 确保您在 Spotify Developer Dashboard 中设置的 `Redirect URI` 与 `.env` 文件中的 `SPOTIPY_REDIRECT_URI` **完全一致** (包括 `http://` 或 `https://` 以及尾部的 `/`)。
      * 检查 `.env` 文件中的 `SPOTIPY_CLIENT_ID` 和 `SPOTIPY_CLIENT_SECRET` 是否正确无误。
  * **`requests.exceptions.SSLError`**:
      * 这可能与您系统上的 SSL 证书配置有关。尝试更新 `certifi` 包：`pip install --upgrade certifi`。
  * **歌曲匹配不准确**:
      * 脚本默认选择搜索结果的第一个。如果匹配不佳，可能是因为歌曲信息不够具体，或者 Spotify 的搜索排序问题。未来版本可能会考虑更高级的匹配逻辑。
  * **找不到 `requirements.txt` 或 `.env.example`**:
      * 确保您在正确的项目根目录下执行命令。

## 贡献指南 (可选)

如果您想为这个项目做出贡献：

1.  Fork 本仓库。
2.  创建一个新的分支 (`git checkout -b feature/你的特性`)。
3.  提交您的更改 (`git commit -am '添加某个特性'`)。
4.  将您的分支推送到 Origin (`git push origin feature/你的特性`)。
5.  创建一个新的 Pull Request。

请确保更新测试用例，并遵循项目的编码标准。

## 许可证

本项目采用 [MIT许可证](https://www.google.com/search?q=LICENSE.txt) (如果适用，您需要创建一个 `https://www.google.com/search?q=LICENSE.txt` 文件)。

```

---

**关于此 `README.md` 草稿的说明:**

* **占位符**: `https://your-repository-url/spotify-playlist-importer.git` 需要替换为您实际的代码仓库 URL。`https://www.google.com/search?q=LICENSE.txt` 部分也需要您确定许可证。
* **`requirements.txt` 和 `.env.example`**: 这些文件我们会在后续步骤中定义其内容。
* **CLI 库**: 我在示例中使用了通用的 `python main.py [选项] <参数>` 格式。如果您选择使用 `Click` 或 `Typer`，这些库会自动生成帮助信息，可以进一步简化使用说明。
* **错误处理**: 提到了一些常见的错误，实际开发中可能会遇到更多，可以后续补充。