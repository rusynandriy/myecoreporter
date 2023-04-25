<!--
title: 'MyEcoReporter'
description: 'A simpler way to collect data about environmental issues.'
layout: Doc
framework: v3
platform: AWS
language: python
authorLink: 'https://github.com/andriyrusyn'
authorName: 'Andriy Rusyn'
-->

# MyEcoReporter
This is a simple chat bot that gives people an easier way to report environmental quality concerns to their local government. You just text the bot over SMS and talk to it instead of filling out a form.

## Setup (see windows notes below)
1. Clone repo to your machine: `git clone origin https://github.com/andriyrusyn/myejbot`
2. Make sure you have python 3.9 installed: `brew install python@3.9`
3. Set up a virtual environment running python 3.9: 
`pip3 install virtualenv` and then `virtualenv venv -p python3.9`
4. Activate the virtual environment: `source venv/bin/activate`
5. Install the requirements: `pip install -r requirements.txt`

## WINDOWS SETUP NOTES
- follow this guide instead to set up virtualenv, etc.
- https://mothergeo-py.readthedocs.io/en/latest/development/how-to/venv-win.html

## set up AWS Cli
1. install the AWS CLI by following these intstructions
2. configure it using the keys and the `aws configure` command (ask Andriy for keys)

## Usage
0. first activate your virtual environment: `source venv/bin/activate`
1. run `python handler.py` to test locally 

### Deployment
0. make sure you have serverless-python-requirements installed (run `serverless plugin install -n serverless-python-requirements` if not)
1. make sure docker is running (may need to install if you don't have it already)
1. run `serverless deploy` to deploy your updated code
2. make sure to `git commit -am 'commit message here'` + `git push origin master` as well
