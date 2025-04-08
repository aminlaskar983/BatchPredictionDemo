"""
Transcript management routes for the Gemini Batch Prediction web application.
"""
from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
from flask_login import current_user, login_required
from datetime import datetime

from app import db
from models import Transcript
from forms.transcripts import TranscriptForm, VideoURLForm
from video_transcript_extractor import VideoTranscriptExtractor

transcripts_bp = Blueprint('transcripts', __name__)


@transcripts_bp.route('/')
@login_required
def index():
    """Display all user transcripts."""
    transcripts = Transcript.query.filter_by(user_id=current_user.id).order_by(Transcript.created_at.desc()).all()
    return render_template('transcripts/index.html', transcripts=transcripts)


@transcripts_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new transcript."""
    form = TranscriptForm()
    
    if form.validate_on_submit():
        transcript = Transcript(
            title=form.title.data,
            content=form.content.data,
            source_url=form.source_url.data,
            user_id=current_user.id
        )
        db.session.add(transcript)
        db.session.commit()
        
        flash('Transcript created successfully!', 'success')
        return redirect(url_for('transcripts.index'))
        
    return render_template('transcripts/create.html', form=form)


@transcripts_bp.route('/<int:id>')
@login_required
def view(id):
    """View a specific transcript."""
    transcript = Transcript.query.get_or_404(id)
    
    # Ensure the user owns this transcript
    if transcript.user_id != current_user.id:
        abort(403)
        
    return render_template('transcripts/view.html', transcript=transcript)


@transcripts_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edit an existing transcript."""
    transcript = Transcript.query.get_or_404(id)
    
    # Ensure the user owns this transcript
    if transcript.user_id != current_user.id:
        abort(403)
        
    form = TranscriptForm(obj=transcript)
    
    if form.validate_on_submit():
        transcript.title = form.title.data
        transcript.content = form.content.data
        transcript.source_url = form.source_url.data
        db.session.commit()
        
        flash('Transcript updated successfully!', 'success')
        return redirect(url_for('transcripts.view', id=transcript.id))
        
    return render_template('transcripts/edit.html', form=form, transcript=transcript)


@transcripts_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Delete a transcript."""
    transcript = Transcript.query.get_or_404(id)
    
    # Ensure the user owns this transcript
    if transcript.user_id != current_user.id:
        abort(403)
        
    db.session.delete(transcript)
    db.session.commit()
    
    flash('Transcript deleted successfully!', 'success')
    return redirect(url_for('transcripts.index'))


@transcripts_bp.route('/extract-from-video', methods=['GET', 'POST'])
@login_required
def extract_from_video():
    """Extract a transcript from a video URL."""
    form = VideoURLForm()
    
    if form.validate_on_submit():
        video_url = form.video_url.data
        
        # Extract transcript using our VideoTranscriptExtractor
        extractor = VideoTranscriptExtractor()
        result = extractor.extract_transcript(video_url)
        
        if result:
            # Pre-fill a transcript form with the extracted content
            transcript_form = TranscriptForm()
            transcript_form.title.data = result.get('title', 'Extracted Video Transcript')
            transcript_form.content.data = result.get('transcript', '')
            transcript_form.source_url.data = video_url
            
            flash('Transcript successfully extracted!', 'success')
            return render_template(
                'transcripts/create.html', 
                form=transcript_form, 
                video_extraction=True
            )
        else:
            flash('Failed to extract transcript from the provided video URL. Please check the URL and try again, or enter the transcript manually.', 'danger')
    
    return render_template('transcripts/extract_from_video.html', form=form)