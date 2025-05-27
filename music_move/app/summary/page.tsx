// @ts-nocheck
import Image from "next/image"
import { ChevronDown, ChevronLeft, Music, Github } from "lucide-react"
import { Button } from "@/components/ui/button"

export default function SummaryPage() {
  return (
    <div className="min-h-screen bg-[#121212] text-white">
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
        <div className="w-full max-w-3xl mx-auto">
          {/* Title */}
          <div className="text-center mb-8">
            <h1 className="text-white text-2xl font-medium mb-2">概要</h1>
            <div className="flex justify-center items-center text-[#B3B3B3] text-sm">
              <ChevronLeft className="h-4 w-4" />
              <span>2/3</span>
            </div>
          </div>

          {/* Transfer Card */}
          <div className="bg-[#282828] rounded-xl p-6 mb-8">
            <div className="flex items-center justify-center gap-4 mb-6">
              <div className="h-8 w-8 bg-[#333333] border border-[#555555] rounded flex items-center justify-center">
                <Music className="h-4 w-4 text-white" />
              </div>
              <div className="text-[#B3B3B3]">→</div>
              <Image
                src="/spotify-logo.svg"
                alt="Spotify"
                width={32}
                height={32}
                className="rounded"
              />
            </div>

            <div className="text-center mb-6">
              <p className="text-sm text-[#B3B3B3]">正在转移1播放列表（2 曲目）</p>
            </div>

            {/* Playlist Items */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 bg-[#333333] rounded flex items-center justify-center">
                    <Music className="h-5 w-5 text-white" />
                  </div>
                  <div>
                    <p className="text-sm font-medium">My Playlist</p>
                    <p className="text-xs text-[#B3B3B3]">2/2已完成</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <div className="h-6 w-6 bg-[#1DB954] rounded-full"></div>
                  <ChevronDown className="h-4 w-4 text-[#B3B3B3]" />
                </div>
              </div>

              <div className="flex items-center gap-3 pl-1">
                <div className="h-10 w-10 bg-[#333333] rounded flex items-center justify-center">
                  <Music className="h-5 w-5 text-white" />
                </div>
                <div>
                  <p className="text-sm">从无到有 feat 安苏 - 姜云升</p>
                </div>
              </div>

              <div className="flex items-center gap-3 pl-1">
                <div className="h-10 w-10 bg-[#333333] rounded flex items-center justify-center">
                  <Music className="h-5 w-5 text-white" />
                </div>
                <div>
                  <p className="text-sm">28.7 - 姜云升 / 朴冉</p>
                </div>
              </div>
            </div>
          </div>

          {/* Action Button */}
          <div className="flex justify-center">
            <a href="/edit" className="bg-[#1DB954] hover:bg-[#1DB954]/90 text-white px-12 py-3 rounded-full font-medium text-center">开始转移</a>
          </div>
        </div>
      </main>
    </div>
  )
} 