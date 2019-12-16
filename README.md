# CollectTemplate

CollectTemplate is an app for Django framework, which allows you to collect
different app templates to working project templates directory.

## Installation

1. pip install CollectTemplate
2. Add CollectTemplate to settings as shown below
```
INSTALLED_APPS = (
    ...
    'CollectTemplate',
    ...
)
```
## Usage

|  Commmand  |Description  |
|---|---|
| manage.py collecttemplates  -h |Help  |  
| manage.py collecttemplates  |Copy all installed apps templates  | 
|manage.py collecttemplates -e app1 app2 app3|Copy all installed apps templates and exclude app1, app2 | 
|manage.py collecttemplates app1,app2,app3|Copy selected installed apps templates | 
|manage.py collecttemplates -t app1/home.html|Copy template app1/home.html | 
    
#### This app is inspired from Mezzanine CMS command collecttemplates

