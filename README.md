#aws-swf-poc
>amazon web services

>simple workflow

>proof of concept

## Instructions
1. create venv: `virtualenv --python=python3.5 venv`
1. activate it: `source venv/bin/activate`
1. install requirements: `pip install -r requirements.txt`
1. make sure you have your config set up: https://boto.readthedocs.io/en/latest/boto_config_tut.html
1. run: `python register.py`

Every 3 seconds the generator will initiate a new workflow. The decider & worker will handle it to completion.

## Screenshot
![](screenshot.png?raw=true)