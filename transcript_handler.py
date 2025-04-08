"""
Transcript Handler module for processing and managing video transcripts.

This module provides functionality to process transcripts, split them into
manageable chunks for the API, and handle context retrieval.
"""

import re
import logging

logger = logging.getLogger(__name__)

class TranscriptHandler:
    """
    Handles processing and chunking of video transcripts to optimize for
    Gemini API's context window limitations.
    """
    
    # Maximum tokens per chunk (Gemini 1.5 Pro has a context window of 1M tokens)
    # We'll be more conservative to account for response tokens
    MAX_TOKENS_PER_CHUNK = 100000
    CHARS_PER_TOKEN = 4  # Approximation for English text
    
    def __init__(self):
        """Initialize the TranscriptHandler."""
        logger.debug("Initializing TranscriptHandler")
    
    def process_transcript(self, transcript):
        """
        Process a raw transcript to clean and standardize the format.
        
        Args:
            transcript (str): The raw transcript text
            
        Returns:
            str: The processed transcript
        """
        if not transcript:
            logger.warning("Empty transcript provided")
            return ""
        
        # Remove excessive whitespace
        processed = re.sub(r'\s+', ' ', transcript)
        
        # Ensure proper sentence spacing
        processed = re.sub(r'\.(?=[A-Z])', '. ', processed)
        
        # Remove any special characters that might cause issues
        processed = re.sub(r'[^\w\s\.\,\;\:\?\!\"\'\/\-\(\)\[\]]', '', processed)
        
        logger.info(f"Processed transcript: {len(processed)} characters")
        return processed
    
    def chunk_transcript(self, transcript):
        """
        Split a transcript into chunks that fit within the API's context window.
        
        Args:
            transcript (str): The processed transcript
            
        Returns:
            list: List of transcript chunks
        """
        if not transcript:
            return []
        
        # Calculate approximate max chars per chunk
        max_chars = self.MAX_TOKENS_PER_CHUNK * self.CHARS_PER_TOKEN
        
        # If transcript is small enough, return it as a single chunk
        if len(transcript) <= max_chars:
            return [transcript]
        
        # Split transcript into paragraphs first
        paragraphs = transcript.split('\n')
        
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            # If adding this paragraph would exceed the limit, start a new chunk
            if len(current_chunk) + len(paragraph) > max_chars:
                if current_chunk:  # Don't add empty chunks
                    chunks.append(current_chunk)
                current_chunk = paragraph
            else:
                if current_chunk:
                    current_chunk += "\n" + paragraph
                else:
                    current_chunk = paragraph
        
        # Add the last chunk if not empty
        if current_chunk:
            chunks.append(current_chunk)
        
        logger.info(f"Split transcript into {len(chunks)} chunks")
        return chunks
    
    def find_relevant_context(self, transcript, question, window_size=20000):
        """
        Find the most relevant section of the transcript for a given question.
        
        This implementation uses a combined approach of keyword matching and 
        semantic relevance scoring to find the most relevant section of the transcript.
        
        Args:
            transcript (str): The full transcript
            question (str): The question to find context for
            window_size (int): The approximate context window size in characters
            
        Returns:
            str: The most relevant section of transcript for the question
        """
        # For very short transcripts, return the entire transcript
        if len(transcript) <= window_size * 1.5:
            return transcript
            
        # Extract keywords from the question (enhanced approach)
        # Expanded stop words list
        stop_words = {
            'what', 'when', 'where', 'who', 'why', 'how', 'is', 'are', 'was', 'were', 
            'the', 'to', 'and', 'a', 'an', 'in', 'on', 'at', 'of', 'for', 'with', 'by',
            'that', 'this', 'these', 'those', 'it', 'its', 'as', 'from', 'about', 'some',
            'would', 'could', 'should', 'shall', 'will', 'can', 'may', 'might', 'must',
            'do', 'does', 'did', 'done', 'have', 'has', 'had', 'get', 'gets', 'got',
            'been', 'be', 'am', 'not', 'or', 'if', 'then', 'than', 'but'
        }
        
        # Convert to lowercase and tokenize
        question_lower = question.lower()
        question_words = re.findall(r'\b\w+\b', question_lower)
        
        # Filter out stop words but include shorter words that might be important
        standard_keywords = [word for word in question_words if word not in stop_words and len(word) > 2]
        
        # Extract potential named entities (capitalized words in the original question)
        named_entities = re.findall(r'\b[A-Z][a-z]+\b', question)
        named_entities_lower = [entity.lower() for entity in named_entities]
        
        # Combine all keywords, giving higher weight to named entities
        keywords = standard_keywords + [entity for entity in named_entities_lower if entity not in standard_keywords]
        
        # Extract potential quote matches (text within quotation marks)
        quotes = re.findall(r'"([^"]*)"', question)
        quotes += re.findall(r"'([^']*)'", question)
        
        if not keywords and not quotes:
            # If no significant keywords found, return a segment from the beginning
            logger.warning("No significant keywords or quotes found in question")
            if len(transcript) <= window_size:
                return transcript
            return transcript[:window_size]
        
        transcript_lower = transcript.lower()
        best_position = 0
        best_score = 0
        
        # First check for exact quote matches (highest priority)
        for quote in quotes:
            if len(quote) < 3:  # Skip very short quotes
                continue
                
            quote_lower = quote.lower()
            quote_matches = [m.start() for m in re.finditer(re.escape(quote_lower), transcript_lower)]
            
            if quote_matches:
                # Quote match found, this is a strong indicator
                best_position = quote_matches[0]
                best_score = 100  # Assign high score to exact quote matches
                logger.info(f"Found exact quote match: '{quote}'")
                break
        
        # If no exact quote match found, use keyword matching with improved scoring
        if best_score == 0:
            # Weigh sections by keyword density
            section_size = window_size // 4  # Check in smaller sections for precision
            overlap = section_size // 2  # Use overlapping sections
            
            for i in range(0, len(transcript) - section_size + 1, overlap):
                section = transcript_lower[i:i+section_size]
                
                # Calculate base score from keyword frequency
                score = 0
                for keyword in keywords:
                    keyword_count = len(re.findall(r'\b' + re.escape(keyword) + r'\b', section))
                    score += keyword_count
                
                # Bonus for having multiple unique keywords
                unique_keywords_present = sum(1 for keyword in keywords if keyword in section)
                score += unique_keywords_present * 2
                
                # Bonus for sections with multiple keywords close together
                for j in range(len(keywords)):
                    for k in range(j+1, len(keywords)):
                        if keywords[j] in section and keywords[k] in section:
                            # Find their closest occurrence
                            pos_j = section.find(keywords[j])
                            pos_k = section.find(keywords[k])
                            if pos_j != -1 and pos_k != -1:
                                proximity = abs(pos_j - pos_k)
                                if proximity < 100:  # If keywords are close
                                    score += (100 - proximity) // 10
                
                if score > best_score:
                    best_score = score
                    best_position = i
        
        # Extract context around the best position
        half_window = window_size // 2
        start = max(0, best_position - half_window)
        end = min(len(transcript), best_position + half_window)
        
        # Adjust to start/end at sentence boundaries where possible
        if start > 0:
            # Find the first period or newline before start, within reasonable bounds
            look_back = min(500, start)  # Look back max 500 chars to find sentence boundary
            sentence_start = max(
                transcript.rfind('. ', start - look_back, start),
                transcript.rfind('! ', start - look_back, start),
                transcript.rfind('? ', start - look_back, start),
                transcript.rfind('\n', start - look_back, start)
            )
            if sentence_start != -1:
                start = sentence_start + 2  # Skip the punctuation and space
        
        if end < len(transcript):
            # Find the first period or newline after end, within reasonable bounds
            look_forward = min(500, len(transcript) - end)  # Look ahead max 500 chars
            possible_ends = [
                transcript.find('. ', end, end + look_forward),
                transcript.find('! ', end, end + look_forward),
                transcript.find('? ', end, end + look_forward),
                transcript.find('\n', end, end + look_forward)
            ]
            # Filter out -1 values (not found)
            valid_ends = [e for e in possible_ends if e != -1]
            if valid_ends:
                sentence_end = min(valid_ends)
                end = sentence_end + 1  # Include the punctuation
        
        context = transcript[start:end]
        logger.info(f"Found relevant context: {len(context)} characters with score {best_score}")
        return context
