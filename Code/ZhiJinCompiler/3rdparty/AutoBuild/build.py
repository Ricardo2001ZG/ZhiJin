import subprocess
import shutil
import os
import sys

def compile_project(project_path, build_command, fbuild_path=None)->str:
    """
    编译指定项目并检查环境内是否存在FBuild可执行文件

    :param project_path: 要编译的项目路径
    :param build_command: 编译命令字符串
    :param fbuild_path: FBuild 可执行文件的路径；如果为 None，则会自动查找
    :return: 返回编译的结果，成功则返回编译信息，失败则抛出异常
    """
    # 检查编译环境是否符合要求
    if not check_compilation_environment(fbuild_path):
        raise Exception("Compilation environment is not ready.")
    print("Compilation environment is already")

    # 更改当前工作目录为项目根目录
    os.chdir(project_path)

    # 执行编译命令，并返回编译结果
    result = subprocess.run(build_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True,cwd=project_path)
    try:
        return result.stdout.decode("utf-8")
    except:
        return result.stdout.decode("gbk")


def build_project(project_dir, build_command=None):
    """
    构建项目

    :param project_dir: 项目所在文件夹路径
    :param project_name: 项目名称
    :param build_command: 构建命令，默认为 None，使用 FBuild 进行构建
    :return: 若构建成功，返回 {"code": 0, "error": "", "message": "构建成功！"}，
             否则返回 {"code": 2, "error": "构建失败！", "message": "构建失败！"}
    """
    # 如果没有指定构建命令，则默认使用 FBuild 进行构建
    if not build_command:
        fbuild_path = shutil.which("FBuild")
        if not fbuild_path:
            raise Exception("FBuild executable file not found in system environment.")
        build_command = "{}".format(fbuild_path)
    os.chdir(project_dir)
    print("开始构建项目...")
    # 执行构建命令
    result = subprocess.run(build_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True,cwd=project_dir)
    if result.returncode == 0:
        print("构建完成！")
        return {"code": 0, "error": "", "message": "构建成功！"}
    else:
        print("构建失败！错误信息：{}".format(result.stderr.decode("utf-8")))
        return {"code": 2, "error": "构建失败！", "message": "构建失败！"}


def check_compilation_environment(fbuild_path=None):
    """
    检查编译环境是否符合要求

    :param fbuild_path: FBuild 可执行文件的路径；如果为 None，则会自动查找
    :return: 如果 FBuild 可执行文件存在，则返回 True，否则返回 False
    """
    # 如果用户没有指定 fbuild 执行文件路径，则从环境变量 PATH 中查找
    if not fbuild_path:
        if sys.platform.startswith('win'):
            fbuild_executable = "FBuild.exe"
        else:
            fbuild_executable = "FBuild"
        fbuild_path = shutil.which(fbuild_executable)
    # 如果仍然没有找到，则说明编译环境不符合要求
    if not os.path.isfile(fbuild_path):
        return False
    return True


def main():
    project_dir = "C:\\Users\\Administrator\\AppData\\Local\\Temp\\ZhiJin"
    build_command = "cd .\\Code\\ZhiJinCompiler\\3rdparty\\fastbuild\\Code && FBuild.exe -clean -monitor -summary -j2 FBuild-x64-Release"
    
    try:
        result = compile_project(project_dir, build_command)
        print(result)
        if "FBuild: OK" in result:
            print("编译成功!")
    except Exception as e:
        print(e)

if __name__ == '__main__':
    main()