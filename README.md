# OpenPolyEdu

## Project goal
OpenEdu portal provides an information about user activity on the course in the log file.  

Since the log can be large enough (for exampel, it can be about 18GB and may contain more than 10 000 000 actions), then its manual analysis becomes impossible.

The project goal is to create an infrastructure with set of default analytic tasks that can be applyed on any OpenEdut course.

## Getting started 

## Pre-requisites
 - Windows 10 (x64)

## The First run
In order to start working with project just launch 'bin/startup.bat'.
The script then perform following actions:
 - clean 'workdir', 'system_logs' and 'result'
 - install required software from 'soft' folder
 - copy logs from 'input' folder to 'workdir'
 - create PostgreSQL database and launch server
 - ingest the data to database
 - ask a user on which the analytic task to execute
 - after the analytic task is executed, then the result can be found in 'result' folder
 
 ## The Second run
 If the software (Python, its packages and PostgreSQL) is already installed, if the database is already exists and the data is already loaded, then user may use only 
  - launch PostgreSQL server with corresponding 'bat' script in the 'bin' directory
  - launch 'query_analytic_task.bat' from 'bin' directory' in order to see the results
  
 ## Custom run
 The scripts in 'bin' folder allows a user flexible operations over the alaytic utility. User may run server, load data, clean working directory or run analytic tasks independently. But it is required a bit of experience with teh product. 
 
## OpenEdu logs
The OpenEdu portal provides an activity log in [JSON](http://json.org/) format.
More precisely, log is a multiline file, where each line is an JSON object. 

### Example of log line 
```
{
  "username": "plain-unkempt-blackstork",
  "event_type": "/api/extended/calendar/course-v1:spbstu+PHYLOS+fall_2018",
  "ip": "anon_589f9e54da703049b9d40434a51ad0201823251c338e768fc63f2838ab9bfa38",
  "agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134",
  "host": "courses.openedu.ru",
  "referer": "https://openedu.ru/my/",
  "accept_language": "ru-RU",
  "event": "{\"POST\": {}, \"GET\": {}}",
  "event_source": "server",
  "context": {
    "user_id": null,
    "org_id": "",
    "course_id": "",
    "path": "/api/extended/calendar/course-v1:spbstu+PHYLOS+fall_2018"
  },
  "time": "2018-09-03T16:36:06.348392+00:00",
  "page": null
}
```

===

### Edx even types documentation
Description of [edx event types](https://github.com/edx/edx-documentation/blob/b5bf2cad349b4a330c3159301a51975884d1d5ad/en_us/data/source/internal_data_formats/tracking_logs/student_event_types.rst#id383):
