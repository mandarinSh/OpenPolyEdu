# OpenPolyEdu

# Log's analysis

The log provided to us has [JSON](http://json.org/) format. More precisely, log is a multiline file, where each line is an JSON object.

### Example of 1 line: 
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

Since the log is large (18GB and may be larger in the future), its manual analysis becomes impossible.

In order to understand what information is contained in the log, unique keys were allocated from all objects for further analysis.

The script to extract the keys was written in Python3.

### Usage: 
`./log/parser.py [path-to-file]` where `[path-to-file]` - is path to log file.
