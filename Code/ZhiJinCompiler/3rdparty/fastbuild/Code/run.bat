@echo off
REM 显示所有编译的目标
FBuild.exe -showtargets

REM 强制远程协同+开启记录+统计编译结果
Fbuild.exe -clean -dist -monitor -summary -forceremote -j2 FBuild-x64-Release 