import yt_dlp
from typing import List, Dict
import sys
import os
import concurrent.futures

def search_videos(keyword: str, max_results: int = 20) -> List[Dict]:
    """
    搜索视频并返回结果列表
    """
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'force_generic_extractor': True,
        'no_warnings': True
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_results = ydl.extract_info(
                f"ytsearch{max_results}:{keyword}",
                download=False
            )['entries']
            
            return search_results
    except Exception as e:
        print(f"搜索时发生错误: {str(e)}")
        return []

def format_duration(duration: int) -> str:
    """
    将秒数转换为人类可读的时长格式
    """
    if not duration:
        return 'N/A'
    
    # 将duration转换为整数
    duration = int(duration)
    minutes, seconds = divmod(duration, 60)
    hours, minutes = divmod(minutes, 60)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"

def format_date(date_str: str) -> str:
    """
    将YYYYMMDD格式转换为YYYY-MM-DD格式
    """
    if not date_str or len(date_str) != 8:
        return 'N/A'
    return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"

def display_results(results: List[Dict]) -> None:
    """
    显示搜索结果
    """
    print("\n搜索结果:")
    # 定义颜色代码
    GREEN = '\033[32m'
    RED = '\033[31m'
    RESET = '\033[0m'
    
    for idx, video in enumerate(results, 1):
        duration = video.get('duration')
        duration_str = format_duration(duration)
        title = video.get('title', 'Unknown Title')
        uploader = video.get('uploader', 'Unknown Uploader')
        
        # 使用奇偶判断选择颜色
        color = GREEN if idx % 2 == 1 else RED
        print(f"{color}{idx}. [{duration_str}] {title} - {uploader}{RESET}")
        print()

def download_video(url: str, download_dir: str) -> None:
    """
    下载单个视频
    """
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
        'quiet': False,
        'no_warnings': True
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def download_videos_parallel(videos: List[Dict], download_dir: str, max_workers: int = 3) -> None:
    """
    并行下载多个视频
    """
    # 确保下载目录存在
    os.makedirs(download_dir, exist_ok=True)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 创建视频URL和标题的映射
        video_info = [(video['url'], video['title']) for video in videos]
        # 并行下载所有视频
        futures = {
            executor.submit(
                download_video, 
                url, 
                download_dir
            ): title for url, title in video_info
        }
        
        for future in concurrent.futures.as_completed(futures):
            video_title = futures[future]
            try:
                future.result()
                print(f"\n成功下载: {video_title}")
            except Exception as e:
                print(f"\n下载失败 {video_title}: {str(e)}")

def main():
    download_dir = "downloads"  # 可以根据需要修改下载目录
    
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
            choice = input("\n请选择要下载的视频编号 (多个编号用逗号分隔，输入 'a' 下载全部，'n' 新搜索): ")
            
            if choice.lower() == 'n':
                break
            
            if choice.lower() == 'a':
                # 并行下载所有搜索结果
                download_videos_parallel(results, download_dir)
                break
            
            try:
                # 处理多选下载
                if ',' in choice:
                    indices = [int(x.strip()) for x in choice.split(',')]
                else:
                    indices = [int(choice)]
                
                # 获取选中的视频列表
                selected_videos = [results[idx-1] for idx in indices if 1 <= idx <= len(results)]
                if selected_videos:
                    download_videos_parallel(selected_videos, download_dir)
                else:
                    print("没有有效的选择")
                break
            except ValueError:
                print("输入无效，请重试")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n程序已退出")
        sys.exit(0) 