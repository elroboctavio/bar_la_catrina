from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(message="El nombre de usuario es obligatorio.")])
    password = PasswordField('Password', validators=[
        DataRequired(message="La contraseña es obligatoria."),
        Length(min=8, max=20, message="La contraseña debe tener entre 8 y 20 caracteres.")
    ])
    submit = SubmitField('Login')