'use client';

import { useEffect, useState } from "react";
import Image from "next/image";
import { CheckCircle, ChevronDown, Github, ChevronLeft, ExternalLink, AlertCircle } from "lucide-react";
import { usePlaylistStore, useSongSelectionStore, useSongProcessStore } from "@/store/useStore";
import { useAppSteps } from "@/hooks/useAppSteps";
import ProtectedRoute from "@/components/ProtectedRoute";

export default function CompletePage() {
  const [error, setError] = useState<string | null>(null);
  
  // 使用 Zustand 状态管理
  const {
    createdPlaylistData,
    resetPlaylistState
  } = usePlaylistStore();
  
  const {
    matchedSongsData,
    resetProcessState
  } = useSongProcessStore();
  
  const {
    deselectAllSongs
  } = useSongSelectionStore();
  
  // 使用步骤管理
  const { goToInputStep, currentStep } = useAppSteps();
  
  // 调试信息
  useEffect(() => {
    console.log('完成页面 - 当前路径:', currentStep);
    console.log('完成页面 - 播放列表数据状态:', !!createdPlaylistData);
    console.log('完成页面 - 匹配数据状态:', !!matchedSongsData);
    
    if (createdPlaylistData) {
      console.log('完成页面 - 播放列表名称:', createdPlaylistData.playlist_name);
      console.log('完成页面 - 添加歌曲数量:', createdPlaylistData.added_tracks_count);
    }
  }, [currentStep, createdPlaylistData, matchedSongsData]);
  
  // 如果没有创建的播放列表数据，重定向到输入页
  useEffect(() => {
    if (!createdPlaylistData && !matchedSongsData) {
      // 如果没有任何数据，重定向到输入页
      console.log('完成页面 - 没有数据，重定向到输入页');
      goToInputStep();
    } else if (!createdPlaylistData) {
      // 如果有匹配数据但没有创建的播放列表数据，可能是直接访问此页面
      console.log('完成页面 - 没有播放列表数据，设置错误');
      setError("未找到播放列表创建数据，请先处理歌曲并创建播放列表");
    }
  }, [createdPlaylistData, matchedSongsData, goToInputStep]);
  
  // 重置所有状态，开始新的导入
  const handleContinue = () => {
    try {
      console.log('完成页面 - 开始重置状态');
      
      // 按顺序重置各个状态
      resetProcessState();
      console.log('完成页面 - 已重置处理状态');
      
      resetPlaylistState();
      console.log('完成页面 - 已重置播放列表状态');
      
      deselectAllSongs();
      console.log('完成页面 - 已重置选择状态');
      
      // 添加延迟确保状态更新完成后再跳转
      setTimeout(() => {
        // 重定向到输入页
        console.log('完成页面 - 正在跳转到输入页');
        goToInputStep();
      }, 100);
    } catch (err) {
      console.error('重置状态失败:', err);
      setError('重置状态失败，请刷新页面重试');
    }
  };
  
  // 如果没有创建的播放列表数据，显示加载状态或错误
  if (!createdPlaylistData) {
    return (
      <div className="min-h-screen bg-[#121212] text-white flex items-center justify-center">
        <div className="text-center">
          {error ? (
            <>
              <div className="h-12 w-12 rounded-full bg-transparent border-2 border-red-500 flex items-center justify-center mx-auto mb-4">
                <AlertCircle className="h-6 w-6 text-red-500" />
              </div>
              <p className="text-lg mb-4">{error}</p>
              <button
                onClick={goToInputStep}
                className="bg-[#1DB954] hover:bg-[#1DB954]/90 text-white py-2 px-6 rounded-full transition"
              >
                返回首页
              </button>
            </>
          ) : (
            <>
              <div className="animate-spin h-12 w-12 border-4 border-t-[#1DB954] border-r-[#1DB954] border-b-transparent border-l-transparent rounded-full mx-auto mb-4"></div>
              <p className="text-lg">加载中...</p>
            </>
          )}
        </div>
      </div>
    );
  }
  
  return (
    <ProtectedRoute>
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
            <div className="flex items-center space-x-4">
              <button 
                onClick={goToInputStep}
                className="text-white hover:text-[#1DB954] transition text-sm"
              >
                返回首页
              </button>
              <a href="https://github.com" className="text-white hover:text-[#1DB954] transition">
                <Github className="h-5 w-5" />
              </a>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-4xl mx-auto py-12 px-4">
          {/* Title and Step Indicator */}
          <div className="text-center mb-8">
            <h1 className="text-white text-2xl font-medium mb-2">完成</h1>
            <div className="flex justify-center items-center text-[#B3B3B3] text-sm">
              <ChevronLeft className="h-4 w-4" />
              <span>3/3</span>
            </div>
          </div>

          <div className="bg-[#282828] border-none rounded-xl p-8 shadow-lg text-white">
            {/* Success Message */}
            <div className="flex flex-col items-center mb-8">
              <div className="h-12 w-12 rounded-full bg-transparent border-2 border-[#1DB954] flex items-center justify-center mb-4">
                <CheckCircle className="h-6 w-6 text-[#1DB954]" />
              </div>
              <h1 className="text-white text-2xl font-medium mb-6">转移完成！</h1>

              {/* Platform Icons */}
              <div className="flex items-center gap-4">
                <div className="h-8 w-8 bg-[#333333] rounded flex items-center justify-center">
                  <span className="text-white text-xs">其他</span>
                </div>
                <div className="text-[#B3B3B3]">→</div>
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

            {/* Summary Info */}
            <div className="bg-[#333333] rounded-xl p-5 mb-6">
              <div className="flex justify-between items-center">
                <div className="text-center">
                  <p className="text-sm text-[#B3B3B3]">已添加歌曲</p>
                  <p className="text-xl font-semibold text-[#1DB954]">{createdPlaylistData.added_tracks_count}</p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-[#B3B3B3]">失败歌曲</p>
                  <p className="text-xl font-semibold text-[#ff5722]">{createdPlaylistData.failed_tracks_count || 0}</p>
                </div>
              </div>
            </div>

            {/* Playlist Info */}
            <div className="bg-[#181818] rounded-lg p-4 mb-6">
              <div className="flex items-center">
                <div className="h-12 w-12 bg-[#333333] rounded flex items-center justify-center mr-4">
                  <Image
                    src="/spotify-logo.svg"
                    alt="Playlist"
                    width={24}
                    height={24}
                    className="object-contain"
                  />
                </div>
                <div className="flex-1">
                  <div className="text-white font-medium">{createdPlaylistData.playlist_name}</div>
                  <div className="text-[#B3B3B3] text-sm">
                    {createdPlaylistData.added_tracks_count} 首歌曲已添加
                  </div>
                </div>
                {createdPlaylistData.playlist_url && (
                  <a 
                    href={createdPlaylistData.playlist_url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="flex items-center gap-1 text-[#1DB954] hover:text-[#1DB954]/80 transition"
                  >
                    <span className="text-sm">查看</span>
                    <ExternalLink className="h-4 w-4" />
                  </a>
                )}
              </div>
            </div>
            
            {/* Additional Information */}
            <div className="text-center text-[#B3B3B3] text-sm">
              <p>您可以随时回到主页面开始新的歌曲转移操作</p>
            </div>
          </div>

          {/* Continue Button */}
          <div className="mt-8 flex justify-center">
            <button 
              onClick={handleContinue}
              className="bg-[#1DB954] hover:bg-[#1DB954]/90 text-white py-3 px-12 rounded-full inline-block w-full max-w-xs text-center font-medium"
            >
              转移新的歌曲
            </button>
          </div>
        </main>
      </div>
    </ProtectedRoute>
  );
} 