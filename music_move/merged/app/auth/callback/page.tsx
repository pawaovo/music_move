'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuthStore } from '@/store/useStore';
import { checkAuthStatus } from '@/services/api';

export default function AuthCallbackPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [errorMessage, setErrorMessage] = useState('');
  
  const { setAuthState } = useAuthStore();
  
  useEffect(() => {
    async function handleCallback() {
      try {
        // 验证是否有错误参数
        const error = searchParams.get('error');
        if (error) {
          setStatus('error');
          setErrorMessage(error);
          return;
        }
        
        // 获取授权码
        const code = searchParams.get('code');
        if (!code) {
          setStatus('error');
          setErrorMessage('缺少授权码');
          return;
        }
        
        // 这里不需要进一步处理，后端API已经处理了授权码
        // 检查认证状态
        const { isAuthenticated, userInfo } = await checkAuthStatus();
        
        // 更新认证状态
        setAuthState(isAuthenticated, userInfo);
        
        if (isAuthenticated) {
          setStatus('success');
          
          // 如果是在弹出窗口中打开的，通知父窗口认证成功
          if (window.opener && !window.opener.closed) {
            // 通知父窗口认证成功
            window.opener.postMessage({ type: 'SPOTIFY_AUTH_SUCCESS', user: userInfo }, window.location.origin);
            
            // 2秒后关闭窗口
            setTimeout(() => {
              window.close();
            }, 2000);
          } else {
            // 如果不是在弹窗中，短暂停留后重定向回主页
            setTimeout(() => {
              router.push('/');
            }, 2000);
          }
        } else {
          setStatus('error');
          setErrorMessage('认证失败，请重试');
        }
      } catch (error) {
        console.error('认证回调处理失败:', error);
        setStatus('error');
        setErrorMessage('认证过程中发生错误');
      }
    }
    
    handleCallback();
  }, [searchParams, router, setAuthState]);
  
  // 渲染认证回调页面
  return (
    <div className="min-h-screen bg-[#121212] flex items-center justify-center">
      <div className="bg-[#282828] rounded-xl p-8 max-w-md w-full text-center">
        {status === 'loading' && (
          <>
            <div className="animate-spin h-12 w-12 border-4 border-t-[#1DB954] border-r-[#1DB954] border-b-transparent border-l-transparent rounded-full mx-auto mb-4"></div>
            <h1 className="text-white text-xl font-medium mb-2">正在处理认证...</h1>
            <p className="text-[#B3B3B3]">请稍候，正在完成Spotify认证</p>
          </>
        )}
        
        {status === 'success' && (
          <>
            <div className="h-12 w-12 rounded-full bg-transparent border-2 border-[#1DB954] flex items-center justify-center mx-auto mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-[#1DB954]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h1 className="text-white text-xl font-medium mb-2">认证成功！</h1>
            <p className="text-[#B3B3B3]">您已成功登录Spotify，此窗口将自动关闭...</p>
          </>
        )}
        
        {status === 'error' && (
          <>
            <div className="h-12 w-12 rounded-full bg-transparent border-2 border-red-500 flex items-center justify-center mx-auto mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <h1 className="text-white text-xl font-medium mb-2">认证失败</h1>
            <p className="text-[#B3B3B3] mb-4">{errorMessage || '认证过程中发生错误，请重试'}</p>
            <button
              onClick={() => window.close()}
              className="bg-[#1DB954] hover:bg-[#1DB954]/90 text-white px-4 py-2 rounded-full transition"
            >
              关闭窗口
            </button>
          </>
        )}
      </div>
    </div>
  );
} 