import yt_dlp
from typing import List, Dict
import sys
import os
from concurrent.futures import ThreadPoolExecutor

def search_videos(keyword: str, max_results: int = 20) -> List[Dict]:
    """
    搜索视频并返回结果列表
    """
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'force_generic_extractor': False,  # 改为False以支持更多提取器
        'no_warnings': True,
        'headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        },
        'extract_info': True
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # 直接使用搜索URL
            search_url = f"https://www.pornhub.com/video/search?search={keyword}"
            result = ydl.extract_info(search_url, download=False)
            # 确保我们获取到entries
            if result and 'entries' in result:
                return result['entries'][:max_results]
            return []
    except Exception as e:
        print(f"搜索时发生错误: {str(e)}")
        return []

def download_video(url: str, download_dir: str) -> bool:
    """
    下载视频并转换为低比特率MP3格式
    """
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '32',  # 降低到32k比特率
        }],
        'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
        'quiet': False,
        'no_warnings': True,
        'headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        },
        'postprocessor_args': [
            '-ar', '44100',  # 采样率
            '-ac', '2',      # 声道数
        ],
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return True
    except Exception as e:
        print(f"下载失败: {str(e)}")
        return False

def download_videos_parallel(videos: List[Dict], download_dir: str, max_workers: int = 3) -> None:
    """
    并行下载多个视频
    """
    os.makedirs(download_dir, exist_ok=True)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for video in videos:
            if 'url' in video:
                future = executor.submit(download_video, video['url'], download_dir)
                futures.append((future, video['title']))
        
        for future, title in futures:
            try:
                success = future.result()
                if success:
                    print(f"\n成功下载: {title}")
                else:
                    print(f"\n下载失败: {title}")
            except Exception as e:
                print(f"\n下载出错 {title}: {str(e)}")

def format_duration(duration: int) -> str:
    """
    将秒数转换为人类可读的时长格式
    """
    if not duration:
        return 'N/A'
    
    try:
        duration = int(duration)
        minutes, seconds = divmod(duration, 60)
        hours, minutes = divmod(minutes, 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
    except:
        return 'N/A'

def display_results(results: List[Dict]) -> None:
    """
    显示搜索结果
    """
    print("\n搜索结果:")
    GREEN = '\033[32m'
    RED = '\033[31m'
    RESET = '\033[0m'
    
    for idx, video in enumerate(results, 1):
        duration = video.get('duration')
        duration_str = format_duration(duration)
        title = video.get('title', 'Unknown Title')
        views = video.get('view_count', 'N/A')
        
        color = GREEN if idx % 2 == 1 else RED
        print(f"{color}{idx}. [{duration_str}] {title}")
        print(f"   观看次数: {views}{RESET}")
        print()

def main():
    download_dir = "downloads"
    
    while True:
        keyword = input("\n请输入搜索关键词 (输入 'q' 退出): ")
        if keyword.lower() == 'q':
            sys.exit(0)
            
        results = search_videos(keyword)
        if not results:
            print("未找到相关视频，请尝试其他关键词")
            continue
            
        display_results(results)
        
        while True:
            choice = input("\n请选择要下载的编号 (多个编号用逗号分隔，输入 'a' 下载全部，'n' 新搜索): ")
            
            if choice.lower() == 'n':
                break
            
            if choice.lower() == 'a':
                print("\n开始下载所有视频...")
                download_videos_parallel(results, download_dir)
                break
            
            try:
                if ',' in choice:
                    indices = [int(x.strip()) for x in choice.split(',')]
                    selected_videos = [results[idx-1] for idx in indices if 1 <= idx <= len(results)]
                else:
                    idx = int(choice)
                    if 1 <= idx <= len(results):
                        selected_videos = [results[idx-1]]
                    else:
                        print(f"无效的选择: {idx}")
                        continue
                
                if selected_videos:
                    download_videos_parallel(selected_videos, download_dir)
                break
            except ValueError:
                print("输入无效，请重试")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n程序已退出")
        sys.exit(0) 