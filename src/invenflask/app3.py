import os
from flask_sqlalchemy import SQLAlchemy
import sqlite3
from pathlib import Path
from importlib.metadata import version

import pandas as pd
from flask import (Flask, flash, g, redirect, render_template, request,
                   session, url_for)
from flask_bootstrap import Bootstrap5
from werkzeug.utils import secure_filename
from flask_modals import Modal
from flask import Flask, render_template, request, redirect, url_for, flash


config_path = Path.cwd().joinpath('config.py')

upload_folder = os.path.join('static', 'uploads')
allowed_ext = {'csv'}

app = Flask(__name__)
app.config.from_pyfile(config_path)
app.config['upload_folder'] = upload_folder
os.makedirs(app.config['upload_folder'], exist_ok=True)
print(config_path)
bootstrap = Bootstrap5(app)
modal = Modal(app)
# print(app.config)


@app.context_processor
def get_version():
    return dict(app_version=version("invenflask"))


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = get_db_connection()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


def get_asset(asset_id, action):
    conn = get_db()
    asset = conn.execute('SELECT * FROM assets WHERE id = ?',
                         (asset_id,)).fetchone()
    conn.commit()
    if action == "edit":
        if asset is None:
            return False
        else:
            print(asset)
            return asset
    if action == "create":
        if asset:
            return False
    return asset


def get_staff(staff_id):
    conn = get_db()
    staff = conn.execute('SELECT * FROM staffs WHERE id = ?',
                         (staff_id,)).fetchone()
    conn.commit()
    print(f'Get Staff {staff}')
    if not staff:
        return False
    return staff


def get_checkout(asset_id):
    conn = get_db()
    asset = conn.execute('SELECT * FROM checkouts WHERE assetid = ?',
                         (asset_id,)).fetchone()
    conn.commit()
    return asset


@app.route('/')
def index():

    conn = get_db()
    assets = conn.execute('SELECT * FROM assets').fetchall()
    asset_total = conn.execute('SELECT COUNT(*) FROM assets').fetchone()[0]
    asset_types = conn.execute(
        'SELECT asset_type, COUNT(*) FROM assets GROUP BY asset_type'
    ).fetchall()
    asset_status = conn.execute(
        "SELECT asset_type, COUNT() AS TotalCount,"
        "SUM(asset_status = 'checkedout') AS AvailCount from assets GROUP BY asset_type;"
    ).fetchall()
    checkouts = conn.execute(
        "select * from checkouts").fetchall()
    conn.commit()
    return render_template(
        'index.html', assets=assets, asset_total=asset_total,
        asset_type=asset_types, asset_status=asset_status, checkouts=checkouts)


@app.route('/create_asset', methods=('GET', 'POST'))
def create_asset():
     assets = Table('assets', MetaData(bind=engine), autoload=True)

    if request.method == 'POST':
        asset_id = request.form['assetid']
        asset_name = request.form['assetname']
        asset_type = request.form['assettype']

        if not asset_id or not asset_name or not asset_type:
            flash('All fields are required', "warning")
        else:
            try:
                db_session.execute(
                    insert(assets).values(
                        id=asset_id, name=asset_name, type=asset_type, status='available'
                    )
                )
                db_session.commit()
                return redirect(url_for('assets'))
            except Exception as e:
                flash("Asset already exists", 'warning')
                return redirect(url_for('asset_create'))

    return render_template('asset_create.html')


@app.route('/<id>/edit/', methods=('GET', 'POST'))
def edit_asset(id):

    if request.method == 'POST':
        asset_type = request.form['asset_type']
        asset_status = request.form['asset_status']
        conn = get_db()
        old_record = get_asset(id, "edit")
        if old_record['asset_status'].lower() != asset_status.lower():
            if asset_status == 'checkedout':
                flash('Manual checkeouts without staff ID not allowed', "warnin")
                return redirect(url_for('checkout'))
        conn.execute('UPDATE assets SET asset_type = ?, asset_status = ?'
                     ' WHERE id = ?', (asset_type, asset_status, id))
        conn.commit()
        # flash("YOU WANKER")
        return redirect(url_for('status'))
    if request.method == 'GET':
        conn = get_db()
        asset = get_asset(id, "edit")
        asset_types = conn.execute(
            'Select DISTINCT(asset_type) from assets').fetchall()
        return render_template('edit_asset.html', asset=asset, asset_types=asset_types)


@app.route('/status')
def status():
    conn = get_db()
    assets = conn.execute('SELECT * FROM assets').fetchall()
    conn.commit()
    return render_template('status.html', assets=assets)


@app.route('/delete/<id>', methods=('POST',))
def delete(id):
    asset = get_asset(id, "edit")
    conn = get_db()
    conn.execute('DELETE FROM assets WHERE id = ?', (asset,))
    conn.commit()
    flash('Asset "{}" was successfully deleted!'.format(id), "success")
    return redirect(url_for('index'))


@app.route('/staff/create', methods=('GET', 'POST'))
def staff_create():
    staffs = Table('staffs', MetaData(bind=engine), autoload=True)
    staff_div = "--"
    staff_dept = "--"
    if request.method == 'POST':
        staff_id = request.form['staffid']
        first_name = request.form['firstname']
        last_name = request.form['lastname']
        staff_title = request.form['title']
        if request.form['division']:
            staff_div = request.form['division']
        if request.form['department']:
            staff_dept = request.form['department']

        if not staff_id:
            flash('Staff ID or Auto Generate is required', "warning")
        elif not first_name or not last_name:
            flash('Missing Name information', "warning")
        else:
            try:
                db_session.execute(
                    insert(staffs).values(
                        staff_id=staff_id, first_name=first_name, last_name=last_name,
                        title=staff_title, division=staff_div, department=staff_dept
                    )
                )
                db_session.commit()
                return redirect(url_for('staff'))
            except Exception as e:
                flash("Staff already exists", 'warning')
                return redirect(url_for('staff_create'))

    return render_template('staff_create.html')


@app.route('/staff/delete/<id>/', methods=('POST',))
def staff_delete(id):
    staffs = Table('staffs', MetaData(bind=engine), autoload=True)
    db_session.execute(delete(staffs).where(staffs.c.staff_id == staff_id))
    db_session.commit()
    flash(f'Staff "{staff_id}" was successfully deleted!', "success")
    return redirect(url_for('staff'))


@app.route('/staff/edit/<id>/', methods=('GET', 'POST'))
def staff_edit(id):
    staffs = Table('staffs', MetaData(bind=engine), autoload=True)
    staff = staffs.select().where(staffs.c.staff_id == staff_id).execute().fetchone()

    if request.method == 'POST':
        first_name = request.form['firstname']
        last_name = request.form['lastname']
        staff_title = request.form['title']
        staff_div = request.form['division']
        staff_dept = request.form['department']

        db_session.execute(
            update(staffs).where(staffs.c.staff_id == staff_id).values(
                first_name=first_name, last_name=last_name,
                title=staff_title, division=staff_div, department=staff_dept
            )
        )
        db_session.commit()
        return redirect(url_for('staff'))

    return render_template('staff_edit.html', staff=staff)


@app.route('/staff/', methods=('GET', 'POST'))
def staff():
    staffs = Table('staffs', MetaData(bind=engine), autoload=True)
    staff_list = staffs.select().execute().fetchall()
    return render_template('staff.html', staff=staff_list)


@app.route('/checkout', methods=('GET', 'POST'))
def checkout():
    assets = Table('assets', MetaData(bind=engine), autoload=True)
    staffs = Table('staffs', MetaData(bind=engine), autoload=True)
    checkouts = Table('checkouts', MetaData(bind=engine), autoload=True)

    if request.method == 'POST':
        asset_id = request.form['assetid']
        staff_id = request.form['staffid']

        if not asset_id or not staff_id:
            flash('Asset ID and Staff ID are required', "warning")
        else:
            asset = assets.select().where(assets.c.id == asset_id).execute().fetchone()
            staff = staffs.select().where(staffs.c.staff_id == staff_id).execute().fetchone()

            if not asset or not staff:
                flash('Asset ID or Staff ID not found', "warning")
            elif asset['asset_status'] == 'checkedout':
                flash('Asset already checked out', "warning")
            else:
                db_session.execute(
                    insert(checkouts).values(asset_id=asset_id, staff_id=staff_id)
                )
                db_session.execute(
                    assets.update().where(assets.c.id == asset_id).values(asset_status='checkedout')
                )
                db_session.commit()
                return redirect(url_for('index'))

    return render_template('checkout.html')


@app.route('/checkin', methods=('GET', 'POST'))
def checkin():
     assets = Table('assets', MetaData(bind=engine), autoload=True)
    checkouts = Table('checkouts', MetaData(bind=engine), autoload=True)

    if request.method == 'POST':
        asset_id = request.form['assetid']

        if not asset_id:
            flash('Asset ID is required', "warning")
        else:
            asset = assets.select().where(assets.c.id == asset_id).execute().fetchone()

            if not asset:
                flash('Asset ID not found', "warning")
            elif asset['asset_status'] == 'available':
                flash('Asset already checked in', "warning")
            else:
                db_session.execute(
                    checkouts.delete().where(checkouts.c.asset_id == asset_id)
                )
                db_session.execute(
                    assets.update().where(assets.c.id == asset_id).values(asset_status='available')
                )
                db_session.commit()
                return redirect(url_for('index'))

    return render_template('checkin.html')


@app.route('/history')
def history():
    checkouts = Table('checkouts', MetaData(bind=engine), autoload=True)
    history_list = checkouts.select().execute().fetchall()
    return render_template('history.html', history=history_list)

@app.route('/staff/<staff_id>/history')
def staff_history(staff_id):
    checkouts = Table('checkouts', MetaData(bind=engine), autoload=True)
    history_list = checkouts.select().where(checkouts.c.staff_id == staff_id).execute().fetchall()
    return render_template('staff_history.html', history=history_list)

@app.route('/asset/<asset_id>/history')
def asset_history(asset_id):
    checkouts = Table('checkouts', MetaData(bind=engine), autoload=True)
    history_list = checkouts.select().where(checkouts.c.asset_id == asset_id).execute().fetchall()
    return render_template('asset_history.html', history=history_list)


@app.route('/bulk_import', methods=('GET', 'POST'))
def bulk_import():
    if request.method == 'POST':
        uploaded_file = request.files.get('file')
        print(uploaded_file)
        data_filename = secure_filename(uploaded_file.filename)
        file_path = os.path.join(app.config['upload_folder'], data_filename)
        uploaded_file.save(os.path.join(
            app.config['upload_folder'], data_filename))
        session['uploaded_data_file_path'] = file_path
        form_type = request.form['select_type']

        return redirect(url_for('showData', form_type=form_type))
    if request.method == "GET":
        return render_template('bulk_import.html')


@app.route('/show_data', methods=["GET", "POST"])
def showData():
    # Retrieving uploaded file path from session
    data_file_path = session.get('uploaded_data_file_path', None)

    # read csv file in python flask (reading uploaded csv file from uploaded server location)
    uploaded_df = pd.read_csv(data_file_path)

    # pandas dataframe to html table flask
    uploaded_df_html = uploaded_df.to_html()
    if request.method == "GET":
        headers = pd.read_csv(data_file_path, nrows=1).columns.tolist()
        form_type = request.args.get('form_type')
        return render_template(
            'bulk_import_verify.html', data_var=uploaded_df_html,
            headers_list=headers, form_type=form_type)
    if request.method == "POST":
        form_type = request.args.get('form_type')
        if form_type == 'assets':
            asset_id_field = request.form['asset_id']
            asset_type_field = request.form['asset_type']
            asset_status_field = request.form['asset_status']

            parseCSV_assets(
                data_file_path, asset_id_field,
                asset_type_field, asset_status_field)
            return redirect(url_for('status'))
        elif form_type == 'staff':
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            staff_id = request.form['staff_id']
            division = request.form['division']
            department = request.form['department']
            title = request.form['title']
            parseCSV_staff(
                data_file_path, first_name, last_name, staff_id,
                division, department, title)

            return redirect(url_for('staff'))
            # First Name	Last Name	Staff ID	Division	Department	Title


def parseCSV_assets(filePath, asset_id, asset_type, asset_status):
    # Use Pandas to parse the CSV file
    csvData = pd.read_csv(filePath, header=0, keep_default_na=False)
    # Loop through the Rows

    print("PARSING DATA")
    print(asset_status)
    for i, row in csvData.iterrows():
        if asset_status != 'Available':
            asset_status == row[asset_status]

        try:
            conn = get_db()
            conn.execute(
                'INSERT INTO assets (id, asset_type, asset_status)'
                'VALUES(?,?,?)',
                (str(row[asset_id]).lower(), row[asset_type], asset_status)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            flash("Asset upload failed import", "danger")
            return redirect(url_for('create_asset'))
    return redirect(url_for('status'))


def parseCSV_staff(
        filePath, first_name, last_name, staff_id, division, department, title):
    # Use Pandas to parse the CSV file
    csvData = pd.read_csv(filePath, header=0, keep_default_na=False)
    # Loop through the Rows

    for i, row in csvData.iterrows():
        try:
            conn = get_db()
            conn.execute(
                'INSERT INTO staffs (id, first_name, last_name, division, department, title)'
                'VALUES(?,?,?,?,?,?)',
                (row[staff_id], row[first_name], row[last_name],
                 row[division], row[department], row[title]))
            conn.commit()
        except sqlite3.IntegrityError:
            flash("Asset upload failed import", "danger")
            return redirect(url_for('create_asset'))
    return redirect(url_for('status'))

