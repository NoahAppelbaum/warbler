from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import InputRequired, Email, Length, URL, Optional


class MessageForm(FlaskForm):
    """Form for adding/editing messages."""

    text = TextAreaField('text', validators=[InputRequired(),Length(max=140)])


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField(
        'Username',
        validators=[InputRequired(), Length(max=30)],
    )

    email = StringField(
        'E-mail',
        validators=[InputRequired(), Email(), Length(max=50)],
    )

    password = PasswordField(
        'Password',
        validators=[InputRequired(), Length(min=6, max=50)],
    )

    image_url = StringField(
        '(Optional) Image URL',
        validators=[Optional(), URL(), Length(max=255)]
    )

class UserEditForm(FlaskForm):
    """Form for editing user information."""

    username = StringField(
        'Username',
        validators=[Optional(), Length(max=30)],
    )

    email = StringField(
        'E-mail',
        validators=[Optional(), Email(), Length(max=50)],
    )


    image_url = StringField(
        'Image URL',
        validators=[Optional(), URL(), Length(max=255)]
    )

    header_image_url = StringField(
        'Header Image URL',
        validators=[Optional(), URL(), Length(max=255)]
    )

    location = StringField(
        'Location',
        validators=[Optional(), Length(max=30)],
    )

    bio = TextAreaField(
        'Bio',
        validators=[Optional()]

    )

    password = PasswordField(
        'Password',
        validators=[InputRequired(), Length(min=6, max=50)],
    )



class LoginForm(FlaskForm):
    """Login form."""

    username = StringField(
        'Username',
        validators=[InputRequired(), Length(max=30)],
    )

    password = PasswordField(
        'Password',
        validators=[InputRequired(), Length(min=6, max=50)],
    )

class CSRFForm(FlaskForm):
    """Secure Form for CSRF protection"""
