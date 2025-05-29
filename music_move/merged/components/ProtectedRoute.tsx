'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/useStore';
import { checkAuthStatus, getAuthUrl } from '@/services/api';
import Image from 'next/image';
import { AlertCircle, RefreshCw } from 'lucide-react';

/**
 * 需要认证的路由包装组件
 * 保护需要认证的页面，未认证时显示授权提示或重定向到首页
 */
export default function ProtectedRoute({
  children,
  redirectTo = '/',
}: {
  children: React.ReactNode;
  redirectTo?: string;
}) {
  const router = useRouter();
  const { isAuthenticated, isCheckingAuth, setAuthState, setCheckingAuth } = useAuthStore();
  const [isChecked, setIsChecked] = useState(false);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authUrl, setAuthUrl] = useState('');
  const [spotifyLoginStatus, setSpotifyLoginStatus] = useState<'unknown' | 'logged_in' | 'logged_out'>('unknown');
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    async function checkAuth() {
      if (!isAuthenticated && !isCheckingAuth) {
        try {
          setCheckingAuth(true);
          const response = await checkAuthStatus();
          setAuthState(response.isAuthenticated, response.userInfo);
          
          // 设置Spotify登录状态
          if (response.spotifyLoginStatus !== undefined) {
            setSpotifyLoginStatus(response.spotifyLoginStatus ? 'logged_in' : 'logged_out');
          }
          
          if (!response.isAuthenticated) {
            // 用户已登录Spotify但未授权本应用，显示授权模态框
            if (response.spotifyLoginStatus === true) {
              try {
                // 获取授权URL
                const url = await getAuthUrl();
                if (url) {
                  setAuthUrl(url);
                  setShowAuthModal(true);
                } else {
                  // 无法获取授权URL，重定向到首页
                  router.push(redirectTo);
                }
              } catch (error) {
                console.error('获取授权URL失败:', error);
                router.push(redirectTo);
              }
            } else {
              // 用户未登录Spotify，直接重定向到首页
            router.push(redirectTo);
            }
          }
        } catch (error) {
          console.error('检查认证状态失败:', error);
          // 发生错误，重定向到指定页面
          router.push(redirectTo);
        } finally {
          setCheckingAuth(false);
          setIsChecked(true);
        }
      } else {
        setIsChecked(true);
      }
    }
    
    checkAuth();
  }, [isAuthenticated, isCheckingAuth, setAuthState, setCheckingAuth, router, redirectTo]);
  
  // 手动刷新认证状态
  const handleRefreshAuth = async () => {
    try {
      setError(null);
      setCheckingAuth(true);
      
      console.log('手动刷新认证状态...');
      const response = await checkAuthStatus();
      
      setAuthState(response.isAuthenticated, response.userInfo);
      
      if (response.isAuthenticated) {
        setShowAuthModal(false);
      }
    } catch (error) {
      console.error('刷新认证状态失败:', error);
      setError('刷新认证状态失败，请稍后重试');
    } finally {
      setCheckingAuth(false);
    }
  };
  
  // 如果正在检查认证状态或尚未完成检查，显示加载状态
  if (isCheckingAuth || !isChecked) {
    return (
      <div className="min-h-screen bg-[#121212] flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin h-12 w-12 border-4 border-t-[#1DB954] border-r-[#1DB954] border-b-transparent border-l-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-white text-lg">验证身份中...</p>
        </div>
      </div>
    );
  }
  
  // 如果显示授权模态框
  if (showAuthModal) {
    return (
      <div className="min-h-screen bg-[#121212] flex items-center justify-center p-4">
        <div className="bg-[#282828] rounded-xl p-6 max-w-md w-full">
          <h2 className="text-white text-xl font-medium mb-4 text-center">需要授权访问</h2>
          
          <div className="mb-6">
            <div className="flex items-center justify-center mb-4">
              <Image src="/spotify-logo.svg" alt="Spotify Logo" width={40} height={40} />
            </div>
            
            <p className="text-[#B3B3B3] mb-4 text-center whitespace-pre-line">
              {spotifyLoginStatus === 'logged_in' 
                ? '您已登录Spotify账号，但需要授权本应用访问您的Spotify数据，才能创建播放列表。\n\n授权后，本应用仅会创建您指定的播放列表，不会修改您现有的内容。您可以随时在Spotify设置中撤销授权。'
                : '访问此页面需要先登录Spotify账号并授权本应用。\n\n此过程分为两步：\n1. 使用您的Spotify账号登录\n2. 授权本应用访问您的数据以创建播放列表'}
            </p>
            
            <div className="bg-[#1DB954]/10 rounded-md p-3 mb-4">
              <p className="text-[#1DB954] text-sm text-center">
                请在完成授权后点击"我已完成授权"按钮
              </p>
            </div>
          </div>
          
          {error && (
            <div className="mb-6 bg-red-500/10 text-red-500 px-4 py-3 rounded-md flex items-center">
              <AlertCircle className="h-5 w-5 mr-2 flex-shrink-0" />
              <span className="text-sm flex-grow">{error}</span>
              <button 
                onClick={() => setError(null)} 
                className="ml-2 text-red-500 hover:text-red-400 flex-shrink-0"
              >
                ×
              </button>
            </div>
          )}
          
          <div className="flex flex-col gap-4">
            <button
              onClick={() => {
                // 使用窗口打开Spotify授权页面
                window.open(
                  authUrl,
                  'SpotifyAuth',
                  'width=500,height=700,left=200,top=200'
                );
              }}
              className="flex items-center justify-center w-full bg-[#1DB954] hover:bg-[#1ed760] text-white py-3 px-4 rounded-full transition-colors font-medium"
            >
              <Image src="/spotify-logo.svg" alt="Spotify Logo" width={24} height={24} className="mr-2" />
              {spotifyLoginStatus === 'logged_in' ? '授权本应用' : '登录并授权Spotify'}
            </button>
            
            <button
              onClick={handleRefreshAuth}
              className="flex items-center justify-center w-full bg-[#333333] hover:bg-[#444444] text-white py-3 px-4 rounded-full transition-colors font-medium"
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              我已完成授权
            </button>
            
            <button
              onClick={() => router.push(redirectTo)}
              className="w-full py-2 px-4 border border-[#535353] text-white rounded-full hover:bg-[#333333] transition-colors"
            >
              返回首页
            </button>
          </div>
          
          <div className="mt-4 text-[#B3B3B3] text-xs text-center">
            <p>本应用仅请求创建播放列表所需的最小权限</p>
            <p>您可以随时在Spotify设置中撤销授权</p>
          </div>
        </div>
      </div>
    );
  }
  
  // 已认证，显示子组件
  return isAuthenticated ? <>{children}</> : null;
} 