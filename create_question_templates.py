import os

# Create templates directory if it doesn't exist
if not os.path.exists('templates/questions'):
    os.makedirs('templates/questions')

# Create sets.html
with open('templates/questions/sets.html', 'w') as f:
    f.write('''{% extends "base.html" %}

{% block title %}My Question Sets{% endblock %}

{% block content %}
<div class="container mt-4">
    <h1>My Question Sets</h1>
    
    <div class="mb-4">
        <a href="{{ url_for('main.dashboard') }}" class="btn btn-secondary">Back to Dashboard</a>
    </div>
    
    {% if question_sets %}
        <div class="row">
            {% for set in question_sets %}
                <div class="col-md-6 mb-4">
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title">{{ set.name }}</h5>
                            <p class="card-text">
                                <small class="text-muted">
                                    Created: {{ set.created_at.strftime('%Y-%m-%d %H:%M') }}
                                </small>
                            </p>
                            <p class="card-text">
                                <strong>Transcript:</strong> {{ set.transcript.title }}
                            </p>
                            <p class="card-text">
                                <strong>Questions:</strong> {{ set.questions.count() }}
                            </p>
                            <a href="{{ url_for('questions.view_set', id=set.id) }}" class="btn btn-primary">View Questions</a>
                        </div>
                    </div>
                </div>
            {% endfor %}
        </div>
    {% else %}
        <div class="alert alert-info">
            You don't have any question sets yet. Create one by going to a transcript and clicking "Create Question Set".
        </div>
        <a href="{{ url_for('transcripts.index') }}" class="btn btn-primary">View Transcripts</a>
    {% endif %}
</div>
{% endblock %}''')

# Create create_set.html
with open('templates/questions/create_set.html', 'w') as f:
    f.write('''{% extends "base.html" %}

{% block title %}Create Question Set{% endblock %}

{% block content %}
<div class="container mt-4">
    <h1>Create Question Set</h1>
    
    <div class="mb-4">
        <a href="{{ url_for('transcripts.view', id=transcript.id) }}" class="btn btn-secondary">Back to Transcript</a>
    </div>
    
    <div class="card mb-4">
        <div class="card-header">
            <h5>Transcript Information</h5>
        </div>
        <div class="card-body">
            <h6>{{ transcript.title }}</h6>
            <p><small class="text-muted">Created: {{ transcript.created_at.strftime('%Y-%m-%d %H:%M') }}</small></p>
        </div>
    </div>
    
    <div class="card">
        <div class="card-header">
            <h5>New Question Set</h5>
        </div>
        <div class="card-body">
            <form method="POST">
                {{ form.hidden_tag() }}
                
                <div class="mb-3">
                    {{ form.name.label(class="form-label") }}
                    {{ form.name(class="form-control") }}
                    {% for error in form.name.errors %}
                        <div class="text-danger">{{ error }}</div>
                    {% endfor %}
                </div>
                
                {{ form.submit(class="btn btn-primary") }}
            </form>
        </div>
    </div>
</div>
{% endblock %}''')

# Create view_set.html
with open('templates/questions/view_set.html', 'w') as f:
    f.write('''{% extends "base.html" %}

{% block title %}{{ question_set.name }}{% endblock %}

{% block content %}
<div class="container mt-4">
    <h1>{{ question_set.name }}</h1>
    
    <div class="mb-4">
        <a href="{{ url_for('questions.sets') }}" class="btn btn-secondary">Back to Question Sets</a>
        <a href="{{ url_for('questions.add_question', id=question_set.id) }}" class="btn btn-primary">Add Question</a>
        {% if questions %}
            <form method="POST" action="{{ url_for('questions.process_questions', id=question_set.id) }}" class="d-inline">
                <button type="submit" class="btn btn-success">Process Questions</button>
            </form>
        {% endif %}
    </div>
    
    <div class="card mb-4">
        <div class="card-header">
            <h5>Transcript Information</h5>
        </div>
        <div class="card-body">
            <h6>{{ question_set.transcript.title }}</h6>
            <p><small class="text-muted">Created: {{ question_set.transcript.created_at.strftime('%Y-%m-%d %H:%M') }}</small></p>
            <a href="{{ url_for('transcripts.view', id=question_set.transcript.id) }}" class="btn btn-outline-primary btn-sm">View Transcript</a>
        </div>
    </div>
    
    {% if questions %}
        <h3>Questions</h3>
        
        {% for question in questions %}
            <div class="card mb-3">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <h5 class="mb-0">Question</h5>
                    <form method="POST" action="{{ url_for('questions.delete_question', id=question.id) }}" onsubmit="return confirm('Are you sure you want to delete this question?');">
                        <button type="submit" class="btn btn-danger btn-sm">Delete</button>
                    </form>
                </div>
                <div class="card-body">
                    <p>{{ question.content }}</p>
                    
                    {% if question.answer %}
                        <hr>
                        <h6>Answer:</h6>
                        <p>{{ question.answer }}</p>
                        
                        {% if question.processed_at %}
                            <small class="text-muted">Processed: {{ question.processed_at.strftime('%Y-%m-%d %H:%M') }}</small>
                        {% endif %}
                        
                        {% if question.response_metadata %}
                            <div class="mt-3">
                                <button class="btn btn-sm btn-outline-secondary" type="button" data-bs-toggle="collapse" data-bs-target="#metadata-{{ question.id }}">
                                    Show Advanced Info
                                </button>
                                <div class="collapse mt-2" id="metadata-{{ question.id }}">
                                    <div class="card card-body">
                                        <h6>Context Used:</h6>
                                        <pre class="small">{{ question.context_used[:500] }}{% if question.context_used and question.context_used|length > 500 %}...{% endif %}</pre>
                                        
                                        <h6>Metadata:</h6>
                                        <pre class="small">{{ question.response_metadata|tojson(indent=2) }}</pre>
                                    </div>
                                </div>
                            </div>
                        {% endif %}
                    {% else %}
                        <div class="alert alert-info">
                            This question has not been processed yet. Click "Process Questions" to generate answers.
                        </div>
                    {% endif %}
                </div>
            </div>
        {% endfor %}
    {% else %}
        <div class="alert alert-info">
            You don't have any questions in this set yet. Click "Add Question" to add your first question.
        </div>
    {% endif %}
</div>
{% endblock %}''')

# Create add_question.html
with open('templates/questions/add_question.html', 'w') as f:
    f.write('''{% extends "base.html" %}

{% block title %}Add Question{% endblock %}

{% block content %}
<div class="container mt-4">
    <h1>Add Question</h1>
    
    <div class="mb-4">
        <a href="{{ url_for('questions.view_set', id=question_set.id) }}" class="btn btn-secondary">Back to Question Set</a>
    </div>
    
    <div class="card mb-4">
        <div class="card-header">
            <h5>Question Set Information</h5>
        </div>
        <div class="card-body">
            <h6>{{ question_set.name }}</h6>
            <p><strong>Transcript:</strong> {{ question_set.transcript.title }}</p>
        </div>
    </div>
    
    <div class="card">
        <div class="card-header">
            <h5>New Question</h5>
        </div>
        <div class="card-body">
            <form method="POST">
                {{ form.hidden_tag() }}
                
                <div class="mb-3">
                    {{ form.content.label(class="form-label") }}
                    {{ form.content(class="form-control", rows=3) }}
                    {% for error in form.content.errors %}
                        <div class="text-danger">{{ error }}</div>
                    {% endfor %}
                    <div class="form-text">Enter a question about the transcript content.</div>
                </div>
                
                {{ form.submit(class="btn btn-primary") }}
            </form>
        </div>
    </div>
</div>
{% endblock %}''')

print("Question templates created successfully!")