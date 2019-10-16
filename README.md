# OpenPolyEdu

## Project goal
OpenEdu portal provides an information about user activity on the course in the log file.  

Since the log can be large enough (for example, it can be about 18GB and may contain more than 10 000 000 actions), then its manual analysis becomes impossible.

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
 If the software (Python, its packages and PostgreSQL) is already installed, if the database is already exists and the data is already loaded, then user may use only: 
  - launch PostgreSQL server with corresponding 'bat' script in the 'bin' directory
  - launch 'query_analytic_task.bat' script from 'bin' directory' in order to see the results
  
 ## Custom run
 The scripts in 'bin' folder allows a user flexible operations over the analytic utility. User may run server, load data, clean working directory or run analytic tasks independently. But it is required a bit of experience with teh product. 
 
## OpenEdu logs
The OpenEdu portal provides an activity log in [JSON](http://json.org/) format.
More precisely, log is a multiline file, where each line is an JSON object. 

### Example of log line 
The below log line shows the even generated for the user action, when starting playing video
```
{
	"username": "proud-glamorous-spottedhyena",
	"event_source": "browser",
	"name": "play_video",
	"accept_language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
	"time": "2018-09-17T09:06:05.756647+00:00",
	"agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
	"page": "https://courses.openedu.ru/courses/course-v1:spbstu+PHYLOS+fall_2018/courseware/a1b314bc847145cdbbce7722cf290a46/33f75534cc894cc19e617d50927f2d48/?child=first",
	"host": "courses.openedu.ru",
	"session": "fa9c50d7084768b72f308c8d1f5e9a8e",
	"referer": "https://courses.openedu.ru/courses/course-v1:spbstu+PHYLOS+fall_2018/courseware/a1b314bc847145cdbbce7722cf290a46/33f75534cc894cc19e617d50927f2d48/?child=first",
	"context": {
		"user_id": 150319,
		"org_id": "spbstu",
		"course_id": "course-v1:spbstu+PHYLOS+fall_2018",
		"path": "/event"
	},
	"ip": "anon_f25ec949f0b37ae92ce8808b5d54f20dd124441261a895fc1900de95b9fac77e",
	"event": "{\"code\": \"html5\", \"id\": \"25f98e9e5c8f44ce8ecb388317824c36\", \"currentTime\": 0}",
	"event_type": "play_video"
}
```



### Edx even types documentation
Description of [edx event types](https://github.com/edx/edx-documentation/blob/b5bf2cad349b4a330c3159301a51975884d1d5ad/en_us/data/source/internal_data_formats/tracking_logs/student_event_types.rst#id383)
