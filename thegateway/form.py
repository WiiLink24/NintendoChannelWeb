from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired
from wtforms import (
    StringField,
    SubmitField,
    FileField,
    SelectField,
)
from wtforms.validators import DataRequired, Length
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


class VideoForm(FlaskForm):
    video = FileField("Video")
    title_jpn = StringField(
        "Title (Japanese)", validators=[DataRequired(), Length(max=102)]
    )
    title_en = StringField(
        "Title (English)", validators=[DataRequired(), Length(max=102)]
    )
    title_de = StringField(
        "Title (German)", validators=[DataRequired(), Length(max=102)]
    )
    title_es = StringField(
        "Title (Spanish)", validators=[DataRequired(), Length(max=102)]
    )
    title_fr = StringField(
        "Title (French)", validators=[DataRequired(), Length(max=102)]
    )
    title_it = StringField(
        "Title (Italian)", validators=[DataRequired(), Length(max=102)]
    )
    title_dutch = StringField(
        "Title (Dutch)", validators=[DataRequired(), Length(max=102)]
    )
    video_type = SelectField("Video Type", choices=VideoType.choices())
    thumbnail = FileField("Video thumbnail")
    upload = SubmitField("Add Video")


class BannerForm(FlaskForm):
    title_jpn = StringField(
        "Title (Japanese)", validators=[DataRequired(), Length(max=102)]
    )
    title_en = StringField(
        "Title (English)", validators=[DataRequired(), Length(max=102)]
    )
    title_de = StringField(
        "Title (German)", validators=[DataRequired(), Length(max=102)]
    )
    title_es = StringField(
        "Title (Spanish)", validators=[DataRequired(), Length(max=102)]
    )
    title_fr = StringField(
        "Title (French)", validators=[DataRequired(), Length(max=102)]
    )
    title_it = StringField(
        "Title (Italian)", validators=[DataRequired(), Length(max=102)]
    )
    title_dutch = StringField(
        "Title (Dutch)", validators=[DataRequired(), Length(max=102)]
    )
    thumbnail = FileField("Image", validators=[FileRequired()])
    upload = SubmitField("Add")


class DeleteForm(FlaskForm):
    given_id = StringField("ID", validators=[DataRequired()])
    submit = SubmitField("Delete")
