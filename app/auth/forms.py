from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo, Email, \
    Regexp, ValidationError
from app.models import User


# -----------------------
# Login
# -----------------------


class LoginForm(FlaskForm):
    """Login Form"""
    username = StringField(
        'Username',
        validators=[DataRequired(), Length(1, 64)],
        render_kw={'autofocus': True, 'placeholder': 'johndoe'})
    password = PasswordField(
        'Password:',
        validators=[DataRequired(), Length(min=8, max=20),
        Regexp(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$',
               message='Password must be at least 8 characters long and '
               'contain at least one letter (Capital) and one number.')],
        render_kw={'placeholder': 'Example: Hard2Gue55'})
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')


# -----------------------
# End of user login
# -----------------------



# -----------------------
# Password reset
# -----------------------



class RequestPasswordResetForm(FlaskForm):
    """User can request for a password reset"""
    email = StringField(
        'Email',
        validators=[DataRequired(), Email()],
        render_kw={'autofocus': True, 'placeholder': 'You have access to this email address'})
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    """User can change their password"""
    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(min=8, max=20),
        Regexp(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$',
               message='Password must be at least 8 characters long and '
               'contain at least one letter and one number.')],
        render_kw={'autofocus':True, 'placeholder': 'Password'})
    confirm_password = PasswordField(
        'Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

# -----------------------
# End of password reset
# -----------------------


# -----------------------
# User registration
# -----------------------


class RegistrationForm(FlaskForm):
    """General User Data"""
    username = StringField(
        'Username',
        validators=[DataRequired(), Length(1, 64)],
        render_kw={'autofocus': True, 'placeholder': 'johndoe'})
    email = StringField(
        'Email',
        validators=[DataRequired(), Email()],
        render_kw={'placeholder': 'johndoe@email.com'})
    password = PasswordField(
        'Password:',
        validators=[DataRequired(), Length(min=8, max=20),
        Regexp(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$',
               message='Password must be at least 8 characters long and '
               'contain at least one letter and one number.')],
        render_kw={'placeholder': 'Example: Hard2Gue55'})
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[DataRequired(), EqualTo('password')],
        render_kw={'placeholder': 'Confirm Your Password Above'})
    submit = SubmitField('Register')

    def validate_username(self, username):
        """Check if username already exists"""
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        """Check if email already exists"""
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class VerifyForm(FlaskForm):
    """Email token verification form"""
    token = StringField(
        'Token',
        validators=[DataRequired()],
        render_kw={'autofocus': True, 'placeholder': 'Enter token sent'})
    submit = SubmitField('Verify')


# -----------------------
# End of user registration
# -----------------------
