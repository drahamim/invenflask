# Invenflask
[![Release](https://github.com/drahamim/invenflask/actions/workflows/release.yml/badge.svg)](https://github.com/drahamim/invenflask/actions/workflows/release.yml)

A small inventory ledger, based on Flask.

[Setup](#setup)

[Import Staff](#import-staff)
[Import Assets](#import-assets)
[]


## Setup

Proper Python distributions are currently a work in progress. Until then, install from a git clone or a source code snapshot from [releases](https://github.com/drahamim/invenflask/releases).


### PIP/VENV configuration 
Within the unpacked directory:
1. Set up virtual environment:
   ```
   python3 -m venv venv
   ```
2. Install invenflask:
   ```
   venv/bin/pip install .
   ```

### Database
1. Install a Postgres Database https://www.postgresql.org/
2. export Database URI as `DATABASE_URI`  


## Development Instructions
For development, perform an _editable install_ instead at step 2 above, with `pip install -e .`
 Start a development server:
   ```
   venv/bin/flask --app invenflask.app run
   ```



## Gunicorn (Production)
Follow Steps 1-4 of the Setup guide then continue with the following:
1. Install Gunicorn
   ```
   venv/bin/pip install gunicorn
   ```
2. Run gunicorn
   ```
   venv/bin/gunicorn -w 1 --bind 0.0.0.0:8000 wsgi:app
   ```


## Import Staff
This can be done on the **Bulk Import** page.

Staff information support the following columns of information:

```ID, First Name, Last Name, Division, Department, Title``` 
*ID must be unique*

Currently we do not support less than 6 columns on the import. 
If you don't have all the matching just create blank columns with the headers as needed. 

## Import Assets
This can be done on the **Bulk Import** page.

Assets currently support the following columns:

```ID, Model, Status```
*ID must be unique*

Status is special because by default it will import as **Available** unless a column is specified for unique status tracking
