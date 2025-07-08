@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"
cd ..
echo Starting deployment from %CD%...

rem 创建必要的目录
mkdir "deployment\api" 2>nul
mkdir "deployment\db\pre" 2>nul
mkdir "deployment\db\report" 2>nul
mkdir "deployment\log" 2>nul
mkdir "deployment\analyse" 2>nul
mkdir "deployment\analyse\htmls" 2>nul

rem 复制主要执行文件
copy /Y "xxlJobRun.py" "deployment\"

rem 复制API文件
copy /Y "api\miniApi.py" "deployment\api\"

rem 复制数据库相关文件
copy /Y "db\db_manager.py" "deployment\db\"
copy /Y "db\pre\*.py" "deployment\db\pre\"
copy /Y "db\report\*.py" "deployment\db\report\"

rem 复制日志相关文件
copy /Y "log\logger.py" "deployment\log\"

rem 复制分析相关文件
echo Copying analysis files...
copy /Y "analyse\date_utils.py" "deployment\analyse\" && echo Copied date_utils.py
copy /Y "analyse\generate_report.py" "deployment\analyse\" && echo Copied generate_report.py
copy /Y "analyse\createHtml.py" "deployment\analyse\" && echo Copied createHtml.py
copy /Y "analyse\__init__.py" "deployment\analyse\" && echo Copied __init__.py
copy /Y "analyse\performance_analysis.html" "deployment\analyse\" && echo Copied performance_analysis.html

echo.
echo Verifying files...
if exist "deployment\analyse\date_utils.py" (
    echo date_utils.py exists
) else (
    echo ERROR: date_utils.py not copied
)
if exist "deployment\analyse\generate_report.py" (
    echo generate_report.py exists
) else (
    echo ERROR: generate_report.py not copied
)
if exist "deployment\analyse\createHtml.py" (
    echo createHtml.py exists
) else (
    echo ERROR: createHtml.py not copied
)
if exist "deployment\analyse\performance_analysis.html" (
    echo performance_analysis.html exists
) else (
    echo ERROR: performance_analysis.html not copied
)

echo.
echo Deployment completed!
pause
