# Spotify 搜索脚本

这个Python脚本使用Spotify Web API来根据歌曲名和艺术家名搜索歌曲，并显示搜索结果。

## 准备工作

1. 首先，你需要安装必要的Python包：

```bash
pip install -r requirements.txt
```

2. 你需要在Spotify开发者平台创建一个应用以获取API凭证：
   - 访问 [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)
   - 登录你的Spotify账户
   - 点击"Create an App"
   - 填写应用名称和描述
   - 获取Client ID和Client Secret

3. 创建`.env`文件：
   - 在项目根目录（或指定路径如`D:\ai\music_move\.env`）创建一个名为`.env`的文件
   - 添加以下内容，替换为你的实际凭证：

```
SPOTIFY_CLIENT_ID=你的客户端ID
SPOTIFY_CLIENT_SECRET=你的客户端密钥
```

## 基础版使用方法

### 歌曲名+艺术家名搜索

基础版脚本 `spotify_search.py` 提供使用歌曲名和艺术家名搜索的功能：

```bash
python spotify_search.py "歌曲名" "艺术家名"
```

例如：

```bash
python spotify_search.py "会魔法的老人" "法老"
```

### 仅歌曲名搜索

如果你只想使用歌曲名搜索，可以使用 `spotify_search_by_track.py` 脚本：

```bash
python spotify_search_by_track.py "歌曲名"
```

例如：

```bash
python spotify_search_by_track.py "会魔法的老人"
```

## 增强版使用方法

### 歌曲名+艺术家名搜索（增强版）

增强版脚本 `spotify_search_extended.py` 提供更多功能选项：

```bash
python spotify_search_extended.py "歌曲名" "艺术家名" [选项]
```

可用选项：
- `-d, --detailed`: 显示详细信息（包括专辑、发行日期、时长等）
- `-l, --limit NUMBER`: 设置最大结果数量（默认：10）
- `-s, --save`: 将结果保存为JSON文件
- `-o, --output FILENAME`: 指定JSON输出文件名（默认使用时间戳）

例如：

```bash
# 显示详细信息
python spotify_search_extended.py "会魔法的老人" "法老" --detailed

# 显示15条结果
python spotify_search_extended.py "会魔法的老人" "法老" --limit 15

# 保存结果到JSON文件
python spotify_search_extended.py "会魔法的老人" "法老" --save

# 保存结果到指定文件
python spotify_search_extended.py "会魔法的老人" "法老" --save --output results.json
```

### 仅歌曲名搜索（增强版）

如果你只想使用歌曲名搜索，但需要更多功能选项，可以使用 `spotify_search_by_track_extended.py` 脚本：

```bash
python spotify_search_by_track_extended.py "歌曲名" [选项]
```

可用选项与 `spotify_search_extended.py` 相同：

```bash
# 显示详细信息
python spotify_search_by_track_extended.py "会魔法的老人" --detailed

# 显示15条结果
python spotify_search_by_track_extended.py "会魔法的老人" --limit 15

# 保存结果到JSON文件
python spotify_search_by_track_extended.py "会魔法的老人" --save
```

## 输出示例

基础版输出：
```
2023-xx-xx xx:xx:xx,xxx - INFO - 搜索歌曲: 会魔法的老人, 艺术家: 法老
2023-xx-xx xx:xx:xx,xxx - INFO - 搜索查询: track:会魔法的老人 artist:法老
2023-xx-xx xx:xx:xx,xxx - INFO - 找到 X 条结果:
2023-xx-xx xx:xx:xx,xxx - INFO - 1. 歌曲: 歌曲名1 - 艺术家: 艺术家名1
2023-xx-xx xx:xx:xx,xxx - INFO - 2. 歌曲: 歌曲名2 - 艺术家: 艺术家名2
...
```

增强版详细输出：
```
2023-xx-xx xx:xx:xx,xxx - INFO - 搜索歌曲: 会魔法的老人, 艺术家: 法老
2023-xx-xx xx:xx:xx,xxx - INFO - 搜索查询: track:会魔法的老人 artist:法老
2023-xx-xx xx:xx:xx,xxx - INFO - 找到 X 条结果:
2023-xx-xx xx:xx:xx,xxx - INFO - 1. 歌曲: 歌曲名1 - 艺术家: 艺术家名1
2023-xx-xx xx:xx:xx,xxx - INFO -    专辑: 专辑名1
2023-xx-xx xx:xx:xx,xxx - INFO -    发行日期: 2023-01-01
2023-xx-xx xx:xx:xx,xxx - INFO -    时长: 3分45秒
2023-xx-xx xx:xx:xx,xxx - INFO -    热门度: 85/100
2023-xx-xx xx:xx:xx,xxx - INFO -    Spotify链接: https://open.spotify.com/track/...
...
``` 