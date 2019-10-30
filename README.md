# OpenPolyEdu
This is a project of Peter the Great St.Petersburg Polytechnic University (SPbPU) students based on course [Big Data](https://openedu.ru/course/spbstu/BIGDATA/).
More information can be found at presentation: 'docs/2019_OpenEdu_Concept_v2.pptx'

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
 The scripts in 'bin' folder allows a user flexible operations over the analytic utility. User may run server, load data, clean working directory or run analytic tasks independently. But it is required a bit of experience with the product. 
 
## OpenEdu logs
The OpenEdu portal provides an activity log in [JSON](http://json.org/) format.
More precisely, log is a multiline file, where each line is an JSON object. 

### Edx even types documentation
There is a most full docs in [Edx Research Guide](https://edx.readthedocs.io/projects/devdata/en/stable/internal_data_formats/tracking_logs.html)

Description of [common log fields](https://github.com/edx/edx-documentation/blob/b5bf2cad349b4a330c3159301a51975884d1d5ad/en_us/data/source/internal_data_formats/tracking_logs/common_fields.rst)

Description of [edx event types](https://github.com/edx/edx-documentation/blob/b5bf2cad349b4a330c3159301a51975884d1d5ad/en_us/data/source/internal_data_formats/tracking_logs/student_event_types.rst#id383)

Description of [course team events](https://github.com/edx/edx-documentation/blob/b5bf2cad349b4a330c3159301a51975884d1d5ad/en_us/data/source/internal_data_formats/tracking_logs/course_team_event_types.rst)

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

## Relative works
 - Out-of-the-box [Edx analytics](https://edx.readthedocs.io/projects/edx-data-analytics-api/en/latest/index.html)
 - [Towards the Development of a Learning Analytics extension in Open edX](https://www.researchgate.net/publication/280099474_Towards_the_Development_of_a_Learning_Analytics_extension_in_Open_edX) 
 - Research of one of [university](http://docs.lms.tpu.ru/projects/devdata/ru/latest/front_matter/index.html)
 

# Development 
Code-style for Python scripts is defined by PEP 8 standard. It may be found on the official website: https://www.python.org/dev/peps/pep-0008/

Also PEP8-codestyle auto-check may be plugged into the IDE (e.g. PyCharm).

## Test environment
Nikita needs to be asked about VM IP and creds

## Useful links
Edx docs: Installing, Configuring, and Running the Open edX Platform: [Hawthorn Release](https://buildmedia.readthedocs.org/media/pdf/edx-installing-configuring-and-running/open-release-hawthorn.master/edx-installing-configuring-and-running.pdf)

There is a Python library to [work with edx](https://github.com/coursera-dl/edx-dl). It may help us. 

Edx tools are [here](https://github.com/edx/edx-tools/wiki)

Edx [REST API Guide and Authentication](https://buildmedia.readthedocs.org/media/pdf/course-catalog-api-guide/latest/course-catalog-api-guide.pdf#page11)
