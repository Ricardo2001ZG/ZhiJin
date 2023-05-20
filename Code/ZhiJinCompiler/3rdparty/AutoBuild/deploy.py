import os
import zipfile
import shutil
import requests
import subprocess
from datetime import datetime
import time
from common import Result

# 临时目录
TEMP_DIR = os.environ.get("TEMP") or "./TMP"
# Windows 下的工作路径是在本地的 ./TMP 下面
if os.name == "nt":
    TEMP_DIR = "./TMP"

def check_project_access(project_dir: str) -> Result:
    """
    检查项目是否存在以及是否可以被访问
    :param project_dir: 项目路径
    :return: Result对象，包含操作结果状态码、错误信息、操作结果信息
    """
    if not os.path.exists(project_dir):
        return Result(4, "{}不存在".format(project_dir), "项目路径不存在")
    if not os.access(project_dir, os.R_OK):
        return Result(5, "{}不可读".format(project_dir), "项目路径不可读")
    return Result(0, "", "检查成功！")


def download_package(download_url: str, download_path: str) -> Result:
    """
    下载安装包
    :param download_url: 安装包下载地址
    :param download_path: 安装包保存路径
    :return: Result对象，包含操作结果状态码、错误信息、操作结果信息
    """
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)
    try:
        response = requests.get(download_url, stream=True)
        with open(download_path, "wb") as fw:
            for chunk in response.iter_content(chunk_size=1024):
                fw.write(chunk)
        return Result(0, "", "下载成功！")
    except Exception as e:
        return Result(1, str(e), "下载失败！{}".format(str(e)))


def unzip_install_package(package_path: str, install_dir: str) -> Result:
    """
    解压安装包
    :param package_path: 安装包路径
    :param install_dir: 安装目录
    :return: Result对象，包含操作结果状态码、错误信息、操作结果信息
    """
    if not os.path.exists(install_dir):
        os.makedirs(install_dir)
    try:
        with zipfile.ZipFile(package_path, 'r') as z:
            z.extractall(install_dir)
        return Result(0, "", "解压成功！")
    except Exception as e:
        return Result(1, str(e), "解压失败！{}".format(str(e)))


def install_git_and_svn(git_install_url=None, svn_install_url=None) -> Result:
    """
    安装 Git 和 SVN
    :param git_install_url: Git安装包下载地址
    :param svn_install_url: SVN安装包下载地址
    :return: Result对象，包含操作结果状态码、错误信息、操作结果信息以及Git和SVN的执行文件路径
    """
    # 判断是否需要下载和安装 Git
    if git_install_url:
        # 下载安装包
        git_package_path = os.path.join(TEMP_DIR, "git-install.zip")
        git_download_result = download_package(git_install_url, git_package_path)
        if git_download_result.code != 0:
            return Result(1, "下载 Git 安装包失败！", "下载 Git 安装包失败！{}".format(git_download_result.error))

        # 解压安装包
        git_install_dir = os.path.join(TEMP_DIR, "git")
        git_unzip_result = unzip_install_package(git_package_path, git_install_dir)
        if git_unzip_result.code != 0:
            return Result(1, "解压 Git 安装包失败！", "解压 Git 安装包失败！{}".format(git_unzip_result.error))

        # 设置 Git 的执行文件路径
        git_executable_path = os.path.join(git_install_dir, "bin", "git.exe")
    else:
        git_executable_path = ""

    # 判断是否需要下载和安装 SVN
    if svn_install_url:
        # 下载安装包
        svn_package_path = os.path.join(TEMP_DIR, "svn-install.zip")
        svn_download_result = download_package(svn_install_url, svn_package_path)
        if svn_download_result.code != 0:
            return Result(1, "下载 SVN 安装包失败！", "下载 SVN 安装包失败！{}".format(svn_download_result.error))

        # 解压安装包
        svn_install_dir = os.path.join(TEMP_DIR, "svn")
        svn_unzip_result = unzip_install_package(svn_package_path, svn_install_dir)
        if svn_unzip_result.code != 0:
            return Result(1, "解压 SVN 安装包失败！", "解压 SVN 安装包失败！{}".format(svn_unzip_result.error))

        # 设置 SVN 的执行文件路径
        svn_executable_path = os.path.join(svn_install_dir, "bin", "svn.exe")
    else:
        svn_executable_path = ""

    # 返回安装结果
    return Result(0, "", "Git 和 SVN 安装完成！", git_executable_path=git_executable_path,
                  svn_executable_path=svn_executable_path)


def pull_project(project_name: str, url: str, branch: str = "master", commit_id: str = None,
                  git_executable_path: str = "", svn_executable_path: str = "") -> Result:
    """
    从 Git 或 SVN 拉取项目代码或更新已有项目
    :param project_name: str，要拉取或更新的项目名称或路径
    :param url: str，项目代码的远程仓库地址
    :param branch: str，可选参数，Git 仓库的分支名，默认为 master 分支
    :param commit_id: str，可选参数，需要切换到的 Git 或 SVN 的提交 ID
    :param git_executable_path: str，可选参数，Git 可执行文件所在路径，如果为空则自动搜索系统 PATH 中的 Git
    :param svn_executable_path: str，可选参数，SVN 可执行文件所在路径，如果为空则自动搜索系统 PATH 中的 SVN
    :return: Result，函数执行结果，包括 code（执行结果状态码）、message（执行消息）和 project_path（项目物理路径地址）、error（错误消息）
    """
    start_time = datetime.now() # 记录开始时间

    # 安装 Git 和 SVN（如果未安装）
    if not git_executable_path and not svn_executable_path:
        install_result = install_git_and_svn()
        if install_result.code != 0:
            return install_result
        git_executable_path = install_result.git_executable_path
        svn_executable_path = install_result.svn_executable_path

    # 判断临时目录是否存在，如果已经存在则检查目标项目是否存在，如果存在则直接执行拉取、更新操作
    project_path = os.path.abspath(os.path.join(TEMP_DIR, project_name))
    if os.path.exists(TEMP_DIR) and os.path.exists(project_path):
        check_result = check_project_access(project_path)
        if check_result.code == 0:
            os.chdir(project_path)
            if url.endswith(".git"):
                # 使用 Git 拉取代码
                command = [git_executable_path, "pull"]
                result = subprocess.run(command,  capture_output=True, encoding="utf-8")
                if result.returncode != 0:
                    return Result(1, "使用 Git 拉取代码失败！", f"使用 Git 拉取代码失败！{result.stderr.strip()}，路径为：{project_path}",project_path=project_path)
                if commit_id:
                    command_commit = [git_executable_path, "checkout", commit_id]
                    result_commit = subprocess.run(command_commit,  capture_output=True, encoding="utf-8")
                    if result_commit.returncode != 0:
                        return Result(1, "使用 Git 切换到指定提交ID失败！", f"使用 Git 切换到指定提交ID失败！{result_commit.stderr.strip()}，路径为：{project_path}",project_path=project_path)
                else:
                    command_branch = [git_executable_path, "checkout", branch]
                    result_branch = subprocess.run(command_branch,  capture_output=True, encoding="utf-8")
                    if result_branch.returncode != 0:
                        return Result(1, "使用 Git 切换分支失败！", f"使用 Git 切换分支失败！{result_branch.stderr.strip()}，路径为：{project_path}",project_path=project_path)
            else:
                # 使用 SVN 拉取代码
                command = [svn_executable_path, "update"]
                result = subprocess.run(command,  capture_output=True, encoding="utf-8")
                if result.returncode != 0:
                    return Result(1, "使用 SVN 拉取代码失败！", f"使用 SVN 拉取代码失败！{result.stderr.strip()}，路径为：{project_path}",project_path=project_path)
                if commit_id:
                    command_commit = [svn_executable_path, "update", "-r", commit_id]
                    result_commit = subprocess.run(command_commit,  capture_output=True, encoding="utf-8")
                    if result_commit.returncode != 0:
                        return Result(1, "使用 SVN 切换到指定提交ID失败！", f"使用 SVN 切换到指定提交ID失败！{result_commit.stderr.strip()}，路径为：{project_path}",project_path=project_path)
            # 返回拉取或更新结果
            end_time = datetime.now() # 记录结束时间
            cost_time = (end_time - start_time).total_seconds() # 统计花费时间
            return Result(0, "", f"更新代码完成！项目路径为：{project_path}，更新时间为：{end_time}，花费时间为：{cost_time:.2f}秒。", project_path=project_path)

    # 临时目录不存在或目标项目不存在，则重新拉取
    else:
        os.makedirs(TEMP_DIR,exist_ok=True)

    # 将当前路径切换到工作路径
    os.chdir(TEMP_DIR)

    # 如果目标项目不存在则重新拉取
    if url.endswith(".git"):
        # 使用 Git 拉取代码
        command = [git_executable_path, "clone", "-b", branch, url, project_name]
        result = subprocess.run(command,  capture_output=True, encoding="utf-8")
        if result.returncode != 0:
            return Result(1, "使用 Git 拉取代码失败！", f"使用 Git 拉取代码失败！{result.stderr.strip()}，路径为：{project_path}")
        if commit_id:
            os.chdir(project_name)
            command_commit = [git_executable_path, "checkout", commit_id]
            result_commit = subprocess.run(command_commit,  capture_output=True, encoding="utf-8")
            if result_commit.returncode != 0:
                return Result(1, "使用 Git 切换到指定提交ID失败！", f"使用 Git 切换到指定提交ID失败！{result_commit.stderr.strip()}，路径为：{project_path}")
    else:
        # 使用 SVN 拉取代码
        command = [svn_executable_path, "checkout", url, project_name]
        result = subprocess.run(command,  capture_output=True, encoding="utf-8")
        if result.returncode != 0:
            return Result(1, "使用 SVN 拉取代码失败！", f"使用 SVN 拉取代码失败！{result.stderr.strip()}，路径为：{project_path}")
        if commit_id:
            os.chdir(project_name)
            command_commit = [svn_executable_path, "update", "-r", commit_id]
            result_commit = subprocess.run(command_commit,  capture_output=True, encoding="utf-8")
            if result_commit.returncode != 0:
                return Result(1, "使用 SVN 切换到指定提交ID失败！", f"使用 SVN 切换到指定提交ID失败！{result_commit.stderr.strip()}，路径为：{project_path}")
    # 返回拉取结果
    end_time = datetime.now()
    cost_time = (end_time - start_time).total_seconds()
    return Result(0, "", f"代码拉取完成！项目路径为：{project_path}，拉取时间为：{end_time}，花费时间为：{cost_time:.2f}秒。", project_path=project_path)

# 以下代码仅作演示使用
import sys
import os
import stat

def remove_readonly(func, path, _):
    "Clear the readonly bit and reattempt the removal"
    os.chmod(path, stat.S_IWRITE)
    func(path)

if __name__ == "__main__":
    # 拉取的项目名称
    project_name = "ZhiJin"
    # 项目拉取地址
    url = "https://github.com/Ricardo2001ZG/ZhiJin.git"
    # 分支名称
    branch = "main"

    # 从系统PATH环境变量中查找Git执行文件路径
    if os.name == "nt":
        git_executable_name = "git.exe"
    else:
        git_executable_name = "git"
    git_executable_path = shutil.which(git_executable_name)

    # 删除之前已经拉取的项目（如果存在）
    # project_path = os.path.join(TEMP_DIR, project_name)
    # if os.path.exists(project_path):
    #     shutil.rmtree(project_path, onerror=remove_readonly)

    # # 检查临时目录是否存在
    # if not os.path.exists(TEMP_DIR):
    #     os.mkdir(TEMP_DIR)

    # 拉取并更新项目代码
    pull_result = pull_project(project_name, url, branch, git_executable_path=git_executable_path)
    if pull_result.code == 0:
        print(pull_result.message)  # 输出消息
        print(pull_result.project_path)  # 输出项目的物理地址
    else:
        print(pull_result.error)  # 输出错误信息

