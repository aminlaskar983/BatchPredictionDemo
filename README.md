# Batch Prediction with Gemini API for Video Content Analysis 🚀🧠

This project demonstrates batch prediction with Google's Gemini AI API, leveraging long context handling and context caching for efficiently answering questions about a video transcript.

## Features

- **Batch Prediction**: Optimizes API calls by processing multiple questions efficiently in parallel
- **Long Context Handling**: Processes and chunks large transcripts to fit within API context limits
- **Context Caching**: Implements an in-memory LRU cache to reuse results and reduce API calls
- **Interconnected Questions**: Maintains conversation history to answer related follow-up questions
- **Enhanced Output Formatting**: Presents results in a clear, structured format
- **Robust Error Handling**: Gracefully handles API errors with retry logic and exponential backoff
- **System Instruction Compatibility**: Adaptively handles different versions of the Gemini API

## Why This Matters

Extracting information from long-form video content by asking multiple questions is a common use case. This approach:

- **Reduces API Costs**: By minimizing redundant API calls through optimized batching and caching
- **Improves Response Time**: By parallelizing requests and reusing previous results
- **Handles Large Content**: By intelligently managing context windows for long transcripts
- **Maintains Conversational Context**: By tracking question relationships for more coherent responses

## Requirements

- Python 3.9+
- Google Generative AI SDK
- Rich (for terminal formatting)
- Python-dotenv (for environment variables)
- Flask, Flask-Login, Flask-WTF, Flask-SQLAlchemy (for web interface)

## Usage

The application can be run in two different modes:

### Web Application Mode (Default)

Run the Flask web application:

```bash
python main.py
```

This provides a web interface for managing transcripts, question sets, and viewing results.

### Demo Mode

Run the batch prediction demonstration with a limited number of questions:

```bash
python main.py --demo [num_questions]
```

Where `num_questions` is an optional parameter to specify how many questions to process (default is 3).

For example:
```bash
python main.py --demo 2
```

This will:
1. Load the sample transcript (a lecture about AI)
2. Process the specified number of sample questions about the transcript
3. Display the results in a formatted table
4. Generate a markdown report (batch_results.md)
5. Show cache statistics

**Note**: Using a smaller number of questions helps avoid API quota limitations.

## Project Structure

- **main.py**: Main entry point and demonstration script
- **app.py**: Flask application setup
- **batch_predictor.py**: Handles batch processing of questions with optimized API usage
- **context_cache.py**: Implements caching mechanism to store and reuse results
- **transcript_handler.py**: Processes transcripts and finds relevant context for questions
- **gemini_batch_processor.py**: Manages API interactions with Google's Generative AI
- **output_formatter.py**: Formats and presents results in a structured way
- **models.py**: Database models for the web application
- **forms/**: Flask-WTF forms for the web interface
- **routes/**: Flask route handlers for the web interface
- **templates/**: Jinja2 templates for the web interface
- **sample_transcript.py**: Contains a sample video transcript for demonstration
- **sample_questions.py**: Contains sample questions about the transcript

## Recent Improvements

- Added API compatibility layer for system_instruction to handle different versions of the Gemini API
- Enhanced rate limiting with configurable delays between batches
- Improved error handling and retry mechanisms for API quota limits
- Added delay between batches to better manage API rate limits
- Modified demo mode to accept custom number of questions parameter
- Added markdown report generation for better result sharing

## Error Handling

The application implements robust error handling:
- API rate limiting with exponential backoff
- Retries for transient errors
- Graceful degradation for permanent failures
- Informative error messages

