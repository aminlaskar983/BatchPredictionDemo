"""
Routes for directly processing questions about videos.
"""

import asyncio
import logging
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import current_user, login_required

from app import db
from models import Transcript, QuestionSet, Question
from forms.video_questions import VideoQuestionForm
from video_transcript_extractor import VideoTranscriptExtractor
from batch_predictor import BatchPredictor
from context_cache import ContextCache
from transcript_handler import TranscriptHandler
from output_formatter import OutputFormatter
import os

# Set up logging
logger = logging.getLogger(__name__)

video_questions_bp = Blueprint('video_questions', __name__, url_prefix='/video-questions')


@video_questions_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    """Form for submitting video URL and questions."""
    form = VideoQuestionForm()
    
    if form.validate_on_submit():
        video_url = form.video_url.data
        questions_text = form.questions.data
        
        # Split questions into a list (one per line)
        questions_list = [q.strip() for q in questions_text.split('\n') if q.strip()]
        
        if not questions_list:
            flash('Please enter at least one question', 'danger')
            return render_template('video_questions/index.html', form=form)
        
        # Extract transcript from the video
        extractor = VideoTranscriptExtractor()
        result = extractor.extract_transcript(video_url)
        
        if not result:
            flash('Failed to extract transcript from the provided video URL. Please check the URL and try again.', 'danger')
            return render_template('video_questions/index.html', form=form)
        
        # Save the transcript to the database
        transcript_title = result.get('title', 'YouTube Video Transcript')
        transcript_content = result.get('transcript', '')
        
        transcript = Transcript(
            title=transcript_title,
            content=transcript_content,
            source_url=video_url,
            user_id=current_user.id
        )
        db.session.add(transcript)
        db.session.commit()
        
        # Create a question set
        question_set = QuestionSet(
            name=f"Questions for {transcript_title}",
            user_id=current_user.id,
            transcript_id=transcript.id
        )
        db.session.add(question_set)
        db.session.commit()
        
        # Store the question set ID in the session
        session['question_set_id'] = question_set.id
        session['questions_list'] = questions_list
        
        # Create empty question records for all questions
        for question_text in questions_list:
            question = Question(
                content=question_text,
                question_set_id=question_set.id
            )
            db.session.add(question)
        
        db.session.commit()
        
        # Redirect to processing page
        return redirect(url_for('video_questions.process'))
    
    return render_template('video_questions/index.html', form=form)


@video_questions_bp.route('/process')
@login_required
def process():
    """Process and answer questions about the video."""
    # Get data from session
    question_set_id = session.get('question_set_id')
    questions_list = session.get('questions_list')
    
    if not question_set_id or not questions_list:
        flash('No questions to process. Please submit questions first.', 'danger')
        return redirect(url_for('video_questions.index'))
    
    # Get the question set and transcript from the database
    question_set = QuestionSet.query.get_or_404(question_set_id)
    transcript = Transcript.query.get_or_404(question_set.transcript_id)
    
    # Ensure the user owns this question set
    if question_set.user_id != current_user.id:
        flash('Access denied', 'danger')
        return redirect(url_for('video_questions.index'))
    
    # Get the questions objects from the database
    questions = question_set.questions.all()
    
    # First, show the processing page
    if request.args.get('start') != 'true':
        redirect_url = url_for('video_questions.process', start='true')
        return render_template('video_questions/processing.html', 
                               questions=questions_list,
                               redirect_url=redirect_url)
    
    # Process the questions asynchronously
    try:
        # Set up the batch predictor
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            flash('Gemini API key not found. Please contact the administrator.', 'danger')
            return redirect(url_for('video_questions.index'))
        
        # Create required components
        cache = ContextCache(max_size=200, ttl=7200)
        transcript_handler = TranscriptHandler()
        batch_predictor = BatchPredictor(api_key, cache, transcript_handler)
        
        # Run the batch processing
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(
            batch_predictor.process_batch(questions_list, transcript.content)
        )
        loop.close()
        
        # Save results to the database
        for i, (question_obj, result) in enumerate(zip(questions, results)):
            question_obj.answer = result.get('answer', 'No answer generated')
            question_obj.context_used = result.get('context_used', '')
            question_obj.response_metadata = result.get('response_metadata', {})
            question_obj.processed_at = db.func.now()
            
            # Extract timestamp if available
            if result.get('timestamp'):
                question_obj.timestamp = result.get('timestamp')
        
        db.session.commit()
        
        # Redirect to results page
        return redirect(url_for('video_questions.results', id=question_set.id))
        
    except Exception as e:
        logger.error(f"Error processing video questions: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        flash(f'Error processing questions: {str(e)}', 'danger')
        return redirect(url_for('video_questions.index'))


@video_questions_bp.route('/results/<int:id>')
@login_required
def results(id):
    """Display the results of the question processing."""
    question_set = QuestionSet.query.get_or_404(id)
    transcript = Transcript.query.get_or_404(question_set.transcript_id)
    
    # Ensure the user owns this question set
    if question_set.user_id != current_user.id:
        flash('Access denied', 'danger')
        return redirect(url_for('question_sets.index'))
    
    # Format the results for display
    questions = question_set.questions.all()
    
    # Clear the session data
    if 'question_set_id' in session:
        del session['question_set_id']
    if 'questions_list' in session:
        del session['questions_list']
    
    return render_template(
        'video_questions/results.html', 
        question_set=question_set,
        transcript=transcript,
        questions=questions
    )