import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { 
  SpotifyUserInfo, 
  ProcessSongsData, 
  CreatePlaylistData,
  MatchedSong,
  ApiError
} from './types';

// 定义 store 状态接口
interface StoreState {
  // 用户输入
  rawSongList: string;
  
  // API 加载状态
  isProcessingSongs: boolean;
  isCreatingPlaylist: boolean;
  isCheckingAuth: boolean;
  
  // API 错误状态
  processSongsError: ApiError | null;
  createPlaylistError: ApiError | null;
  authError: ApiError | null;
  
  // API 返回数据
  matchedSongsData: ProcessSongsData | null;
  createdPlaylistData: CreatePlaylistData | null;
  
  // 用户选择
  selectedSongUris: string[];
  
  // 播放列表信息
  newPlaylistName: string;
  newPlaylistDescription: string;
  isPlaylistPublic: boolean;
  
  // Spotify 认证状态
  isAuthenticated: boolean;
  userInfo: SpotifyUserInfo | null;
  
  // Actions
  setRawSongList: (songList: string) => void;
  setProcessingSongs: (isLoading: boolean) => void;
  setCreatingPlaylist: (isLoading: boolean) => void;
  setCheckingAuth: (isLoading: boolean) => void;
  
  setProcessSongsError: (error: ApiError | null) => void;
  setCreatePlaylistError: (error: ApiError | null) => void;
  setAuthError: (error: ApiError | null) => void;
  
  setMatchedSongsData: (data: ProcessSongsData | null) => void;
  setCreatedPlaylistData: (data: CreatePlaylistData | null) => void;
  
  toggleSongSelection: (uri: string) => void;
  selectAllSongs: () => void;
  deselectAllSongs: () => void;
  initializeSelectedSongs: (matchedSongs: MatchedSong[]) => void;
  
  setNewPlaylistName: (name: string) => void;
  setNewPlaylistDescription: (description: string) => void;
  setIsPlaylistPublic: (isPublic: boolean) => void;
  
  setAuthState: (isAuthenticated: boolean, userInfo: SpotifyUserInfo | null) => void;
  
  resetProcessState: () => void;
  resetPlaylistState: () => void;
  resetAllState: () => void;
}

// 创建持久化 store
export const useStore = create<StoreState>()(
  persist(
    (set, get) => ({
      // 初始状态
      rawSongList: '',
      
      isProcessingSongs: false,
      isCreatingPlaylist: false,
      isCheckingAuth: false,
      
      processSongsError: null,
      createPlaylistError: null,
      authError: null,
      
      matchedSongsData: null,
      createdPlaylistData: null,
      
      selectedSongUris: [],
      
      newPlaylistName: '我的歌曲转移',
      newPlaylistDescription: '从其他平台转移到 Spotify 的歌曲收藏',
      isPlaylistPublic: false,
      
      isAuthenticated: false,
      userInfo: null,
      
      // Actions
      setRawSongList: (songList) => set({ rawSongList: songList }),
      
      setProcessingSongs: (isLoading) => set({ isProcessingSongs: isLoading }),
      setCreatingPlaylist: (isLoading) => set({ isCreatingPlaylist: isLoading }),
      setCheckingAuth: (isLoading) => set({ isCheckingAuth: isLoading }),
      
      setProcessSongsError: (error) => set({ processSongsError: error }),
      setCreatePlaylistError: (error) => set({ createPlaylistError: error }),
      setAuthError: (error) => set({ authError: error }),
      
      setMatchedSongsData: (data) => {
        // 确保数据符合预期格式
        if (data) {
          // 标准化数据结构，确保关键字段存在
          const normalizedData = {
            ...data,
            matched_songs: data.matched_songs || [],
            unmatched_songs: data.unmatched_songs || [],
            total_songs: data.total_songs || 0
          };
          
          console.log('Store - 设置标准化匹配数据:', normalizedData);
          set({ matchedSongsData: normalizedData });
        } else {
          console.log('Store - 设置空匹配数据');
          set({ matchedSongsData: null });
        }
      },
      
      setCreatedPlaylistData: (data) => set({ createdPlaylistData: data }),
      
      toggleSongSelection: (uri) => {
        const { selectedSongUris } = get();
        if (selectedSongUris.includes(uri)) {
          set({ selectedSongUris: selectedSongUris.filter(id => id !== uri) });
        } else {
          set({ selectedSongUris: [...selectedSongUris, uri] });
        }
      },
      
      selectAllSongs: () => {
        const { matchedSongsData } = get();
        if (matchedSongsData?.matched_songs) {
          set({ 
            selectedSongUris: matchedSongsData.matched_songs.map(song => song.spotify_uri) 
          });
        }
      },
      
      deselectAllSongs: () => set({ selectedSongUris: [] }),
      
      initializeSelectedSongs: (matchedSongs) => {
        // 确保matchedSongs是一个数组
        if (!matchedSongs || !Array.isArray(matchedSongs)) {
          console.warn('初始化选中歌曲失败：匹配歌曲为空或不是数组');
          return;
        }
        
        // 默认选中所有非低置信度匹配的歌曲
        set({ 
          selectedSongUris: matchedSongs
            .filter(song => !song.is_low_confidence)
            .map(song => song.spotify_uri) 
        });
      },
      
      setNewPlaylistName: (name) => set({ newPlaylistName: name }),
      setNewPlaylistDescription: (description) => set({ newPlaylistDescription: description }),
      setIsPlaylistPublic: (isPublic) => set({ isPlaylistPublic: isPublic }),
      
      setAuthState: (isAuthenticated, userInfo) => 
        set({ isAuthenticated, userInfo }),
      
      resetProcessState: () => set({
        rawSongList: '',
        isProcessingSongs: false,
        processSongsError: null,
        matchedSongsData: null,
        selectedSongUris: []
      }),
      
      resetPlaylistState: () => set({
        isCreatingPlaylist: false,
        createPlaylistError: null,
        createdPlaylistData: null,
        newPlaylistName: '我的歌曲转移',
        newPlaylistDescription: '从其他平台转移到 Spotify 的歌曲收藏',
        isPlaylistPublic: false
      }),
      
      resetAllState: () => {
        const { resetProcessState, resetPlaylistState } = get();
        resetProcessState();
        resetPlaylistState();
      }
    }),
    {
      name: 'spotify-importer-storage',
      storage: createJSONStorage(() => localStorage),
      // 只持久化部分状态，排除加载状态和错误
      partialize: (state) => ({
        matchedSongsData: state.matchedSongsData,
        selectedSongUris: state.selectedSongUris,
        newPlaylistName: state.newPlaylistName,
        newPlaylistDescription: state.newPlaylistDescription,
        isPlaylistPublic: state.isPlaylistPublic,
        isAuthenticated: state.isAuthenticated,
        userInfo: state.userInfo
      })
    }
  )
);

// 为应用的不同部分提供便捷的 hooks
export const useAuthStore = () => {
  const { 
    isAuthenticated, 
    userInfo, 
    isCheckingAuth, 
    authError,
    setAuthState, 
    setCheckingAuth, 
    setAuthError 
  } = useStore();
  
  return {
    isAuthenticated,
    userInfo,
    isCheckingAuth,
    authError,
    setAuthState,
    setCheckingAuth,
    setAuthError
  };
};

export const useSongProcessStore = () => {
  const { 
    rawSongList, 
    isProcessingSongs, 
    processSongsError, 
    matchedSongsData,
    setRawSongList, 
    setProcessingSongs, 
    setProcessSongsError, 
    setMatchedSongsData,
    resetProcessState
  } = useStore();
  
  return {
    rawSongList,
    isProcessingSongs,
    processSongsError,
    matchedSongsData,
    setRawSongList,
    setProcessingSongs,
    setProcessSongsError,
    setMatchedSongsData,
    resetProcessState
  };
};

export const useSongSelectionStore = () => {
  const { 
    selectedSongUris, 
    toggleSongSelection, 
    selectAllSongs, 
    deselectAllSongs,
    initializeSelectedSongs
  } = useStore();
  
  return {
    selectedSongUris,
    toggleSongSelection,
    selectAllSongs,
    deselectAllSongs,
    initializeSelectedSongs
  };
};

export const usePlaylistStore = () => {
  const { 
    newPlaylistName, 
    newPlaylistDescription, 
    isPlaylistPublic,
    isCreatingPlaylist, 
    createPlaylistError, 
    createdPlaylistData,
    setNewPlaylistName, 
    setNewPlaylistDescription, 
    setIsPlaylistPublic,
    setCreatingPlaylist, 
    setCreatePlaylistError, 
    setCreatedPlaylistData,
    resetPlaylistState
  } = useStore();
  
  return {
    newPlaylistName,
    newPlaylistDescription,
    isPlaylistPublic,
    isCreatingPlaylist,
    createPlaylistError,
    createdPlaylistData,
    setNewPlaylistName,
    setNewPlaylistDescription,
    setIsPlaylistPublic,
    setCreatingPlaylist,
    setCreatePlaylistError,
    setCreatedPlaylistData,
    resetPlaylistState
  };
}; 