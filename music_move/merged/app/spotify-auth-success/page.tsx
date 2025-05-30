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
    async function attemptAuthAndRedirect() {
      const status = searchParams.get('status');
      if (status !== 'true' && status !== 'success') {
        console.warn('授权成功页面收到非成功状态:', status);
        // 即使状态不是 'true' 或 'success'，也尝试检查一次认证并跳转
      }

      console.log('Spotify授权成功，开始检查认证状态并准备跳转...');

      try {
        // 尝试检查认证状态，给后端一点时间设置cookie
        await new Promise(resolve => setTimeout(resolve, 1000)); // 等待1秒，以便cookie设置

        const { isAuthenticated, userInfo } = await checkAuthStatus();

        if (isAuthenticated && userInfo) {
          console.log('认证成功，用户信息:', userInfo, '即将跳转到首页。');
          setAuthState(isAuthenticated, userInfo);
          router.push('/');
        } else {
          console.warn('授权回调后未能立即确认认证状态，尝试跳转到首页让其重新检查。');
          // 即使未能立即确认，也跳转到首页，首页的AuthCheck会再次检查
          // 或者可以尝试一次短暂的重试
          await new Promise(resolve => setTimeout(resolve, 1500)); // 再等待1.5秒
          const { isAuthenticated: retryIsAuthenticated, userInfo: retryUserInfo } = await checkAuthStatus();
          if (retryIsAuthenticated && retryUserInfo) {
            console.log('重试认证成功，用户信息:', retryUserInfo, '即将跳转到首页。');
            setAuthState(retryIsAuthenticated, retryUserInfo);
            router.push('/');
          } else {
            console.warn('重试后仍未认证，跳转到首页并带参数。');
            router.push('/?authRetry=true&source=spotify-auth-success-simplified');
          }
        }
      } catch (error) {
        console.error('在spotify-auth-success页面检查认证状态或跳转时出错:', error);
        // 出错时也尝试跳转到首页
        router.push('/?authError=true&source=spotify-auth-success-simplified-error');
      } finally {
        // 无论结果如何，都标记为不再重定向（虽然此时应该已经跳转了）
        setRedirecting(false); 
      }
    }

    attemptAuthAndRedirect();
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