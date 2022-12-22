import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect, abort

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretkey'


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


def get_asset(asset_id, action):
    conn = get_db_connection()
    asset = conn.execute('SELECT * FROM assets WHERE id = ?',
                         (asset_id,)).fetchone()
    conn.close()
    if action == "edit":
        if asset is None:
            abort(404)
        else:
            return asset
    if action == "create":
        if asset:
            return False
    return asset


@app.route('/')
def index():
    conn = get_db_connection()
    assets = conn.execute('SELECT * FROM assets').fetchall()
    asset_total = conn.execute('SELECT COUNT(*) FROM assets').fetchone()[0]
    asset_types = conn.execute('SELECT asset_type, COUNT(*) FROM assets GROUP BY asset_type').fetchall()
    asset_status = conn.execute('SELECT asset_status, COUNT(*) FROM assets GROUP BY asset_status').fetchall()
    conn.close()
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
                conn = get_db_connection()
                conn.execute('INSERT INTO assets (id, asset_type, asset_status) VALUES (?, ?, ?)',
                            (id, asset_type, asset_status))
                conn.commit()
                conn.close()
                return redirect(url_for('status'))
            except sqlite3.IntegrityError:
                flash("Asset already exists")
                return redirect(url_for('create_asset'))

    return render_template('create_asset.html')


@app.route('/status')
def status():
    conn = get_db_connection()
    assets = conn.execute('SELECT * FROM assets').fetchall()
    conn.close()
    return render_template('status.html', assets=assets)


@app.route('/<id>/edit/', methods=('GET', 'POST'))
def edit_asset(id):
    asset = get_asset(id, "edit")
    print(asset)
    if request.method == 'POST':
        asset_type = request.form['asset_type']
        asset_status = request.form['asset_status']
        conn = get_db_connection()
        conn.execute('UPDATE assets SET asset_type = ?, asset_status = ?'
                        ' WHERE id = ?', (asset_type, asset_status, id))
        conn.commit()
        conn.close()
        return redirect(url_for('status'))
    
    return render_template('edit_asset.html', asset=asset)
    
@app.route('/delete/<id>/', methods=('POST',))
def delete(id):
    asset = get_asset(id, "edit")
    conn = get_db_connection()
    conn.execute('DELETE FROM assets WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Asset "{}" was successfully deleted!'.format(id))
    return redirect(url_for('index'))
