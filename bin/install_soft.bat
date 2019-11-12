@echo off
set BIN_DIR=%~dp0
call %BIN_DIR%set_env.bat

echo Extracting the JDK to '%JDK_PATH%'
%SEV_ZIP_PATH% x "%SOFT_PATH%openjdk-11.0.2_windows-x64_bin.zip" -o"%JDK_PATH%"
echo Extracting PostgreSQL to '%POSTGRESQL_PATH%'
%SEV_ZIP_PATH% x "%SOFT_PATH%postgresql-12.0-1-windows-x64-binaries.zip" -o"%POSTGRESQL_PATH%"
echo Extracting Python to '%PYTHON_PATH%'
%SEV_ZIP_PATH% x "%SOFT_PATH%python-3.7.4.zip" -o"%PYTHON_PATH%"

call %JAVA_HOME%\java.exe -version
call %POSTGRESQL_HOME%\psql --version
call %PYTHON_HOME%\python.exe -V

@rem =======================Install Python Packages=========================================
echo Installing Python packages with 'pip'
call %PYTHON_HOME%\python.exe %SOFT_PATH%PythonAddons\get-pip.py
call %PYTHON_HOME%\Scripts\pip.exe install psycopg2
@rem for visualization
call %PYTHON_HOME%\Scripts\pip install tabulate
call %PYTHON_HOME%\Scripts\pip install plotly==4.1.0
call %PYTHON_HOME%\Scripts\pip install psutil requests
call %PYTHON_HOME%\Scripts\pip install pandas
@rem ============================================================================================
