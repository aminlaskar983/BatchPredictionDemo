"""
Gemini API client to handle interactions with the Gemini API.

This module encapsulates the logic for making API calls to the Google Generative AI
service, providing a clean interface for the batch processor with enhanced error
handling, rate limiting, and context management for optimal API usage.
"""

import logging
import time
import random
import asyncio
import google.generativeai as genai
from google.api_core.exceptions import GoogleAPIError, RetryError, InternalServerError, ResourceExhausted

logger = logging.getLogger(__name__)

class GeminiBatchProcessor:
    """Handles API interactions with Google's Generative AI (Gemini) models."""
    
    # Default model for Gemini API
    DEFAULT_MODEL = "gemini-1.5-pro"
    
    # Maximum retries for API calls
    MAX_RETRIES = 3
    
    # Exponential backoff parameters
    INITIAL_BACKOFF = 1  # seconds
    BACKOFF_FACTOR = 2
    
    def __init__(self, api_key, model=None):
        """
        Initialize the Gemini API client.
        
        Args:
            api_key (str): The API key for Gemini API authentication
            model (str, optional): The model to use. Defaults to gemini-1.5-pro.
        """
        self.api_key = api_key
        self.model_name = model or self.DEFAULT_MODEL
        
        # Configure the Gemini API
        genai.configure(api_key=self.api_key)
        
        # Get the model
        try:
            self.model = genai.GenerativeModel(self.model_name)
            logger.info(f"Initialized Gemini model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {e}")
            raise
    
    async def generate_response(self, prompt, context=None, history=None, system_instruction=None):
        """
        Generate a response from the Gemini API with enhanced retry logic and rate limiting.
        
        Args:
            prompt (str): The question or prompt to send to the API
            context (str, optional): Additional context for the prompt
            history (list, optional): Previous conversation history
            system_instruction (str, optional): System instructions to guide the model's behavior
            
        Returns:
            str: The generated response
        """
        retries = 0
        backoff = self.INITIAL_BACKOFF
        
        # Add jitter to avoid synchronized retries in concurrent requests
        jitter = lambda x: x * (1 + random.uniform(-0.1, 0.1))
        
        # Prepare the full prompt with context if provided
        full_prompt = prompt
        if context:
            # Format context to maximize relevance
            full_prompt = (
                f"Given the following context from a video transcript:\n\n"
                f"{context}\n\n"
                f"Question: {prompt}\n\n"
                f"Please answer the question based only on the information provided in the context. "
                f"If the context doesn't contain enough information to answer, say 'The transcript doesn't provide enough information to answer this question.'"
            )
            
        # Prepare history if provided (for follow-up questions)
        chat_history = []
        if history:
            for entry in history:
                if 'user' in entry:
                    chat_history.append({"role": "user", "parts": [entry['user']]})
                if 'model' in entry:
                    chat_history.append({"role": "model", "parts": [entry['model']]})
        
        # Add a small delay before API request to avoid rate limits in batch processing
        # This helps stagger the requests
        await asyncio.sleep(random.uniform(0.1, 0.5))
        
        while retries <= self.MAX_RETRIES:
            try:
                # Create a chat session if we have history (for follow-up questions)
                if chat_history:
                    chat = self.model.start_chat(history=chat_history)
                    response = chat.send_message(full_prompt)
                else:
                    # Check if system instruction is supported by checking the model's capabilities
                    supports_system_inst = hasattr(self.model, "supports_system_instructions") and self.model.supports_system_instructions
                    
                    if system_instruction and supports_system_inst:
                        # For models that support system instruction
                        response = self.model.generate_content(
                            full_prompt,
                            generation_config={"system_instruction": {"parts": [system_instruction]}}
                        )
                    else:
                        # Fallback for models without system instruction support
                        # Incorporate system instruction directly in the prompt if provided
                        if system_instruction:
                            enhanced_prompt = f"[SYSTEM INSTRUCTION: {system_instruction}]\n\n{full_prompt}"
                            response = self.model.generate_content(enhanced_prompt)
                        else:
                            # Direct generation without system instruction or chat history
                            response = self.model.generate_content(full_prompt)
                
                # Extract and return the text response
                return response.text
                
            except ResourceExhausted as e:
                # Handle quota errors differently - add longer backoff
                retries += 1
                if retries > self.MAX_RETRIES:
                    logger.error(f"API quota exceeded: {e}")
                    return f"ERROR: API quota exceeded. Please try again later."
                
                # Use a longer backoff for quota issues
                quota_backoff = jitter(backoff * 2) 
                logger.warning(f"API quota error: {e}. Retrying in {quota_backoff:.2f} seconds...")
                await asyncio.sleep(quota_backoff)
                backoff *= self.BACKOFF_FACTOR
                
            except (GoogleAPIError, RetryError, InternalServerError) as e:
                retries += 1
                if retries > self.MAX_RETRIES:
                    logger.error(f"Max retries exceeded: {e}")
                    return f"ERROR: Unable to generate response after multiple attempts."
                
                # Apply jitter to backoff to avoid thundering herd problem
                current_backoff = jitter(backoff)
                logger.warning(f"API error occurred: {e}. Retrying in {current_backoff:.2f} seconds...")
                await asyncio.sleep(current_backoff)
                backoff *= self.BACKOFF_FACTOR
                
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                return f"ERROR: An unexpected error occurred while processing your request."
                
    async def batch_generate(self, prompts, context=None, system_instruction=None, max_concurrent=5):
        """
        Process multiple prompts in an optimized batch with rate limiting and parallelization.
        
        Args:
            prompts (List[str]): List of prompts to process
            context (str, optional): Shared context for all prompts
            system_instruction (str, optional): System instructions to guide the model
            max_concurrent (int): Maximum number of concurrent API calls
            
        Returns:
            List[str]: List of responses in the same order as the prompts
        """
        if not prompts:
            return []
            
        # Create a semaphore to limit concurrent API calls
        semaphore = asyncio.Semaphore(max_concurrent)
        
        # For very long transcripts, split into chunks if needed
        
        async def process_single_prompt(prompt):
            # Acquire semaphore to limit concurrent calls
            async with semaphore:
                return await self.generate_response(
                    prompt=prompt,
                    context=context,
                    system_instruction=system_instruction
                )
                
        # Create tasks for all prompts
        tasks = [process_single_prompt(prompt) for prompt in prompts]
        
        # Wait for all tasks to complete
        responses = await asyncio.gather(*tasks)
        
        return responses
