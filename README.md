# Invenflask

Dependancies:
sqlite3 3.32.3
Python 3.10.9
Flask 2.2.2
Werkzeug 2.2.2



## Setup
Initialize the database\
``` python3 init_db.py```

start flask\
```flask app.py```



## import staff
This will require a CSV formatted file 
Fields in order 

```id, FirstName, LastName, Division, Department, Title```

Do not include a header row

```
sqlite3 database.db
sqlite> .mode csv
sqlite> .import ./test_data/<your staff file>.csv staffs
# verify it worked
sqlite> SELECT * from staffs;
```