# TuneMyMusic - 音乐迁移工具

这是一个用于在不同音乐平台之间迁移播放列表和歌曲的工具。

## 项目结构

项目使用 Next.js 15 和 Tailwind CSS 构建，结构如下：

```
/
├── app/                  # 应用页面
│   ├── page.tsx          # 首页 - 选择待移动的播放列表
│   ├── edit/             # 编辑播放列表页面
│   ├── summary/          # 概要页面
│   ├── complete/         # 完成页面
│   ├── globals.css       # 全局样式
│   └── layout.tsx        # 布局组件
├── components/           # 共享组件
│   ├── ui/               # UI 组件库
│   ├── theme-provider.tsx # 主题提供者
│   └── spotify-logo.tsx  # Spotify 图标
├── hooks/                # 自定义钩子
│   ├── use-mobile.tsx    # 移动设备检测
│   └── use-toast.ts      # 提示消息
├── lib/                  # 工具函数
│   └── utils.ts          # 通用工具
├── public/               # 静态资源
└── styles/               # 其他样式
```

## 页面流程

1. **首页** (`/`): 用户可以输入歌曲列表或选择要迁移的播放列表。
2. **编辑页面** (`/edit`): 用户可以编辑要迁移的播放列表。
3. **概要页面** (`/summary`): 显示迁移概要和确认信息。
4. **完成页面** (`/complete`): 显示迁移完成状态和结果。

## 页面效果说明

### 首页 (/)
- 顶部有TuneMyMusic的标志和导航栏
- 中央有"选择待移动的播放列表"标题
- 主要内容区显示一个深色卡片，其中包含：
  - "输入您的歌曲列表"提示
  - 示例文本区域，显示"The Beatles - Hey Jude"和"Beyoncé - Formation"等示例
  - 底部有一个紫色圆形按钮"转换歌曲列表"，点击后导航到/edit页面

### 编辑页面 (/edit)
- 顶部同样有TuneMyMusic标志和导航
- 主内容区是一个模态窗口，标题为"编辑播放列表"
- 包含"转移至"输入框和playlist选择区域
- 有两个保存/开始转移按钮，点击后导航到/summary页面
- 背景中有一些装饰性元素

### 概要页面 (/summary)
- 顶部有TuneMyMusic导航栏
- 中央有"概要"标题和显示步骤"2/3"
- 主要内容是转移卡片，显示：
  - 从音乐来源转到Spotify的指示器
  - "正在转移1播放列表（2 曲目）"的状态
  - 播放列表项目列表，包括"My Playlist"和两首歌曲
  - 底部有一个紫色"开始转移"按钮，点击后导航到/complete页面

### 完成页面 (/complete)
- 顶部有TuneMyMusic导航栏
- 主内容是一个深色卡片，显示：
  - 成功图标和"转移完成！"的消息
  - 平台图标（从未知来源到Spotify）
  - 播放列表项目列表，每项都有绿色完成指示器
  - 底部有紫色"继续"按钮，点击后回到首页

## 技术栈

- **Next.js 15**: React 框架
- **Tailwind CSS**: 样式系统
- **Radix UI**: UI组件基础
- **Lucide React**: 图标库

## 安装和运行

```bash
# 安装依赖
npm install --legacy-peer-deps

# 开发模式运行
npm run dev

# 构建项目
npm run build

# 启动生产服务器
npm start
```

## 后续计划

- 统一所有页面为 Spotify 风格
- 添加更多音乐平台支持
- 优化移动端体验 