from flask_wtf import FlaskForm
from wtforms import (StringField,
                     SubmitField,)
from wtforms.validators import (DataRequired,
                                Length,)


class SearchForm(FlaskForm):
    search = StringField('', validators=[Length(0, 255), DataRequired() ],render_kw={"placeholder": "Please input school name or address here"})
    lat = StringField('')
    lng = StringField('')

    submit = SubmitField('submit')




