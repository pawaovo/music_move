# Music Move - Spotify 播放列表导入工具

Music Move 是一个综合性的 Web 应用，可以帮助用户将其他音乐平台的播放列表无缝导入到 Spotify。该项目由 Next.js 前端和 FastAPI 后端组成。

## 功能特点

- 导入纯文本格式的歌曲列表到 Spotify 播放列表
- 智能歌曲匹配和识别算法，提高匹配准确率
- 支持批量处理和并发请求，加快导入速度
- 用户友好的网页界面，方便操作
- Spotify OAuth 认证流程，安全可靠

## 项目结构

- `music_move/` - Next.js 前端代码
- `spotify_playlist_importer/` - FastAPI 后端代码
- `docs/` - 项目文档

## 快速开始

### 前提条件

1. Node.js 16+ 和 npm/yarn
2. Python 3.9+
3. Spotify 开发者账号和应用

### 本地开发设置

1. 克隆仓库

```bash
git clone https://github.com/yourusername/music_move.git
cd music_move
```

2. 安装后端依赖

```bash
cd spotify_playlist_importer
pip install -r requirements.txt
```

3. 配置 Spotify API 凭证

在 `spotify_playlist_importer` 目录中，复制示例配置文件：

```bash
cp spotify_config.json.example spotify_config.json
```

然后编辑 `spotify_config.json`，添加你从 [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/) 获取的 Client ID 和 Client Secret。

4. 安装前端依赖

```bash
cd ../music_move
npm install
# 或者使用 yarn
yarn install
```

5. 启动后端服务

```bash
cd ../spotify_playlist_importer
python run_fixed_api.py
```

6. 启动前端服务

```bash
cd ../music_move
npm run dev
# 或者使用 yarn
yarn dev
```

7. 访问应用

在浏览器中打开 http://localhost:3000 来访问应用。

## 部署指南

详细的部署步骤可以参考 [部署指南文档](docs/deployment_guide.md)，其中包括：

- 如何部署 Next.js 前端到 Vercel
- 如何部署 FastAPI 后端到 Render
- 配置环境变量和 Spotify API 设置
- CORS 设置和安全考虑

## API 参考

HTTP API 端点的详细信息可以在后端服务运行时通过访问 `/docs` 路径找到 (例如 http://localhost:8888/docs)。这是由 FastAPI 自动生成的 Swagger 文档。

## 贡献指南

1. Fork 仓库
2. 创建你的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交你的改动 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开一个 Pull Request

## 许可证

该项目采用 MIT 许可证 - 详情请查看 LICENSE 文件。 