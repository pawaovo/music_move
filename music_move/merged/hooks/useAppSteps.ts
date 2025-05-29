import { useRouter, usePathname } from 'next/navigation';

// 应用步骤枚举
export enum AppStep {
  INPUT = '/',
  SUMMARY = '/summary',
  COMPLETED = '/complete',
}

/**
 * 使用基于页面路径的步骤管理 hook
 * 
 * 优点:
 * - 使用实际的页面路由，与Next.js的路由系统更好地集成
 * - 通过浏览器历史记录可以实现前进/后退导航
 * - 更清晰的URL结构
 */
export function useAppSteps() {
  const router = useRouter();
  const pathname = usePathname();
  
  // 判断当前是否为特定步骤
  const isInputStep = pathname === AppStep.INPUT;
  const isSummaryStep = pathname === AppStep.SUMMARY;
  const isCompletedStep = pathname === AppStep.COMPLETED;
  
  // 导航到特定步骤（确保不同的页面）
  const goToInputStep = () => {
    console.log('导航到输入步骤:', AppStep.INPUT);
    if (pathname !== AppStep.INPUT) {
      router.push(AppStep.INPUT);
    }
  };
  
  const goToSummaryStep = () => {
    console.log('导航到概要步骤:', AppStep.SUMMARY);
    if (pathname !== AppStep.SUMMARY) {
      router.push(AppStep.SUMMARY);
    }
  };
  
  const goToCompletedStep = () => {
    console.log('导航到完成步骤:', AppStep.COMPLETED);
    if (pathname !== AppStep.COMPLETED) {
      router.push(AppStep.COMPLETED);
    }
  };
  
  return {
    currentStep: pathname as AppStep,
    isInputStep,
    isSummaryStep,
    isCompletedStep,
    goToInputStep,
    goToSummaryStep,
    goToCompletedStep,
  };
} 