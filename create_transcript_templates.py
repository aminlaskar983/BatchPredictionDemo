import os

# Create templates directory if it doesn't exist
if not os.path.exists('templates/transcripts'):
    os.makedirs('templates/transcripts')

# Create index.html
with open('templates/transcripts/index.html', 'w') as f:
    f.write('''{% extends "base.html" %}

{% block title %}My Transcripts{% endblock %}

{% block content %}
<div class="container mt-4">
    <h1>My Transcripts</h1>
    
    <div class="mb-4">
        <a href="{{ url_for('main.dashboard') }}" class="btn btn-secondary">Back to Dashboard</a>
        <a href="{{ url_for('transcripts.create') }}" class="btn btn-primary">Create New Transcript</a>
    </div>
    
    {% if transcripts %}
        <div class="row">
            {% for transcript in transcripts %}
                <div class="col-md-6 mb-4">
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title">{{ transcript.title }}</h5>
                            <p class="card-text">
                                <small class="text-muted">
                                    Created: {{ transcript.created_at.strftime('%Y-%m-%d %H:%M') }}
                                </small>
                            </p>
                            <p class="card-text">
                                {% if transcript.source_url %}
                                    <a href="{{ transcript.source_url }}" target="_blank" class="text-decoration-none">Source</a>
                                {% endif %}
                            </p>
                            <div class="d-flex gap-2">
                                <a href="{{ url_for('transcripts.view', id=transcript.id) }}" class="btn btn-primary">View</a>
                                <a href="{{ url_for('transcripts.edit', id=transcript.id) }}" class="btn btn-secondary">Edit</a>
                                <form method="POST" action="{{ url_for('transcripts.delete', id=transcript.id) }}" onsubmit="return confirm('Are you sure you want to delete this transcript?');">
                                    <button type="submit" class="btn btn-danger">Delete</button>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            {% endfor %}
        </div>
    {% else %}
        <div class="alert alert-info">
            You don't have any transcripts yet. Create your first transcript to get started.
        </div>
    {% endif %}
</div>
{% endblock %}''')

# Create create.html
with open('templates/transcripts/create.html', 'w') as f:
    f.write('''{% extends "base.html" %}

{% block title %}Create Transcript{% endblock %}

{% block content %}
<div class="container mt-4">
    <h1>Create Transcript</h1>
    
    <div class="mb-4">
        <a href="{{ url_for('transcripts.index') }}" class="btn btn-secondary">Back to Transcripts</a>
    </div>
    
    <div class="card">
        <div class="card-header">
            <h5>New Transcript</h5>
        </div>
        <div class="card-body">
            <form method="POST">
                {{ form.hidden_tag() }}
                
                <div class="mb-3">
                    {{ form.title.label(class="form-label") }}
                    {{ form.title(class="form-control") }}
                    {% for error in form.title.errors %}
                        <div class="text-danger">{{ error }}</div>
                    {% endfor %}
                </div>
                
                <div class="mb-3">
                    {{ form.source_url.label(class="form-label") }}
                    {{ form.source_url(class="form-control") }}
                    {% for error in form.source_url.errors %}
                        <div class="text-danger">{{ error }}</div>
                    {% endfor %}
                    <div class="form-text">Optional: URL to the source video</div>
                </div>
                
                <div class="mb-3">
                    {{ form.content.label(class="form-label") }}
                    {{ form.content(class="form-control", rows=15) }}
                    {% for error in form.content.errors %}
                        <div class="text-danger">{{ error }}</div>
                    {% endfor %}
                    <div class="form-text">Paste the full transcript of the video here</div>
                </div>
                
                {{ form.submit(class="btn btn-primary") }}
            </form>
        </div>
    </div>
</div>
{% endblock %}''')

# Create view.html
with open('templates/transcripts/view.html', 'w') as f:
    f.write('''{% extends "base.html" %}

{% block title %}{{ transcript.title }}{% endblock %}

{% block content %}
<div class="container mt-4">
    <h1>{{ transcript.title }}</h1>
    
    <div class="mb-4">
        <a href="{{ url_for('transcripts.index') }}" class="btn btn-secondary">Back to Transcripts</a>
        <a href="{{ url_for('transcripts.edit', id=transcript.id) }}" class="btn btn-primary">Edit</a>
        <a href="{{ url_for('questions.create_set', transcript_id=transcript.id) }}" class="btn btn-success">Create Question Set</a>
    </div>
    
    {% if transcript.source_url %}
        <div class="mb-3">
            <strong>Source:</strong> <a href="{{ transcript.source_url }}" target="_blank">{{ transcript.source_url }}</a>
        </div>
    {% endif %}
    
    <div class="mb-3">
        <small class="text-muted">Created: {{ transcript.created_at.strftime('%Y-%m-%d %H:%M') }}</small>
    </div>
    
    {% if transcript.question_sets.count() > 0 %}
        <div class="card mb-4">
            <div class="card-header">
                <h5>Question Sets</h5>
            </div>
            <div class="card-body">
                <div class="list-group">
                    {% for set in transcript.question_sets %}
                        <a href="{{ url_for('questions.view_set', id=set.id) }}" class="list-group-item list-group-item-action d-flex justify-content-between align-items-center">
                            {{ set.name }}
                            <span class="badge bg-primary rounded-pill">{{ set.questions.count() }} questions</span>
                        </a>
                    {% endfor %}
                </div>
            </div>
        </div>
    {% endif %}
    
    <div class="card">
        <div class="card-header">
            <h5>Transcript Content</h5>
        </div>
        <div class="card-body">
            <pre class="transcript-content">{{ transcript.content }}</pre>
        </div>
    </div>
</div>

<style>
    .transcript-content {
        white-space: pre-wrap;
        font-family: inherit;
        font-size: 1rem;
        background-color: transparent;
        border: none;
        padding: 0;
        margin: 0;
    }
</style>
{% endblock %}''')

# Create edit.html
with open('templates/transcripts/edit.html', 'w') as f:
    f.write('''{% extends "base.html" %}

{% block title %}Edit Transcript{% endblock %}

{% block content %}
<div class="container mt-4">
    <h1>Edit Transcript</h1>
    
    <div class="mb-4">
        <a href="{{ url_for('transcripts.view', id=transcript.id) }}" class="btn btn-secondary">Back to Transcript</a>
    </div>
    
    <div class="card">
        <div class="card-header">
            <h5>Edit Transcript</h5>
        </div>
        <div class="card-body">
            <form method="POST">
                {{ form.hidden_tag() }}
                
                <div class="mb-3">
                    {{ form.title.label(class="form-label") }}
                    {{ form.title(class="form-control") }}
                    {% for error in form.title.errors %}
                        <div class="text-danger">{{ error }}</div>
                    {% endfor %}
                </div>
                
                <div class="mb-3">
                    {{ form.source_url.label(class="form-label") }}
                    {{ form.source_url(class="form-control") }}
                    {% for error in form.source_url.errors %}
                        <div class="text-danger">{{ error }}</div>
                    {% endfor %}
                    <div class="form-text">Optional: URL to the source video</div>
                </div>
                
                <div class="mb-3">
                    {{ form.content.label(class="form-label") }}
                    {{ form.content(class="form-control", rows=15) }}
                    {% for error in form.content.errors %}
                        <div class="text-danger">{{ error }}</div>
                    {% endfor %}
                </div>
                
                {{ form.submit(class="btn btn-primary") }}
            </form>
        </div>
    </div>
</div>
{% endblock %}''')

print("Transcript templates created successfully!")