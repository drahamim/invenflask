from flask_wtf import FlaskForm
from wtforms import SelectField
import pytz


class SettingsForm(FlaskForm):
    timezone = SelectField('Timezone', choices=[
                           (tz, tz) for tz in pytz.all_timezones])
