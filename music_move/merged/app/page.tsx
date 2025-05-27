// @ts-nocheck
import { ChevronLeft, Github } from "lucide-react"

export default function Home() {
  return (
    <div className="min-h-screen bg-[#121212]">
      {/* Header */}
      <header className="bg-[#121212] p-6 border-b border-[#282828]">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center">
            <div className="relative h-8 w-8 mr-2">
              <div className="absolute inset-0 bg-[#1DB954] rounded-full opacity-90"></div>
              <div className="absolute inset-[2px] bg-[#121212] rounded-full"></div>
              <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-4 h-4">
                <div className="absolute inset-0 border-t-2 border-r-2 border-[#1DB954] rounded-full animate-spin"></div>
              </div>
            </div>
            <span className="text-white text-xl font-semibold">MusicMove</span>
          </div>
          <div className="flex items-center">
            <a href="https://github.com" className="text-white hover:text-[#1DB954] transition">
              <Github className="h-5 w-5" />
            </a>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 py-12">
        <div className="text-center mb-8">
          <h1 className="text-white text-2xl font-medium mb-2">选择待移动的播放列表</h1>
          <div className="flex justify-center items-center text-[#B3B3B3] text-sm">
            <ChevronLeft className="h-4 w-4" />
            <span>1/3</span>
          </div>
        </div>

        {/* Card */}
        <div className="bg-[#282828] rounded-xl p-8 max-w-xl mx-auto">
          <h2 className="text-white text-xl font-medium text-center mb-6">输入您的歌曲列表</h2>

          {/* Text Area */}
          <div className="bg-[#181818] rounded-lg p-4 mb-6">
            <div className="text-[#B3B3B3] mb-2">示例:</div>
            <div className="text-white">The Beatles - Hey Jude</div>
            <div className="text-white">Beyoncé - Formation</div>
            <div className="text-[#B3B3B3] mt-4">...</div>
          </div>

          {/* Button */}
          <a href="/summary" className="block w-full py-3 bg-[#1DB954] text-white rounded-full hover:bg-[#1DB954]/90 transition text-center font-medium">
            转换歌曲列表
          </a>
        </div>
      </main>
    </div>
  )
} 