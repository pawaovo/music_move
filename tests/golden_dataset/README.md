# Spotify 歌曲匹配黄金标准数据集

本目录包含用于测试和评估Spotify歌曲匹配算法的黄金标准数据集及相关工具。

## 数据集说明

黄金标准数据集是一个包含已知歌曲及其在Spotify上的匹配结果的集合，用于评估匹配算法的准确性、优化匹配参数，并防止代码更改引入回归问题。

数据集结构:
```json
[
  {
    "input": {
      "title": "歌曲标题",
      "artists": ["艺术家1", "艺术家2"],
      "original_line": "歌曲标题 - 艺术家1 / 艺术家2"
    },
    "expected_match": {
      "spotify_id": "Spotify歌曲ID",
      "name": "Spotify上的歌曲名称",
      "artists": ["Spotify艺术家1", "Spotify艺术家2"],
      "uri": "spotify:track:xxxx",
      "album_name": "专辑名称",
      "duration_ms": 12345
    },
    "variants": []  // 可选的变体匹配
  },
  // ...更多歌曲条目
]
```

## 工具脚本

本目录包含以下用于创建和使用黄金标准数据集的工具脚本：

1. `create_golden_dataset.py`: 从歌曲列表文件创建黄金标准数据集
   ```bash
   python create_golden_dataset.py yunmusic.txt --output golden_dataset.json --sample-size 100
   ```

2. `evaluate_matching.py`: 使用黄金标准数据集评估匹配算法性能
   ```bash
   python evaluate_matching.py golden_dataset.json --output evaluation_report.json --verbose
   ```

## 使用方法

### 创建黄金标准数据集

1. 准备歌曲列表文件，每行一首歌曲，格式为 "标题 - 艺术家1 / 艺术家2"
2. 运行创建脚本
   ```bash
   python create_golden_dataset.py 歌曲列表文件路径 --output 输出文件路径 --sample-size 样本大小
   ```
3. 创建脚本会自动从完整歌曲列表中抽样并获取Spotify的匹配结果

### 评估匹配算法性能

1. 运行评估脚本
   ```bash
   python evaluate_matching.py 数据集路径 --output 报告路径 --verbose
   ```
2. 查看生成的报告文件，了解匹配准确率和其他指标

### 在单元测试中使用

项目的单元测试文件 `tests/test_golden_dataset_matching.py` 展示了如何在单元测试中使用黄金标准数据集：

```python
from spotify_playlist_importer.utils.enhanced_matcher import get_best_enhanced_match

# 加载黄金标准数据集
with open('tests/golden_dataset/golden_dataset.json') as f:
    dataset = json.load(f)

# 使用数据集测试匹配函数
for entry in dataset:
    if entry.get("expected_match"):
        result = get_best_enhanced_match(
            entry["input"]["title"],
            entry["input"]["artists"],
            candidates  # 模拟的候选结果
        )
        
        # 验证匹配是否正确
        assert result["id"] == entry["expected_match"]["spotify_id"]
```

## 数据集维护

为保持黄金标准数据集的有效性和准确性，建议：

1. 定期更新数据集（例如每季度），以适应Spotify目录的变化
2. 保留多个版本的数据集，特别是在重大算法更改前后
3. 确保数据集包含各种匹配场景：
   - 单一艺术家与多艺术家合作
   - 带括号的标题（如Live版本、Remix等）
   - 不同语言的歌曲（中文、英文等）
   - 罕见或有挑战性的匹配案例

## 性能测试

除了准确性测试外，还可以结合 `tests/test_performance_matching.py` 进行性能测试，以评估匹配算法在不同工作负载下的性能表现。性能测试可以帮助识别潜在的瓶颈并优化匹配流程。

性能测试包括：
- 批量处理效率测试
- 不同匹配策略的性能比较
- 内存使用分析
- 阈值参数对匹配率和性能的影响

## 注意事项

- 创建数据集需要有效的Spotify API凭证（CLIENT_ID 和 CLIENT_SECRET）
- 创建大型数据集时可能受到Spotify API速率限制的影响
- 数据集创建脚本会自动处理API错误和重试
- 为了测试的可重复性，create_golden_dataset.py默认使用模拟数据，可以修改代码使用真实的API调用 