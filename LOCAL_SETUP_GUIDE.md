# Local Setup Guide for Gemini Batch Prediction Project

This guide will help you set up and run the Gemini Batch Prediction project on your local machine.

## Prerequisites

- Python 3.9+ installed
- PostgreSQL database installed and running
- Git (optional, for cloning the repository)

## Step 1: Clone or Download the Project

If you have Git installed:
```bash
git clone [repository-url]
cd [project-directory]
```

Alternatively, download and extract the project ZIP file.

## Step 2: Create a Virtual Environment

It's recommended to use a virtual environment to avoid conflicts with other Python projects:

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

## Step 3: Install Dependencies

Use the provided local_requirements.txt file to install all required packages:

```bash
pip install -r local_requirements.txt
```

## Step 4: Set Up the Database

1. Create a PostgreSQL database:
```bash
# Login to PostgreSQL
psql -U postgres

# Create a database
CREATE DATABASE gemini_batch_prediction;

# Create a user (optional)
CREATE USER gemini_user WITH PASSWORD 'your_password';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE gemini_batch_prediction TO gemini_user;

# Exit PostgreSQL
\q
```

## Step 5: Configure Environment Variables

Create a `.env` file in the project root directory with the following variables:

```
# Database configuration
DATABASE_URL=postgresql://username:password@localhost:5432/gemini_batch_prediction

# Google Gemini API key
GEMINI_API_KEY=your_gemini_api_key

# Session secret key (generate a random string)
SESSION_SECRET=your_random_secret_key
```

To get a Gemini API key:
1. Go to https://makersuite.google.com/app/apikey
2. Create a new API key or use an existing one
3. Copy the key to your .env file

## Step 6: Initialize the Database

Run the following commands to create the database tables:

```bash
# Start a Python interactive shell
python

# In the Python shell
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
    exit()
```

## Step 7: Run the Application

### Web Application Mode

```bash
# For development with automatic reloading
flask run --host=0.0.0.0 --port=5000 --debug

# Or using the provided main.py
python main.py
```

### Demo Mode (Command Line)

```bash
# Run with default 3 questions
python main.py --demo

# Run with a specific number of questions
python main.py --demo 5
```

## Step 8: Access the Application

Open your web browser and navigate to:
```
http://localhost:5000
```

You should see the Gemini Batch Prediction homepage. Register a new account to get started.

## Troubleshooting

### Database Connection Issues

If you encounter database connection issues:
- Verify PostgreSQL is running
- Check your DATABASE_URL in the .env file
- Ensure the database and user exist with proper permissions

### API Key Issues

If the Gemini API isn't working:
- Verify your GEMINI_API_KEY in the .env file
- Check that you have quota available in your Google AI Studio account
- Make sure your API key has access to the Gemini models

### Package Installation Issues

If you have issues installing packages:
- Update pip: `pip install --upgrade pip`
- Install PostgreSQL development headers (required for psycopg2-binary)
  - Ubuntu/Debian: `sudo apt-get install libpq-dev`
  - macOS with Homebrew: `brew install postgresql`
  - Windows: Included with PostgreSQL installation

## File and Directory Structure Explanation

### Core Files

- **main.py**: Application entry point with both web and demo modes
- **app.py**: Flask application factory and configuration
- **models.py**: SQLAlchemy database models
- **batch_predictor.py**: Core batch processing logic
- **.env**: Environment variables (you create this)
- **local_requirements.txt**: Python dependencies

### Directories

- **routes/**: Flask route blueprints
  - **auth.py**: Authentication routes
  - **main.py**: Main page routes
  - **questions.py**: Question management routes
  - **transcripts.py**: Transcript management routes
  - **video_questions.py**: Video question processing routes

- **forms/**: Flask-WTF form definitions
  - **auth.py**: Login and registration forms
  - **questions.py**: Question forms
  - **transcripts.py**: Transcript forms
  - **video_questions.py**: Video URL and questions form

- **templates/**: HTML templates organized by feature

## Running in Production

For production deployment, it's recommended to use Gunicorn:

```bash
gunicorn --bind 0.0.0.0:5000 main:app
```

Consider using a process manager like Supervisor or systemd to manage the application process.

## Replit vs Local Differences

When running locally instead of on Replit:

1. **Database**: You'll need to set up and configure your own PostgreSQL database
2. **Environment Variables**: You'll need to create your own .env file
3. **Process Management**: You'll need to start/stop the application manually 
4. **Server**: You may want to set up a proper web server like Nginx in front of the application