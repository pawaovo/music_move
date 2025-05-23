# 批量处理模块 (batch_processor)

## 概述

批量处理模块提供了从文本文件批量导入歌曲列表并搜索Spotify匹配的功能。该模块包含两个主要组件：
- `parse_song_line`: 解析单行歌曲文本为标题和艺术家列表
- `process_song_list_file`: 异步处理整个文件，包含标准化和Spotify搜索

## 功能详情

### 歌曲行解析 (`parse_song_line`)

```python
parse_song_line(line: str) -> Tuple[Optional[str], List[str]]
```

#### 支持的格式：
- `"Title - Artist1 / Artist2"` - 标准格式，带有多位艺术家
- `"Title - Artist"` - 标准格式，单一艺术家
- `"Title"` - 仅标题
- `" - Artist"` - 仅艺术家（标题为None）

#### 特殊处理：
- 使用`rsplit`正确处理标题中可能包含的连字符
- 处理多位艺术家用" / "分隔的情况
- 处理空字符串和只包含空格的情况
- 处理仅包含艺术家的情况（如" - Artist"）

#### 返回值：
- `(title, artists)`，其中title可能为None，artists是字符串列表

### 文件批量处理 (`process_song_list_file`)

```python
async process_song_list_file(
    file_path: str, 
    normalizer,  # TextNormalizer实例
    spotify_search_func,  # 异步搜索函数
    on_result_callback = None  # 可选回调函数
) -> Tuple[int, int, int]
```

#### 参数：
- `file_path`: 包含歌曲列表的文本文件路径
- `normalizer`: TextNormalizer实例，用于标准化歌曲标题和艺术家名称
- `spotify_search_func`: 异步函数，接收ParsedSong对象并返回(MatchedSong对象, 错误消息)
- `on_result_callback`: 可选的异步回调函数，处理每首歌曲的搜索结果

#### 处理流程：
1. 读取文件中的每一行
2. 使用`parse_song_line`解析成标题和艺术家
3. 使用提供的`normalizer`标准化标题和艺术家
4. 创建`ParsedSong`对象
5. 调用`spotify_search_func`在Spotify上搜索歌曲
6. 如果提供了回调函数，调用回调函数处理结果
7. 统计成功匹配和失败匹配的数量

#### 返回值：
- 三元组 `(总歌曲数, 成功匹配数, 失败匹配数)`

## 使用示例

### 基本使用

```python
import asyncio
from spotify_playlist_importer.utils.text_normalizer import TextNormalizer
from spotify_playlist_importer.spotify.async_client import search_song_on_spotify_async
from spotify_playlist_importer.core.batch_processor import process_song_list_file

async def main():
    # 创建TextNormalizer实例
    normalizer = TextNormalizer()
    
    # 创建异步Spotify客户端
    async with AsyncSpotifyClient(auth_token) as client:
        # 定义回调函数
        async def on_result(original_line, title, artists, norm_title, norm_artists, search_result):
            if search_result:
                print(f"找到匹配: {original_line} -> {search_result.name}")
            else:
                print(f"未找到匹配: {original_line}")
        
        # 处理文件
        total, matched, failed = await process_song_list_file(
            "songs.txt",
            normalizer,
            lambda parsed_song: search_song_on_spotify_async(client, parsed_song),
            on_result
        )
        
        print(f"处理完成! 总计: {total}, 成功: {matched}, 失败: {failed}")

asyncio.run(main())
```

### 在命令行工具中使用

本模块主要在命令行工具中使用，通过以下步骤：

1. 用户提供包含歌曲列表的文本文件
2. 使用`process_song_list_file`处理该文件
3. 对于每首找到匹配的歌曲，收集其URI
4. 创建新播放列表并将匹配的歌曲添加到播放列表中

## 测试

模块中的函数已经通过全面的单元测试验证，测试用例包括：
- 各种格式的歌曲行解析测试
- 空文件处理测试
- 不存在文件的错误处理测试
- 成功匹配和失败匹配的回调处理测试

测试代码位于`tests/core/test_batch_processor.py`。 