/**
 * API Service Layer
 *
 * This module provides functions to interact with the backend API.
 */

// Define the base URL for the API. This should ideally come from an environment variable.
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8888';
const API_ENDPOINT = `${API_BASE_URL}/api`;

// --- API Response Types (Consider defining these more robustly based on actual API responses) ---

interface ApiResponse<T = any> {
  status: 'success' | 'error';
  data?: T;
  message?: string;
  error_code?: string;
}

interface MatchedSong {
  title: string;
  artists: string[];
  album: string;
  uri: string;
  matched: boolean;
  confidence: number;
  original_line?: string;
}

interface ProcessSongsData {
  matched_songs: MatchedSong[];
  total: number;
  matched_count: number;
  unmatched_count: number;
}

interface CreatePlaylistData {
  playlist_id: string;
  playlist_url: string;
  name: string;
  added_tracks: number;
}

interface AuthStatusData {
  is_authenticated: boolean;
  user_info?: {
    id: string;
    display_name: string;
    email?: string;
    images?: any[]; // Define more specifically if needed
  };
  expires_in?: number;
}

// --- API Service Functions ---

// 错误代码映射表
export const ErrorMessages: Record<string, string> = {
  'AUTH_REQUIRED': '需要Spotify授权，请先登录',
  'AUTH_FAILED': '授权失败，请重新登录',
  'RATE_LIMIT': 'API请求次数过多，请稍后再试',
  'SPOTIFY_API_ERROR': 'Spotify API调用失败',
  'INVALID_INPUT': '输入数据无效',
  'EMPTY_SONGS': '歌曲列表为空',
  'PLAYLIST_CREATE_FAILED': '创建播放列表失败',
  'NETWORK_ERROR': '网络连接错误',
  'UNKNOWN_ERROR': '发生未知错误'
};

// 处理API错误
const handleApiError = (error: any): ApiResponse => {
  console.error('API错误:', error);
  
  // 网络错误
  if (error.message === 'Failed to fetch' || error.name === 'TypeError') {
    return {
      status: 'error',
      message: ErrorMessages.NETWORK_ERROR,
      error_code: 'NETWORK_ERROR'
    };
  }
  
  // 如果有响应但是失败了
  if (error.response) {
    const status = error.response.status;
    
    // 授权错误
    if (status === 401 || status === 403) {
      return {
        status: 'error',
        message: ErrorMessages.AUTH_FAILED,
        error_code: 'AUTH_FAILED'
      };
    }
    
    // 速率限制
    if (status === 429) {
      return {
        status: 'error',
        message: ErrorMessages.RATE_LIMIT,
        error_code: 'RATE_LIMIT'
      };
    }
  }
  
  // 默认错误
  return {
    status: 'error',
    message: error.message || ErrorMessages.UNKNOWN_ERROR,
    error_code: 'UNKNOWN_ERROR'
  };
};

// 通用API请求函数
async function apiRequest<T>(
  endpoint: string, 
  method: string = 'GET', 
  data?: any
): Promise<ApiResponse<T>> {
  const url = `${API_ENDPOINT}${endpoint}`;
  
  try {
    const options: RequestInit = {
      method,
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include', // 包含cookies
    };
    
    if (data && (method === 'POST' || method === 'PUT')) {
      options.body = JSON.stringify(data);
    }
    
    const response = await fetch(url, options);
    
    // 检查授权状态
    if (response.status === 401) {
      return {
        status: 'error',
        message: ErrorMessages.AUTH_REQUIRED,
        error_code: 'AUTH_REQUIRED'
      };
    }
    
    // 检查其他HTTP错误
    if (!response.ok) {
      let errorData;
      try {
        errorData = await response.json();
      } catch (e) {
        // 如果无法解析JSON，使用状态文本
        return {
          status: 'error',
          message: `HTTP错误: ${response.status} ${response.statusText}`,
          error_code: 'HTTP_ERROR'
        };
      }
      
      // 返回API提供的错误信息
      return {
        status: 'error',
        message: errorData.message || `HTTP错误: ${response.status}`,
        error_code: errorData.error_code || 'API_ERROR'
      };
    }
    
    // 成功响应
    const responseData = await response.json();
    return {
      status: 'success',
      data: responseData
    };
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Processes a list of songs by calling the backend API.
 * @param songList - A string containing the list of songs, one per line.
 * @param concurrency - The number of concurrent requests to make.
 * @param batchSize - The size of each batch for processing.
 * @returns A promise that resolves to the API response for processing songs.
 */
export async function processSongs(
  songList: string,
  concurrency: number = 5,
  batchSize: number = 5
): Promise<ApiResponse<ProcessSongsData>> {
  try {
    const response = await fetch(`${API_ENDPOINT}/process-songs`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        song_list: songList,
        concurrency,
        batch_size: batchSize,
      }),
    });
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ message: 'Failed to process songs and parse error' }));
      throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error: any) {
    console.error('Error processing songs:', error);
    return {
      status: 'error',
      message: error.message || 'An unexpected error occurred while processing songs.',
    };
  }
}

/**
 * Creates a Spotify playlist and adds songs to it.
 * @param name - The name of the playlist.
 * @param description - The description of the playlist.
 * @param isPublic - Whether the playlist should be public.
 * @param uris - An array of Spotify track URIs to add to the playlist.
 * @returns A promise that resolves to the API response for creating a playlist.
 */
export async function createPlaylistAndAddSongs(
  name: string,
  description: string,
  isPublic: boolean,
  uris: string[]
): Promise<ApiResponse<CreatePlaylistData>> {
  try {
    const response = await fetch(`${API_ENDPOINT}/create-playlist`, { // Corrected endpoint
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        name, // Corrected field name
        description,
        public: isPublic, // Corrected field name
        uris, // Corrected field name
      }),
    });
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ message: 'Failed to create playlist and parse error' }));
      throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error: any) {
    console.error('Error creating playlist:', error);
    return {
      status: 'error',
      message: error.message || 'An unexpected error occurred while creating the playlist.',
    };
  }
}

/**
 * Checks the current Spotify authentication status.
 * @returns A promise that resolves to the API response for authentication status.
 */
export async function checkAuthStatus(): Promise<ApiResponse<AuthStatusData>> {
  try {
    const response = await fetch(`${API_ENDPOINT}/auth-status`);
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ message: 'Failed to check auth status and parse error' }));
      throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error: any) {
    console.error('Error checking auth status:', error);
    return {
      status: 'error',
      message: error.message || 'An unexpected error occurred while checking auth status.',
    };
  }
}

/**
 * Gets the Spotify authorization URL.
 * @returns A promise that resolves to the API response containing the auth URL.
 */
export async function getAuthUrl(): Promise<ApiResponse<{ auth_url: string }>> {
  try {
    const response = await fetch(`${API_ENDPOINT}/auth-url`);
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ message: 'Failed to get auth URL and parse error' }));
      throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error: any) {
    console.error('Error getting auth URL:', error);
    return {
      status: 'error',
      message: error.message || 'An unexpected error occurred while getting the auth URL.',
    };
  }
}

/**
 * Refreshes the Spotify access token.
 * @returns A promise that resolves to the API response for token refresh.
 */
export async function refreshToken(): Promise<ApiResponse<{ expires_in: number }>> {
  try {
    const response = await fetch(`${API_ENDPOINT}/refresh-token`, {
      method: 'POST',
    });
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ message: 'Failed to refresh token and parse error' }));
      throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error: any) {
    console.error('Error refreshing token:', error);
    return {
      status: 'error',
      message: error.message || 'An unexpected error occurred while refreshing the token.',
    };
  }
} 