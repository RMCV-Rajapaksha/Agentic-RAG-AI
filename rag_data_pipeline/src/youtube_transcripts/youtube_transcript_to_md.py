from youtube_transcript_api import YouTubeTranscriptApi
import requests
from bs4 import BeautifulSoup
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from llama_index.llms.openai import OpenAI
from llama_index.core.llms import ChatMessage
from config.config import get_openai_api_key

# Initialize configuration and LLM
os.environ["OPENAI_API_KEY"] = get_openai_api_key()

llm = OpenAI(
    model="gpt-4o-mini",
    api_key=get_openai_api_key()
)

INSTRUCTIONS_FOR_LLM = """You are a formatter. 
                            Your ONLY job is to take the given text and reformat it into Markdown. 
                            Do not summarize, drop any content, or change the wording of the paragraph text. 
                            Keep all words exactly as provided for the paragraph/description. 
                            Generate headings only for key or important points. Only these headings should have timestamps.  
                            
                            Rules:
                            - Generate meaningful headings based on key points in the transcript.  
                            - Use # for main sections, ## for subsections, ### for sub-subsections.  
                            - Include timestamps in headings only for very important points.  
                            - Timestamps should use the format [seconds.s], e.g., [4460.32s], not hh:mm:ss.  
                            - All other sentences remain as paragraphs under the nearest heading.  
                            
                            Example:
                            
                            Input:
                            [3.00s] retrieval augmented generation over
                            [5.00s] video corpus now we all know rag
                            [8.00s] retrieval augmented generation we put in a query then it goes and get the retrieval query asking a database
                            [12.00s] and we get back the retrieved text and then we construct the full prompt and we get the response
                            
                            Output:
                            # [3.00s] Introduction to Retrieval-Augmented Generation
                            retrieval augmented generation over
                            video corpus now we all know rag
                            
                            ## [8.00s] Query Processing in RAG
                            retrieval augmented generation we put in a query then it goes and get the retrieval query asking a database
                            and we get back the retrieved text and then we construct the full prompt and we get the response
                            """


# ===============================
# Helper Functions
# ===============================

def get_video_id(url: str) -> str:
    """Extract video ID from YouTube URL
    Args:
        url (str): Full YouTube video URL
    Returns:
        str: Video ID
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
    """Scrape title & description from YouTube page
    Args:
        url (str): YouTube video URL
    Returns:
        dict: Metadata with 'title', 'description', 'url'
    """
    try:
        resp = requests.get(url, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        title = soup.title.string if soup.title else "No title found"
        description_tag = soup.find("meta", attrs={"name": "description"})
        description = description_tag["content"] if description_tag else "No description found"
        return {
            "title": title.strip(),
            "description": description.strip(),
            "url": url
        }
    except Exception as e:
        return {
            "title": "Unknown",
            "description": f"Error fetching metadata: {e}",
            "url": url
        }


def seconds_to_timestamp(seconds: float) -> str:
    """Convert seconds to HH:MM:SS format
    Args:
        seconds (float): Time in seconds
    Returns:
        str: Formatted timestamp as HH:MM:SS
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def segment_transcript(transcript, segment_length: int):
    """Segment transcript into time-based chunks
    Args:
        transcript (list): List of transcript entries from YouTubeTranscriptApi
        segment_length (int): Length of each segment in seconds
    Returns:
        list of segments, each segment is a list of transcript entries
    """
    snippets = [{"text": s.text, "start": s.start, "duration": s.duration} for s in transcript]
    
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


def process_segment_content(segment, segment_index: int, segment_length: int) -> dict:
    """Process a single segment and convert to markdown
    Args:
        segment (list): List of transcript entries in the segment
        segment_index (int): Index of the segment for reference
        segment_length (int): Length of each segment in seconds
    Returns:
        dict with 'start_seconds', 'end_seconds', 'content_markdown'
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

    print("-----------------------------")
    print(content_with_timestamps)
    print("-----------------------------")
    
    # Convert to markdown using LLM
    try:
        enhanced_instructions = INSTRUCTIONS_FOR_LLM + """
        Keep all timestamps in the format [XXX.XXs] at the beginning of each line.
        Preserve the timestamp information exactly as provided in seconds format.
        """
        messages = [
            ChatMessage(role="user", content=enhanced_instructions), 
            ChatMessage(role="user", content=content_with_timestamps)
        ]
        response = llm.chat(messages)

        print("-----------------------------")
        print("LLM response:", response.message.content)
        print("-----------------------------")

        markdown_content = f"**Time Range: {start_time} - {end_time}**\n\n{response.message.content}"
    except Exception as e:
        markdown_content = f"**Time Range: {start_time} - {end_time}**\n\nError processing content: {e}\n\nOriginal content:\n{content_with_timestamps}"
    
    return {
        "start_seconds": start_seconds,
        "end_seconds": end_seconds,
        "content_markdown": markdown_content
    }


# ===============================
# Main Functions
# ===============================

def get_transcript_segments(url: str, language: str = "en", segment_length_minutes: int = 10) -> dict:
    """
    Get segmented transcript + metadata from a YouTube video.
    
    Args:
        url (str): YouTube video URL
        language (str): Language code for transcript (default: "en")
        segment_length_minutes (int): Length of each segment in minutes (default: 10)
        
    Returns:
        dict with 'url', 'metadata', 'segments' (array of segment objects)
    """
    segment_length = segment_length_minutes * 60
    
    try:
        video_id = get_video_id(url)
    except Exception as e:
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
        
        # Segment the transcript
        segments = segment_transcript(transcript, segment_length)
        
        # Process each segment
        processed_segments = []
        for i, segment in enumerate(segments):
            processed_segment = process_segment_content(segment, i, segment_length)
            processed_segments.append(processed_segment)
        
        return {
            "url": url,
            "metadata": metadata,
            "segments": processed_segments
        }
        
    except Exception as e:
        return {
            "url": url,
            "metadata": metadata,
            "segments": [{
                "start_seconds": 0,
                "end_seconds": 0,
                "content_markdown": f"Transcript not available: {e}"
            }]
        }


def get_transcript(url: str, language: str = "en", segment_length_minutes: int = 10) -> dict:
    """Get full transcript as single markdown with timestamps
    
    Args:
        url (str): YouTube video URL
        language (str): Language code for transcript (default: "en")
        segment_length_minutes (int): Length of each segment in minutes (default: 10)
        
    Returns:
        dict with 'url', 'metadata', 'content_markdown' (combined from all segments)
    """
    result = get_transcript_segments(url, language, segment_length_minutes)
    
    # Combine all segments into one markdown with timestamps
    combined_markdown = ""
    for i, segment in enumerate(result["segments"], 1):
        start_time = seconds_to_timestamp(segment["start_seconds"])
        end_time = seconds_to_timestamp(segment["end_seconds"])
        combined_markdown += f"\n\n## Segment {i} ({start_time} - {end_time})\n\n"
        combined_markdown += segment["content_markdown"]
    
    return {
        "url": result["url"],
        "metadata": result["metadata"],
        "content_markdown": combined_markdown.strip()
    }



# Example usage
if __name__ == "__main__":
    yt_url = "https://www.youtube.com/watch?v=LtcHVLkkxjk"
    
    # Get segmented transcript with 10-minute segments
    result = get_transcript_segments(yt_url, language="en", segment_length_minutes=10)

    print("Video URL:", result["url"])
    
    print("Metadata:", result["metadata"])
    
    # Print first few segments
    for i, segment in enumerate(result["segments"][:3]):  # Show first 3 segments
        print(f"\n=== Segment {i + 1} ===")
        print(f"Time: {segment['start_seconds']} - {segment['end_seconds']} seconds")
        print(f"Content preview: {segment['content_markdown'][:200]}...")
        
        if i >= 2:  # Limit output for demo
            break