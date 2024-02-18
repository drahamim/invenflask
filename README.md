# Invenflask
[![Release](https://github.com/drahamim/invenflask/actions/workflows/release.yml/badge.svg)](https://github.com/drahamim/invenflask/actions/workflows/release.yml)

A small inventory ledger, based on Flask. Intitally designed for Radio Checkout at various conventions. 

## Features
- Easy Checkin/Out functionality
- Clean UI/UX 
- Indivudual Staff or Asset History
- Full ledger of all Asset Activity
- Easy inport of Assets or Staff via CSV

## Installation

### Prerequisites
- Python 3.11.7
- Postgres 14.9 or SQLite 3.39.5


### Install Steps

#### Database
1. Install a Postgres Database https://www.postgresql.org/
2. export Database URI as `DATABASE_URI` Ex. `postgresql://<hostaneme>/<databasename>`



#### Zip Deploy
- Install [Prerequisits](#prerequisites)
-  Download Zip from [Releases](https://github.com/drahamim/releases/latest)
-  unzip into local directory
-  pip install -r requirements.txt
-  run with `gunicorn -w 1 --bind 0.0.0.0:8000 wsgi:app`


## Import Staff
This can be done on the **Bulk Import** page.

Staff information support the following columns of information:

```ID, First Name, Last Name, Division, Department, Title``` 
* ID must be unique
* Last NAme, Division and Title have a "Leave BlanK" Option are are thus optional

## Import Assets
This can be done on the **Bulk Import** page.

Assets currently support the following columns:

```ID, Model, Status```
*ID must be unique*

Status is special because by default it will import as **Available** unless a column is specified for unique status tracking



# Contributing
Please file an issue if you encounter a bug or are requesting a feature

If you want to contribute to the development please fork this repository and submit a pull request. 

## Development Instructions
For development, perform an _editable install_ 
1. Clone this repository
2. Run `python -m venv venv`
3. Run `source venv/bin/activate`
4. Run `pip install -e .`
5. Start a development server:
   ```
   venv/bin/flask --app invenflask.app run
   ```
