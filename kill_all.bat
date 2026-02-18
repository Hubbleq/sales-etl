@echo off
echo Killing all python processes...
taskkill /F /IM python.exe /T
taskkill /F /IM uvicorn.exe /T
echo Done.
