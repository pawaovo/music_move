'use client';

import { ReactNode } from 'react';
import AuthCheck from '@/components/AuthCheck';

interface ProvidersProps {
  children: ReactNode;
}

/**
 * 全局客户端组件提供者
 * 用于包装使用use client的组件
 */
export default function Providers({ children }: ProvidersProps) {
  return (
    <>
      {/* 全局认证检查组件 */}
      <AuthCheck />

      {/* 页面内容 */}
      {children}
    </>
  );
} 