from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from wtforms.validators import DataRequired


class MessageForm(FlaskForm):
    message_text = TextAreaField('Message text', validators=[DataRequired()])
    submit = SubmitField('Send')
