@echo off
:: 设置控制台代码页为UTF-8
chcp 65001 >nul

:: 问卷星自动化系统GitHub更新脚本
:: 作者: Ignorant-lu
:: 描述: 用于从GitHub拉取最新更新并应用到本地
:: 版本: 1.0

setlocal enabledelayedexpansion
title 问卷星自动化系统更新

:: 颜色定义
set "CYAN=[36m"
set "GREEN=[32m"
set "YELLOW=[33m"
set "RED=[31m"
set "BLUE=[34m"
set "MAGENTA=[35m"
set "NC=[0m"

echo %CYAN%=======================================================%NC%
echo %CYAN%        问卷星自动化系统GitHub更新脚本 v1.0           %NC%
echo %CYAN%=======================================================%NC%
echo.
echo %BLUE%本脚本将帮助您从GitHub拉取最新更新并应用到本地。%NC%
echo.
echo %YELLOW%更新过程将执行以下操作：%NC%
echo  - 检查Git是否已安装
echo  - 检查远程仓库配置
echo  - 拉取最新更新
echo  - 合并更新到本地
echo.

:: 确认是否继续
set /p confirm=是否继续更新过程？(y/N): 
if /i not "%confirm%"=="y" (
    echo %YELLOW%已取消更新过程。%NC%
    goto :eof
)

:: 检查Git是否已安装
echo %CYAN%正在检查系统要求...%NC%
echo %MAGENTA%[步骤 1/4] 检查Git...%NC%

where git >nul 2>nul
if %errorlevel% neq 0 (
    echo %RED%错误: 未找到Git%NC%
    echo %YELLOW%请安装Git: https://git-scm.com/downloads%NC%
    start https://git-scm.com/downloads
    pause
    exit /b 1
) else (
    echo %GREEN%  ✔ Git已安装%NC%
)

:: 检查远程仓库配置
echo %MAGENTA%[步骤 2/4] 检查远程仓库配置...%NC%

git remote -v | findstr "origin" >nul
if %errorlevel% neq 0 (
    echo %YELLOW%未找到远程仓库配置，正在添加...%NC%
    git remote add origin https://github.com/lgnorant-lu/autollm_wjx.git
    if %errorlevel% neq 0 (
        echo %RED%错误: 无法添加远程仓库%NC%
        pause
        exit /b 1
    ) else {
        echo %GREEN%  ✔ 远程仓库已添加%NC%
    }
) else (
    echo %GREEN%  ✔ 远程仓库已配置%NC%
)

:: 保存当前分支名称
for /f "tokens=*" %%a in ('git rev-parse --abbrev-ref HEAD') do set current_branch=%%a
echo %CYAN%当前分支: !current_branch!%NC%

:: 拉取最新更新
echo %MAGENTA%[步骤 3/4] 拉取最新更新...%NC%

echo %CYAN%正在从GitHub拉取最新更新...%NC%
git fetch origin
if %errorlevel% neq 0 (
    echo %RED%错误: 无法从GitHub拉取更新%NC%
    echo %YELLOW%可能是网络问题或GitHub访问受限%NC%
    pause
    exit /b 1
) else (
    echo %GREEN%  ✔ 已成功拉取最新更新%NC%
)

:: 合并更新
echo %MAGENTA%[步骤 4/4] 合并更新...%NC%

:: 检查是否有本地修改
git diff --quiet
if %errorlevel% neq 0 (
    echo %YELLOW%检测到本地有未提交的修改。%NC%
    echo %YELLOW%请选择处理方式：%NC%
    echo  1. 保存修改并继续更新（推荐）
    echo  2. 丢弃修改并继续更新
    echo  3. 取消更新
    
    set /p choice=请输入选项(1/2/3): 
    
    if "!choice!"=="1" (
        echo %CYAN%正在保存本地修改...%NC%
        git stash
        if %errorlevel% neq 0 (
            echo %RED%错误: 无法保存本地修改%NC%
            pause
            exit /b 1
        ) else {
            echo %GREEN%  ✔ 本地修改已保存%NC%
            set stashed=1
        }
    ) else if "!choice!"=="2" (
        echo %CYAN%正在丢弃本地修改...%NC%
        git reset --hard
        if %errorlevel% neq 0 (
            echo %RED%错误: 无法丢弃本地修改%NC%
            pause
            exit /b 1
        ) else {
            echo %GREEN%  ✔ 本地修改已丢弃%NC%
        }
    ) else (
        echo %YELLOW%已取消更新过程。%NC%
        goto :eof
    )
)

:: 合并远程更新
echo %CYAN%正在合并更新...%NC%
git merge origin/main
if %errorlevel% neq 0 (
    echo %RED%错误: 合并冲突，请手动解决冲突后继续%NC%
    echo %YELLOW%您可以使用以下命令查看冲突文件：%NC%
    echo  git status
    echo %YELLOW%解决冲突后，使用以下命令继续：%NC%
    echo  git add .
    echo  git merge --continue
    pause
    exit /b 1
) else (
    echo %GREEN%  ✔ 更新已成功合并%NC%
)

:: 如果之前有保存的修改，尝试恢复
if defined stashed (
    echo %CYAN%正在恢复本地修改...%NC%
    git stash pop
    if %errorlevel% neq 0 (
        echo %YELLOW%警告: 恢复本地修改时发生冲突，请手动解决%NC%
        echo %YELLOW%您的修改已保存在stash中，可以使用以下命令查看：%NC%
        echo  git stash list
        echo %YELLOW%使用以下命令应用修改：%NC%
        echo  git stash apply
    ) else {
        echo %GREEN%  ✔ 本地修改已恢复%NC%
    }
)

echo.
echo %CYAN%=======================================================%NC%
echo %GREEN%✓✓✓ 更新完成！系统已更新到最新版本 ✓✓✓%NC%
echo %CYAN%=======================================================%NC%
echo.

:: 询问是否重启应用
echo %CYAN%是否需要重启应用以应用更新？(Y/n):%NC%
set /p restart=
if /i not "%restart%"=="n" (
    if exist "deploy.ps1" (
        echo %CYAN%正在重启应用...%NC%
        powershell -ExecutionPolicy Bypass -File deploy.ps1 restart
        echo %GREEN%  ✔ 应用已重启%NC%
    ) else (
        echo %YELLOW%未找到deploy.ps1脚本，请手动重启应用%NC%
    )
)

echo.
echo %BLUE%感谢使用问卷星自动化系统。如需帮助，请参考文档或联系支持团队。%NC%
echo.

pause
