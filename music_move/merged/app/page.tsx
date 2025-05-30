'use client';

import { ChevronLeft, Github, Info, AlertCircle, Loader2, ExternalLink } from "lucide-react"
import { useEffect, useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useSongProcessStore, useAuthStore } from "../store/useStore";
import { useAppSteps, AppStep } from "../hooks/useAppSteps";
import { processSongs, checkAuthStatus, getAuthUrl } from "../services/api";
import { ProcessSongsData, ApiError } from "../store/types";
import AuthCheck from "../components/AuthCheck";

// 创建一个包含useSearchParams的组件
function HomeContent() {
  // 使用 Zustand 状态管理
  const { 
    rawSongList, 
    setRawSongList, 
    isProcessingSongs,
    setProcessingSongs, 
    processSongsError,
    setProcessSongsError,
    setMatchedSongsData
  } = useSongProcessStore();
  
  // 使用认证状态
  const { isAuthenticated, setAuthState } = useAuthStore();
  
  // 使用步骤管理
  const { goToSummaryStep, currentStep } = useAppSteps();
  
  // 搜索参数
  const searchParams = useSearchParams();
  
  // 添加状态管理
  const [isCheckingAuth, setCheckingAuth] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // 加载初始认证状态
  useEffect(() => {
    let isMounted = true;
    
    async function checkAuth() {
      if (!isMounted) return;
      
      console.log('首页加载，开始检查认证状态...');
      setCheckingAuth(true);
      
      try {
        const { isAuthenticated, userInfo, error } = await checkAuthStatus();
        
        // 如果组件已卸载，不要更新状态
        if (!isMounted) return;
        
        if (error) {
          console.error('首页检查认证状态出错:', error);
          setError(error);
          // 即使出错，也要更新认证状态，以防之前的状态是错误的
          setAuthState(false, null);
        } else {
          console.log('首页认证状态已更新, 认证状态:', isAuthenticated, '用户信息:', userInfo);
          setAuthState(isAuthenticated, userInfo);
        }
      } catch (error) {
        // 如果组件已卸载，不要更新状态
        if (!isMounted) return;
        
        console.error('首页检查认证状态异常:', error);
        // 出现异常时，为安全起见也设置为未认证状态
        setAuthState(false, null);
        setError(`检查认证状态失败: ${error instanceof Error ? error.message : String(error)}`);
      } finally {
        // 如果组件已卸载，不要更新状态
        if (isMounted) {
          setCheckingAuth(false);
        }
      }
    }
    
    // 执行认证检查
    checkAuth();
    
    // 组件卸载时设置标志
    return () => {
      isMounted = false;
    };
  }, []); // 仅在组件挂载时执行一次
  
  // 调试信息
  useEffect(() => {
    console.log('当前页面路径:', currentStep);
    console.log('用户认证状态:', isAuthenticated ? '已认证' : '未认证');
  }, [currentStep, isAuthenticated]);
  
  // 处理歌曲列表转换
  const handleConvertSongList = async () => {
    if (!rawSongList.trim()) {
      alert('请输入歌曲列表');
      return;
    }
    
    try {
      // 首先检查用户是否已授权
      if (!isAuthenticated) {
        console.log('用户未授权，获取授权URL');
        
        // 设置加载状态
        setProcessingSongs(true);
        
        try {
          // 获取授权URL
          const authUrl = await getAuthUrl();
          console.log('获取到授权URL:', authUrl);
          
          // 提示用户需要先授权
          alert('需要先授权Spotify账号才能继续操作，即将跳转到授权页面');
          
          // 跳转到授权URL
          window.location.href = authUrl;
          return;
        } catch (error) {
          console.error('获取授权URL失败:', error);
          setProcessSongsError({
            code: 'AUTH_REQUIRED',
            message: '获取授权URL失败，请刷新页面重试',
            details: error
          } as ApiError);
          setProcessingSongs(false);
          return;
        }
      }
      
      // 用户已授权，继续处理歌曲列表
      // 设置加载状态
      setProcessingSongs(true);
      setProcessSongsError(null);
      
      console.log('开始处理歌曲列表...');
      console.log('输入歌曲数量:', rawSongList.trim().split('\n').length);
      
      let matchedSongsData;
      try {
        // 调用真实 API 处理歌曲列表
        matchedSongsData = await processSongs(rawSongList);
        
        // 详细记录API响应结构，帮助调试
        console.log('处理完成，匹配结果:', matchedSongsData);
        console.log('API响应类型:', typeof matchedSongsData);
        console.log('API响应结构:', JSON.stringify(matchedSongsData, null, 2));
        console.log('matched_songs存在:', !!matchedSongsData.matched_songs);
        console.log('unmatched_songs存在:', !!matchedSongsData.unmatched_songs);
      } catch (processError) {
        console.error('API调用失败，创建默认结果:', processError);
        // 即使API调用失败，也创建一个默认的结果对象以允许用户继续
        matchedSongsData = {
          total_songs: rawSongList.trim().split('\n').length,
          matched_songs: [],
          unmatched_songs: rawSongList.trim().split('\n').map(song => ({ 
            original_input: song, 
            reason: '处理失败，可能是网络问题或服务器错误' 
          }))
        } as ProcessSongsData;
        
        // 记录错误，但不终止流程
        setProcessSongsError({
          code: 'PROCESS_WARNING',
          message: '歌曲处理部分失败，但您仍可继续查看结果',
          details: processError
        } as ApiError);
      }
      
      // 确保数据结构完整
      if (!matchedSongsData.matched_songs) {
        console.warn('API响应中缺少matched_songs字段');
        
        // 尝试修复结构问题 - 如果API响应不符合预期格式
        if (matchedSongsData && typeof matchedSongsData === 'object' && 'data' in matchedSongsData && 
            matchedSongsData.data && typeof matchedSongsData.data === 'object' && 
            'matched_songs' in matchedSongsData.data) {
          console.log('尝试从data嵌套对象中获取匹配数据');
          // 从嵌套结构中提取数据并进行类型断言
          matchedSongsData = matchedSongsData.data as ProcessSongsData;
        } else {
          // 如果无法找到嵌套的数据，确保字段存在
          const standardizedData: ProcessSongsData = {
            total_songs: matchedSongsData.total_songs || rawSongList.trim().split('\n').length,
            matched_songs: Array.isArray(matchedSongsData.matched_songs) ? matchedSongsData.matched_songs : [],
            unmatched_songs: Array.isArray(matchedSongsData.unmatched_songs) ? matchedSongsData.unmatched_songs : []
          };
          matchedSongsData = standardizedData;
        }
      }
      
      // 保存匹配结果 - 确保matchedSongsData符合ProcessSongsData类型
      setMatchedSongsData(matchedSongsData as ProcessSongsData);
      
      // 清除本地存储中的初始化标志，确保可以正确初始化新的歌曲集
      localStorage.removeItem(`selection-initialized-${(matchedSongsData as ProcessSongsData).total_songs}`);
      
      // 添加延迟确保状态更新完成后再跳转
      setTimeout(() => {
        // 处理完成后，跳转到概要页
        console.log('正在跳转到概要页...');
        goToSummaryStep();
      }, 500); // 增加延迟时间，确保状态已更新
    } catch (error) {
      console.error('处理歌曲列表失败:', error);
      setProcessSongsError(error as ApiError);
      
      // 即使出现错误，也尝试使用已有数据跳转到概要页
      try {
        if (rawSongList.trim()) {
          const defaultData: ProcessSongsData = {
            total_songs: rawSongList.trim().split('\n').length,
            matched_songs: [],
            unmatched_songs: rawSongList.trim().split('\n').map(song => ({ 
              original_input: song, 
              reason: '处理失败，可能是网络问题或服务器错误' 
            }))
          };
          
          setMatchedSongsData(defaultData);
          
          // 延迟跳转，确保用户看到错误信息
          setTimeout(() => {
            console.log('尽管有错误，仍尝试跳转到概要页...');
            goToSummaryStep();
          }, 1500);
        }
      } catch (fallbackError) {
        console.error('创建备用数据失败:', fallbackError);
        // 在这种情况下只能留在当前页面
      }
    } finally {
      setProcessingSongs(false);
    }
  };
  
  return (
    <div className="min-h-screen bg-[#121212]">
      {/* 全屏加载状态 */}
      {isProcessingSongs && (
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
            {/* 移除左上角的图标动画，只保留文字 */}
            <span className="text-white text-xl font-semibold">MusicMove</span>
          </div>
          
          {/* 导航按钮组 - 调整为right-0确保靠右显示 */}
          <div className="flex items-center space-x-4 ml-auto">
            {/* GitHub 仓库链接 */}
            <a 
              href="https://github.com/pawaovo/music_move" 
              target="_blank" 
              rel="noopener noreferrer" 
              className="flex items-center text-white hover:text-[#1DB954] transition"
              title="查看GitHub仓库"
            >
              <Github className="h-5 w-5" />
            </a>
            
            {/* 歌单处理按钮 */}
            <a 
              href="https://music.unmeta.cn/" 
              target="_blank" 
              rel="noopener noreferrer" 
              className="flex items-center bg-[#9945FF] hover:bg-[#8035DB] text-white rounded-full px-4 py-2 transition shadow-md"
            >
              <ExternalLink className="h-4 w-4 mr-1" />
              <span className="text-sm font-medium">歌单处理</span>
            </a>
            
            {/* Spotify 认证按钮 */}
            <AuthCheck />
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
            <textarea
              value={rawSongList}
              onChange={(e) => setRawSongList(e.target.value)}
              placeholder="输入歌曲列表，每行一首歌，例如：
The Beatles - Hey Jude
Beyoncé - Formation
周杰伦 - 稻香
五月天 - 倔强"
              className="w-full bg-[#181818] text-white resize-none focus:outline-none min-h-[150px] custom-scrollbar"
            />
          </div>

          {/* 搜索与授权提示 */}
          <div className="bg-[#333333] rounded-lg p-4 mb-6">
            <div className="flex items-start">
              <Info className="h-5 w-5 text-[#1DB954] flex-shrink-0 mt-0.5 mr-3" />
              <div className="text-[#B3B3B3] text-sm">
                <p className="font-medium text-white mb-1">功能提示</p>
                {!isAuthenticated ? (
                  <>
                    <p>本应用分为两个功能阶段：</p>
                    <ul className="list-disc list-inside mt-2 mb-2 space-y-1">
                      <li><span className="text-white">歌曲搜索</span>：无需登录，可直接使用本页面搜索Spotify上的歌曲</li>
                      <li><span className="text-white">创建播放列表</span>：需要您授权访问Spotify账号</li>
                    </ul>
                    <p>您可以先搜索歌曲，对结果满意后再进行授权创建播放列表。</p>
                  </>
                ) : (
                  <>
                    <p>您已连接到Spotify账户，可以使用所有功能：</p>
                    <ul className="list-disc list-inside mt-2 space-y-1">
                      <li>输入歌曲列表并点击下方按钮进行搜索</li>
                      <li>在搜索结果中选择要添加的歌曲</li>
                      <li>自定义播放列表名称和设置</li>
                      <li>一键创建播放列表并添加所选歌曲</li>
                    </ul>
                  </>
                )}
              </div>
            </div>
          </div>

          {/* Button */}
          <button 
            onClick={handleConvertSongList}
            disabled={isProcessingSongs}
            className={`block w-full py-3 ${
              isProcessingSongs ? 'bg-[#1DB954]/50' : 'bg-[#1DB954] hover:bg-[#1DB954]/90'
            } text-white rounded-full transition text-center font-medium`}
          >
            {isProcessingSongs ? '处理中...' : '搜索歌曲'}
          </button>
          
          {processSongsError && (
            <div className="mt-4 bg-red-500/10 text-red-500 p-3 rounded-md flex items-start">
              <AlertCircle className="h-5 w-5 mr-2 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-medium">处理歌曲时出错</p>
                <p className="text-sm">{processSongsError.message || '未知错误'}</p>
                {processSongsError.code && (
                  <p className="text-xs mt-1">错误代码: {processSongsError.code}</p>
                )}
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}

// 主页面组件，使用Suspense包裹HomeContent
export default function Home() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-[#121212] flex items-center justify-center">
        <div className="bg-[#282828] rounded-xl p-8 max-w-md w-full text-center">
          <div className="animate-spin h-12 w-12 border-4 border-t-[#1DB954] border-r-[#1DB954] border-b-transparent border-l-transparent rounded-full mx-auto mb-4"></div>
          <h1 className="text-white text-xl font-medium mb-2">加载中...</h1>
        </div>
      </div>
    }>
      <HomeContent />
    </Suspense>
  );
} 