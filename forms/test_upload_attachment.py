from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import *


class TestUploadAttachmentForm(FlaskForm):
    image = FileField("Выбрать файл", validators=[FileRequired(),
                                                       FileAllowed(['jpg', 'png', 'gif'],
                                                                   "Допускаются форматы .jpg, .png и .gif.")])