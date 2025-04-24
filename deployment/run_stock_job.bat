@echo off
chcp 65001
call C:/Publish/python-kksStock/kksStock/Scripts/activate.bat

echo 运行股票数据处理程序...
python C:/Publish/python-kksStock/xxlJobRun.py

echo 任务完成，退出虚拟环境...
deactivate
