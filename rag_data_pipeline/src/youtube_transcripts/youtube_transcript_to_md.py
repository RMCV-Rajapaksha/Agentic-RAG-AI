"""
YouTube Transcript to Markdown Converter

This module fetches YouTube video transcripts and converts them to well-formatted
Markdown with timestamps. It uses Azure OpenAI to intelligently format the raw
transcript into structured Markdown with headings and preserved timing information.
"""

# Standard library imports
import os
import re
import sys
import logging
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Third-party imports
import requests
from bs4 import BeautifulSoup
from youtube_transcript_api import YouTubeTranscriptApi

# LlamaIndex imports
from llama_index.core import Document
from llama_index.core.llms import ChatMessage
from llama_index.llms.azure_openai import AzureOpenAI

# Configure logger
logger = logging.getLogger(__name__)

# Local imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from config.constants import (
    YOUTUBE_TRANSCRIPT_FORMAT_INSTRUCTIONS
)


# ===============================
# Configuration
# ===============================
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
AZURE_OPENAI_MODEL = os.getenv('AZURE_OPENAI_MODEL')
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')
AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
AZURE_OPENAI_API_VERSION = os.getenv('AZURE_OPENAI_API_VERSION')

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

llm = AzureOpenAI(
    model=AZURE_OPENAI_MODEL,
    deployment_name=AZURE_OPENAI_DEPLOYMENT_NAME,
    api_key=AZURE_OPENAI_API_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_version=AZURE_OPENAI_API_VERSION
)



# ===============================
# Helper Functions
# ===============================

def get_video_id(url: str) -> str:
    """
    Extract video ID from YouTube URL.
    
    Args:
        url: Full YouTube video URL
        
    Returns:
        Video ID string
        
    Raises:
        ValueError: If URL format is invalid
    """
    try:
        if "v=" in url:
            return url.split("v=")[1].split("&")[0]
        elif "youtu.be/" in url:
            return url.split("youtu.be/")[1].split("?")[0]
        else:
            raise ValueError("Invalid YouTube URL format")
    except Exception as e:
        raise ValueError(f"Error extracting video ID: {e}")


def fetch_metadata(url: str) -> dict:
    """
    Scrape title and description from YouTube page.
    
    Args:
        url: YouTube video URL
        
    Returns:
        Dictionary with 'title', 'description', and 'url' keys
    """
    try:
        resp = requests.get(url, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        
        title = soup.title.string if soup.title else "No title found"
        description_tag = soup.find("meta", attrs={"name": "description"})
        description = (
            description_tag["content"]
            if description_tag
            else "No description found"
        )
        
        logger.debug(f"Fetched metadata for {url}: {title}")
        return {
            "title": title.strip(),
            "description": description.strip(),
            "url": url
        }
    except Exception as e:
        logger.error(f"Error fetching metadata for {url}: {e}", exc_info=True)
        return {
            "title": "Unknown",
            "description": f"Error fetching metadata: {e}",
            "url": url
        }


def seconds_to_timestamp(seconds: float) -> str:
    """
    Convert seconds to HH:MM:SS format.
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted timestamp as HH:MM:SS
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def segment_transcript(transcript, segment_length: int):
    """
    Segment transcript into time-based chunks.
    
    Args:
        transcript: List of transcript entries from YouTubeTranscriptApi
        segment_length: Length of each segment in seconds
        
    Returns:
        List of segments, each segment is a list of transcript entries
    """
    snippets = [
        {"text": s.text, "start": s.start, "duration": s.duration}
        for s in transcript
    ]
    
    segments = []
    current_segment = []
    current_segment_start = 0
    
    for snippet in snippets:
        while snippet["start"] >= current_segment_start + segment_length:
            if current_segment:
                segments.append(current_segment)
            else:
                segments.append([])
            current_segment = []
            current_segment_start += segment_length
        
        current_segment.append(snippet)
    
    # Append last segment
    if current_segment:
        segments.append(current_segment)
    
    return segments


def process_segment_content(
    segment,
    segment_index: int,
    segment_length: int
) -> dict:
    """
    Process a single segment and convert to markdown.
    
    Args:
        segment: List of transcript entries in the segment
        segment_index: Index of the segment for reference
        segment_length: Length of each segment in seconds
        
    Returns:
        Dictionary with 'start_seconds', 'end_seconds', 'content_markdown'
    """
    if not segment:
        return {
            "start_seconds": segment_index * segment_length,
            "end_seconds": (segment_index + 1) * segment_length,
            "content_markdown": "No content in this segment"
        }
    
    start_seconds = segment[0]["start"]
    end_seconds = segment[-1]["start"] + segment[-1]["duration"]
    
    # Format timestamps
    start_time = seconds_to_timestamp(start_seconds)
    end_time = seconds_to_timestamp(end_seconds)
    
    # Create content with individual timestamps for each sentence/phrase
    timestamped_content = []
    for s in segment:
        timestamp_seconds = s["start"]
        timestamped_content.append(f"[{timestamp_seconds:.2f}s] {s['text']}")
    
    content_with_timestamps = "\n".join(timestamped_content)

    logger.debug(f"Processing segment {segment_index}: {start_time} - {end_time}")
    logger.debug(f"Segment content length: {len(content_with_timestamps)} characters")
    
    # Convert to markdown using LLM
    try:
        messages = [
            ChatMessage(role="user", content=YOUTUBE_TRANSCRIPT_FORMAT_INSTRUCTIONS), 
            ChatMessage(role="user", content=content_with_timestamps)
        ]
        response = llm.chat(messages)

        logger.debug(f"LLM formatting completed for segment {segment_index}")

        markdown_content = (
            f"**Time Range: {start_time} - {end_time}**\n\n"
            f"{response.message.content}"
        )
    except Exception as e:
        logger.error(f"Error processing segment {segment_index} with LLM: {e}", exc_info=True)
        markdown_content = (
            f"**Time Range: {start_time} - {end_time}**\n\n"
            f"Error processing content: {e}\n\n"
            f"Original content:\n{content_with_timestamps}"
        )
    
    return {
        "start_seconds": start_seconds,
        "end_seconds": end_seconds,
        "content_markdown": markdown_content
    }


# ===============================
# Main Functions
# ===============================

def get_transcript_segments(
    url: str,
    language: str = "en",
    segment_length_minutes: int = 10
) -> dict:
    """
    Get segmented transcript and metadata from a YouTube video.
    
    Args:
        url: YouTube video URL
        language: Language code for transcript (default: "en")
        segment_length_minutes: Length of each segment in minutes (default: 10)
        
    Returns:
        Dictionary with 'url', 'metadata', 'segments' (array of segment objects)
    """
    segment_length = segment_length_minutes * 60
    
    try:
        video_id = get_video_id(url)
    except Exception as e:
        logger.error(f"Failed to extract video ID from {url}: {e}")
        metadata = fetch_metadata(url)
        return {
            "url": url,
            "metadata": metadata,
            "segments": [{
                "start_seconds": 0,
                "end_seconds": 0,
                "content_markdown": f"Transcript not available: {e}"
            }]
        }
    
    metadata = fetch_metadata(url)
    
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript = ytt_api.fetch(video_id, languages=[language])
        
        logger.info(f"Fetched transcript for video {video_id}")
        
        # Segment the transcript
        segments = segment_transcript(transcript, segment_length)
        logger.info(f"Segmented transcript into {len(segments)} segments")
        
        # Process each segment
        processed_segments = []
        for i, segment in enumerate(segments):
            processed_segment = process_segment_content(
                segment, i, segment_length
            )
            processed_segments.append(processed_segment)
        
        logger.info(f"Processed all {len(processed_segments)} segments for video {video_id}")
        
        return {
            "url": url,
            "metadata": metadata,
            "segments": processed_segments
        }
        
    except Exception as e:
        logger.error(f"Error fetching transcript for {url}: {e}", exc_info=True)
        return {
            "url": url,
            "metadata": metadata,
            "segments": [{
                "start_seconds": 0,
                "end_seconds": 0,
                "content_markdown": f"Transcript not available: {e}"
            }]
        }


def process_youtube_videos(
    urls: List[str],
    segment_length_minutes: int = 10
) -> List[Document]:
    """
    Process YouTube videos and return document segments.
    
    Args:
        urls: List of YouTube video URLs
        segment_length_minutes: Length of each segment in minutes (default: 10)
        
    Returns:
        List of Document objects, one per segment
    """
    documents = []
    logger.info(f"Processing {len(urls)} YouTube videos for transcript segments...")
    
    for link in urls:
        try:
            video_data = get_transcript_segments(
                link,
                language="en",
                segment_length_minutes=segment_length_minutes
            )
            
            for segment in video_data['segments']:
                video_doc = Document(
                    text=segment['content_markdown'],
                    metadata={
                        'url': video_data['url'],
                        'title': video_data['metadata'].get('title', ''),
                        'description': video_data['metadata'].get('description', ''),
                        'source': 'youtube_transcript',
                        'start_seconds': segment['start_seconds'],
                        'end_seconds': segment['end_seconds'],
                    }
                )
                documents.append(video_doc)
            
            logger.info(f"Processed {len(video_data['segments'])} segments from {link}")
            
        except Exception as e:
            logger.error(f"Error processing YouTube video {link}: {e}", exc_info=True)
    
    logger.info(f"Total YouTube documents processed: {len(documents)}")
    return documents


