'use client';

import { useEffect, useState, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuthStore } from '@/store/useStore';
import { checkAuthStatus } from '@/services/api';

// 创建一个包含useSearchParams的组件
function SuccessPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [redirecting, setRedirecting] = useState(true);
  
  const { setAuthState } = useAuthStore();
  
  useEffect(() => {
    async function checkAuth() {
      try {
        // 从URL参数中获取状态信息
        const status = searchParams.get('status');
        
        if (status !== 'true' && status !== 'success') {
          console.warn('授权成功页面收到非成功状态:', status);
        }
        
        // 添加重试机制，确保认证状态更新
        let retries = 0;
        const maxRetries = 5; // 增加重试次数
        let authSuccess = false;
        
        while (retries < maxRetries && !authSuccess) {
          // 检查认证状态
          console.log(`尝试检查认证状态 (尝试 ${retries + 1}/${maxRetries})...`);
          
          // 首次检查前等待一段时间，确保后端有足够时间处理Cookie
          if (retries === 0) {
            await new Promise(resolve => setTimeout(resolve, 2000)); // 首次等待2秒
          }
          
          const { isAuthenticated, userInfo } = await checkAuthStatus();
          
          if (isAuthenticated && userInfo) {
            console.log('成功获取用户信息:', userInfo);
            // 更新认证状态
            setAuthState(isAuthenticated, userInfo);
            authSuccess = true;
          } else {
            console.log('未获取到用户信息，将重试...');
            retries++;
            // 等待时间随着重试次数增加
            await new Promise(resolve => setTimeout(resolve, 1500 * retries)); // 逐渐增加等待时间
          }
        }
        
        // 成功获取用户信息后再重定向
        if (authSuccess) {
          console.log('认证状态已更新，即将重定向到首页...');
          // 延长等待时间，确保状态更新完成
          setTimeout(() => {
            setRedirecting(false);
            router.push('/');
          }, 3000); // 增加到3秒
        } else {
          console.warn('多次尝试后仍未获取到用户信息');
          setTimeout(() => {
            setRedirecting(false);
            router.push('/?authRetry=true');  // 添加参数，让首页知道需要重试认证
          }, 3000); // 增加到3秒
        }
      } catch (error) {
        console.error('检查认证状态失败:', error);
        // 出错时也重定向回主页
        setTimeout(() => {
          setRedirecting(false);
          router.push('/?authError=true');  // 添加错误参数
        }, 2500);
      }
    }
    
    checkAuth();
  }, [searchParams, router, setAuthState]);
  
  return (
    <div className="min-h-screen bg-[#121212] flex items-center justify-center">
      <div className="bg-[#282828] rounded-xl p-8 max-w-md w-full text-center">
        <div className="h-12 w-12 rounded-full bg-transparent border-2 border-[#1DB954] flex items-center justify-center mx-auto mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-[#1DB954]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <h1 className="text-white text-xl font-medium mb-2">授权成功！</h1>
        <p className="text-[#B3B3B3]">您已成功授权应用访问Spotify，正在返回主页...</p>
        
        {redirecting && (
          <div className="mt-4">
            <div className="h-1 bg-[#535353] rounded-full overflow-hidden">
              <div className="h-full bg-[#1DB954] rounded-full animate-progress"></div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// 主页面组件，使用Suspense包裹SuccessPageContent
export default function SpotifyAuthSuccessPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-[#121212] flex items-center justify-center">
        <div className="bg-[#282828] rounded-xl p-8 max-w-md w-full text-center">
          <div className="animate-spin h-12 w-12 border-4 border-t-[#1DB954] border-r-[#1DB954] border-b-transparent border-l-transparent rounded-full mx-auto mb-4"></div>
          <h1 className="text-white text-xl font-medium mb-2">加载中...</h1>
        </div>
      </div>
    }>
      <SuccessPageContent />
    </Suspense>
  );
} 