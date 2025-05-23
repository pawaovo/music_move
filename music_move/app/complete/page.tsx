// @ts-nocheck
import Image from "next/image"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { CheckCircle, ChevronDown, Github } from "lucide-react"

export default function CompletePage() {
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
      <main className="max-w-4xl mx-auto py-12 px-4">
        <Card className="bg-[#282828] border-none rounded-xl p-8 shadow-lg">
          {/* Success Message */}
          <div className="flex flex-col items-center mb-8">
            <div className="h-12 w-12 rounded-full bg-transparent border-2 border-[#1DB954] flex items-center justify-center mb-4">
              <CheckCircle className="h-6 w-6 text-[#1DB954]" />
            </div>
            <h1 className="text-white text-2xl font-medium mb-6">转移完成！</h1>

            {/* Platform Icons */}
            <div className="flex items-center gap-4">
              <div className="h-8 w-8 bg-[#333333] rounded flex items-center justify-center">
                <span className="text-white text-xs">?</span>
              </div>
              <div className="h-8 w-8 bg-black rounded-full flex items-center justify-center">
                <Image
                  src="/spotify-logo.svg"
                  alt="Spotify"
                  width={24}
                  height={24}
                  className="object-contain"
                />
              </div>
              <span className="text-white font-medium">Spotify</span>
            </div>
          </div>

          {/* Playlist List */}
          <div className="space-y-2">
            {/* Playlist 1 */}
            <div className="bg-[#181818] rounded-lg p-3 flex items-center">
              <div className="h-10 w-10 bg-[#333333] rounded flex items-center justify-center mr-4">
                <Image
                  src="/spotify-logo.svg"
                  alt="Playlist"
                  width={20}
                  height={20}
                  className="object-contain"
                />
              </div>
              <div className="flex-1">
                <div className="text-white font-medium">My Playlist</div>
                <div className="text-[#B3B3B3] text-sm">2/2已迁移</div>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-[#1DB954] text-sm">2首已转</span>
                <div className="h-5 w-5 rounded-full bg-transparent border border-[#1DB954] flex items-center justify-center">
                  <CheckCircle className="h-3 w-3 text-[#1DB954]" />
                </div>
                <ChevronDown className="h-4 w-4 text-[#B3B3B3]" />
              </div>
            </div>

            {/* Playlist 2 */}
            <div className="bg-[#181818] rounded-lg p-3 flex items-center">
              <div className="h-10 w-10 bg-[#333333] rounded flex items-center justify-center mr-4">
                <Image
                  src="/spotify-logo.svg"
                  alt="Playlist"
                  width={20}
                  height={20}
                  className="object-contain"
                />
              </div>
              <div className="flex-1">
                <div className="text-white font-medium">从无到有 feat 安列 - 姜云升</div>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-[#1DB954] text-sm">已转移</span>
                <div className="h-5 w-5 rounded-full bg-transparent border border-[#1DB954] flex items-center justify-center">
                  <CheckCircle className="h-3 w-3 text-[#1DB954]" />
                </div>
              </div>
            </div>

            {/* Playlist 3 */}
            <div className="bg-[#181818] rounded-lg p-3 flex items-center">
              <div className="h-10 w-10 bg-[#333333] rounded flex items-center justify-center mr-4">
                <Image
                  src="/spotify-logo.svg"
                  alt="Playlist"
                  width={20}
                  height={20}
                  className="object-contain"
                />
              </div>
              <div className="flex-1">
                <div className="text-white font-medium">28.7 - 姜云升 / 朴冉</div>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-[#1DB954] text-sm">已转移</span>
                <div className="h-5 w-5 rounded-full bg-transparent border border-[#1DB954] flex items-center justify-center">
                  <CheckCircle className="h-3 w-3 text-[#1DB954]" />
                </div>
              </div>
            </div>
          </div>
        </Card>

        {/* Continue Button */}
        <div className="mt-8 flex justify-center">
          <a href="/" className="bg-[#1DB954] hover:bg-[#1DB954]/90 text-white py-3 px-12 rounded-full inline-block w-full max-w-xs text-center font-medium">
            继续
          </a>
        </div>
      </main>
    </div>
  )
} 