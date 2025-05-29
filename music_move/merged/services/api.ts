import { SpotifyUserInfo, ApiError, AuthStatusResponse, ProcessSongsData } from '../store/types';

// API基础URL - 使用环境变量或默认值
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8888';
// 修复API路径
console.log('使用API基础URL:', API_BASE_URL);

// 错误处理工具
function handleFetchError(error: any): string {
  console.error('API错误详情:', error);

  // 网络连接错误
  if (error.message && error.message.includes('Failed to fetch')) {
    return `网络连接错误：无法连接到后端服务。请确保后端服务在 ${API_BASE_URL} 正常运行，或检查您的网络连接。`;
  }
  
  // CORS错误
  if (error.message && error.message.includes('CORS')) {
    return 'CORS跨域错误：浏览器阻止了跨域请求。请确保后端服务已正确配置CORS并允许当前源访问。';
  }
  
  // 根据HTTP状态码处理错误
  if (error.code) {
    switch (error.code) {
      case '401':
        return '认证错误：您的登录会话可能已过期，请重新登录Spotify并授权本应用。';
      case '403':
        return '授权错误：您没有执行此操作的权限。可能需要重新授权或调整Spotify权限设置。';
      case '404':
        return '资源未找到：请求的API端点不存在或资源已被删除。请检查后端服务是否正常运行。';
      case '429':
        return 'API请求过于频繁：已达到Spotify API速率限制。请稍后再试，或减少请求频率。';
      case '500':
      case '502':
      case '503':
      case '504':
        return '服务器错误：后端服务暂时不可用或发生内部错误。请稍后再试。';
      default:
        // 处理其他错误码
        break;
    }
  }
  
  // Spotify特定错误
  if (error.message) {
    if (error.message.includes('token')) {
      return 'Spotify认证令牌错误：访问令牌可能已过期或无效。请重新授权应用程序。';
    }
    
    if (error.message.includes('playlist')) {
      return 'Spotify播放列表错误：创建播放列表或添加歌曲时出错。请检查您是否有足够的权限。';
    }
    
    if (error.message.includes('rate limit')) {
      return 'Spotify API速率限制：请求过于频繁，请稍后再试。';
    }
  }
  
  // 将对象转换为字符串
  let errorMessage = '';
  if (error.message) {
    errorMessage = error.message;
  } else if (typeof error === 'string') {
    errorMessage = error;
  } else {
    try {
      errorMessage = JSON.stringify(error);
    } catch {
      errorMessage = '未知错误';
    }
  }
  
  return `错误：${errorMessage}。如果问题持续，请联系支持或查看控制台获取更多信息。`;
}

// API请求通用错误处理函数
async function handleResponseError(response: Response): Promise<ApiError> {
  try {
    const errorData = await response.json().catch(() => ({}));
    
    // 构建标准错误对象
    const apiError: ApiError = {
      code: String(response.status),
      message: '',
      details: errorData.detail || errorData
    };
    
    // 根据状态码设置用户友好的错误消息
    switch (response.status) {
      case 400:
        apiError.message = errorData.message || '请求参数错误，请检查输入内容是否正确。';
        break;
      case 401:
        apiError.message = errorData.message || '身份验证失败，请重新登录Spotify。';
        break;
      case 403:
        apiError.message = errorData.message || '您没有执行此操作的权限，请确保已授权本应用。';
        break;
      case 404:
        apiError.message = errorData.message || '请求的资源不存在。';
        break;
      case 429:
        apiError.message = errorData.message || 'API请求过于频繁，请稍后再试。';
        break;
      case 500:
      case 502:
      case 503:
      case 504:
        apiError.message = errorData.message || '服务器内部错误，请稍后再试。';
        break;
      default:
        apiError.message = errorData.message || `请求失败：${response.statusText}`;
    }
    
    return apiError;
  } catch (error) {
    return {
      code: String(response.status),
      message: `请求失败：${response.statusText}`,
      details: null
    };
  }
}

// 统一处理API错误
async function handleApiResponse(response: Response) {
  if (!response.ok) {
    const apiError = await handleResponseError(response);
    throw apiError;
  }
  
  return response.json();
}

// API请求通用选项
const fetchOptions: RequestInit = {
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  mode: 'cors',
  credentials: 'include', // 确保包含跨域请求的凭据（Cookie）
};

// 认证相关API

/**
 * 检查Spotify认证状态
 * @returns 认证状态响应，包含是否已认证和用户信息
 */
export async function checkAuthStatus(): Promise<AuthStatusResponse> {
  try {
    console.log('开始检查认证状态...');
    console.log('API基础URL:', API_BASE_URL);
    console.log('请求地址:', `${API_BASE_URL}/api/auth-status`);
    
    // 增加重试机制
    let retries = 0;
    const maxRetries = 3;
    let lastError: any = null;
    
    while (retries < maxRetries) {
      try {
        const response = await fetch(`${API_BASE_URL}/api/auth-status`, {
          method: 'GET',
          ...fetchOptions,
          credentials: 'include', // 确保包含跨域请求的凭据（Cookie）
        });
        
        console.log('收到认证状态响应:', {
          status: response.status,
          statusText: response.statusText,
          headers: Object.fromEntries(response.headers.entries()),
        });
        
        const data = await handleApiResponse(response);
        console.log('认证状态响应内容:', data);
        
        // 直接使用API返回的格式，不再尝试访问data.data
        return {
          isAuthenticated: data.is_authenticated || false,
          userInfo: data.user_info || null,
          spotifyLoginStatus: data.spotify_login_status || false
        };
      } catch (error) {
        lastError = error;
        console.error(`检查认证状态失败 (尝试 ${retries + 1}/${maxRetries}):`, error);
        retries++;
        
        // 在重试前等待一段时间
        if (retries < maxRetries) {
          await new Promise(resolve => setTimeout(resolve, 1000 * retries));
        }
      }
    }
    
    // 所有重试都失败
    console.error('检查认证状态多次失败:', lastError);
    return {
      isAuthenticated: false,
      userInfo: null,
      spotifyLoginStatus: false,
      error: handleFetchError(lastError)
    };
  } catch (error) {
    console.error('检查认证状态失败:', error);
    return {
      isAuthenticated: false,
      userInfo: null,
      spotifyLoginStatus: false,
      error: handleFetchError(error)
    };
  }
}

/**
 * 获取Spotify授权URL
 * @returns 授权URL
 */
export async function getAuthUrl() {
  try {
    console.log('正在获取Spotify授权URL...');
    
    const response = await fetch(`${API_BASE_URL}/api/auth-url`, {
      method: 'GET',
      ...fetchOptions,
    });
    
    const data = await handleApiResponse(response);
    console.log('授权URL响应:', data);
    
    // 检查响应格式，确保我们能正确提取URL
    if (data && data.data && data.data.auth_url) {
      return data.data.auth_url;
    } else if (data && data.auth_url) {
      return data.auth_url;
    } else {
      console.error('获取授权URL格式错误:', data);
      throw new Error('授权URL格式不正确');
    }
  } catch (error) {
    console.error('获取授权URL失败:', error);
    throw new Error(handleFetchError(error));
  }
}

/**
 * 刷新访问令牌
 * @returns 刷新结果
 */
export async function refreshToken() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/refresh-token`, {
      method: 'POST',
      ...fetchOptions,
    });
    
    return await handleApiResponse(response);
  } catch (error) {
    console.error('刷新令牌失败:', error);
    throw new Error(handleFetchError(error));
  }
}

/**
 * 登出Spotify账户
 * @returns 登出结果
 */
export async function logout() {
  try {
    console.log('调用登出API...');
    const response = await fetch(`${API_BASE_URL}/api/logout`, {
      method: 'POST',
      ...fetchOptions,
    });
    
    // 即使后端返回错误状态码，也视为成功，因为前端已经清除了登录状态
    if (!response.ok) {
      console.warn(`登出API返回非成功状态码: ${response.status} - ${response.statusText}`);
      // 不抛出异常，返回模拟成功
      return { status: "success", message: "用户已在前端登出" };
    }
    
    return await handleApiResponse(response);
  } catch (error) {
    console.warn('登出API调用失败，但用户已在前端登出:', error);
    // 返回模拟成功
    return { status: "success", message: "用户已在前端登出" };
  }
}

// 歌曲处理API

/**
 * 处理歌曲列表
 * @param songList 歌曲列表文本
 * @param concurrency 并发数
 * @param batchSize 批处理大小
 * @returns 处理结果
 */
export async function processSongs(songList: string, concurrency = 5, batchSize = 5) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/process-songs`, {
      method: 'POST',
      ...fetchOptions,
      body: JSON.stringify({
        song_list: songList,
        concurrency,
        batch_size: batchSize
      })
    });
    
    const responseData = await handleApiResponse(response);
    console.log('处理歌曲API原始响应:', responseData);
    
    // 标准化响应格式：处理可能的嵌套数据结构
    let result: ProcessSongsData;
    
    if (responseData.data && (responseData.data.matched_songs || responseData.data.unmatched_songs)) {
      // 如果数据嵌套在data字段中
      console.log('API响应使用嵌套data结构');
      result = responseData.data;
    } else if (responseData.matched_songs || responseData.unmatched_songs) {
      // 数据直接在顶层
      console.log('API响应使用顶层数据结构');
      result = responseData;
    } else {
      // 未找到预期的数据结构，创建一个空结构
      console.warn('API响应中未找到预期的数据结构，创建默认结构');
      result = {
        total_songs: responseData.total_songs || 0,
        matched_songs: [],
        unmatched_songs: []
      };
    }
    
    // 确保关键字段存在
    result.matched_songs = result.matched_songs || [];
    result.unmatched_songs = result.unmatched_songs || [];
    result.total_songs = result.total_songs || 0;
    
    console.log('处理后的标准化数据:', result);
    return result;
  } catch (error) {
    console.error('处理歌曲列表失败:', error);
    throw error instanceof Error ? error : new Error(handleFetchError(error));
  }
}

/**
 * 创建播放列表并添加歌曲
 * @param name 播放列表名称
 * @param isPublic 是否公开
 * @param uris 歌曲URI列表
 * @param description 播放列表描述（可选）
 * @returns 创建结果
 */
export async function createPlaylistAndAddSongs(
  name: string,
  isPublic: boolean,
  uris: string[],
  description: string = ''
) {
  try {
    // 创建请求数据
    const requestData = {
      name,
      public: isPublic,
      description,
      uris
    };
    
    console.log('创建播放列表参数:', requestData);
    
    const response = await fetch(`${API_BASE_URL}/api/create-playlist`, {
      method: 'POST',
      ...fetchOptions,
      body: JSON.stringify(requestData)
    });
    
    const data = await handleApiResponse(response);
    console.log('创建播放列表响应:', data);
    
    return {
      playlist_id: data.data.playlist_id,
      playlist_url: data.data.playlist_url,
      playlist_name: data.data.name || name,
      added_tracks_count: data.data.added_tracks || 0,
      failed_tracks_count: data.data.failed_tracks || 0
    };
  } catch (error) {
    console.error('创建播放列表失败:', error);
    throw new Error(handleFetchError(error));
  }
}