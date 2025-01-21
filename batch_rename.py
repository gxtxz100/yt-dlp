import os
from pathlib import Path

def rename_files(directory_path, remove_text):
    """
    批量重命名文件，去除文件名中的指定字符串
    
    Args:
        directory_path: 文件夹路径
        remove_text: 需要删除的字符串
    """
    try:
        # 将路径转换为 Path 对象
        directory = Path(directory_path)
        
        # 确保目录存在
        if not directory.exists():
            print(f"错误：目录 '{directory_path}' 不存在！")
            return
            
        # 记录重命名的文件数量
        renamed_count = 0
        
        # 遍历目录中的所有文件
        for file_path in directory.iterdir():
            if file_path.is_file():  # 只处理文件，不处理文件夹
                # 获取原文件名（不含扩展名）和扩展名
                old_name = file_path.stem
                extension = file_path.suffix
                
                # 如果文件名中包含要删除的字符串
                if remove_text in old_name:
                    # 新文件名（删除指定字符串）
                    new_name = old_name.replace(remove_text, '')
                    
                    # 构建新的完整文件路径
                    new_file_path = file_path.parent / f"{new_name}{extension}"
                    
                    try:
                        # 重命名文件
                        file_path.rename(new_file_path)
                        print(f"已重命名: {file_path.name} -> {new_file_path.name}")
                        renamed_count += 1
                    except Exception as e:
                        print(f"重命名文件 '{file_path.name}' 时出错: {str(e)}")
        
        # 显示处理结果
        if renamed_count > 0:
            print(f"\n成功重命名 {renamed_count} 个文件")
        else:
            print(f"\n没有找到包含 '{remove_text}' 的文件")
            
    except Exception as e:
        print(f"处理过程中出错: {str(e)}")

def main():
    """主函数"""
    print("文件批量重命名工具")
    print("=" * 30)
    
    # 获取用户输入
    directory_path = input("请输入文件夹路径: ").strip()
    remove_text = input("请输入要删除的字符串: ").strip()
    
    # 确认操作
    print(f"\n将要从目录 '{directory_path}' 中的文件名删除字符串 '{remove_text}'")
    confirm = input("确认继续吗？(y/n): ").strip().lower()
    
    if confirm == 'y':
        rename_files(directory_path, remove_text)
    else:
        print("操作已取消")

if __name__ == "__main__":
    main() 