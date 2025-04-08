"""
Batch Predictor module for handling batch prediction with the Gemini API.

This module implements batch processing of questions, optimizing API calls
and managing context for long-form content like video transcripts.
"""

import logging
import asyncio
import time
import re
from typing import List, Dict, Any, Callable, Optional

from gemini_batch_processor import GeminiBatchProcessor

logger = logging.getLogger(__name__)

class BatchPredictor:
    """
    Handles batch processing of questions with optimized context handling
    and caching for Gemini API.
    """
    
    # Maximum concurrent API requests - use a lower number to avoid rate limits
    MAX_CONCURRENT_REQUESTS = 2
    
    # Maximum batch size for grouped processing
    MAX_BATCH_SIZE = 5
    
    # Delay between batches to avoid hitting rate limits
    BATCH_DELAY_SECONDS = 2
    
    def __init__(self, api_key, cache, transcript_handler):
        """
        Initialize the batch predictor.
        
        Args:
            api_key (str): Gemini API key
            cache (ContextCache): Instance of the context cache
            transcript_handler (TranscriptHandler): Instance of the transcript handler
        """
        self.api = GeminiBatchProcessor(api_key)
        self.cache = cache
        self.transcript_handler = transcript_handler
        self.conversation_history = []
        logger.info("Initialized BatchPredictor")
    
    async def process_batch(self, questions: List[str], transcript: str, 
                           progress_callback: Optional[Callable] = None) -> List[Dict[str, Any]]:
        """
        Process a batch of questions about a transcript.
        
        Args:
            questions (List[str]): List of questions to process
            transcript (str): The full transcript text
            progress_callback (Callable, optional): Callback function to report progress
            
        Returns:
            List[Dict[str, Any]]: List of response dictionaries
        """
        if not questions:
            logger.warning("Empty question list provided")
            return []
        
        if not transcript:
            logger.warning("Empty transcript provided")
            return [{"error": "No transcript provided"} for _ in questions]
        
        batch_start_time = time.time()
        logger.info(f"Starting batch processing of {len(questions)} questions")
        
        # Preprocess transcript for efficiency
        processed_transcript = self.transcript_handler.process_transcript(transcript)
        transcript_chunks = self.transcript_handler.chunk_transcript(processed_transcript)
        
        # Analyze for related questions to optimize processing
        related_questions_map = self._group_related_questions(questions)
        
        # Create semaphore to limit concurrent API calls
        semaphore = asyncio.Semaphore(self.MAX_CONCURRENT_REQUESTS)
        
        # Split questions into smaller batches if needed
        question_batches = [questions[i:i+self.MAX_BATCH_SIZE] 
                          for i in range(0, len(questions), self.MAX_BATCH_SIZE)]
        
        all_results = []
        processed_count = 0
        
        for batch_index, batch in enumerate(question_batches):
            batch_start = time.time()
            logger.info(f"Processing batch {batch_index+1}/{len(question_batches)}, size {len(batch)}")
            
            # Process each batch of questions
            batch_tasks = []
            
            for q_index, question in enumerate(batch):
                # Create task for each question with additional metadata
                question_index = batch_index * self.MAX_BATCH_SIZE + q_index
                
                # Get related questions for this question
                related = related_questions_map.get(question, [])
                
                task = asyncio.create_task(
                    self._process_question(
                        question=question,
                        full_transcript=processed_transcript,
                        transcript_chunks=transcript_chunks,
                        semaphore=semaphore,
                        question_index=question_index,
                        related_questions=related
                    )
                )
                batch_tasks.append(task)
            
            # Wait for all tasks in the batch to complete
            batch_results = await asyncio.gather(*batch_tasks)
            
            # Add batch timing information
            batch_time = time.time() - batch_start
            for result in batch_results:
                if "response_metadata" in result:
                    result["response_metadata"]["batch_time"] = batch_time
                    result["response_metadata"]["batch_index"] = batch_index
            
            all_results.extend(batch_results)
            processed_count += len(batch)
            
            # Call progress callback if provided
            if progress_callback:
                progress_callback(processed_count, len(questions))
            
            # Add a delay between batches to avoid API rate limiting
            if batch_index < len(question_batches) - 1:
                logger.info(f"Adding delay of {self.BATCH_DELAY_SECONDS}s between batches to avoid rate limits")
                await asyncio.sleep(self.BATCH_DELAY_SECONDS)
        
        total_batch_time = time.time() - batch_start_time
        logger.info(f"Completed batch processing of {len(questions)} questions in {total_batch_time:.2f}s")
        
        # Add relationships between questions and answers in the metadata
        self._add_question_relationships(all_results, related_questions_map)
        
        return all_results
        
    def _group_related_questions(self, questions: List[str]) -> Dict[str, List[str]]:
        """
        Group related questions to optimize context sharing.
        
        This uses a simple keyword-based approach to find related questions.
        In a production system, you would use embeddings and semantic similarity.
        
        Args:
            questions (List[str]): List of questions to analyze
            
        Returns:
            Dict[str, List[str]]: Dictionary mapping each question to a list of related questions
        """
        related = {}
        
        # Simple keyword extraction (remove common words)
        stop_words = {'what', 'when', 'where', 'who', 'why', 'how', 'is', 'are', 'the', 'to', 'and', 'a', 'in', 'of', 'that', 'this'}
        question_keywords = {}
        
        for q in questions:
            # Extract keywords from each question
            words = re.findall(r'\b\w+\b', q.lower())
            keywords = [w for w in words if w not in stop_words and len(w) > 3]
            question_keywords[q] = set(keywords)
        
        # Find related questions based on keyword overlap
        for q1 in questions:
            related[q1] = []
            kw1 = question_keywords[q1]
            
            for q2 in questions:
                if q1 == q2:
                    continue
                    
                kw2 = question_keywords[q2]
                # Calculate Jaccard similarity
                if kw1 and kw2:  # Avoid division by zero
                    similarity = len(kw1.intersection(kw2)) / len(kw1.union(kw2))
                    if similarity > 0.3:  # Threshold for relatedness
                        related[q1].append(q2)
        
        return related
        
    def _add_question_relationships(self, results: List[Dict[str, Any]], related_map: Dict[str, List[str]]):
        """
        Add relationship metadata to all results.
        
        This improves the data model by explicitly linking related questions/answers.
        
        Args:
            results (List[Dict[str, Any]]): List of result dictionaries
            related_map (Dict[str, List[str]]): Mapping of questions to related questions
            
        Returns:
            None (modifies results in-place)
        """
        # Create a mapping from questions to result indices
        question_to_index = {}
        for i, result in enumerate(results):
            if "question" in result:
                question_to_index[result["question"]] = i
        
        # Add relationship metadata to each result
        for i, result in enumerate(results):
            question = result.get("question")
            if not question:
                continue
                
            if "response_metadata" not in result:
                result["response_metadata"] = {}
                
            # Add indices of related questions
            related_indices = []
            for related_q in related_map.get(question, []):
                if related_q in question_to_index:
                    related_indices.append(question_to_index[related_q])
            
            result["response_metadata"]["related_indices"] = related_indices
    
    async def _process_question(self, question, full_transcript, transcript_chunks, semaphore, 
                           question_index=None, related_questions=None):
        """
        Process a single question with appropriate context handling.
        
        Args:
            question (str): The question to process
            full_transcript (str): The complete transcript
            transcript_chunks (List[str]): Chunked transcript if needed
            semaphore (asyncio.Semaphore): Semaphore for limiting concurrent requests
            question_index (int, optional): Index of question in batch for tracking
            related_questions (List[str], optional): List of related questions
            
        Returns:
            Dict[str, Any]: Response dictionary
        """
        # Initialize or use default parameters
        if related_questions is None:
            related_questions = []
            
        # Track processing time from the beginning
        start_time = time.time()
        
        # Check cache first - this avoids redundant API calls for similar questions
        cache_key = question
        cached_result = self.cache.get(cache_key, "transcript")
        if cached_result:
            logger.info(f"Cache hit for question: {question[:30]}...")
            # Update the cached result with a note that it came from cache
            if "response_metadata" in cached_result:
                cached_result["response_metadata"]["cache_hit"] = True
            elif "metadata" in cached_result:
                cached_result["metadata"]["cache_hit"] = True
            return cached_result
        
        try:
            # Start context selection timing
            context_selection_start = time.time()
            
            # Find the most relevant context for this question
            relevant_context = self.transcript_handler.find_relevant_context(
                full_transcript, question
            )
            
            context_selection_time = time.time() - context_selection_start
            
            # If we have related questions, include them in our system context
            related_context = ""
            if related_questions:
                related_context = (
                    "This question is part of a sequence of related questions:\n" +
                    "\n".join([f"- {q}" for q in related_questions]) +
                    "\n\nEnsure your answer is consistent with how you would answer these related questions."
                )
            
            # Prepare response with connection to previous questions if available
            history_context = ""
            if self.conversation_history:
                # Take last 3 exchanges at most to avoid context explosion
                recent_history = self.conversation_history[-3:]
                history_context = "\n\n".join([
                    f"Previous Q: {item['user']}\nPrevious A: {item['model']}"
                    for item in recent_history
                ])
                history_context = f"\nRelevant conversation history:\n{history_context}\n\n"
            
            # Combine contexts for the final prompt
            combined_context = f"{relevant_context}\n{history_context}"
            
            # Create system instruction for better, more consistent answers
            system_instruction = (
                "You are an AI assistant analyzing video transcripts. "
                "You should provide clear, accurate answers based strictly on the transcript content. "
                "If the transcript doesn't contain enough information to answer, acknowledge this limitation. "
                "Include timestamps or speaker names when they are available in the transcript. "
                "Keep your answers concise but complete."
            )
            
            if related_context:
                system_instruction += f"\n\n{related_context}"
            
            # Acquire semaphore to limit concurrent API calls
            api_call_start = time.time()
            async with semaphore:
                response = await self.api.generate_response(
                    question, 
                    context=combined_context,
                    history=self.conversation_history if self.conversation_history else None,
                    system_instruction=system_instruction
                )
            api_call_time = time.time() - api_call_start
                
            # Extract timestamps if available in the transcript
            # Simple regex to find potential timestamps in the relevant context
            # This could be made more sophisticated for production use
            timestamp_match = re.search(r'(\d{1,2}:\d{2}(:\d{2})?)', relevant_context)
            timestamp = timestamp_match.group(1) if timestamp_match else None
            
            # Create detailed result object with rich metadata
            result = {
                "question": question,
                "answer": response,
                "context_used": relevant_context,  # Include the context used
                "timestamp": timestamp,  # Video timestamp if found
                "related_questions": related_questions,  # Track related questions
                "response_metadata": {  # Use response_metadata to match the database field name
                    "processing_time": time.time() - start_time,
                    "context_selection_time": context_selection_time,
                    "api_call_time": api_call_time,
                    "model": self.api.model_name,
                    "context_length": len(combined_context) if combined_context else 0,
                    "question_index": question_index,
                    "cache_hit": False
                }
            }
            
            # Update conversation history for potential follow-up questions
            self.conversation_history.append({
                "user": question,
                "model": response
            })
            
            # Limit conversation history to prevent context explosion
            if len(self.conversation_history) > 5:
                # Keep the most recent conversations
                self.conversation_history = self.conversation_history[-5:]
            
            # Cache the result for future similar questions
            self.cache.set(cache_key, result, "transcript")
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing question '{question[:30]}...': {str(e)}")
            # Calculate processing time since we know start_time is defined at the beginning of the method
            processing_time = time.time() - start_time
                
            error_result = {
                "question": question,
                "answer": f"Sorry, an error occurred while processing this question: {str(e)}",
                "error": str(e),
                "response_metadata": {
                    "error": True,
                    "error_message": str(e),
                    "processing_time": processing_time,
                    "question_index": question_index
                }
            }
            return error_result
