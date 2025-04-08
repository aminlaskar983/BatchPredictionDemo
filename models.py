"""
Database models for the Gemini Batch Prediction web application.
"""
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON

from app import db


class User(UserMixin, db.Model):
    """User model for authentication."""
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    transcripts = db.relationship('Transcript', backref='user', lazy='dynamic')
    question_sets = db.relationship('QuestionSet', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        """Set password hash."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against stored hash."""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Transcript(db.Model):
    """Transcript model for storing video transcripts."""
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    source_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    question_sets = db.relationship('QuestionSet', backref='transcript', lazy='dynamic')
    
    def __repr__(self):
        return f'<Transcript {self.title}>'


class QuestionSet(db.Model):
    """Question set model for storing groups of questions about a transcript."""
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    transcript_id = db.Column(db.Integer, db.ForeignKey('transcript.id'), nullable=False)
    
    # Relationships
    questions = db.relationship('Question', backref='question_set', lazy='dynamic')
    
    def __repr__(self):
        return f'<QuestionSet {self.name}>'


class Question(db.Model):
    """Question model for storing individual questions and their answers."""
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text)
    context_used = db.Column(db.Text)
    timestamp = db.Column(db.String(50))  # Video timestamp if available
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)
    response_metadata = db.Column(JSON)
    question_set_id = db.Column(db.Integer, db.ForeignKey('question_set.id'), nullable=False)
    
    def __repr__(self):
        return f'<Question {self.content[:30]}...>'