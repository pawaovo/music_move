'use client';

import { ReactNode } from 'react';

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
      {/* 移除全局认证检查组件 */}

      {/* 页面内容 */}
      {children}
    </>
  );
} 