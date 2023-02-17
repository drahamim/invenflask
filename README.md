# Invenflask
[![Release](https://github.com/drahamim/invenflask/actions/workflows/release.yml/badge.svg)](https://github.com/drahamim/invenflask/actions/workflows/release.yml)

A small inventory ledger, based on Flask.


## Setup

Proper Python distributions are currently a work in progress. Until then, install from a git clone or a source code snapshot from [releases](https://github.com/drahamim/invenflask/releases).

Within the unpacked directory:
1. Set up virtual environment:
   ```
   python3 -m venv venv
   ```
2. Install invenflask:
   ```
   venv/bin/pip install .
   ```
3. Initialize database:
   ```
   venv/bin/invenflask-init-db
   ```
   This will create or overwrite a sqlite3 database named `database.db` in the current directory, which is the only setup the application currently understands.

   Note that this is a destructive operation. If `database.db` already exists, all tables that  
4. Start a development server:
   ```
   venv/bin/flask --app invenflask.app run
   ```

For development, perform an _editable install_ instead at step 2 above, with `pip install -e .`

## Import Staff
This can be done on the **Bulk Import** page.

Staff information support the following columns of information:

```ID, First Name, Last Name, Division, Department, Title``` 
*ID must be unique*

Currently we do not support less than 6 columns on the import. 
If you don't have all the matching just create blank columns with the headers as needed. 

## Import Assets
This can be done on teh **Bulk Import** page.

Assets currently support the following columns:

```ID, Model, Status```
*ID must be unique*

Status is special because by default it will import as **Available** unless a column is specified for unique status tracking
