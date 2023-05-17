import os
import re
import shutil

# 处理清理指令
def handle_clean_command(targets):
    total_deleted_files = 0  # 总共删除的文件数
    total_freed_space = 0  # 总共释放的空间大小
    for target in targets:
        target_path, pattern = target["path"], target["pattern"]
        # 检查目标路径是否存在
        if not os.path.exists(target_path):
            print("目标路径 {} 不存在！".format(target_path))
            continue
        # 统计目标路径下被删除的文件数量和释放的空间大小
        deleted_files, freed_space = clean_target_path(target_path, pattern)
        total_deleted_files += deleted_files
        total_freed_space += freed_space
    print("共清理了{}个文件，释放了{:.2f}MB空间".format(total_deleted_files, total_freed_space / 1024 / 1024))

# 清理目标路径
def clean_target_path(path, pattern):
    deleted_files = 0
    freed_space = 0
    for root, dirs, files in os.walk(path):
        for f in files:
            if re.search(pattern, f):
                try:
                    file_path = os.path.join(root, f)
                    file_size = os.path.getsize(file_path)
                    os.remove(file_path)
                    deleted_files += 1
                    freed_space += file_size
                except Exception as e:
                    print("删除文件 {} 失败：{}".format(file_path, e))
    return deleted_files, freed_space

# 示例指令
targets = [
    {"path": "/tmp/logs/", "pattern": ".*\.log"},
    {"path": "/tmp/data/", "pattern": "large.*\.txt"},
    {"path": "/tmp/images/", "pattern": ".*\.jpg"},
]

# 处理清理指令
handle_clean_command(targets)
