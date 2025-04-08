"""
Question management routes for the Gemini Batch Prediction web application.
"""
import os
import asyncio
import logging
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash, abort, jsonify
from flask_login import current_user, login_required

from app import db
from models import Transcript, QuestionSet, Question
from forms.questions import QuestionSetForm, QuestionForm
from batch_predictor import BatchPredictor
from context_cache import ContextCache
from transcript_handler import TranscriptHandler
from output_formatter import OutputFormatter

questions_bp = Blueprint('questions', __name__)


def get_gemini_api_key():
    """Get the Gemini API key from environment variables."""
    return os.environ.get('GEMINI_API_KEY')


@questions_bp.route('/sets')
@login_required
def sets():
    """Display all user question sets."""
    question_sets = QuestionSet.query.filter_by(user_id=current_user.id).order_by(QuestionSet.created_at.desc()).all()
    return render_template('questions/sets.html', question_sets=question_sets)


@questions_bp.route('/sets/create/<int:transcript_id>', methods=['GET', 'POST'])
@login_required
def create_set(transcript_id):
    """Create a new question set for a transcript."""
    transcript = Transcript.query.get_or_404(transcript_id)
    
    # Ensure the user owns this transcript
    if transcript.user_id != current_user.id:
        abort(403)
        
    form = QuestionSetForm()
    
    if form.validate_on_submit():
        question_set = QuestionSet(
            name=form.name.data,
            user_id=current_user.id,
            transcript_id=transcript.id
        )
        db.session.add(question_set)
        db.session.commit()
        
        flash('Question set created successfully!', 'success')
        return redirect(url_for('questions.view_set', id=question_set.id))
        
    return render_template('questions/create_set.html', form=form, transcript=transcript)


@questions_bp.route('/sets/<int:id>')
@login_required
def view_set(id):
    """View a specific question set."""
    question_set = QuestionSet.query.get_or_404(id)
    
    # Ensure the user owns this question set
    if question_set.user_id != current_user.id:
        abort(403)
        
    questions = Question.query.filter_by(question_set_id=question_set.id).all()
    
    return render_template('questions/view_set.html', question_set=question_set, questions=questions)


@questions_bp.route('/sets/<int:id>/add', methods=['GET', 'POST'])
@login_required
def add_question(id):
    """Add a question to a question set."""
    question_set = QuestionSet.query.get_or_404(id)
    
    # Ensure the user owns this question set
    if question_set.user_id != current_user.id:
        abort(403)
        
    form = QuestionForm()
    
    if form.validate_on_submit():
        question = Question(
            content=form.content.data,
            question_set_id=question_set.id
        )
        db.session.add(question)
        db.session.commit()
        
        flash('Question added successfully!', 'success')
        return redirect(url_for('questions.view_set', id=question_set.id))
        
    return render_template('questions/add_question.html', form=form, question_set=question_set)


@questions_bp.route('/sets/<int:id>/process', methods=['POST'])
@login_required
def process_questions(id):
    """Process all unanswered questions in a question set."""
    question_set = QuestionSet.query.get_or_404(id)
    
    # Ensure the user owns this question set
    if question_set.user_id != current_user.id:
        abort(403)
        
    # Get API key
    api_key = get_gemini_api_key()
    if not api_key:
        flash('Gemini API key not found. Please contact the administrator.', 'error')
        return redirect(url_for('questions.view_set', id=id))
        
    # Get transcript
    transcript = question_set.transcript
    
    # Get unanswered questions
    unanswered_questions = Question.query.filter_by(
        question_set_id=id, 
        answer=None
    ).all()
    
    if not unanswered_questions:
        flash('No unanswered questions found.', 'info')
        return redirect(url_for('questions.view_set', id=id))
    
    # Process questions asynchronously in the background task
    # This is a simplified version; in production, you'd use Celery or similar
    async def process_questions_async():
        # Initialize components
        cache = ContextCache()
        transcript_handler = TranscriptHandler()
        batch_predictor = BatchPredictor(api_key, cache, transcript_handler)
        
        # Process transcript
        processed_transcript = transcript_handler.process_transcript(transcript.content)
        
        # Get questions as strings
        question_contents = [q.content for q in unanswered_questions]
        
        # Define a progress callback function
        def progress_callback(current=None, total=None):
            if current is not None and total is not None:
                print(f"Processing question {current} of {total}")
        
        # Process batch
        try:
            results = await batch_predictor.process_batch(
                question_contents,
                processed_transcript,
                progress_callback
            )
            
            # Update questions with answers
            for i, question in enumerate(unanswered_questions):
                if i < len(results):
                    result = results[i]
                    question.answer = result.get('answer', 'No answer generated')
                    question.context_used = result.get('context_used', '')
                    # Use response_metadata instead of metadata to match the model field name
                    question.response_metadata = {}  # Initialize empty dict
                    if 'metadata' in result:
                        question.response_metadata = result.get('metadata', {})
                    question.processed_at = datetime.utcnow()
            
            db.session.commit()
            return True
        except Exception as e:
            print(f"Error processing questions: {str(e)}")
            logging.error(f"Error processing questions: {str(e)}")
            return False
    
    # Start processing (this would be a background task in production)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    success = loop.run_until_complete(process_questions_async())
    
    if success:
        flash('Questions processed successfully!', 'success')
    else:
        flash('Error processing questions. Please try again.', 'error')
        
    return redirect(url_for('questions.view_set', id=id))


@questions_bp.route('/questions/<int:id>/delete', methods=['POST'])
@login_required
def delete_question(id):
    """Delete a question."""
    question = Question.query.get_or_404(id)
    question_set_id = question.question_set_id
    
    # Ensure the user owns this question (via the question set)
    if question.question_set.user_id != current_user.id:
        abort(403)
        
    db.session.delete(question)
    db.session.commit()
    
    flash('Question deleted successfully!', 'success')
    return redirect(url_for('questions.view_set', id=question_set_id))