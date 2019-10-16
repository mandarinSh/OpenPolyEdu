@echo off
call set_env.bat

echo Stopping PostrgeSQL server
%POSTGRESQL_HOME%\pg_ctl -D "%POSTGRESQL_DATABASE_PATH%" stop
