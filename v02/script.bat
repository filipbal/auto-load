@echo off

rem //set variables
set _comport=%1
set _version=%2
set _baudrate=57600
set _cpu=0x419
set _loader_dir=W:\Sestavy_elektro\Detektory\Toy18_Baby18_serie\Boards\AMY17\Rev_1\Common\Firmware\MCU\v%_version%\Loader_v%_version%
set _hexfile=%_loader_dir%\Amy17_v%_version%.hex
set _file1=%_loader_dir%\stm32_flash.exe
set _file2=%_loader_dir%\STDFU.dll
set _file3=%_loader_dir%\STTubeDevice30.dll
set _interface=
set _ip=
set _mac=
set _logfile=%TEMP%\amy.log
set _again=n

rem //test file1
if not exist "%_file1%" (set _file1=W:\Sestavy_elektro\Software\ECOM_Programy\stm32_flash\bin\stm32_flash.exe)
if not "%_logfile%"=="" (set _logfile=-l%_logfile%)

rem //menu
:MENU
echo.

rem Run the firmware loader on the specified COM port
:COM
rem //flash through the serial port
:COM2
start "" "%_file1%" -cCOM%_comport% -IBABY;COM/%_baudrate% -d%_cpu% -nV -p %_logfile% "%_hexfile%"
if %ERRORLEVEL% NEQ 0 goto END

rem The script continues with the next COM port without asking for input
goto END

rem //end
:END
