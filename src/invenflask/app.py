from flask import Flask
from flask import render_template, request, url_for, flash, redirect, abort, g, session
from pathlib import Path
import sqlite3
import os
import pandas as pd
from werkzeug.utils import secure_filename


config_path = Path.cwd().joinpath('config.py')

upload_folder = os.path.join('static', 'uploads')
allowed_ext = {'csv'}

app = Flask(__name__)
app.config.from_pyfile(config_path)
app.config['upload_folder'] = upload_folder
os.makedirs(app.config['upload_folder'], exist_ok=True)
print(config_path)

print(app.config)


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
                         (asset_id,)).fetchone
    conn.commit()
    if action == "edit":
        if asset is None:
            abort(404)
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
    conn.commit()
    return render_template(
        'index.html', assets=assets, asset_total=asset_total,
        asset_type=asset_types, asset_status=asset_status)


@app.route('/create_asset', methods=('GET', 'POST'))
def create_asset():
    if request.method == 'POST':
        id = request.form['id']
        asset_type = request.form['asset_type']
        asset_status = request.form['asset_status']

        if not id:
            flash('Asset ID is required')
        elif not asset_type:
            flash('Asset Type required')
        else:
            try:
                conn = get_db()
                conn.execute(
                    'INSERT INTO assets (id, asset_type, asset_status)'
                    'VALUES (?, ?, ?)',
                    (id, asset_type, asset_status))
                conn.commit()
                return redirect(url_for('status'))
            except sqlite3.IntegrityError:
                flash("Asset already exists")
                return redirect(url_for('create_asset'))

    return render_template('create_asset.html')


@app.route('/status')
def status():
    conn = get_db()
    assets = conn.execute('SELECT * FROM assets').fetchall()
    conn.commit()
    return render_template('status.html', assets=assets)


@app.route('/<id>/edit/', methods=('GET', 'POST'))
def edit_asset(id):
    asset = get_asset(id, "edit")
    print(asset)
    if request.method == 'POST':
        asset_type = request.form['asset_type']
        asset_status = request.form['asset_status']
        conn = get_db()
        conn.execute('UPDATE assets SET asset_type = ?, asset_status = ?'
                     ' WHERE id = ?', (asset_type, asset_status, id))
        conn.commit()
        return redirect(url_for('status'))

    return render_template('edit_asset.html', asset=asset)


@app.route('/delete/<id>/', methods=('POST',))
def delete(id):
    asset = get_asset(id, "edit")
    conn = get_db()
    conn.execute('DELETE FROM assets WHERE id = ?', (asset,))
    conn.commit()
    flash('Asset "{}" was successfully deleted!'.format(id))
    return redirect(url_for('index'))


@app.route('/staff/', methods=('GET', 'POST'))
def staff():
    conn = get_db()
    if request.method == 'POST':
        pass
    staff = conn.execute('SELECT * FROM staffs').fetchall()
    conn.commit()
    return render_template('staff.html', staffs=staff)


@app.route('/checkout', methods=('GET', 'POST'))
def checkout():
    if request.method == 'POST':
        asset_id = request.form['id']
        accessory_id = request.form['accessoryid']
        staff_id = request.form['staffid']
        if not asset_id:
            flash('Asset ID is required')
        elif not staff_id:
            flash('Staff ID required')
        elif get_staff(staff_id) is None:
            flash('Staff does not exist')
            return redirect(url_for('checkout'))
        elif get_asset(asset_id, 'edit') is False:
            flash("Asset does not exist. Please make it below")
            return redirect(url_for('create_asset'))
        elif get_asset(asset_id, 'edit') is dict:
            if get_asset(asset_id, 'edit')['asset_status'] == 'damaged':
                flash("Asset should not be checked out. Please choose another one")
                return redirect(url_for('checkout'))
            else:
                flash(
                    f"Something went wrong with {get_asset(asset_id, 'edit')}")
        else:
            staff_dept = get_staff(staff_id)['Department']
            # flash(get_asset(asset_id, 'edit'))
            try:
                conn = get_db()
                conn.execute(
                    'INSERT INTO checkouts (assetid, staffid, department) '
                    'VALUES (?, ?, ?)', (asset_id, staff_id, staff_dept))
                conn.execute('UPDATE assets SET asset_status = "checkedout" '
                             'WHERE id = ?', (asset_id,))
                if accessory_id:
                    conn.execute(
                        'INSERT INTO checkouts (assetid, staffid, department)'
                        ' VALUES (?, ?, ?)',
                        (accessory_id, staff_id, staff_dept))
                    conn.execute(
                        'UPDATE assets SET asset_status = "checkedout" '
                        'WHERE id = ?',
                        (accessory_id,))

                conn.commit()
                flash('Asset Checkout Completed')
                return redirect(url_for('checkout'))
            except sqlite3.IntegrityError:
                flash(
                    "Asset already checked out! Please check-in "
                    "before checking out")
                return redirect(url_for('checkout'))
    return render_template('checkout.html')


@app.route('/checkin', methods=('GET', 'POST'))
def checkin():
    if request.method == 'POST':
        asset_id = request.form['id']
        if not asset_id:
            flash('Asset ID is required')
        elif get_asset(asset_id, "edit") is False:
            flash("Asset does not exist. Please make it below")
            return redirect(url_for('create_asset'))
        elif get_checkout(asset_id) is None:
            flash("Asset Not checked out")
            return redirect(url_for('checkin'))
        else:
            asset_checkout = get_checkout(asset_id)
            print(asset_checkout)
            staff_div = get_staff(asset_checkout['staffid'])['Division']
            try:
                conn = get_db()
                conn.execute(
                    'INSERT INTO history (assetid, staffid, department, division, checkouttime) VALUES (?,?,?,?,?)',
                    (asset_id, asset_checkout['staffid'],
                     asset_checkout['department'], staff_div,
                     asset_checkout['timestamp']))
                conn.execute(
                    'DELETE from checkouts WHERE assetid = ?', (asset_id,))
                if get_asset(asset_id, 'edit') is dict:
                    if get_asset(asset_id, "edit")['asset_status'] == "damaged":
                        conn.execute(
                            'UPDATE assets SET asset_status = ? WHERE id = ?',
                            ('damaged', asset_id))
                    else:
                        conn.execute(
                            'UPDATE assets SET asset_status = ? WHERE id = ?',
                            ('Available', asset_id))
                conn.commit()
                flash('Asset checkin Completed')
                return redirect(url_for('checkout'))
            except sqlite3.IntegrityError as e:
                flash(f"{e}")
                return redirect(url_for('checkin'))
    return render_template('checkin.html')


@app.route('/history')
def history():
    conn = get_db()
    assets = conn.execute('SELECT * FROM history').fetchall()
    conn.commit()
    return render_template('history.html', assets=assets)


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
    csvData = pd.read_csv(filePath, header=0)
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
                (row[asset_id], row[asset_type], asset_status)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            flash("Asset upload failed import")
            return redirect(url_for('create_asset'))
    return redirect(url_for('status'))


def parseCSV_staff(
        filePath, first_name, last_name, staff_id, division, department, title):
    # Use Pandas to parse the CSV file
    csvData = pd.read_csv(filePath, header=0)
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
            flash("Asset upload failed import")
            return redirect(url_for('create_asset'))
    return redirect(url_for('status'))
