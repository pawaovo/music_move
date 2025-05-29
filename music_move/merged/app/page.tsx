'use client';

import { ChevronLeft, Github, Info, AlertCircle, Loader2 } from "lucide-react"
import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import StoreDemo from "../components/StoreDemo";
import { useSongProcessStore, useAuthStore } from "../store/useStore";
import { useAppSteps, AppStep } from "../hooks/useAppSteps";
import { processSongs, checkAuthStatus } from "../services/api";
import { ProcessSongsData, ApiError } from "../store/types";

export default function Home() {
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
  
  // 演示模式切换
  const [showDemo, setShowDemo] = useState(false);

  // 处理从认证页面返回
  useEffect(() => {
    // 检查URL参数
    const authRetry = searchParams.get('authRetry');
    const authError = searchParams.get('authError');
    
    if (authRetry === 'true' || authError === 'true' || !isAuthenticated) {
      console.log('检测到认证参数或未认证状态，刷新认证状态...');
      
      const refreshAuthStatus = async () => {
        try {
          // 添加重试机制
          let retries = 0;
          const maxRetries = 3;
          let authSuccess = false;
          
          while (retries < maxRetries && !authSuccess) {
            console.log(`尝试刷新认证状态 (尝试 ${retries + 1}/${maxRetries})...`);
            const { isAuthenticated, userInfo } = await checkAuthStatus();
            
            if (isAuthenticated && userInfo) {
              console.log('成功获取用户信息:', userInfo);
              // 更新认证状态
              setAuthState(isAuthenticated, userInfo);
              authSuccess = true;
              break;
            } else {
              console.log('未获取到用户信息，将重试...');
              retries++;
              // 等待短暂时间后重试
              await new Promise(resolve => setTimeout(resolve, 1000));
            }
          }
          
          if (!authSuccess) {
            console.warn('多次尝试后仍未获取到用户信息');
          }
        } catch (error) {
          console.error('刷新认证状态失败:', error);
        }
      };
      
      refreshAuthStatus();
    }
  }, [searchParams, isAuthenticated, setAuthState]);
  
  // 调试信息
  useEffect(() => {
    console.log('当前页面路径:', currentStep);
    console.log('API基础URL:', process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8888');
    console.log('用户认证状态:', isAuthenticated ? '已认证' : '未认证');
  }, [currentStep, isAuthenticated]);
  
  // 处理歌曲列表转换
  const handleConvertSongList = async () => {
    if (!rawSongList.trim()) {
      alert('请输入歌曲列表');
      return;
    }
    
    try {
      // 设置加载状态
      setProcessingSongs(true);
      setProcessSongsError(null);
      
      console.log('开始处理歌曲列表...');
      console.log('输入歌曲数量:', rawSongList.trim().split('\n').length);
      
      // 调用真实 API 处理歌曲列表
      const matchedSongsData = await processSongs(rawSongList);
      
      // 详细记录API响应结构，帮助调试
      console.log('处理完成，匹配结果:', matchedSongsData);
      console.log('API响应类型:', typeof matchedSongsData);
      console.log('API响应结构:', JSON.stringify(matchedSongsData, null, 2));
      console.log('matched_songs存在:', !!matchedSongsData.matched_songs);
      console.log('unmatched_songs存在:', !!matchedSongsData.unmatched_songs);
      
      if (!matchedSongsData.matched_songs) {
        console.error('API响应中缺少matched_songs字段');
        
        // 尝试修复结构问题 - 如果API响应不符合预期格式
        if (matchedSongsData && typeof matchedSongsData === 'object' && 'data' in matchedSongsData && 
            matchedSongsData.data && typeof matchedSongsData.data === 'object' && 
            'matched_songs' in matchedSongsData.data) {
          console.log('尝试从data嵌套对象中获取匹配数据');
          // @ts-ignore - 处理可能的嵌套数据结构
          setMatchedSongsData(matchedSongsData.data);
        } else {
          // 如果无法找到嵌套的数据，至少确保字段存在
          setMatchedSongsData({
            ...matchedSongsData,
            matched_songs: matchedSongsData.matched_songs || [],
            unmatched_songs: matchedSongsData.unmatched_songs || []
          });
        }
      } else {
        // 保存匹配结果
        setMatchedSongsData(matchedSongsData);
      }
      
      // 清除本地存储中的初始化标志，确保可以正确初始化新的歌曲集
      localStorage.removeItem(`selection-initialized-${matchedSongsData.total_songs}`);
      
      // 添加延迟确保状态更新完成后再跳转
      setTimeout(() => {
        // 处理完成后，跳转到概要页
        console.log('正在跳转到概要页...');
        goToSummaryStep();
      }, 100);
    } catch (error) {
      console.error('处理歌曲列表失败:', error);
      setProcessSongsError(error as ApiError);
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
              onClick={() => setShowDemo(!showDemo)}
              className="text-white hover:text-[#1DB954] transition text-sm"
            >
              {showDemo ? '隐藏演示' : '显示演示'}
            </button>
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
        
        {/* 演示组件 */}
        {showDemo && (
          <div className="mt-8">
            <StoreDemo />
          </div>
        )}
      </main>
    </div>
  )
} 