import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

def download_video(url, download_directory):
    """ 使用yt-dlp下载单个视频，默认下载m4a格式 """
    command = f"yt-dlp -f m4a -o '{download_directory}/%(title)s.%(ext)s' {url}"
    subprocess.run(command, shell=True)

def download_from_file(file_path, download_directory, max_workers=4):
    """ 从文本文件中读取URL并并行下载视频，默认下载m4a格式 """
    with open(file_path, 'r') as file:
        urls = file.readlines()
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(download_video, url.strip(), download_directory): url for url in urls}
        for future in as_completed(futures):
            url = futures[future]
            try:
                future.result()
            except Exception as e:
                print(f"Error downloading {url.strip()}: {e}")

def main():
    # 创建下载目录
    download_directory = './downloaded' 
    os.makedirs(download_directory, exist_ok=True)
    
    # 用户输入URL或文件路径
    input_value = input("请输入视频URL或包含URL的文本文件路径: ")
    
    if os.path.isfile(input_value):
        download_from_file(input_value, download_directory)
    else:
        download_video(input_value, download_directory)
    print("下载完成！")

if __name__ == "__main__":
    main()
    