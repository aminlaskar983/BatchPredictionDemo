"""
Main entry point for the Gemini Batch Prediction application.

This script demonstrates batch prediction with Gemini APIs, leveraging long context
and context caching for efficiently answering questions about a video transcript.
"""
import os
import logging
import asyncio
from dotenv import load_dotenv

from app import app
from batch_predictor import BatchPredictor
from context_cache import ContextCache
from transcript_handler import TranscriptHandler
from output_formatter import OutputFormatter
from sample_transcript import SAMPLE_TRANSCRIPT
from sample_questions import SAMPLE_QUESTIONS

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


def load_api_key():
    """Load API key from environment variables."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.error("Gemini API key not found. Please set the GEMINI_API_KEY environment variable.")
        return None
    return api_key


async def process_batch_demo(num_questions=3):
    """
    Run a demonstration of the batch prediction system.
    
    Args:
        num_questions (int): Number of questions to process (default: 3)
    """
    # Initialize components
    api_key = load_api_key()
    if not api_key:
        logger.error("No API key found. Please set the GEMINI_API_KEY environment variable.")
        return

    # Create required components with improved configuration
    cache = ContextCache(max_size=200, ttl=7200)  # Larger cache with longer TTL
    transcript_handler = TranscriptHandler()
    batch_predictor = BatchPredictor(api_key, cache, transcript_handler)
    formatter = OutputFormatter()
    
    # Limit number of questions to avoid API quota issues
    limited_questions = SAMPLE_QUESTIONS[:num_questions]
    
    # Process transcript and questions
    logger.info(f"Processing transcript of {len(SAMPLE_TRANSCRIPT)} characters")
    logger.info(f"Preparing to process {len(limited_questions)} questions (limited to avoid API quota issues)")
    
    # Define progress tracking
    start_time = asyncio.get_event_loop().time()
    
    def progress_callback(current, total):
        """Display progress of batch processing with time estimates."""
        percent = (current / total) * 100
        elapsed = asyncio.get_event_loop().time() - start_time
        
        # Calculate estimated time remaining
        if current > 0:
            time_per_question = elapsed / current
            remaining = time_per_question * (total - current)
            time_str = f", ~{remaining:.1f}s remaining"
        else:
            time_str = ""
            
        logger.info(f"Processing question {current}/{total} ({percent:.1f}%{time_str})")
    
    # Process the batch
    try:
        # Execute batch processing with progress reporting
        results = await batch_predictor.process_batch(
            limited_questions, 
            SAMPLE_TRANSCRIPT,  # Pass raw transcript, processing happens inside batch_predictor
            progress_callback
        )
        
        # Calculate and log statistics
        total_time = asyncio.get_event_loop().time() - start_time
        cache_hits = sum(1 for r in results if "cache_hit" in r.get("response_metadata", {}) and r["response_metadata"]["cache_hit"])
        
        logger.info(f"Batch processing complete! Processed {len(results)} questions in {total_time:.2f}s")
        logger.info(f"Cache hits: {cache_hits}/{len(results)} ({(cache_hits/len(results))*100:.1f}%)")
        
        # Format and display results in structured format
        result_table = formatter.format_batch_results(limited_questions, results)
        print(result_table)
        
        # Generate markdown for documentation
        md_output = formatter.format_markdown_output(limited_questions, results)
        with open("batch_results.md", "w") as f:
            f.write(md_output)
        logger.info("Results saved to batch_results.md")
        
        # Also generate Q&A format output
        qa_output = formatter.format_qa_output(limited_questions, results)
        with open("qa_results.txt", "w") as f:
            f.write(qa_output)
        logger.info("Q&A format results saved to qa_results.txt")
        
        # Display the Q&A format in the console as well
        print("\nQuestion/Answer Format Output:")
        print("============================\n")
        print(qa_output)
        
    except Exception as e:
        logger.error(f"Error during batch processing: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())


async def main():
    """Main function to run the batch prediction demonstration."""
    logger.info("Starting Gemini Batch Prediction Demo")
    # Check for command line arguments to determine number of questions
    import sys
    num_questions = 3  # Default to a small number to avoid API quota issues
    
    if len(sys.argv) > 2:
        try:
            num_questions = int(sys.argv[2])
            logger.info(f"Processing {num_questions} questions from command line argument")
        except ValueError:
            logger.warning(f"Invalid number of questions specified: {sys.argv[2]}. Using default: {num_questions}")
    
    # Run with the specified (or default) number of questions
    await process_batch_demo(num_questions)


if __name__ == "__main__":
    # Check if we should run in demo mode or Flask mode
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        # Run in standalone demo mode
        logger.info("Running in standalone demo mode")
        asyncio.run(main())
    else:
        # Run in Flask web application mode by default
        logger.info("Running in Flask web application mode")
        logger.info("For standalone demo mode, use: python main.py --demo")
        app.run(host="0.0.0.0", port=5000, debug=True)