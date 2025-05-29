# 贡献指南

感谢您考虑为 Spotify 歌单导入工具项目贡献代码！以下是参与本项目的一些指南。

## 开发环境设置

1. 克隆仓库并进入项目目录
   ```bash
   git clone https://github.com/yourusername/spotify-playlist-importer.git
   cd spotify-playlist-importer
   ```

2. 创建并激活虚拟环境
   ```bash
   python -m venv venv
   source venv/bin/activate  # 在Windows上: venv\Scripts\activate
   ```

3. 安装开发依赖
   ```bash
   pip install -e ".[dev]"
   ```

4. 复制配置示例文件并根据需要修改
   ```bash
   cp config.example.json config.json
   # 编辑 config.json 设置你的Spotify API凭据
   ```

## 代码风格

- 遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 代码风格指南
- 使用 4 个空格进行缩进
- 最大行长度为 100 字符
- 使用有意义的变量名和函数名
- 添加类型注解

我们使用以下工具保证代码质量：
- flake8：代码风格检查
- mypy：静态类型检查
- pytest：单元测试

## 提交变更的流程

1. 创建一个新的分支
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. 进行您的更改

3. 运行测试确保代码正常工作
   ```bash
   python -m pytest
   ```

4. 提交您的更改
   ```bash
   git commit -m "feat: 添加了某项功能"
   ```
   我们遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范

5. 推送到您的分支
   ```bash
   git push origin feature/your-feature-name
   ```

6. 提交 Pull Request

## 代码审查

所有代码都需要经过审查后才能合并。请确保：

- 代码通过所有自动化测试
- 遵循项目代码风格
- 包含适当的文档
- 针对新功能添加单元测试

## 项目结构

```
spotify_playlist_importer/
├── docs/                     # 文档
├── spotify_playlist_importer/ # 源代码
│   ├── core/                 # 核心功能
│   ├── spotify/              # Spotify API交互
│   ├── utils/                # 工具函数
│   ├── main.py               # 主程序入口
│   └── main_async.py         # 异步主程序入口
└── tests/                    # 测试代码
    ├── core/                 # 核心功能测试
    ├── spotify/              # Spotify API交互测试
    └── utils/                # 工具函数测试
```

## 添加新功能

1. 确保理解现有代码和项目结构
2. 遵循模块化设计原则
3. 编写全面的测试用例
4. 更新相关文档

## 报告问题

如果您发现问题但没有时间修复，请在 GitHub Issues 中报告，包括：

- 问题的简要描述
- 复现步骤
- 预期行为
- 实际行为
- 环境信息（操作系统、Python版本等）

## 资源

- [项目README](README.md)
- [开发者文档](docs/)

再次感谢您的贡献！ 