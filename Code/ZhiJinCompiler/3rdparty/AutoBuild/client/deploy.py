import os
import zipfile
import shutil
import requests

# 临时目录
TEMP_DIR = os.environ.get("TEMP") or "./TMP"

class Result:
    def __init__(self, code, error, message, **kwargs):
        self.code = code
        self.error = error
        self.message = message
        for k, v in kwargs.items():
            setattr(self, k, v)


# 检查项目是否存在以及是否可以被访问
def check_project_access(project_dir: str) -> Result:
    # 判断指定目录是否存在
    if not os.path.exists(project_dir):
        return Result(4, "{}不存在".format(project_dir), "项目路径不存在")
    # 判断指定目录是否可读
    if not os.access(project_dir, os.R_OK):
        return Result(5, "{}不可读".format(project_dir), "项目路径不可读")
    # 返回检查结果
    return Result(0, "", "检查成功！")


# 下载安装包
def download_package(download_url: str, download_path: str) -> Result:
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


# 解压安装包
def unzip_install_package(package_path: str, install_dir: str) -> Result:
    if not os.path.exists(install_dir):
        os.makedirs(install_dir)
    try:
        with zipfile.ZipFile(package_path, 'r') as z:
            z.extractall(install_dir)
        return Result(0, "", "解压成功！")
    except Exception as e:
        return Result(1, str(e), "解压失败！{}".format(str(e)))


# 安装 Git 和 SVN
def install_git_and_svn(git_install_url=None, svn_install_url=None) -> Result:
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


# 拉取代码
def pull_project(project_name: str, url: str, branch: str = "master", commit_id: str = None, git_executable_path: str = "",
                  svn_executable_path: str = "") -> Result:
    # 安装 Git 和 SVN（如果未安装）
    if not git_executable_path and not svn_executable_path:
        install_result = install_git_and_svn()
        if install_result.code != 0:
            return install_result
        git_executable_path = install_result.git_executable_path
        svn_executable_path = install_result.svn_executable_path

    # 判断临时目录是否存在，如果已经存在则检查目标项目是否存在，如果存在则直接执行拉取、更新操作
    if os.path.exists(TEMP_DIR):
        project_dir = os.path.join(TEMP_DIR, project_name)
        if os.path.exists(project_dir):
            check_result = check_project_access(project_dir)
            if check_result.code == 0:
                os.chdir(project_dir)
                if url.endswith(".git"):
                    # 使用 Git 拉取代码
                    command = f"{git_executable_path} fetch"
                    result_code = os.system(command)
                    if result_code != 0:
                        return Result(1, "使用 Git 拉取代码失败！", "使用 Git 拉取代码失败！{}".format(result_code))
                    if commit_id:
                        result_code_commit = os.system(f"{git_executable_path} checkout {commit_id}")
                        if result_code_commit != 0:
                            return Result(1, "使用 Git 切换到指定提交ID失败！", "使用 Git 切换到指定提交ID失败！{}".format(result_code_commit))
                    else:
                        result_code_branch = os.system(f"{git_executable_path} checkout {branch}")
                        if result_code_branch != 0:
                            return Result(1, "使用 Git 切换分支失败！", "使用 Git 切换分支失败！{}".format(result_code_branch))
                else:
                    # 使用 SVN 拉取代码
                    command = f"{svn_executable_path} update"
                    result_code = os.system(command)
                    if result_code != 0:
                        return Result(1, "使用 SVN 拉取代码失败！", "使用 SVN 拉取代码失败！{}".format(result_code))
                    if commit_id:
                        result_code_commit = os.system(f"{svn_executable_path} update -r {commit_id}")
                        if result_code_commit != 0:
                            return Result(1, "使用 SVN 切换到指定提交ID失败！", "使用 SVN 切换到指定提交ID失败！{}".format(result_code_commit))
                # 返回拉取结果
                return Result(0, "", "更新代码完成！")
        else:
            # 如果目标项目不存在则重新拉取
            shutil.rmtree(TEMP_DIR)
    # 临时目录不存在或目标项目不存在，则重新拉取
    os.makedirs(TEMP_DIR)
    if url.endswith(".git"):
        # 使用 Git 拉取代码
        command = f"{git_executable_path} clone -b {branch} {url} {project_name}"
        result_code = os.system(command)
        if result_code != 0:
            return Result(1, "使用 Git 拉取代码失败！", "使用 Git 拉取代码失败！{}".format(result_code))
        if commit_id:
            os.chdir(project_name)
            result_code_commit = os.system(f"{git_executable_path} checkout {commit_id}")
            if result_code_commit != 0:
                return Result(1, "使用 Git 切换到指定提交ID失败！", "使用 Git 切换到指定提交ID失败！{}".format(result_code_commit))
    else:
        # 使用 SVN 拉取代码
        command = f"{svn_executable_path} checkout {url} {project_name}"
        result_code = os.system(command)
        if result_code != 0:
            return Result(1, "使用 SVN 拉取代码失败！", "使用 SVN 拉取代码失败！{}".format(result_code))
        if commit_id:
            os.chdir(project_name)
            result_code_commit = os.system(f"{svn_executable_path} update -r {commit_id}")
        if result_code_commit != 0:
            return Result(1, "使用 SVN 切换到指定提交ID失败！", "使用 SVN 切换到指定提交ID失败！{}".format(result_code_commit))
        # 返回拉取结果
        return Result(0, "", "代码拉取完成！")