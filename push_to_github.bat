@echo off
:: 设置控制台代码页为UTF-8
chcp 65001 >nul

echo 删除远程仓库内容并推送本地更新脚本
echo ======================================

REM 添加远程仓库
git remote add origin https://github.com/lgnorant-lu/autollm_wjx.git

REM 强制推送本地dev分支到远程main分支
echo.
echo 正在强制推送本地dev分支到远程main分支...
echo 这将删除远程仓库中的所有内容并替换为本地内容
echo.
git push -f origin dev:main

REM 检查推送结果
if %errorlevel% neq 0 (
    echo.
    echo 推送失败！可能需要输入GitHub凭据。
    echo 请尝试以下替代方法：
    echo.
    echo 1. 使用GitHub个人访问令牌：
    echo    git remote set-url origin https://[用户名]:[个人访问令牌]@github.com/lgnorant-lu/autollm_wjx.git
    echo    git push -f origin dev:main
    echo.
    echo 2. 或者使用SSH方式：
    echo    git remote set-url origin git@github.com:lgnorant-lu/autollm_wjx.git
    echo    git push -f origin dev:main
    echo.
) else (
    echo.
    echo 推送成功！远程仓库已更新。
    echo.
)

pause
