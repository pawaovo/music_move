'use client';

import { useEffect, useState } from 'react';
import { useAuthStore } from '@/store/useStore';
// 使用真实API
import { checkAuthStatus, getAuthUrl, logout } from '@/services/api';
import { SpotifyUserInfo } from '@/store/types';
import Image from 'next/image';
import { LogOut, AlertCircle, RefreshCw } from 'lucide-react';

/**
 * 全局认证检查组件
 * 在应用加载时检查认证状态
 * 未认证时提供登录/授权功能
 */
export default function AuthCheck() {
  const { isAuthenticated, userInfo, isCheckingAuth, setAuthState, setCheckingAuth } = useAuthStore();
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authUrl, setAuthUrl] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [backendStatus, setBackendStatus] = useState<'unknown' | 'online' | 'offline'>('unknown');
  
  // 新增：用户Spotify登录状态
  const [spotifyLoginStatus, setSpotifyLoginStatus] = useState<'unknown' | 'logged_in' | 'logged_out'>('unknown');
  
  // 初始化时检查认证状态
  useEffect(() => {
    async function checkAuth() {
      try {
        setCheckingAuth(true);
        setError(null);
        
        console.log('正在检查认证状态...');
        // 使用真实API
        const response = await checkAuthStatus();
        console.log('认证状态响应:', response);
        
        if (response.error) {
          setBackendStatus('offline');
          throw new Error(response.error as string);
        }
        
        setBackendStatus('online');
        
        // 检查并更新认证状态和用户信息
        if (response.isAuthenticated && response.userInfo) {
          console.log('用户已认证，用户信息:', response.userInfo);
          setAuthState(true, response.userInfo as SpotifyUserInfo);
        } else {
          console.log('用户未认证或无用户信息');
          setAuthState(false, null);
        }
        
        // 设置Spotify登录状态 - 从API响应中获取
        if (response.spotifyLoginStatus) {
          setSpotifyLoginStatus(response.spotifyLoginStatus === true ? 'logged_in' : 'logged_out');
        } else {
          // 向后兼容 - 如果后端未提供登录状态信息
          setSpotifyLoginStatus('unknown');
        }
      } catch (error) {
        console.error('检查认证状态失败:', error);
        setBackendStatus('offline');
        setError('无法连接到服务器，请确保后端服务正在运行(http://localhost:8888)。后端报错：' + (error instanceof Error ? error.message : String(error)));
      } finally {
        setCheckingAuth(false);
      }
    }
    
    checkAuth();
  }, [setAuthState, setCheckingAuth]);
  
  // 获取授权URL
  const handleGetAuthUrl = async () => {
    try {
      setError(null);
      console.log('点击获取授权URL按钮');
      
      // 使用真实API
      const url = await getAuthUrl();
      console.log('获取到的授权URL:', url);
      
      if (!url) {
        throw new Error('获取授权URL失败：返回的URL为空');
      }
      
      // 直接重定向到Spotify授权页面
      window.location.href = url;
    } catch (error) {
      console.error('获取授权URL失败:', error);
      setError('无法获取Spotify授权链接，请确保后端服务正在运行(http://localhost:8888)。后端报错：' + (error instanceof Error ? error.message : String(error)));
    }
  };
  
  // 手动刷新认证状态
  const handleRefreshAuth = async () => {
    try {
      setError(null);
      setCheckingAuth(true);
      
      console.log('手动刷新认证状态...');
      // 使用真实API
      const response = await checkAuthStatus();
      console.log('手动刷新认证状态响应:', response);
      
      if (response.error) {
        setBackendStatus('offline');
        throw new Error(response.error as string);
      }
      
      setBackendStatus('online');
      setAuthState(response.isAuthenticated, response.userInfo as SpotifyUserInfo);
      
      // 更新Spotify登录状态
      if (response.spotifyLoginStatus) {
        setSpotifyLoginStatus(response.spotifyLoginStatus === true ? 'logged_in' : 'logged_out');
      }
      
      setCheckingAuth(false);
    } catch (error) {
      console.error('刷新认证状态失败:', error);
      setBackendStatus('offline');
      setError('刷新认证状态失败，请确保后端服务正在运行(http://localhost:8888)。后端报错：' + (error instanceof Error ? error.message : String(error)));
      setCheckingAuth(false);
    }
  };
  
  // 登出
  const handleLogout = async () => {
    try {
      console.log('开始登出操作...');
      setError(null);
      
      // 先清除前端状态，确保即使API调用失败，用户体验上也是已登出状态
      setAuthState(false, null);
      // 重置Spotify登录状态
      setSpotifyLoginStatus('unknown');
      
      try {
        // 尝试调用后端登出API
        await logout();
        console.log('后端登出API调用成功');
      } catch (error) {
        // 即使后端API调用失败，也保持前端已登出状态
        console.error('后端登出API调用失败:', error);
        // 不显示错误给用户，因为前端已经清除了登录状态
      }
    } catch (error) {
      console.error('登出过程中发生意外错误:', error);
      // 即使在整个过程中出现错误，也不还原登录状态
    }
  };
  
  // 获取认证按钮文本，根据Spotify登录状态显示不同文案
  const getAuthButtonText = () => {
    if (spotifyLoginStatus === 'logged_in') {
      return '授权访问Spotify';
    } else if (spotifyLoginStatus === 'logged_out') {
      return '登录并授权Spotify';
    } else {
      return '连接 Spotify';
    }
  };
  
  // 获取模态框说明文本，根据Spotify登录状态显示不同文案
  const getAuthModalText = () => {
    if (spotifyLoginStatus === 'logged_in') {
      return '您已登录Spotify账号，现在需要授权本应用访问您的Spotify数据。授权后，本应用可以根据您的需求创建播放列表并添加歌曲，但不会修改您现有的任何内容。您可以随时在Spotify设置中撤销授权。';
    } else if (spotifyLoginStatus === 'logged_out') {
      return '您需要先登录Spotify账号，然后授权本应用访问您的Spotify数据。此过程分为两步：\n1. 使用您的Spotify账号登录\n2. 授权本应用访问您的数据以创建播放列表';
    } else {
      return '要使用完整功能，您需要连接到Spotify账户。\n\n歌曲搜索功能无需登录即可使用，但创建播放列表需要您的授权。点击下方按钮跳转到Spotify授权页面。';
    }
  };
  
  // 获取模态框按钮文本
  const getAuthModalButtonText = () => {
    if (spotifyLoginStatus === 'logged_in') {
      return '授权本应用';
    } else if (spotifyLoginStatus === 'logged_out') {
      return '登录并授权';
    } else {
      return '前往Spotify授权';
    }
  };
  
  // 如果正在检查认证状态，显示加载状态
  if (isCheckingAuth) return (
    <div className="fixed top-4 right-4 z-50">
      <div className="flex items-center bg-[#282828] rounded-full p-2 pr-4 shadow-md">
        <RefreshCw className="h-4 w-4 mr-2 text-[#1DB954] animate-spin" />
        <span className="text-white text-sm">检查认证状态...</span>
      </div>
    </div>
  );
  
  return (
    <>
      {/* 认证状态显示/登录按钮 */}
      <div className="fixed top-4 right-4 z-50">
        {isAuthenticated && userInfo ? (
          <div className="flex items-center bg-[#282828] rounded-full p-1 pr-4 shadow-md">
            {userInfo.images && userInfo.images.length > 0 ? (
              <Image
                src={userInfo.images[0].url}
                alt={userInfo.display_name}
                width={32}
                height={32}
                className="rounded-full mr-2"
              />
            ) : (
              <div className="w-8 h-8 rounded-full bg-[#1DB954] flex items-center justify-center mr-2">
                <span className="text-white text-sm font-medium">
                  {userInfo.display_name?.charAt(0).toUpperCase() || 'U'}
                </span>
              </div>
            )}
            <span className="text-white text-sm mr-2">{userInfo.display_name}</span>
            <button
              onClick={handleLogout}
              className="text-[#B3B3B3] hover:text-white transition"
              title="登出"
            >
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        ) : (
          <button
            onClick={handleGetAuthUrl}
            className="flex items-center bg-[#1DB954] hover:bg-[#1DB954]/90 text-white rounded-full px-4 py-2 transition shadow-md"
          >
            <span className="text-sm font-medium">{getAuthButtonText()}</span>
          </button>
        )}
      </div>
      
      {/* Spotify登录状态指示器 */}
      {!isAuthenticated && spotifyLoginStatus === 'logged_in' && (
        <div className="fixed top-16 right-4 z-50">
          <div className="flex items-center bg-[#282828] rounded-full py-2 px-4 shadow-md">
            <div className="w-3 h-3 rounded-full bg-[#1DB954] mr-2"></div>
            <span className="text-white text-sm">已登录Spotify，需授权本应用</span>
          </div>
        </div>
      )}
      
      {/* 后端状态指示器 */}
      {backendStatus === 'offline' && (
        <div className="fixed top-4 left-4 z-50">
          <div className="flex items-center bg-[#282828] rounded-full py-2 px-4 shadow-md">
            <div className="w-3 h-3 rounded-full bg-red-500 mr-2"></div>
            <span className="text-white text-sm mr-3">后端离线</span>
            <button 
              onClick={handleRefreshAuth}
              className="text-[#1DB954] hover:text-[#1ed760] transition text-sm flex items-center"
            >
              <RefreshCw className="h-3 w-3 mr-1" />
              重新连接
            </button>
          </div>
        </div>
      )}
      
      {/* 错误提示 */}
      {error && (
        <div className="fixed top-16 left-1/2 transform -translate-x-1/2 z-50 bg-red-500 text-white px-4 py-3 rounded-md flex items-center shadow-lg max-w-md w-full">
          <AlertCircle className="h-5 w-5 mr-2 flex-shrink-0" />
          <span className="text-sm flex-grow">{error}</span>
          <button 
            onClick={() => setError(null)} 
            className="ml-2 text-white hover:text-red-100 flex-shrink-0"
          >
            ×
          </button>
        </div>
      )}
      
      {/* 认证模态框 */}
      {showAuthModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="bg-[#282828] rounded-xl p-6 max-w-md w-full">
            <h2 className="text-white text-xl font-medium mb-4 text-center">
              {spotifyLoginStatus === 'logged_in' ? '授权应用访问' : '连接到Spotify'}
            </h2>
            
            <div className="mb-6">
              <div className="flex items-center justify-center mb-4">
                <Image 
                  src="/spotify-logo.svg" 
                  alt="Spotify Logo" 
                  width={40} 
                  height={40} 
                />
              </div>
              
              <p className="text-[#B3B3B3] text-center whitespace-pre-line">
                {getAuthModalText()}
              </p>
            </div>
            
            <div className="flex flex-col gap-4">
              <button
                onClick={() => {
                  if (authUrl) {
                    window.location.href = authUrl;
                  }
                }}
                className="w-full bg-[#1DB954] hover:bg-[#1DB954]/90 text-white rounded-full py-3 font-medium transition"
              >
                {getAuthModalButtonText()}
              </button>
              
              <button
                onClick={() => setShowAuthModal(false)}
                className="w-full py-2 px-4 border border-[#535353] text-white rounded-full hover:bg-[#333333] transition"
              >
                稍后再说
              </button>
            </div>
            
            <div className="mt-4 text-[#B3B3B3] text-xs text-center">
              <p>本应用仅请求创建播放列表所需的最小权限</p>
              <p>您可以随时在Spotify设置中撤销授权</p>
            </div>
          </div>
        </div>
      )}
    </>
  );
} 