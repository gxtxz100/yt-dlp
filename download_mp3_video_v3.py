import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm  # 添加进度条支持

def download_video(url, download_directory):
    """使用yt-dlp下载单个视频并转换为最优化的mp3格式"""
    try:
        command = (
            f'yt-dlp -f "bestaudio/best" --extract-audio --audio-format mp3 '
            f'--audio-quality 32K --yes-playlist '
            f'--postprocessor-args "-q:a 0" '
            f'-o "{download_directory}/%(title)s.%(ext)s" {url}'
        )
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"下载失败: {result.stderr}")
        return True
    except Exception as e:
        print(f"下载出错 {url}: {str(e)}")
        return False

def download_from_file(file_path, download_directory, max_workers=8):
    """从文本文件中读取URL并并行下载视频"""
    with open(file_path, 'r') as file:
        urls = [url.strip() for url in file.readlines() if url.strip()]
    
    successful_downloads = 0
    failed_downloads = 0
    
    # 创建总进度条
    progress_bar = tqdm(total=len(urls), desc="下载进度", ncols=100)
    
    def download_with_progress(url):
        """带进度更新的下载函数"""
        try:
            result = download_video(url, download_directory)
            progress_bar.update(1)  # 每完成一个下载就更新进度
            return result
        except Exception as e:
            progress_bar.update(1)  # 即使失败也要更新进度
            return False

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 使用修改后的下载函数
        results = list(executor.map(download_with_progress, urls))
        
    progress_bar.close()
    
    # 统计结果
    successful_downloads = sum(1 for r in results if r)
    failed_downloads = len(urls) - successful_downloads
    
    return successful_downloads, failed_downloads

def main():
    # 创建下载目录
    download_directory = './downloaded'
    os.makedirs(download_directory, exist_ok=True)
    
    # 用户输入URL或文件路径
    input_value = input("请输入视频URL或包含URL的文本文件路径: ")
    
    if os.path.isfile(input_value):
        successful, failed = download_from_file(input_value, download_directory)
        print(f"\n下载完成！成功: {successful}, 失败: {failed}")
    else:
        if download_video(input_value, download_directory):
            print("下载成功！")
        else:
            print("下载失败！")

if __name__ == "__main__":
    main()