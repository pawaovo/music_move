import requests
import json

def test_process_songs_api():
    """测试歌曲处理API端点"""
    url = "http://localhost:8888/api/process-songs"
    
    # 测试数据
    data = {
        "song_list": "周杰伦 - 晴天\nTaylor Swift - Love Story",
        "concurrency": 5,
        "batch_size": 5
    }
    
    # 发送POST请求
    print(f"正在发送POST请求到 {url}")
    print(f"请求数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(url, json=data)
        
        # 打印响应状态和内容
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("请求成功!")
            result = response.json()
            print(f"响应数据: {json.dumps(result, ensure_ascii=False, indent=2)}")
            return True
        else:
            print(f"请求失败: {response.text}")
            return False
    except Exception as e:
        print(f"发生错误: {e}")
        return False

if __name__ == "__main__":
    print("=== 开始测试API端点 ===")
    success = test_process_songs_api()
    print("=== 测试完成 ===")
    print(f"测试结果: {'成功' if success else '失败'}") 