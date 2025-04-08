"""
Video Transcript Extractor module for extracting transcripts from various video platforms.

This module provides functionality to extract transcripts from video platforms like YouTube,
returning both the transcript text and relevant metadata.
"""

import re
import logging
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

# Set up logging
logger = logging.getLogger(__name__)


class VideoTranscriptExtractor:
    """
    Handles extraction of transcripts from various video platforms.
    Currently supports YouTube.
    """
    
    def __init__(self):
        """Initialize the video transcript extractor."""
        pass
    
    def extract_transcript(self, video_url):
        """
        Extract transcript from a video URL.
        
        Args:
            video_url (str): URL of the video
            
        Returns:
            dict: Dictionary containing transcript text and metadata, or None if extraction failed
        """
        # Currently only YouTube is supported
        if 'youtube.com' in video_url or 'youtu.be' in video_url:
            return self._extract_youtube_transcript(video_url)
        else:
            logger.warning(f"Unsupported video platform: {video_url}")
            return None
    
    def _extract_youtube_transcript(self, youtube_url):
        """
        Extract transcript from a YouTube video.
        
        Args:
            youtube_url (str): URL of the YouTube video
            
        Returns:
            dict: Dictionary containing transcript and metadata, or None if extraction failed
        """
        try:
            # Extract video ID from URL
            video_id = self._extract_youtube_video_id(youtube_url)
            if not video_id:
                logger.error(f"Could not extract video ID from YouTube URL: {youtube_url}")
                return None
            
            # Get transcript data
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            if not transcript_list:
                logger.warning(f"Empty transcript returned for video ID: {video_id}")
                return None
            
            # Try to get video info (title, etc.)
            video_info = self._get_youtube_video_info(video_id)
            
            # Format the transcript with timestamps
            formatted_transcript = self._format_youtube_transcript(transcript_list)
            
            return {
                'title': video_info.get('title', f'YouTube Video: {video_id}'),
                'transcript': formatted_transcript,
                'video_id': video_id,
                'language': transcript_list[0].get('language', 'en') if transcript_list else 'en',
                'segments': len(transcript_list),
                'duration': transcript_list[-1]['start'] + transcript_list[-1]['duration'] if transcript_list else 0
            }
            
        except TranscriptsDisabled:
            logger.error(f"Transcripts are disabled for this YouTube video: {youtube_url}")
            return None
        except NoTranscriptFound:
            logger.error(f"No transcript found for this YouTube video: {youtube_url}")
            return None
        except Exception as e:
            logger.error(f"Error extracting YouTube transcript: {str(e)}")
            return None
    
    def _extract_youtube_video_id(self, youtube_url):
        """
        Extract the video ID from a YouTube URL.
        
        Args:
            youtube_url (str): URL of the YouTube video
            
        Returns:
            str: YouTube video ID or None if extraction failed
        """
        # Standard YouTube URL pattern
        youtube_regex = r'(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
        match = re.search(youtube_regex, youtube_url)
        
        if match:
            return match.group(1)
        else:
            return None
    
    def _get_youtube_video_info(self, video_id):
        """
        Get metadata for a YouTube video (without using YouTube API).
        
        This is a simplified implementation that only returns the video ID.
        For a complete solution, you'd need to use the YouTube Data API.
        
        Args:
            video_id (str): YouTube video ID
            
        Returns:
            dict: Dictionary containing video metadata
        """
        # In a production system, you would use the YouTube Data API to get complete video metadata
        # For this sample, we'll just return a simple dict with the video ID
        return {
            'title': f'YouTube Video Transcript'
        }
    
    def _format_youtube_transcript(self, transcript_list):
        """
        Format a YouTube transcript with timestamps.
        
        Args:
            transcript_list (list): List of transcript segments from YouTubeTranscriptApi
            
        Returns:
            str: Formatted transcript text with timestamps
        """
        formatted_lines = []
        
        for item in transcript_list:
            # Convert timestamp to MM:SS format
            timestamp = self._format_timestamp(item['start'])
            text = item['text']
            formatted_lines.append(f"[{timestamp}] {text}")
        
        return "\n".join(formatted_lines)
    
    def _format_timestamp(self, seconds):
        """
        Format timestamp in seconds to MM:SS format.
        
        Args:
            seconds (float): Timestamp in seconds
            
        Returns:
            str: Formatted timestamp
        """
        minutes = int(seconds // 60)
        remaining_seconds = int(seconds % 60)
        return f"{minutes:02d}:{remaining_seconds:02d}"