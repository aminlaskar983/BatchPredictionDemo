"""
Context Cache module for efficient reuse of API contexts.

This module implements an in-memory caching mechanism to store and reuse
contexts for similar questions, reducing API calls and improving performance.
"""

import logging
import time
import hashlib
from collections import OrderedDict

logger = logging.getLogger(__name__)

class ContextCache:
    """
    Implements an in-memory LRU (Least Recently Used) cache for contexts
    and conversation history to reduce API calls for similar questions.
    """
    
    def __init__(self, max_size=100, ttl=3600):
        """
        Initialize the context cache.
        
        Args:
            max_size (int): Maximum number of items to store in the cache
            ttl (int): Time-to-live in seconds for cache items
        """
        self.max_size = max_size
        self.ttl = ttl  # Time-to-live in seconds
        self.cache = OrderedDict()  # Using OrderedDict for LRU functionality
        self.timestamps = {}  # To track item age
        self.hits = 0
        self.misses = 0
        logger.info(f"Initialized context cache with max_size={max_size}, ttl={ttl}s")
    
    def _generate_key(self, query, context_id=None):
        """
        Generate a unique cache key for a query/context combination.
        
        Args:
            query (str): The question or prompt
            context_id (str, optional): An identifier for the context
            
        Returns:
            str: A cache key
        """
        # Create a deterministic hash from the query and context_id
        key_material = f"{query.lower().strip()}:{context_id or ''}"
        return hashlib.md5(key_material.encode()).hexdigest()
    
    def get(self, query, context_id=None):
        """
        Retrieve a cached result.
        
        Args:
            query (str): The query to look up
            context_id (str, optional): Context identifier
            
        Returns:
            dict or None: The cached result or None if not found
        """
        key = self._generate_key(query, context_id)
        
        # Check if key exists and not expired
        if key in self.cache:
            timestamp = self.timestamps.get(key, 0)
            if time.time() - timestamp <= self.ttl:
                # Move to the end (most recently used)
                self.cache.move_to_end(key)
                self.hits += 1
                logger.debug(f"Cache hit for key: {key[:8]}...")
                return self.cache[key]
            else:
                # Expired entry
                self._remove(key)
        
        self.misses += 1
        logger.debug(f"Cache miss for key: {key[:8]}...")
        return None
    
    def set(self, query, result, context_id=None):
        """
        Store a result in the cache.
        
        Args:
            query (str): The query 
            result (dict): The result to cache
            context_id (str, optional): Context identifier
            
        Returns:
            bool: True if successful
        """
        key = self._generate_key(query, context_id)
        
        # Check if we need to remove oldest entry
        if len(self.cache) >= self.max_size:
            # Remove the first item (oldest)
            oldest = next(iter(self.cache))
            self._remove(oldest)
        
        # Add new entry
        self.cache[key] = result
        self.timestamps[key] = time.time()
        logger.debug(f"Cached result for key: {key[:8]}...")
        return True
    
    def _remove(self, key):
        """
        Remove an item from the cache.
        
        Args:
            key (str): The cache key to remove
        """
        if key in self.cache:
            self.cache.pop(key)
            self.timestamps.pop(key, None)
            logger.debug(f"Removed key from cache: {key[:8]}...")
    
    def clear(self):
        """Clear the entire cache."""
        self.cache.clear()
        self.timestamps.clear()
        logger.info("Cache cleared")
    
    def get_stats(self):
        """
        Get cache statistics.
        
        Returns:
            dict: Dictionary with cache statistics
        """
        return {
            "size": len(self.cache),
            "hits": self.hits,
            "misses": self.misses,
            "hit_ratio": self.hits / (self.hits + self.misses) if (self.hits + self.misses) > 0 else 0
        }
