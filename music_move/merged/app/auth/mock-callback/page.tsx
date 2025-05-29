'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { mockSetAuthState } from '@/services/mockApi';

export default function MockAuthCallbackPage() {
  const router = useRouter();
  const [status, setStatus] = useState<'loading' | 'success'>('loading');
  
  useEffect(() => {
    // 模拟认证成功
    mockSetAuthState(true);
    setStatus('success');
    
    // 2秒后重定向回主页
    const timer = setTimeout(() => {
      router.push('/');
    }, 2000);
    
    return () => clearTimeout(timer);
  }, [router]);
  
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
            <h1 className="text-white text-xl font-medium mb-2">模拟认证成功！</h1>
            <p className="text-[#B3B3B3]">您已成功登录Spotify，即将返回主页...</p>
            <p className="mt-4 text-[#B3B3B3] text-xs">
              这是一个模拟的认证回调，用于演示UI流程。<br />
              在实际环境中，您将被重定向到Spotify的真实授权页面。
            </p>
          </>
        )}
      </div>
    </div>
  );
} 