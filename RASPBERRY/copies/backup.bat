scp -r -o "StrictHostKeyChecking no" lqh@192.168.200.67:/home/lqh/programes/* D:\ASIXc\PROJECTE\THEPROJECT

@echo off
set "source=D:\ASIXc\PROJECTE\THEPROJECT"
set "datestamp=%date:~6,4%-%date:~3,2%-%date:~0,2%"
set "destination=I:\Mi unidad\PROJECTE\SCRIPTS\main\%datestamp%"
set "desktop_destination=C:\Users\quimd\Escritorio\PROJECTE\%datestamp%"

mkdir "%destination%" 2>nul
mkdir "%desktop_destination%" 2>nul

if exist "%destination%" (
    echo Copiando archivos a %destination%...
    xcopy "%source%\*" "%destination%" /s /e /i /h /y
    echo Archivos copiados exitosamente a %destination%.
) else (
    echo No se pudo crear el directorio de destino en %destination%.
)

if exist "%desktop_destination%" (
    echo Copiando archivos a %desktop_destination%...
    xcopy "%source%\*" "%desktop_destination%" /s /e /i /h /y
    echo Archivos copiados exitosamente a %desktop_destination%.
) else (
    echo No se pudo crear el directorio de destino en %desktop_destination%.
)

pause