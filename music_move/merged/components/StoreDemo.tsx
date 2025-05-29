'use client';

import { useEffect } from 'react';
import { 
  useStore, 
  useSongProcessStore,
  useSongSelectionStore,
  usePlaylistStore,
  useAuthStore
} from '../store/useStore';
import { useAppSteps } from '../hooks/useAppSteps';

/**
 * 状态管理演示组件
 * 这个组件展示了如何使用状态管理 hooks
 */
export default function StoreDemo() {
  // 使用分离的 hooks 获取不同部分的状态
  const {
    rawSongList,
    isProcessingSongs,
    matchedSongsData,
    setRawSongList
  } = useSongProcessStore();
  
  const {
    selectedSongUris,
    toggleSongSelection,
    selectAllSongs,
    deselectAllSongs
  } = useSongSelectionStore();
  
  const {
    newPlaylistName,
    setNewPlaylistName
  } = usePlaylistStore();
  
  const {
    isAuthenticated,
    userInfo
  } = useAuthStore();
  
  // 使用步骤管理
  const {
    currentStep,
    goToInputStep,
    goToSummaryStep,
    goToCompletedStep
  } = useAppSteps();
  
  // 演示: 从 URL 步骤自动执行相应的操作
  useEffect(() => {
    console.log(`当前步骤: ${currentStep}`);
    // 这里可以根据当前步骤执行相应的操作
  }, [currentStep]);
  
  return (
    <div className="p-4 space-y-4 bg-gray-50 rounded-lg">
      <h2 className="text-xl font-bold">状态管理演示</h2>
      
      <div>
        <h3 className="font-semibold">当前步骤: {currentStep}</h3>
        <div className="flex gap-2 mt-2">
          <button 
            onClick={goToInputStep}
            className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            去输入页
          </button>
          <button 
            onClick={goToSummaryStep}
            className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            去概要页
          </button>
          <button 
            onClick={goToCompletedStep}
            className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            去完成页
          </button>
        </div>
      </div>
      
      <div>
        <h3 className="font-semibold">歌曲输入</h3>
        <textarea 
          value={rawSongList}
          onChange={(e) => setRawSongList(e.target.value)}
          className="w-full p-2 border rounded mt-1"
          placeholder="输入歌曲列表..."
          rows={3}
        />
      </div>
      
      <div>
        <h3 className="font-semibold">播放列表名称</h3>
        <input 
          type="text"
          value={newPlaylistName}
          onChange={(e) => setNewPlaylistName(e.target.value)}
          className="w-full p-2 border rounded mt-1"
        />
      </div>
      
      <div>
        <h3 className="font-semibold">认证状态</h3>
        <p>
          {isAuthenticated 
            ? `已认证 - 用户: ${userInfo?.display_name || '未知'}`
            : '未认证'
          }
        </p>
      </div>
      
      <div>
        <h3 className="font-semibold">匹配结果</h3>
        <p>
          {matchedSongsData 
            ? `已匹配 ${matchedSongsData.matched_songs.length} 首歌曲，未匹配 ${matchedSongsData.unmatched_songs.length} 首歌曲`
            : '暂无匹配结果'
          }
        </p>
      </div>
      
      <div>
        <h3 className="font-semibold">已选择歌曲</h3>
        <p>选择了 {selectedSongUris.length} 首歌曲</p>
        <div className="flex gap-2 mt-2">
          <button 
            onClick={selectAllSongs}
            className="px-3 py-1 bg-green-500 text-white rounded hover:bg-green-600"
          >
            全选
          </button>
          <button 
            onClick={deselectAllSongs}
            className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600"
          >
            取消全选
          </button>
        </div>
      </div>
      
      <p className="text-sm text-gray-500">
        注意: 这是一个演示组件，展示了如何使用状态管理。在实际应用中，这些状态和操作会分布在不同的页面和组件中。
      </p>
    </div>
  );
} 