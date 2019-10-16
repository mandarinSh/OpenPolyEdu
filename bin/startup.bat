@echo off
call set_env.bat

@rem =======================Cleaning Working Directory===========================================
call clean_workdir.bat
@rem ============================================================================================


@rem =======================Installing required soft=============================================
call install_soft.bat
@rem ============================================================================================


@rem =======================Creating and Starting PostgresSQL====================================
call create_database.bat
call launch_database_server.bat
@rem ============================================================================================


@rem =======================Loading Logs to Database=============================================
@rem Ask user if to use prepared logs, or to download from OpenEdu
@rem and ingest the data to postgresql
call load_data_to_database.bat
@rem ============================================================================================


@rem =======================Doing Analytics=====================================================
@rem At this point the PostgreSQL database has been launched, data is loaded and ready for consumers
call launch_analytics_tasks.bat
@rem ============================================================================================


@rem =======================Stopping PostgresSQL====================================
@rem At the very end of the analysis just shutdown the PostgeSQL server
pause
call stop_database_server.bat
