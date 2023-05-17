import os
import subprocess

# 构建指令进度更新间隔时间（秒）
BUILD_PROGRESS_UPDATE_INTERVAL = 5

def compile_project(project_path, build_command, fbuild_path=None):
    # 检查编译环境是否符合要求
    if not check_compilation_environment(fbuild_path):
        return "编译环境不通过"
    
    # 更改当前工作目录为项目根目录
    os.chdir(project_path)

    # 执行编译命令
    p = subprocess.Popen(build_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, universal_newlines=True)
    stdout, stderr = p.communicate()
    return stdout + "\n" + stderr

def check_compilation_environment(fbuild_path=None):
    # 如果用户没有指定 fbuild.exe 路径，则从环境变量 PATH 中查找
    if not fbuild_path:
        for path in os.environ["PATH"].split(os.pathsep):
            fbuild_path = os.path.join(path.strip('"'), "fbuild.exe")
            if os.path.isfile(fbuild_path):
                break
    # 如果仍然没有找到，则说明编译环境不符合要求
    if not os.path.isfile(fbuild_path):
        return False
    return True


# 执行构建操作
def build_project(project_dir, project_name):
    print("开始构建 {} 项目...".format(project_name))
    # 计算进度更新次数
    total_files = sum(len(files) for _, _, files in os.walk(project_dir))
    progress_update_count = total_files // BUILD_PROGRESS_UPDATE_INTERVAL + 1
    # 构建命令，以 Maven 为例
    build_command = "mvn clean install"
    # 执行构建命令
    try:
        os.chdir(project_dir)
        # 执行构建命令，并实时打印构建进度
        process = subprocess.Popen(build_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        current_file_count = 0
        for line in iter(process.stdout.readline, b''):
            line_str = line.decode().strip()
            print(line_str)
            # 更新构建进度
            current_file_count += line_str.count("Compiling ") + line_str.count("Downloading ") + line_str.count("Building ")
            if current_file_count % progress_update_count == 0:
                progress = current_file_count / total_files * 100
                print("构建进度：{:.2f}%".format(progress))
        process.wait()
        # 检查构建结果
        if process.returncode == 0:
            return {"code": 0, "error": "", "message": "构建成功！"}
        else:
            return {"code": 2, "error": "构建失败！", "message": "构建失败！"}
    except subprocess.CalledProcessError as e:
        return {"code": 2, "error": str(e), "message": "构建失败！"}

