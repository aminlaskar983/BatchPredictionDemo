import os

# Create about.html
with open('templates/about.html', 'w') as f:
    f.write('''{% extends "base.html" %}

{% block title %}About{% endblock %}

{% block content %}
<div class="container mt-4">
    <h1>About Gemini Batch Prediction</h1>
    
    <div class="card mb-4">
        <div class="card-body">
            <h5 class="card-title">Project Overview</h5>
            <p class="card-text">
                Gemini Batch Prediction is a demonstration project showcasing the capabilities of 
                Google\'s Gemini API for processing video transcripts and efficiently answering 
                multiple questions in a batch. This application highlights advanced techniques for 
                handling long context and optimizing API usage through context caching.
            </p>
        </div>
    </div>
    
    <div class="row">
        <div class="col-md-6 mb-4">
            <div class="card h-100">
                <div class="card-body">
                    <h5 class="card-title">Key Features</h5>
                    <ul>
                        <li>Batch processing of questions about video content</li>
                        <li>Efficient handling of long-form content (transcripts)</li>
                        <li>Context caching to optimize API usage</li>
                        <li>User management with secure authentication</li>
                        <li>Transcript management and organization</li>
                        <li>Question set creation and processing</li>
                    </ul>
                </div>
            </div>
        </div>
        
        <div class="col-md-6 mb-4">
            <div class="card h-100">
                <div class="card-body">
                    <h5 class="card-title">Technologies Used</h5>
                    <ul>
                        <li>Google Generative AI (Gemini API)</li>
                        <li>Flask Web Framework</li>
                        <li>SQLAlchemy ORM</li>
                        <li>PostgreSQL Database</li>
                        <li>Asynchronous Processing</li>
                        <li>Bootstrap CSS Framework</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
    
    <div class="card">
        <div class="card-body">
            <h5 class="card-title">Getting Started</h5>
            <p class="card-text">
                To get started with Gemini Batch Prediction:
            </p>
            <ol>
                <li>Create an account or log in</li>
                <li>Create a new transcript from a video source</li>
                <li>Create a question set for your transcript</li>
                <li>Add questions about the video content</li>
                <li>Process the questions to get AI-generated answers</li>
            </ol>
            
            <div class="mt-3">
                <a href="{{ url_for(\'auth.register\') }}" class="btn btn-primary">Register Now</a>
                <a href="{{ url_for(\'auth.login\') }}" class="btn btn-secondary">Login</a>
            </div>
        </div>
    </div>
</div>
{% endblock %}''')

print("About template created successfully!")