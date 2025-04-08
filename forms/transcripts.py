"""
Transcript forms for the Gemini Batch Prediction web application.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, URL, Optional


class TranscriptForm(FlaskForm):
    """Form for creating or updating a transcript."""
    title = StringField('Title', validators=[DataRequired(), Length(min=3, max=200)])
    content = TextAreaField('Transcript Content', validators=[DataRequired()])
    source_url = StringField('Source URL', validators=[Optional(), URL()])
    submit = SubmitField('Save Transcript')


class VideoURLForm(FlaskForm):
    """Form for submitting a video URL to extract transcript."""
    video_url = StringField('Video URL', validators=[
        DataRequired(), 
        URL(message="Please enter a valid URL"),
        Length(min=10, max=500)
    ])
    submit = SubmitField('Extract Transcript')