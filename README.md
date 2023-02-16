
# “织锦”分布式 Shader 编译平台

织锦平台是一款基于 FastBuild(C++)、Flutter(Dart)、Element-plus(Vue)、Flask(Python) 开发而成的综合分布式编译平台，提供 Web 与 桌面版本的可视化客户端。

## 代码文件夹组织

```
- Code 
-- ZhiJinComplier
-- ZhiJinFlaskServer
-- ZhiJinFlutterClient
-- ZhiJinFlutterServer
-- ZhiJinGamesDemo
-- ZhiJinVue
-- Inner
```

ZhiJinComplier 对应分布式编译系统后端模块，负责分发编译任务与回收编译产物，基于 FastBuild 开发。

ZhiJinFlutterClient 对应平台的可视化前端模块，负责发起与管理任务等前端逻辑，基于 Flutter 开发。

ZhiJinFlutterServer 对应平台的可视化前端模块，负责发起与管理任务等后端逻辑的可视化操作，业务逻辑由 ZhiJinFlaskServer 负责，基于 Flutter 开发。

ZhiJinGamesDemo 对应一个 Unity 游戏 demo，分布式编译测试用。

ZhiJinFlaskServer 对应平台的后端业务模块，负责发起与管理任务等后端业务逻辑的处理，基于 Flask 开发。

ZhiJinVue 对应平台的 Web 前端模块，负责发起与管理任务等前端逻辑，基于 Element-plus 开发。

Inner 对应平台的额外部署模块，用于第三方开发者的私有功能接入，gitignore 默认屏蔽上传。

## 开发环境配置

### 一键配置

若使用本方式进行安装，无需进行后续手动配置流程。

#### 图形化配置形式

待开发

#### 命令行配置形式

待开发

### ZhiJinComplier

This product uses [FASTBuild](https://github.com/fastbuild/fastbuild) © 2012-2023 Franta Fulin

本项目使用 [FASTBuild](https://github.com/fastbuild/fastbuild) 作为部分开发组件，感谢所有开源开发者的贡献。

#### Windows

使用 Visual Studio Installer 进行安装，选择 C++ 与游戏开发相关模块安装即可。

下载链接：[Visual Studio 2022](https://visualstudio.microsoft.com/zh-hans/downloads/)

建议使用 Visual Studio 2022 进行开发，点击 ZhiJinComplier.sln 启动解决方案。

#### Linux

待完成。

#### MacOS

待完成。

### ZhiJinFlutterClient

请按照 Flutter 官方指引 [Install(flutter.dev)](https://docs.flutter.dev/get-started/install) 进行安装。

国内用户请访问：[安装和环境配置(flutter.cn)](https://flutter.cn/docs/get-started/install)。

### ZhiJinFlutterServer

请按照 Flutter 官方指引 [Install(flutter.dev)](https://docs.flutter.dev/get-started/install) 进行安装。

国内用户请访问：[安装和环境配置(flutter.cn)](https://flutter.cn/docs/get-started/install)。

### ZhiJinGamesDemo

请根据 Unity 官网手册指引安装。

链接：[安装 Unity](https://docs.unity3d.com/cn/2023.1/Manual/GettingStartedInstallingUnity.html)。

如安装完毕后需要激活，请访问以下手册。

链接：[许可证与激活](https://docs.unity3d.com/cn/2023.1/Manual/LicensesAndActivation.html)。

### ZhiJinFlaskServer

#### 一键配置

若使用本方式进行安装，无需进行后续手动配置流程。

**Windows:**

1. 将 ZhiJinFlaskServer-Library.zip 内文件解压，放在本工程根目录。

2. 点击文件夹内 zhijin_flask_server_installer.bat 进行一键安装。

3. 点击 dev_environment.bat 启动开发环境。

4. 输入 python app.py 启动项目编译。

#### Windows 手动配置

待完成。

#### Linux 手动配置

待完成。

#### MacOS 手动配置

请手动安装 python 及其相关组件。

```
cd ./Code/ZhiJinFlaskServer

# 国内镜像更换，选填
# pip config set global.index-url https://mirrors.cloud.tencent.com/pypi/simple

pip install pip -U
pip install pyenv 
pyenv virtualenv flask_api
pyenv activate flask_api
pip install -r requirements.txt
```

### ZhiJinVue

#### 一键配置

若使用本方式进行安装，无需进行后续手动配置流程。

**Windows:**

1. 将 ZhiJinVue-Library.zip 内文件解压，放在本工程根目录。

2. 点击文件夹内 zhijin_vue_installer.bat 进行一键安装。

3. 点击 dev_environment.bat 启动开发环境。

4. 输入 vue-cli-service build 启动项目编译。

#### Windows 手动配置

1. 安装node：[NodeJS 官网](https://nodejs.org/en/) 下载。

2. 检查是否安装成功
```
node -v
npm -v
```

3. 设置腾讯云镜像源(选填)
```
npm config set registry http://mirrors.cloud.tencent.com/npm/
```

4. 下载相关依赖
```
npm install
```
#### Linux 手动配置

待完成。

#### MacOS 手动配置

待完成。

### Inner

请按照文件夹内第三方开发者相关 README 文件指引进行第三方开发环境的配置。

## 关于

织锦平台研发团队 2023

MIT License
