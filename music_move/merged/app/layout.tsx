import type { Metadata } from 'next'
import './globals.css'
import Providers from './providers'

export const metadata: Metadata = {
  title: 'MusicMove - Spotify 歌曲导入工具',
  description: '轻松将您的歌曲列表导入到 Spotify 播放列表',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="zh-CN">
      <body className="bg-[#121212] text-white">
        {/* 使用客户端组件提供者包装应用 */}
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  )
}
