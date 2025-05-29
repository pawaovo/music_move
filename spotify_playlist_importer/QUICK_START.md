# Spotify歌单导入工具快速入门指南

本指南将帮助您快速设置和使用Spotify歌单导入工具。此工具允许您将文本格式的歌曲列表导入到Spotify播放列表中。

## 1. 前提条件

- Python 3.7 或更高版本
- Spotify账户
- Spotify开发者应用程序（将在下面的步骤中创建）

## 2. 安装

克隆或下载本仓库后，在项目目录中安装依赖项：

```bash
pip install -r requirements.txt
```

## 3. 创建Spotify开发者应用

1. 访问 [Spotify开发者控制台](https://developer.spotify.com/dashboard/)
2. 登录您的Spotify账户
3. 点击"创建应用程序"按钮
4. 填写应用信息：
   - 名称：例如 "My Playlist Importer"
   - 描述：例如 "导入歌曲到Spotify"
   - 重定向URI：添加 `http://127.0.0.1:8888/callback`
5. 同意条款并点击"创建"
6. 创建后，您可以在应用程序页面看到您的"Client ID"和"Client Secret"
7. 保存这些信息，将在下一步中使用

## 4. 配置API凭据

我们提供了一个简单的脚本来帮助创建必要的配置文件：

```bash
python spotify_playlist_importer/create_env.py
```

按照提示输入您的Spotify客户端ID、密钥和回调URI。这将创建一个`.env`文件，用于存储您的API凭据。

或者，您也可以手动创建一个`.env`文件，内容如下：

```
SPOTIPY_CLIENT_ID=your_client_id_here
SPOTIPY_CLIENT_SECRET=your_client_secret_here
SPOTIPY_REDIRECT_URI=http://127.0.0.1:8888/callback
```

## 5. 准备歌曲列表

创建一个文本文件（例如`songs.txt`），每行包含一首歌曲，格式为：

```
歌曲名 - 艺术家名
歌曲名 - 艺术家1 / 艺术家2
```

例如：

```
Shape of You - Ed Sheeran
See You Again - Wiz Khalifa / Charlie Puth
Blinding Lights - The Weeknd
```

## 6. 运行工具

现在您可以运行工具来导入您的歌曲列表：

```bash
python -m spotify_playlist_importer.main_async batch-import songs.txt --output-report matching_report.txt
```

### 首次运行的授权过程

首次运行时，您需要完成Spotify授权流程：

1. 程序会自动打开浏览器，引导您登录Spotify
2. 登录后，点击"同意"授权应用程序访问您的账户
3. 浏览器将被重定向到一个新的页面
4. **关键步骤**：复制浏览器地址栏中的完整URL
5. 返回命令行窗口，粘贴URL并按回车键
6. 此过程仅需在首次运行时完成，之后会自动使用缓存的令牌

## 7. 查看结果

成功执行后，会创建一个新的Spotify播放列表，并显示匹配结果。匹配报告将被保存到您指定的文件中，如上面例子中的`matching_report.txt`。

## 8. 常用选项

```bash
# 指定播放列表名称
--playlist-name "我的自定义播放列表"

# 创建公开播放列表
--public

# 添加播放列表描述
--description "这是我导入的歌曲"

# 设置并发数量（默认10）
--concurrency 5

# 设置批处理大小（默认50）
--batch-size 10
```

## 9. 故障排除

- **授权问题**: 如果遇到授权问题，可以删除`.cache`文件并重新运行
- **API错误**: 确保您的Spotify开发者应用有正确的回调URI
- **匹配问题**: 尝试修改歌曲列表中的格式，或使用更明确的艺术家名

## 10. 高级配置

如果需要更改更多高级配置，可以编辑`spotify_config.json`文件。您可以查看`spotify_config.json.example`中的示例配置和说明。

祝您使用愉快！ 