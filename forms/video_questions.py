"""
Forms for directly asking questions about videos.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, URL, Optional


class VideoQuestionForm(FlaskForm):
    """Form for submitting a video URL and questions to ask about it."""
    video_url = StringField('Video URL', validators=[
        DataRequired(), 
        URL(message="Please enter a valid URL"),
        Length(min=10, max=500)
    ])
    questions = TextAreaField('Questions', validators=[
        DataRequired(),
        Length(min=5, max=5000, message="Questions must be between 5 and 5000 characters")
    ])
    submit = SubmitField('Get Answers')