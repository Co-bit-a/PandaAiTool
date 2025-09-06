@echo off
chcp 65001 >nul
title 重新打包PandaAI工具管理助手
echo 重新打包PandaAI工具管理助手...
echo.

echo 步骤1: 清理旧的构建文件...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
if exist "__pycache__" rmdir /s /q __pycache__
echo ✅ 清理完成

echo.
echo 步骤2: 开始打包...
echo 使用PyInstaller打包Python脚本...
pyinstaller panda_deploy_tool.spec

if errorlevel 1 (
    echo ❌ 打包失败！请检查错误信息
    pause
    exit /b 1
)

echo.
echo 步骤3: 检查打包结果...
if exist "dist\PandaAI工具管理助手.exe" (
    echo ✅ 打包成功！
    echo 📁 exe文件位置: dist\PandaAI工具管理助手.exe
    
    echo.
    echo 文件信息:
    dir "dist\PandaAI工具管理助手.exe"
    
    echo.
    echo 🎉 打包完成！你可以分发dist目录中的exe文件了
    echo.
    echo 提示:
    echo - exe文件已包含所有必需的依赖
    echo - 可以在没有安装Python的Windows系统上运行
    echo - 建议将发布说明.md一起提供给用户
    
) else (
    echo ❌ 未找到生成的exe文件，打包可能失败
)

echo.
pause
