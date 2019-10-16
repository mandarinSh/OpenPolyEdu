@echo off
call set_env.bat

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
call %PYTHON_HOME%\Scripts\pip install tabulate
@rem ============================================================================================
