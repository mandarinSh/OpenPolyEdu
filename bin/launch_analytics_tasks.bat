@echo off
call set_env.bat

:enterTaskName
echo.
echo Select the task number to be executed:
echo   1. Calculate unique user names.
echo   2. Calculate unique event names.
echo   3. Calculate unique user names and ids.
echo   4. Show page activity on course (total number of visits).
echo   5. Show page activity on course distributed by day.
echo   6. Show events distribution per day.
echo   7. Show amount of video play events per day.
echo   8. Compare courses launches.
echo   9. Exit
echo.
echo   NOTE: the result of analytics can be found in "result" directory or the browser will be opened automatically.
echo.
set /p TASK_TO_EXECUTE="Task number to execute: "
echo.
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
  call %PYTHON_HOME%\python.exe %PY_SCRIPT_DIR%page_activity_on_course_total_number_of_visits.py %DATABASE_NAME% %USER_NAME% %RESULT_DIR%page_activity_on_course_total_number_of_visits.csv
  goto enterTaskName
) ELSE IF "%TASK_TO_EXECUTE%"=="5" (
   call %PYTHON_HOME%\python.exe %PY_SCRIPT_DIR%page_activity_on_course_distributed_by_day.py %DATABASE_NAME% %USER_NAME% %RESULT_DIR%page_activity_on_course_distributed_by_day.csv
   goto enterTaskName
) ELSE IF "%TASK_TO_EXECUTE%"=="6" (
   call %PYTHON_HOME%\python.exe %PY_SCRIPT_DIR%distribution_of_events_per_day.py %DATABASE_NAME% %USER_NAME% %RESULT_DIR%distribution_of_events_per_day.csv
   goto enterTaskName
) ELSE IF "%TASK_TO_EXECUTE%"=="7" (
   call %PYTHON_HOME%\python.exe %PY_SCRIPT_DIR%play_video_count_per_day.py %DATABASE_NAME% %USER_NAME% %RESULT_DIR%play_video_count_per_day.csv
   goto enterTaskName
) ELSE IF "%TASK_TO_EXECUTE%"=="8" (
   @rem TODO: Put here invocation of the required implementation '..\libs\analytic_tasks'
   echo TODO
   goto enterTaskName
) ELSE IF "%TASK_TO_EXECUTE%"=="9" (
   echo Thank you for using the tool!
   goto end
) ELSE (
  echo Selected unsupported option.
  goto enterTaskName
)

:end
@rem ============================================================================================
