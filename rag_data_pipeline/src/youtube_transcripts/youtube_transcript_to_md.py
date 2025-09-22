from youtube_transcript_api import YouTubeTranscriptApi
import requests
from bs4 import BeautifulSoup
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from llama_index.llms.openai import OpenAI
from llama_index.core.llms import ChatMessage
from config.config import get_config

config = get_config()
os.environ["OPENAI_API_KEY"] = config.openai_api_key
llm = OpenAI(model="gpt-4o-mini", temperature=0)

instructions_for_llm = """You are a formatter. 
Your ONLY job is to take the given text and reformat it into Markdown. 
Do not summarize, change wording, or drop any content. 
Keep all words exactly as provided, only improve spacing, 
line breaks, and basic Markdown structure (headings, lists, paragraphs)."""

class YouTubeTranscriptScraper:
    def __init__(self, language="en", segment_length_minutes=10):
        self.language = language
        self.segment_length = segment_length_minutes * 60  

        
    def _get_video_id(self, url: str) -> str:
        """Extract video ID from YouTube URL"""
        try:
            if "v=" in url:
                return url.split("v=")[1].split("&")[0]
            elif "youtu.be/" in url:
                return url.split("youtu.be/")[1].split("?")[0]
            else:
                raise ValueError("Invalid YouTube URL format")
        except Exception as e:
            raise ValueError(f"Error extracting video ID: {e}")
    
    def _fetch_metadata(self, url: str) -> dict:
        """Scrape title & description from YouTube page"""
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
    
    def _format_time(self, seconds):
        """Format timestamp nicely"""
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        return f"{h:02d}:{m:02d}:{s:02d}"
    
    def _segment_transcript(self, transcript):
        """Segment transcript into time-based chunks"""
      
        snippets = [{"text": s.text, "start": s.start, "duration": s.duration} for s in transcript]
        
        segments = []
        current_segment = []
        current_segment_start = 0
        
        for snippet in snippets:
         
            while snippet["start"] >= current_segment_start + self.segment_length:
                if current_segment:
                    segments.append(current_segment)
                else:
                    segments.append([])  # empty segment for skipped time
                current_segment = []
                current_segment_start += self.segment_length
            
            current_segment.append(snippet)
        
        # Append last segment
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def _process_segment_content(self, segment, segment_index):
        """Process a single segment and convert to markdown"""
        if not segment:
            return {
                "start_seconds": segment_index * self.segment_length,
                "end_seconds": (segment_index + 1) * self.segment_length,
                "content_markdown": "No content in this segment"
            }
        
        start_seconds = segment[0]["start"]
        end_seconds = segment[-1]["start"] + segment[-1]["duration"]
        content = " ".join(s["text"] for s in segment)
        
        # Convert to markdown using LLM
        try:
            messages = [
                ChatMessage(role="user", content=instructions_for_llm), 
                ChatMessage(role="user", content=content)
            ]
            response = llm.chat(messages)
            markdown_content = response.message.content
        except Exception as e:
            markdown_content = f"Error processing content: {e}\n\nOriginal content:\n{content}"
        
        return {
            "start_seconds": start_seconds,
            "end_seconds": end_seconds,
            "content_markdown": markdown_content
        }
    
    def get_transcript_segments(self, url: str) -> dict:
        """
        Get segmented transcript + metadata from a YouTube video.
        
        Args:
            url (str): YouTube video URL
            
        Returns:
            dict with 'url', 'metadata', 'segments' (array of segment objects)
        """
        try:
            video_id = self._get_video_id(url)
        except Exception as e:
            metadata = self._fetch_metadata(url)
            return {
                "url": url,
                "metadata": metadata,
                "segments": [{
                    "start_seconds": 0,
                    "end_seconds": 0,
                    "content_markdown": f"Transcript not available: {e}"
                }]
            }
        
        metadata = self._fetch_metadata(url)
        
        try:
            ytt_api = YouTubeTranscriptApi()
            transcript = ytt_api.fetch(video_id, languages=[self.language])
            
            # Segment the transcript
            segments = self._segment_transcript(transcript)
            
            # Process each segment
            processed_segments = []
            for i, segment in enumerate(segments):
                processed_segment = self._process_segment_content(segment, i)
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
    
    # Keep the original method for backward compatibility
    def get_transcript(self, url: str) -> dict:
        """Original method - returns full transcript as single markdown"""
        result = self.get_transcript_segments(url)
        
        # Combine all segments into one markdown
        combined_markdown = ""
        for i, segment in enumerate(result["segments"], 1):
            combined_markdown += f"\n\n## Segment {i}\n\n"
            combined_markdown += segment["content_markdown"]
        
        return {
            "url": result["url"],
            "metadata": result["metadata"],
            "content_markdown": combined_markdown.strip()
        }

# Example usage
if __name__ == "__main__":
    yt_url = "https://www.youtube.com/watch?v=-nwIoiPB8CE"
    
    # Create scraper with 10-minute segments (default)
    scraper = YouTubeTranscriptScraper(segment_length_minutes=10)
    
    # Get segmented transcript
    result = scraper.get_transcript_segments(yt_url)
    
    print("Metadata:", result["metadata"])
    
    # Print first few segments
    for i, segment in enumerate(result["segments"][:3]):  # Show first 3 segments
        print(f"\n=== Segment {i + 1} ===")
        print(f"Time: {segment['start_seconds']} - {segment['end_seconds']} seconds")
        print(f"Content preview: {segment['content_markdown'][:200]}...")
        
        if i >= 2:  # Limit output for demo
            break