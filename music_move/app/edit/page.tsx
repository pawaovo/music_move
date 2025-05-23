// @ts-nocheck
import { ChevronDown, X, Plus, Github } from "lucide-react"

export default function EditPage() {
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

      {/* Main Content with Modal */}
      <main className="relative max-w-4xl mx-auto px-4 py-12 flex justify-center items-center min-h-[calc(100vh-80px)]">
        {/* Background Elements */}
        <div className="absolute left-1/4 top-1/4 transform -translate-x-1/2 -translate-y-1/2">
          <div className="w-16 h-16 bg-[#282828] rounded-lg flex items-center justify-center">
            <span className="text-[#B3B3B3] text-2xl">音乐</span>
          </div>
        </div>

        {/* Modal */}
        <div className="relative z-10 bg-[#282828] rounded-xl w-full max-w-md shadow-xl">
          <div className="p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-white text-2xl font-medium">编辑播放列表</h2>
              <button className="text-[#1DB954]/70 hover:text-[#1DB954]">
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="mb-4">
              <label className="block text-white mb-2">转移至</label>
              <input type="text" placeholder="现有播放列表" className="w-full p-3 rounded-lg bg-[#333333] text-white border border-[#555555] focus:border-[#1DB954] focus:outline-none" />
            </div>

            <div className="space-y-2 mb-6">
              <div className="flex items-center p-3 bg-[#181818] rounded-lg">
                <div className="w-10 h-10 bg-[#333333] rounded mr-3 flex-shrink-0 overflow-hidden">
                  <div className="grid grid-cols-2 grid-rows-2 h-full w-full">
                    <div className="bg-red-500"></div>
                    <div className="bg-blue-500"></div>
                    <div className="bg-yellow-500"></div>
                    <div className="bg-green-500"></div>
                  </div>
                </div>
                <div>
                  <p className="text-white">My Playlist</p>
                </div>
                <ChevronDown className="ml-auto text-[#B3B3B3] h-4 w-4" />
              </div>

              <div className="flex items-start p-3 bg-[#181818] rounded-lg">
                <div className="w-10 h-10 bg-[#333333] rounded mr-3 flex-shrink-0 overflow-hidden">
                  <div className="grid grid-cols-2 grid-rows-2 h-full w-full">
                    <div className="bg-red-500"></div>
                    <div className="bg-blue-500"></div>
                    <div className="bg-yellow-500"></div>
                    <div className="bg-green-500"></div>
                  </div>
                </div>
                <div>
                  <p className="text-white">My Playlist</p>
                  <p className="text-[#B3B3B3] text-sm mt-1">Post-rock is just music about ghosts and mountains.</p>
                </div>
              </div>
            </div>

            <a href="/complete" className="block w-full py-3 bg-[#1DB954] text-white rounded-full hover:bg-[#1DB954]/90 transition text-center font-medium">
              保存
            </a>
          </div>
        </div>

        {/* Bottom Button */}
        <div className="absolute bottom-20 left-1/2 transform -translate-x-1/2">
          <a href="/complete" className="block py-3 px-8 bg-[#1DB954] text-white rounded-full hover:bg-[#1DB954]/90 transition font-medium">
            开始转移
          </a>
        </div>

        {/* Add Button */}
        <div className="absolute right-1/4 top-1/3">
          <button className="w-12 h-12 bg-[#1DB954] rounded-full flex items-center justify-center text-white">
            <Plus className="h-6 w-6" />
          </button>
        </div>
      </main>
    </div>
  )
} 