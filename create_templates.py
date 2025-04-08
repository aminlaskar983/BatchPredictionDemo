import os

# Create templates directory if it doesn't exist
if not os.path.exists('templates'):
    os.makedirs('templates')

# Create index.html
with open('templates/index.html', 'w') as f:
    f.write('''<!DOCTYPE html>
<html data-bs-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gemini Batch Prediction</title>
    <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <div class="row">
            <div class="col-md-8 offset-md-2 text-center">
                <h1 class="display-4">Gemini Batch Prediction</h1>
                <p class="lead">Process transcripts with Gemini AI and answer multiple questions efficiently</p>
                <hr class="my-4">
                <p>Analyze video transcripts with advanced context handling and efficient batch processing.</p>
                <a href="/auth/register" class="btn btn-primary btn-lg mt-3">Get Started</a>
            </div>
        </div>
    </div>
</body>
</html>''')

# Create dashboard.html
with open('templates/dashboard.html', 'w') as f:
    f.write('''<!DOCTYPE html>
<html data-bs-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - Gemini Batch Prediction</title>
    <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-4">
        <h1>Dashboard</h1>
        <div class="row mt-4">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">My Transcripts</h5>
                        <p class="card-text">Manage your video transcripts for AI analysis.</p>
                        <a href="/transcripts" class="btn btn-primary">View Transcripts</a>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">My Question Sets</h5>
                        <p class="card-text">Create and manage sets of questions about your transcripts.</p>
                        <a href="/questions/sets" class="btn btn-primary">View Question Sets</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>''')

# Create about.html
with open('templates/about.html', 'w') as f:
    f.write('''<!DOCTYPE html>
<html data-bs-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>About - Gemini Batch Prediction</title>
    <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-4">
        <h1>About Gemini Batch Prediction</h1>
        <div class="row mt-4">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Project Overview</h5>
                        <p class="card-text">
                            Gemini Batch Prediction is a demonstration of using Google's Gemini API for efficiently processing 
                            multiple questions about video transcripts. The system implements advanced techniques including:
                        </p>
                        <ul>
                            <li>Batch processing of questions to optimize API usage</li>
                            <li>Long context handling for working with large transcripts</li>
                            <li>Context caching to improve response times for similar queries</li>
                            <li>Smart chunking of long transcripts to work within API limits</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>''')

print("Templates created successfully!")