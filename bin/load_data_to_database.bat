@echo off
call set_env.bat

echo Where to take the data from:
echo   - (1) local 'input' directory,
echo   - (2) Download from OpenEdu by provided settings from 'config/application.yml'
set /p TAKE_INPUT_DATA_FROM="Selected: "

IF NOT DEFINED TAKE_INPUT_DATA_FROM SET "TAKE_INPUT_DATA_FROM=1"

IF "%TAKE_INPUT_DATA_FROM%"=="1" (
   echo Extracting logs from "..\input\anonymized_logs.zip" to "%WORKDIR_PATH%init_data_for_analysis\"
   mkdir "%WORKDIR_PATH%init_data_for_analysis
   %SEV_ZIP_PATH% x "..\input\anonymized_logs.zip" -o"%WORKDIR_PATH%init_data_for_analysis\"
) ELSE IF "%TAKE_INPUT_DATA_FROM%"=="2" (
   @rem There should be an invocation of a program (java, python, whatever else)
   @rem that performing authorization to OpenEdu based on provided credentials in 'application.yml' file
   @rem and downloading logs from course, that is specified by id in 'application.yml' file
   echo TODO
) ELSE (
   echo Selected unsupported option.
   EXIT /B 1
)

call %PYTHON_HOME%\python.exe %PY_SCRIPT_DIR%load_logs_to_database.py %DATABASE_NAME% %USER_NAME% %WORKDIR_PATH%init_data_for_analysis\anonymized_logs.json
