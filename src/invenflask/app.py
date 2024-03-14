import os
from datetime import datetime
import subprocess

import pandas as pd
from flask import Flask, flash, redirect, render_template, request, url_for, session
from flask_bootstrap import Bootstrap5
from flask_migrate import Migrate
from importlib.metadata import version, PackageNotFoundError
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename
from flask_moment import Moment
from sqlalchemy import func
from .models import Asset, Staff, Checkout, History, db, GlobalSet
from .forms import SettingsForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URI', 'sqlite:////tmp/test.db')
bootstrap = Bootstrap5(app)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY','os.urandom(24)')
app.config['upload_folder'] = '/tmp/uploads'
moment = Moment(app)

if not os.path.exists(app.config['upload_folder']):
    os.makedirs(app.config['upload_folder'])

# Init DB
with app.app_context():
    db.init_app(app)
    db.create_all()
    db.session.commit()
migrate = Migrate(app, db)

# @app.context
# def inject_settings():
#     if not db.session.query(GlobalSet).filter(GlobalSet.settingid == "timezone"):
#         db.session.add(GlobalSet(settingid="timezone", setting="UTC"))
#         db.session.commit()
#     else:
#         print("timezone already set")
#     return dict(settings=db.session.query(GlobalSet).all())


@app.context_processor
def get_version():
    try:
        version("invenflask")
    except PackageNotFoundError:
        return dict(app_version=subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            capture_output=True).stdout.decode('utf-8').strip())
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

# ASSET ROUTES


@app.route('/create/asset', methods=('GET', 'POST'))
def asset_create():

    if request.method == 'POST':
        asset_id = request.form['id']
        asset_type = request.form['asset_type']
        asset_status = request.form['asset_status']

        if not asset_id or not asset_status or not asset_type:
            flash('All fields are required', "warning")
        if db.session.query(Asset).filter(
                func.lower(Asset.id) == asset_id.lower()).all():
            flash('Asset already exists', "warning")
            return redirect(url_for('asset_create'))
        else:
            try:
                new_asset = Asset(id=asset_id, asset_status=asset_status,
                                  asset_type=asset_type)
                db.session.add(new_asset)
                db.session.commit()
                flash(
                    f'Asset "{asset_id}" was successfully created!', "success")
                return redirect(url_for('assets'))
            except Exception as e:
                app.logger.error(e)
                flash("Asset creation failed", 'warning')
                return redirect(url_for('asset_create'))

    return render_template('asset_create.html')


@app.route('/edit/asset/<asset_id>', methods=('GET', 'POST'))
def asset_edit(asset_id):
    asset = db.session.query(Asset).filter_by(id=asset_id).first()

    if request.method == 'POST':
        asset_id = asset_id
        asset_type = request.form['asset_type']
        asset_status = request.form['asset_status']

        db.session.query(Asset).filter(Asset.id == asset_id).update(
            values={Asset.asset_status: asset_status,
                    Asset.asset_type: asset_type})
        db.session.commit()
        return redirect(url_for('assets'))

    return render_template('asset_edit.html', asset=asset)


@app.route('/delete/asset/<asset_id>', methods=('POST',))
def asset_delete(asset_id):
    db.session.delete(Asset.query.get(asset_id))
    db.session.commit()
    flash(f'Asset "{asset_id}" was successfully deleted!', "success")
    return redirect(url_for('assets'))

# STAFF ROUTES


@app.route('/create/staff', methods=('GET', 'POST'))
def staff_create():

    if request.method == 'POST':
        staff_id = request.form['staffid']
        first_name = request.form['firstname']
        last_name = request.form['lastname']
        division = request.form['division']
        department = request.form['department']
        title = request.form['title']

        if not staff_id or not first_name:
            flash('All fields are required', "warning")

        if db.session.query(Staff).filter(
                func.lower(Staff.id) == staff_id.lower()).all():
            flash('Staff already exists', "warning")
            return redirect(url_for('staff_create'))
        else:
            try:
                db.session.add(Staff(id=staff_id, first_name=first_name,
                                     last_name=last_name, division=division,
                                     department=department, title=title))
                db.session.commit()
                return redirect(url_for('staffs'))
            except Exception as e:
                app.logger.error(e)
                flash("Staff already exists", 'warning')
                return redirect(url_for('staff_create'))

    return render_template('staff_create.html')


@ app.route('/staffs')
def staffs():
    staff_list = db.session.query(Staff).all()
    return render_template('staff.html', staffs=staff_list)


@app.route('/edit/staff/<staff_id>', methods=('GET', 'POST'))
def staff_edit(staff_id):
    staff = db.session.query(Staff).filter_by(id=staff_id).first()
    if request.method == 'POST':
        first_name = request.form['firstname']
        last_name = request.form['lastname']
        division = request.form['division']
        department = request.form['department']
        title = request.form['title']

        db.session.query(Staff).filter(Staff.id == staff_id).update(
            values={Staff.first_name: first_name, Staff.last_name: last_name,
                    Staff.division: division, Staff.department: department,
                    Staff.title: title})
        db.session.commit()
        return redirect(url_for('staffs'))

    return render_template('staff_edit.html', staff=staff)

# Disable Staff Delete function
# @app.route('/delete/staff/<staff_id>', methods=('POST',))
# def staff_delete(staff_id):
#     staffs = Table('staffs', MetaData(bind=engine), autoload=True)
#     db_session.execute(delete(staffs).where(staffs.c.staff_id == staff_id))
#     db_session.commit()
#     flash(f'Staff "{staff_id}" was successfully deleted!', "success")
#     return redirect(url_for('staffs'))

# ACTION ROUTES


@app.route('/checkout', methods=('GET', 'POST'))
def checkout():

    if request.method == 'POST':
        asset_id = request.form['id']
        staff_id = request.form['staffid']
        accessory_id = request.form['accessoryid']
        if not asset_id or not staff_id:
            flash('Staff and or Asset fields are required', "warning")

        if not db.session.query(Asset).filter_by(
                func.lower(id) == asset_id.lower()).scalar():
            flash('Asset does not exist', "warning")
            return render_template('checkout.html')

        if not db.session.query(Staff).filter_by(
                func.lower(id) == staff_id.lower()).scalar():
            flash('Staff does not exist', "warning")
            return render_template('checkout.html')

        if not db.session.query(Asset).filter_by(
                func.lower(id) == accessory_id.lower()
        ).scalar() and accessory_id != '':
            flash('Accessory does not exist', "warning")
            return render_template('checkout.html')

        else:
            try:
                staffer = db.session.query(Staff).filter(
                    func.lower(Staff.id) == staff_id.lower()).first()
                asset = db.session.query(Asset).filter(
                    func.lower(Asset.id) == asset_id.lower()).first()
                app.logger.info(staffer)
                db.session.add(Checkout(
                    assetid=asset, staffid=staff_id,
                    department=staffer.department,
                    timestamp=datetime.now()))
                db.session.query(Asset).filter(
                    Asset.id == asset).update(values={
                        'asset_status': 'checkedout'})

                if accessory_id:
                    accessory = db.session.query(Asset).filter(
                        func.lower(Asset.id) == accessory_id.lower()).first()

                    db.session.add(Checkout(
                        assetid=accessory, staffid=staff_id,
                        department=staffer.department,
                        timestamp=datetime.now()))
                    db.session.query(Asset).filter(func.lower(
                        Asset.id) == accessory_id.lower()).update(values={
                            'asset_status': 'checkedout'})

                db.session.commit()
                flash('Asset was successfully checked out!', "success")
                return redirect(url_for('checkout'))
            except Exception as e:
                app.logger.error(e)
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
            try:
                checkout_info = db.session.query(Checkout).filter(
                    func.lower(Checkout.assetid) == asset_id.lower()).first()
                staffer = db.session.query(Staff).filter(
                    func.lower(Staff.id) == checkout_info.staffid.lower()).first()

                db.session.add(History(
                    assetid=checkout_info.assetid,
                    staffid=checkout_info.staffid,
                    department=staffer.department,
                    division=staffer.division,
                    checkouttime=checkout_info.timestamp,
                    returntime=datetime.now()
                ))
                db.session.query(Checkout).filter(
                    func.lower(Checkout.assetid) == asset_id.lower()).delete()

                db.session.query(Asset).filter(
                    func.lower(Asset.id) == asset_id.lower()).update(values={
                        'asset_status': 'Available'})

                db.session.commit()
                return redirect(url_for('history'))
            except Exception as e:
                app.logger.error(e)
                flash("Return failed", 'warning')
                return redirect(url_for('return_asset'))

    return render_template('return.html')

# READ ROUTES


@ app.route('/history')
def history():
    try:
        history_list = db.session.query(History).all()
        db.session.commit()
    except Exception as e:
        app.logger.error(e)
        flash("History not found", 'warning')
        return redirect(url_for('history'))
    return render_template('history.html', assets=history_list)


@ app.route('/assets')
def assets():
    asset_list = Asset.query.all()
    return render_template('status.html', assets=asset_list)


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
    return render_template(
        'single_history.html', hist_type=rq_type,
        current=current, history=history, item_info=item_info
    )


# IMPORT TASKS
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
        except IntegrityError as e:
            app.logger.error(e)
            flash(
                "Asset upload failed import. This mabe be due to ID conflicts", "danger")
            return redirect(url_for('asset_create'))
    return redirect(url_for('assets'))


def parseCSV_staff(filePath, first_name=False, last_name=False, staff_id=False, division=False, department=False, title=False):
    csvData = pd.read_csv(filePath, header=0, keep_default_na=False)
    for i, row in csvData.iterrows():
        try:
            last_name = row[last_name] if last_name else ""
            division = row[division] if division else ""
            title = row[title] if title else ""

            staff = Staff(id=row[staff_id], first_name=row[first_name], last_name=last_name,
                          division=division, department=row[department], title=title)
            db.session.add(staff)
            db.session.commit()
        except IntegrityError:
            flash(
                "Staff upload failed import. This may be due to ID conflicts.", "danger")
            return redirect(url_for('staff_create'))
    return redirect(url_for('staffs'))


@ app.route('/show_data', methods=["GET", "POST"])
def showData():
    # Retrieving uploaded file path from session
    data_file_path = session.get('uploaded_data_file_path', None)
    print("Data_FIle_Path" + data_file_path)
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
            return redirect(url_for('assets'))
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

            return redirect(url_for('staffs'))


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    form = SettingsForm()
    if form.validate_on_submit():
        tz = GlobalSet.query.filter_by(settingid="timezone").first()
        tz.setting = form.timezone.data
        db.session.commit()
        flash('Your settings have been updated.')
        return redirect(url_for('settings'))
    elif request.method == 'GET':
        form.timezone.data = db.session.query(GlobalSet).filter(
            GlobalSet.settingid == "timezone").first().setting
    return render_template('settings.html', title='Settings', form=form)
