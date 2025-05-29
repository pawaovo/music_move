"use client"
import { useState, useEffect } from "react"
import Image from "next/image"
import { ChevronDown, ChevronLeft, Music, Github, X, Plus, Pencil, CheckCircle, AlertCircle, Loader2 } from "lucide-react"
import { useSongProcessStore, useSongSelectionStore, usePlaylistStore } from "@/store/useStore"
import { useAppSteps } from "@/hooks/useAppSteps"
import { useRouter } from "next/navigation"
import ProtectedRoute from "@/components/ProtectedRoute"
import { createPlaylistAndAddSongs } from "@/services/api"
import { ApiError } from "@/store/types"

export default function SummaryPage() {
  const router = useRouter();
  const [showEditModal, setShowEditModal] = useState(false);
  
  // 使用 Zustand 状态管理
  const { 
    matchedSongsData, 
    isProcessingSongs, 
    processSongsError 
  } = useSongProcessStore();
  
  const {
    selectedSongUris,
    toggleSongSelection,
    selectAllSongs,
    deselectAllSongs,
    initializeSelectedSongs
  } = useSongSelectionStore();
  
  const {
    newPlaylistName,
    newPlaylistDescription,
    isPlaylistPublic,
    isCreatingPlaylist,
    createPlaylistError,
    setNewPlaylistName,
    setNewPlaylistDescription,
    setIsPlaylistPublic,
    setCreatingPlaylist,
    setCreatePlaylistError,
    setCreatedPlaylistData
  } = usePlaylistStore();
  
  // 使用步骤管理
  const { goToInputStep, goToCompletedStep, currentStep } = useAppSteps();
  
  // 调试信息
  useEffect(() => {
    console.log('摘要页面 - 当前路径:', currentStep);
    console.log('摘要页面 - 匹配数据状态:', !!matchedSongsData);
    if (matchedSongsData) {
      console.log('摘要页面 - 详细匹配数据:', JSON.stringify(matchedSongsData, null, 2));
      console.log('摘要页面 - 匹配歌曲数量:', matchedSongsData.matched_songs?.length || 0);
      console.log('摘要页面 - 未匹配歌曲数量:', matchedSongsData.unmatched_songs?.length || 0);
      console.log('摘要页面 - 已选择歌曲数量:', selectedSongUris.length);
    }
  }, [currentStep, matchedSongsData, selectedSongUris]);
  
  // 如果没有匹配数据，重定向到输入页
  useEffect(() => {
    if (!matchedSongsData) {
      console.log('摘要页面 - 没有匹配数据，重定向到输入页');
      goToInputStep();
    }
  }, [matchedSongsData, goToInputStep]);
  
  // 单独的useEffect用于初始化选中歌曲，只在匹配数据首次加载时执行
  useEffect(() => {
    if (matchedSongsData && matchedSongsData.matched_songs && matchedSongsData.matched_songs.length > 0) {
      console.log('摘要页面 - 初始化选中歌曲');
      // 使用一次性初始化标记，避免重复初始化
      const hasInitializedSelection = localStorage.getItem(`selection-initialized-${matchedSongsData.total_songs}`);
      
      if (!hasInitializedSelection) {
        initializeSelectedSongs(matchedSongsData.matched_songs);
        localStorage.setItem(`selection-initialized-${matchedSongsData.total_songs}`, 'true');
      }
    }
  // 该useEffect只在组件挂载和匹配数据变化时运行，不依赖于initializeSelectedSongs
  }, [matchedSongsData]);
  
  // 处理开始转移
  const handleStartTransfer = async () => {
    if (selectedSongUris.length === 0) {
      alert('请至少选择一首歌曲');
      return;
    }
    
    try {
      // 设置加载状态
      setCreatingPlaylist(true);
      setCreatePlaylistError(null);
      
      console.log('摘要页面 - 开始创建播放列表');
      console.log('摘要页面 - 播放列表名称:', newPlaylistName);
      console.log('摘要页面 - 选中歌曲数量:', selectedSongUris.length);
      
      // 调用 API 创建播放列表
      const result = await createPlaylistAndAddSongs(
        newPlaylistName,
        isPlaylistPublic,
        selectedSongUris
      );
      
      console.log('摘要页面 - 创建播放列表成功:', result);
      
      // 保存创建结果
      setCreatedPlaylistData(result);
      
      // 添加延迟确保状态更新完成后再跳转
      setTimeout(() => {
        // 跳转到完成页
        console.log('摘要页面 - 正在跳转到完成页');
        goToCompletedStep();
      }, 100);
    } catch (error) {
      console.error('创建播放列表失败:', error);
      setCreatePlaylistError(error as ApiError);
    } finally {
      setCreatingPlaylist(false);
    }
  };
  
  // 如果没有匹配数据，显示加载状态
  if (!matchedSongsData) {
    return (
      <div className="min-h-screen bg-[#121212] text-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin h-12 w-12 border-4 border-t-[#1DB954] border-r-[#1DB954] border-b-transparent border-l-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-lg">加载中...</p>
        </div>
      </div>
    );
  }
  
  // 使用 ProtectedRoute 包装内容
  return (
    <ProtectedRoute redirectTo="/">
    <div className="min-h-screen bg-[#121212] text-white">
      {/* 全屏加载状态 */}
      {isCreatingPlaylist && (
        <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center flex-col">
          <Loader2 className="h-12 w-12 text-[#1DB954] animate-spin mb-4" />
          <p className="text-white text-lg font-medium">正在处理歌曲...</p>
          <p className="text-[#B3B3B3] text-sm mt-2">请稍候，这可能需要一些时间</p>
        </div>
      )}
      
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
                返回输入
              </button>
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

            {/* Stats Summary */}
            <div className="bg-[#333333] rounded-xl p-5 mb-6">
              <div className="flex justify-between items-center">
                <div className="text-center">
                  <p className="text-sm text-[#B3B3B3]">总歌曲数</p>
                  <p className="text-xl font-semibold">{matchedSongsData.total_songs}</p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-[#B3B3B3]">已匹配</p>
                  <p className="text-xl font-semibold text-[#1DB954]">{matchedSongsData.matched_songs?.length || 0}</p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-[#B3B3B3]">未匹配</p>
                  <p className="text-xl font-semibold text-[#ff5722]">{matchedSongsData.unmatched_songs?.length || 0}</p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-[#B3B3B3]">已选择</p>
                  <p className="text-xl font-semibold text-[#1DB954]">{selectedSongUris.length}</p>
                </div>
              </div>
            </div>

            {/* Transfer Card */}
            <div className="bg-[#282828] rounded-xl p-6 mb-8">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-lg font-semibold text-[#1DB954] flex items-center">
                  <CheckCircle className="h-4 w-4 mr-1" /> 
                  已匹配歌曲 ({matchedSongsData.matched_songs?.length || 0})
                </h2>
                <div className="flex gap-2">
                  <button 
                    className="text-sm px-3 py-1 bg-[#333333] rounded-full hover:bg-[#444444] flex items-center"
                    onClick={() => setShowEditModal(true)}
                  >
                    <Pencil className="h-3 w-3 mr-1" /> 编辑
                  </button>
                  <button 
                    className="text-sm px-3 py-1 bg-[#333333] rounded-full hover:bg-[#444444]"
                    onClick={selectAllSongs}
                  >
                    全选
                  </button>
                  <button 
                    className="text-sm px-3 py-1 bg-[#333333] rounded-full hover:bg-[#444444]"
                    onClick={deselectAllSongs}
                  >
                    取消全选
                  </button>
                </div>
              </div>

              {/* Matched Songs */}
              <div className="space-y-3 mb-4">
                <div className="max-h-60 overflow-y-auto pr-2 space-y-2 custom-scrollbar">
                  {matchedSongsData.matched_songs && 
                   [...matchedSongsData.matched_songs]
                    .sort((a, b) => {
                      // 低匹配度歌曲排在前面
                      if (a.is_low_confidence && !b.is_low_confidence) return -1;
                      if (!a.is_low_confidence && b.is_low_confidence) return 1;
                      return 0;
                    })
                    .map((song) => (
                    <div 
                      key={song.spotify_uri}
                      className={`flex items-center p-2 rounded ${
                        selectedSongUris.includes(song.spotify_uri) ? 'bg-[#333333]' : 'hover:bg-[#333333]'
                      } transition cursor-pointer`}
                      onClick={() => toggleSongSelection(song.spotify_uri)}
                    >
                      <input 
                        type="checkbox" 
                        className="mr-3 h-4 w-4 accent-[#1DB954]"
                        checked={selectedSongUris.includes(song.spotify_uri)}
                        onChange={() => {}} // 处理在父级 div
                      />
                      <div className="flex-1 min-w-0">
                        <p className={`text-sm truncate ${song.is_low_confidence ? 'text-[#ff9800]' : 'text-[#1DB954]'}`}>
                          {song.title} - {song.artists.join(', ')}
                        </p>
                        <p className="text-xs text-[#B3B3B3] truncate">
                          {song.original_input}
                        </p>
                      </div>
                      {song.is_low_confidence && (
                        <span className="text-xs text-[#ff9800] ml-2 whitespace-nowrap">
                          低匹配度
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* Unmatched Songs */}
              {matchedSongsData.unmatched_songs && matchedSongsData.unmatched_songs.length > 0 && (
                <div className="space-y-3">
                  <h3 className="font-medium text-[#ff5722] flex items-center">
                    <AlertCircle className="h-4 w-4 mr-1" /> 
                    未匹配歌曲 ({matchedSongsData.unmatched_songs.length})
                  </h3>
                  
                  <div className="max-h-40 overflow-y-auto pr-2 space-y-2 custom-scrollbar">
                    {matchedSongsData.unmatched_songs.map((song, index) => (
                      <div 
                        key={index}
                        className="flex items-center p-2 rounded bg-[#333333] opacity-75"
                      >
                        <div className="flex-1 min-w-0">
                          <p className="text-sm truncate">{song.original_input}</p>
                          <p className="text-xs text-[#ff5722] truncate">{song.reason}</p>
                        </div>
                      </div>
                    ))}
                </div>
                </div>
              )}
          </div>

          {/* Action Button */}
          <div className="flex justify-center">
              <button 
                onClick={handleStartTransfer}
                disabled={isCreatingPlaylist || selectedSongUris.length === 0}
                className={`${
                  isCreatingPlaylist || selectedSongUris.length === 0 
                    ? 'bg-[#1DB954]/50 cursor-not-allowed' 
                    : 'bg-[#1DB954] hover:bg-[#1DB954]/90'
                } text-white px-12 py-3 rounded-full font-medium text-center transition`}
              >
                {isCreatingPlaylist 
                  ? '处理中...' 
                  : selectedSongUris.length === 0 
                    ? '请选择歌曲' 
                    : `开始转移 (${selectedSongUris.length}首歌曲)`
                }
              </button>
              
              {/* 显示错误信息 */}
              {createPlaylistError && (
                <p className="mt-4 text-red-500 text-sm text-center">
                  {createPlaylistError.message || '创建播放列表时出错'}
                </p>
              )}
          </div>
        </div>
      </main>

      {/* Edit Modal */}
      {showEditModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 px-4">
          <div className="relative z-10 bg-[#282828] rounded-xl w-full max-w-md shadow-xl">
            <div className="p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-white text-2xl font-medium">编辑播放列表</h2>
                <button 
                  className="text-[#1DB954]/70 hover:text-[#1DB954]"
                  onClick={() => setShowEditModal(false)}
                >
                  <X className="h-5 w-5" />
                </button>
              </div>

              <div className="mb-4">
                  <label className="block text-white mb-2">播放列表名称</label>
                  <input 
                    type="text" 
                    value={newPlaylistName}
                    onChange={(e) => setNewPlaylistName(e.target.value)}
                    placeholder="输入播放列表名称" 
                    className="w-full p-3 rounded-lg bg-[#333333] text-white border border-[#555555] focus:border-[#1DB954] focus:outline-none" 
                  />
              </div>

                <div className="mb-4">
                  <label className="block text-white mb-2">播放列表描述</label>
                  <textarea 
                    value={newPlaylistDescription}
                    onChange={(e) => setNewPlaylistDescription(e.target.value)}
                    placeholder="输入播放列表描述" 
                    className="w-full p-3 rounded-lg bg-[#333333] text-white border border-[#555555] focus:border-[#1DB954] focus:outline-none resize-none custom-scrollbar"
                    rows={3}
                  />
                </div>

                <div className="mb-6">
                  <label className="flex items-center cursor-pointer">
                    <input 
                      type="checkbox" 
                      checked={isPlaylistPublic}
                      onChange={(e) => setIsPlaylistPublic(e.target.checked)}
                      className="accent-[#1DB954] h-4 w-4 mr-2" 
                    />
                    <span className="text-white">公开播放列表</span>
                  </label>
              </div>

              <div className="flex gap-4">
                <button 
                  className="flex-1 py-3 bg-[#333333] text-white rounded-full hover:bg-[#444444] transition text-center font-medium"
                  onClick={() => setShowEditModal(false)}
                >
                  取消
                </button>
                <button 
                  className="flex-1 py-3 bg-[#1DB954] text-white rounded-full hover:bg-[#1DB954]/90 transition text-center font-medium"
                  onClick={() => setShowEditModal(false)}
                >
                  保存
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
    </ProtectedRoute>
  )
} 