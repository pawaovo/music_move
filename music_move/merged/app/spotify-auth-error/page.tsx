'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuthStore } from '@/store/useStore';

export default function SpotifyAuthErrorPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [errorMessage, setErrorMessage] = useState('授权过程中发生错误');
  
  useEffect(() => {
    // 从URL参数中获取错误信息
    const message = searchParams.get('message');
    if (message) {
      setErrorMessage(decodeURIComponent(message));
    }
    
    // 清除可能有的错误认证状态
    // 这里不需要调用checkAuthStatus，因为我们已经知道授权失败了
  }, [searchParams]);
  
  // 返回主页
  const handleGoHome = () => {
    router.push('/');
  };
  
  // 重试授权
  const handleRetry = () => {
    router.push('/');
    // 通过URL参数告诉首页打开授权窗口
    // 这里添加一个参数，主页可以检测这个参数并自动触发授权流程
    window.history.replaceState({}, '', '/?openAuth=true');
    window.location.reload();
  };
  
  return (
    <div className="min-h-screen bg-[#121212] flex items-center justify-center">
      <div className="bg-[#282828] rounded-xl p-8 max-w-md w-full text-center">
        <div className="h-12 w-12 rounded-full bg-transparent border-2 border-red-500 flex items-center justify-center mx-auto mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </div>
        <h1 className="text-white text-xl font-medium mb-2">授权失败</h1>
        <p className="text-[#B3B3B3] mb-6">{errorMessage}</p>
        
        <div className="flex flex-col gap-3">
          <button
            onClick={handleRetry}
            className="w-full bg-[#1DB954] hover:bg-[#1DB954]/90 text-white rounded-full py-3 font-medium transition"
          >
            重新尝试
          </button>
          
          <button
            onClick={handleGoHome}
            className="w-full py-2 px-4 border border-[#535353] text-white rounded-full hover:bg-[#333333] transition"
          >
            返回首页
          </button>
        </div>
      </div>
    </div>
  );
} 