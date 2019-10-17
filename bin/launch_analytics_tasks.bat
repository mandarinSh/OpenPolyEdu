@echo off
call set_env.bat

:enterTaskName
echo Select the task number to be executed:
echo   1. Calculate unique user names.
echo   2. Calculate unique event names.
echo   3. Calculate unique user names and ids.
echo   4. Show amount of video play events per day.
echo   5. Show events distribution per day.
echo   6. Compare courses launches.
echo   7. Exit
echo   ' ... '
echo   NOTE: the result of analytics can be found in "result" directory or the browser will be opened automatically.

set /p TASK_TO_EXECUTE="Task number to execute: "

IF NOT DEFINED TASK_TO_EXECUTE SET "TASK_TO_EXECUTE=0"
IF "%TASK_TO_EXECUTE%"=="1" (
  call %PYTHON_HOME%\python.exe %PY_SCRIPT_DIR%unique_user_names.py %DATABASE_NAME% %USER_NAME% %RESULT_DIR%unique_user_names.txt
  goto enterTaskName
) ELSE IF "%TASK_TO_EXECUTE%"=="2" (
  call %PYTHON_HOME%\python.exe %PY_SCRIPT_DIR%unique_event_names.py %DATABASE_NAME% %USER_NAME% %RESULT_DIR%unique_event_names.txt
  goto enterTaskName
) ELSE IF "%TASK_TO_EXECUTE%"=="3" (
  call %PYTHON_HOME%\python.exe %PY_SCRIPT_DIR%unique_user_names_and_ids.py %DATABASE_NAME% %USER_NAME% %RESULT_DIR%unique_user_names_and_ids.txt
  goto enterTaskName
) ELSE IF "%TASK_TO_EXECUTE%"=="4" (
  call %PYTHON_HOME%\python.exe %PY_SCRIPT_DIR%play_video_count_per_day.py %DATABASE_NAME% %USER_NAME% %RESULT_DIR%play_video_count_per_day.csv
  goto enterTaskName
) ELSE IF "%TASK_TO_EXECUTE%"=="5" (
   call %PYTHON_HOME%\python.exe %PY_SCRIPT_DIR%distribution_of_events_per_day.py %DATABASE_NAME% %USER_NAME% %RESULT_DIR%distribution_of_events_per_day.csv
   goto enterTaskName
 ) ELSE IF "%TASK_TO_EXECUTE%"=="6" (
   @rem TODO: Put here invocation of the required implementation '..\libs\analytic_tasks'
   echo TODO
   goto enterTaskName
) ELSE IF "%TASK_TO_EXECUTE%"=="7" (
   echo Thank you for using the tool!
   goto end
) ELSE (
  echo Selected unsupported option.
  goto enterTaskName
)

:end
@rem ============================================================================================
