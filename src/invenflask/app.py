from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy import create_engine, Table, MetaData, insert, select, update, delete
from datetime import datetime
import os
from pathlib import Path
from importlib.metadata import version
import pandas as pd
from flask_bootstrap import Bootstrap5
from werkzeug.utils import secure_filename
from flask_modals import Modal
from invenflask.models import Asset, Staff, Checkout, History, db
from sqlalchemy import Table, MetaData, select, update, delete
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URI', 'sqlite:////tmp/test.db')
db.init_app(app)
bootstrap = Bootstrap5(app)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SECRET_KEY'] = os.urandom(24)
migrate = Migrate(app, db)


with app.app_context():
    db.create_all(app=app)


@app.context_processor
def get_version():
    return dict(app_version=version("invenflask"))


@app.route('/')
def index():
    assets = db.session.query(Asset).all()
    asset_total = db.session.query(Asset).count()
    asset_types = db.session.query(
        Asset.asset_type, db.func.count()).group_by(Asset.asset_type).all()
    asset_status = db.session.query(
        Asset.asset_type,
        db.func.count().label('TotalCount'),
        db.func.sum(db.case((Asset.asset_status == 'checkedout', 1), else_=0)).label(
            'AvailCount')
    ).group_by(Asset.asset_type).all()
    checkouts = db.session.query(Checkout).all()
    return render_template(
        'index.html', assets=assets, asset_total=asset_total,
        asset_type=asset_types, asset_status=asset_status, checkouts=checkouts)

## ASSET ROUTES
@app.route('/create/asset', methods=('GET', 'POST'))
def asset_create():
    assets = db.session.query(Asset).all()

    if request.method == 'POST':
        asset_id = request.form['id']
        asset_type = request.form['asset_type']
        asset_status = request.form['asset_status']

        if not asset_id or not asset_status or not asset_type:
            flash('All fields are required', "warning")
        else:
            try:
                new_asset = Asset(id=asset_id, asset_status=asset_status,
                                  asset_type=asset_type)
                db.session.add(new_asset)
                db.session.commit()
                return redirect(url_for('assets'))
            except Exception as e:
                app.logger.error(e)
                flash("Asset already exists", 'warning')
                return redirect(url_for('asset_create'))

    return render_template('asset_create.html')


@app.route('/edit/asset/<asset_id>', methods=('GET', 'POST'))
def asset_edit(asset_id):
    assets = db.session.query(Asset).all()
    asset = db.session.query(Asset).filter_by(id=asset_id).first()

    if request.method == 'POST':
        asset_id = request.form['id']
        asset_type = request.form['asset_type']
        asset_status = request.form['asset_status']

        db.session.update(assets).where(assets.c.id == asset_id).values(
            asset_status=asset_status, asset_type=asset_type)
        db.session.commit()
        return redirect(url_for('assets'))

    return render_template('asset_edit.html', asset=asset)


@app.route('/delete/asset/<asset_id>', methods=('POST',))
def asset_delete(asset_id):
    db.session.delete(Asset.query.get(asset_id))
    db.session.commit()
    flash(f'Asset "{asset_id}" was successfully deleted!', "success")
    return redirect(url_for('assets'))

## STAFF ROUTES
@app.route('/create/staff', methods=('GET', 'POST'))
def staff_create():

    if request.method == 'POST':
        staff_id = request.form['staffid']
        first_name = request.form['firstname']
        last_name = request.form['lastname']
        division = request.form['division']
        department = request.form['department']
        title = request.form['title']
        
        if not staff_id or not staff_name:
            flash('All fields are required', "warning")
            
        if db.session.query(Staff).filter_by(id=staff_id).scalar():
            flash('Staff already exists', "warning")
            return redirect(url_for('staff_create'))
        else:
            try:
                db.session.execute(
                    insert(staffs).values(
                        id=staff_id, first_name=
                    )
                )
                db_session.execute(
                    insert(staffs).values(
                        staff_id=staff_id, name=staff_name
                    )
                )
                db_session.commit()
                return redirect(url_for('staffs'))
            except Exception as e:
                flash("Staff already exists", 'warning')
                return redirect(url_for('staff_create'))

    return render_template('staff_create.html')


@app.route('/edit/staff/<staff_id>', methods=('GET', 'POST'))
def staff_edit(staff_id):
    staffs = Table('staffs', MetaData(bind=engine), autoload=True)
    staff = db_session.execute(select(staffs).where(
        staffs.c.staff_id == staff_id)).fetchone()

    if request.method == 'POST':
        staff_name = request.form['staffname']

        db_session.execute(
            update(staffs).where(staffs.c.staff_id == staff_id).values(
                name=staff_name
            )
        )
        db_session.commit()
        return redirect(url_for('staffs'))

    return render_template('staff_edit.html', staff=staff)


@app.route('/delete/staff/<staff_id>', methods=('POST',))
def staff_delete(staff_id):
    staffs = Table('staffs', MetaData(bind=engine), autoload=True)
    db_session.execute(delete(staffs).where(staffs.c.staff_id == staff_id))
    db_session.commit()
    flash(f'Staff "{staff_id}" was successfully deleted!', "success")
    return redirect(url_for('staffs'))

## ACTION ROUTES
@app.route('/checkout', methods=('GET', 'POST'))
def checkout():

    if request.method == 'POST':
        asset_id = request.form['assetid']
        staff_id = request.form['staffid']

        if not db.session.query(Asset).filter_by(id=asset_id).scalar():
            flash('Asset does not exist', "warning")
            return render_template('checkout.html')
        
        if not asset_id or not staff_id:
            flash('All fields are required', "warning")
        else:
            try:
                db_session.execute(
                    insert(checkouts).values(
                        asset_id=asset_id, staff_id=staff_id, checkout_date=datetime.now()
                    )
                )
                db_session.execute(
                    update(assets).where(assets.c.id == asset_id).values(
                        status='checked out'
                    )
                )
                db_session.commit()
                return redirect(url_for('history'))
            except Exception as e:
                flash("Checkout failed", 'warning')
                return redirect(url_for('checkout'))

    return render_template('checkout.html')


@app.route('/return_asset', methods=('GET', 'POST'))
def return_asset():
    if request.method == 'POST':
        asset_id = request.form['id']

        if not asset_id:
            flash('Asset ID is required', "warning")
        else:
            asset_checkout_date = db.session.query(
                Checkout.timestamp).filter(asset_id == asset_id).scalar()

            try:
                db.session.update(History).where(history.c.asset_id == asset_id).values(
                    asset_id=asset_id, staff_id=staff_id,
                    checkouttime=asset_checkout_date, returntime=datetime.now()
                )
                db.session.delete(Checkout).where(
                    checkouts.c.asset_id == asset_id)

                db.session.update(Assets).where(assets.c.id == asset_id).values(
                    status='available')

                db.session.commit()
                return redirect(url_for('history'))
            except Exception as e:
                flash("Return failed", 'warning')
                return redirect(url_for('return_asset'))

    return render_template('return.html')

## READ ROUTES
@ app.route('/history')
def history():
    history_list = db.session.query(History).all()

    return render_template('history.html', history=history_list)


@ app.route('/assets')
def assets():
    asset_list = Asset.query.all()
    return render_template('status.html', assets=asset_list)


@ app.route('/staffs')
def staffs():
    staffs = Table('staffs', MetaData(bind=engine), autoload=True)

    staff_list = db_session.execute(
        select([
            staffs.c.staff_id,
            staffs.c.name
        ])
    ).fetchall()

    return render_template('staffs.html', staffs=staff_list)

@app.route('/single_history/<rq_type>/<item_id>')
def single_history(rq_type, item_id):

    if rq_type == 'asset':
        item_info = db.session.query(Asset).get(item_id)
        current = db.session.query(Checkout).filter_by(assetid=item_id).all()
        history = db.session.query(History).filter_by(assetid=item_id).all()
    elif rq_type == 'staff':
        item_info = db.session.query(Staff).get(item_id)
        current = db.session.query(Checkout).filter_by(staffid=item_id).all()
        history = db.session.query(History).filter_by(staffid=item_id).all()
    return render_template('single_history.html', hist_type=rq_type,
                           current=current, history=history, item_info=item_info
                           )



## IMPORT TASKS
@ app.route('/bulk_import', methods=('GET', 'POST'))
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


@ app.route('/show_data', methods=["GET", "POST"])
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


def parseCSV_assets(filePath, asset_id, asset_type, asset_status):
    csvData = pd.read_csv(filePath, header=0, keep_default_na=False)
    for i, row in csvData.iterrows():
        if asset_status != 'Available':
            asset_status == row[asset_status]

        try:
            asset = Asset(id=str(row[asset_id]).lower(
            ), asset_type=row[asset_type], asset_status=asset_status)
            db.session.add(asset)
            db.session.commit()
        except IntegrityError:
            flash("Asset upload failed import", "danger")
            return redirect(url_for('create_asset'))
    return redirect(url_for('status'))


def parseCSV_staff(filePath, first_name, last_name, staff_id, division, department, title):
    csvData = pd.read_csv(filePath, header=0, keep_default_na=False)
    for i, row in csvData.iterrows():
        try:
            staff = Staff(id=row[staff_id], first_name=row[first_name], last_name=row[last_name],
                          division=row[division], department=row[department], title=row[title])
            db.session.add(staff)
            db.session.commit()
        except IntegrityError:
            flash("Staff upload failed import", "danger")
            return redirect(url_for('create_asset'))
    return redirect(url_for('status'))



if __name__ == '__main__':
    app.run(host=config.HOST, port=config.PORT, debug=True)
