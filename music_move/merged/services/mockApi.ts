import { SpotifyUserInfo } from '../store/types';

// 模拟用户数据
const mockUser: SpotifyUserInfo = {
  id: 'mock-user-id',
  display_name: '测试用户',
  images: [{ url: 'https://i.scdn.co/image/ab6775700000ee85d3ed8577304b97115b19c8a8' }]
};

/**
 * 模拟延迟函数
 * @param ms 延迟毫秒数
 */
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

/**
 * 模拟检查认证状态API
 * @returns 认证状态响应
 */
export async function mockCheckAuthStatus() {
  await delay(500); // 模拟网络延迟
  
  // 从localStorage获取认证状态
  const isAuthenticated = localStorage.getItem('mock_authenticated') === 'true';
  
  return {
    isAuthenticated,
    userInfo: isAuthenticated ? mockUser : null
  };
}

/**
 * 模拟获取授权URL API
 * @returns 授权URL
 */
export async function mockGetAuthUrl() {
  await delay(500); // 模拟网络延迟
  
  // 返回模拟授权URL，实际上是本地callback页面
  return '/auth/mock-callback';
}

/**
 * 模拟设置认证状态
 * @param authenticated 是否已认证
 */
export function mockSetAuthState(authenticated: boolean) {
  localStorage.setItem('mock_authenticated', authenticated.toString());
} 