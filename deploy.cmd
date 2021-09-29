
@echo off
set REGISTRY_IP=192.168.1.3
set REGISTRY_PORT=5001
set IMAGE_NAME=nw_server_monitor
set IMAGE_TAG=latest
set BUILD_TAG=%REGISTRY_IP%:%REGISTRY_PORT%/%IMAGE_NAME%:%IMAGE_TAG%
set BUILD_PATH=.
@REM set "_DOCKER=C:\Program Files\Docker\Docker\resources\bin\docker.exe"
set "_DOCKER=docker"
pushd %~dp0
net start com.docker.service
"%_DOCKER%" build -t %BUILD_TAG% %BUILD_PATH% || exit /b
"%_DOCKER%" push %REGISTRY_IP%:%REGISTRY_PORT%/%IMAGE_NAME% || exit /b
@REM net stop com.docker.service || exit /b
