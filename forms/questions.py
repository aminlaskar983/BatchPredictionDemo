"""
Question forms for the Gemini Batch Prediction web application.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length


class QuestionSetForm(FlaskForm):
    """Form for creating question sets."""
    name = StringField('Set Name', validators=[DataRequired(), Length(max=200)])
    submit = SubmitField('Create Question Set')


class QuestionForm(FlaskForm):
    """Form for creating questions."""
    content = TextAreaField('Question', validators=[DataRequired()])
    submit = SubmitField('Add Question')