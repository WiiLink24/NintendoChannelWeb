from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired
from wtforms import (
    StringField,
    SubmitField,
    PasswordField,
    FileField,
    SelectField,
    TextAreaField,
    BooleanField,
    IntegerField,
)
from wtforms.validators import DataRequired, Length, ValidationError
import enum


class VideoType(enum.Enum):
    Nil = 0
    Wii = 1
    WiiWare = 2
    WiiVirtualConsole = 3
    DS = 4
    DSi = 5
    DSiWare = 6
    Message = 7
    ThreeDS = 8
    ThreeDSVirtualConsole = 10

    @classmethod
    def choices(cls):
        return [(choice.value, choice.name) for choice in cls]

class LoginForm(FlaskForm):
    username = StringField("Username")
    password = PasswordField("Password")
    submit = SubmitField("Enter the gateway")


class NewUserForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password1 = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField("Confirm Password", validators=[DataRequired()])
    upload = SubmitField("Complete")

    def validate_password1(self, _):
        if self.password1.data != self.password2.data:
            return ValidationError("New passwords must be the same")


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField("Password", validators=[DataRequired()])
    new_password = PasswordField("New Password", validators=[DataRequired()])
    new_password_confirmation = PasswordField(
        "Confirm New Password", validators=[DataRequired()]
    )
    complete = SubmitField("Complete")

    def validate_current_password(self, _):
        if self.current_password.data == self.new_password.data:
            return ValidationError("New password cannot be the same as current!")

    def validate_new_password(self, _):
        if self.new_password.data != self.new_password_confirmation.data:
            return ValidationError("New passwords must be the same")


class VideoForm(FlaskForm):
    video = FileField("Video", validators=[FileRequired()])
    title_jpn = StringField("Title (Japanese)", validators=[DataRequired(), Length(max=102)])
    title_en = StringField("Title (English)", validators=[DataRequired(), Length(max=102)])
    title_de = StringField("Title (German)", validators=[DataRequired(), Length(max=102)])
    title_es = StringField("Title (Spanish)", validators=[DataRequired(), Length(max=102)])
    title_fr = StringField("Title (French)", validators=[DataRequired(), Length(max=102)])
    title_it = StringField("Title (Italian)", validators=[DataRequired(), Length(max=102)])
    title_dutch = StringField("Title (Dutch)", validators=[DataRequired(), Length(max=102)])
    video_type = SelectField("Video Type", choices=VideoType.choices())
    thumbnail = FileField("Video thumbnail", validators=[FileRequired()])
    upload = SubmitField("Add Video")
