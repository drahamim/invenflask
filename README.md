# Invenflask
[![Release](https://github.com/drahamim/invenflask/actions/workflows/release.yml/badge.svg)](https://github.com/drahamim/invenflask/actions/workflows/release.yml)

A small inventory ledger, based on Flask.

[Setup](#setup)

[Import Staff](#import-staff)
[Import Assets](#import-assets)
[]

## Setup

Proper Python distributions are currently a work in progress. Until then, install from a git clone or a source code snapshot from [releases](https://github.com/drahamim/invenflask/releases).

Within the unpacked directory:
1. Set up virtual environment:
   If /usr/bin/python is an old version, replace the below "python" with "python3.9"
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

   Note that this is a destructive operation. If `database.db` already exists, it will be erased.

4. Configuration:
   1. Copy example to config file:
      ``` 
      cp -i example.config.py config.py
      ```
   2. Set a secret key:
      ```
      sed --in-place -e 's/^SECRET_KEY *=.*/SECRET_KEY = "'"$(python3 -c 'import uuid; print(uuid.uuid4().hex);')"'"/' config.py
      ```

## Development Instructions

Start a development server:
  ```
  venv/bin/flask --app invenflask.app run
  ```

For development, perform an _editable install_ instead at step 2 above, with `pip install -e .`

## Production onetime setup

```
ssh 172.18.1.32
sudo useradd --create-home invenflask
sudo chown -R kjw /home/invenflask

# from laptop/dev environment:
# Note this may need redoing i.e. config.py is edited or the db needs wiping
scp database.db config.py 172.18.1.32:/home/invenflask/

# back on server, change ownership to invenflask so it can write.
# TODO: instead make it writable by group invenflask
ssh 172.18.1.32
sudo chown invenflask /home/invenflask/database.db

# AS KJW, because I'm lazy and it's easier if I own the files
ssh kjw@172.18.1.32
cd /home/invenflask
python3 -m venv venv
. venv/bin/activate
pip install gunicorn

# verify all the pieces are there:
venv/bin/gunicorn -w 1 --bind 0.0.0.0:8000 wsgi:app
```

## Deployment via wheel

Build `.whl`
```
pip wheel .
scp init.d_invenflask init.sh wsgi.py invenflask-*.whl 172.18.1.32:/home/invenflask/
```

Upgrade and restart server
```
ssh kjw@172.18.1.32
cd /home/invenflask
. venv/bin/activate
pip3 install invenflask-2.6.1.dev0+gb4afd65.d20230524-py2.py3-none-any.whl
sudo ./init.d_invenflask install
sudo /etc/init.d/invenflask restart
# TODO: turn this into a service so it auto restarts after a crash. should also fix the "stop" bug in initd_invenflask
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

Status is special because by default it will import as **Available** unless a column is specified for unique status tracking.
