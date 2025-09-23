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


class YouTubeTranscriptScraper:

    """Scraper to fetch and segment YouTube video transcripts into Markdown format.
    Uses YouTubeTranscriptApi to get transcripts, segments them into time-based chunks,
    and processes each chunk with an LLM to convert to Markdown.   """

    def __init__(self, language="en", segment_length_minutes=10):
        self.language = language
        self.segment_length = segment_length_minutes * 60  

        
    def _get_video_id(self, url: str) -> str:
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
        

    
    def _fetch_metadata(self, url: str) -> dict:
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
    
    def _seconds_to_timestamp(self, seconds: float) -> str:
        """Convert seconds to HH:MM:SS format
        Args:
            seconds (float): Time in seconds
        Returns:
            str: Formatted timestamp as HH:MM:SS
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        

    
    def _segment_transcript(self, transcript):
        """Segment transcript into time-based chunks
        Args:
            transcript (list): List of transcript entries from YouTubeTranscriptApi
        Returns:
            list of segments, each segment is a list of transcript entries
        
        """
      
        snippets = [{"text": s.text, "start": s.start, "duration": s.duration} for s in transcript]
        
        segments = []
        current_segment = []
        current_segment_start = 0
        
        for snippet in snippets:
         
            while snippet["start"] >= current_segment_start + self.segment_length:
                if current_segment:
                    segments.append(current_segment)
                else:
                    segments.append([])  
                current_segment = []
                current_segment_start += self.segment_length
            
            current_segment.append(snippet)
        
        # Append last segment
        if current_segment:
            segments.append(current_segment)
        
        return segments
    

    
    def _process_segment_content(self, segment, segment_index):
        """Process a single segment and convert to markdown
        Args:
            segment (list): List of transcript entries in the segment
            segment_index (int): Index of the segment for reference
        Returns:
            dict with 'start_seconds', 'end_seconds', 'content_markdown'
        
        """
        if not segment:
            return {
                "start_seconds": segment_index * self.segment_length,
                "end_seconds": (segment_index + 1) * self.segment_length,
                "content_markdown": "No content in this segment"
            }
        
        start_seconds = segment[0]["start"]
        end_seconds = segment[-1]["start"] + segment[-1]["duration"]
        
        # Format timestamps
        start_time = self._seconds_to_timestamp(start_seconds)
        end_time = self._seconds_to_timestamp(end_seconds)
        
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
            enhanced_instructions = instructions_for_llm + """
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
        """Original method - returns full transcript as single markdown with timestamps"""
        result = self.get_transcript_segments(url)
        
        # Combine all segments into one markdown with timestamps
        combined_markdown = ""
        for i, segment in enumerate(result["segments"], 1):
            start_time = self._seconds_to_timestamp(segment["start_seconds"])
            end_time = self._seconds_to_timestamp(segment["end_seconds"])
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
    
    # Create scraper with 10-minute segments (default)
    scraper = YouTubeTranscriptScraper(segment_length_minutes=10)
    
    # Get segmented transcript
    result = scraper.get_transcript_segments(yt_url)

    print("Video URL:", result)
    
    print("Metadata:", result["metadata"])
    
    # Print first few segments
    for i, segment in enumerate(result["segments"][:3]):  # Show first 3 segments
        print(f"\n=== Segment {i + 1} ===")
        print(f"Time: {segment['start_seconds']} - {segment['end_seconds']} seconds")
        print(f"Content preview: {segment['content_markdown'][:200]}...")
        
        if i >= 2:  # Limit output for demo
            break