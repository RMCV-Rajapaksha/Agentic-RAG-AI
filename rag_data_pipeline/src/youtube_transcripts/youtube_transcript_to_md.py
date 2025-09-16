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
instructions_for_llm =  """  "You are a formatter. "
                    "Your ONLY job is to take the given text and reformat it into Markdown. "
                    "Do not summarize, change wording, or drop any content. "
                    "Keep all words exactly as provided, only improve spacing, "
                    "line breaks, and basic Markdown structure (headings, lists, paragraphs). "
                """


class YouTubeTranscriptScraper:
    def __init__(self, language="en"):
        self.language = language

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

    def get_transcript(self, url: str) -> dict:
        """
        Get transcript + metadata from a YouTube video.

        Args:
            url (str): YouTube video URL

        Returns:
            dict with 'url', 'metadata', 'content_markdown'
        """
        try:
            video_id = self._get_video_id(url)
        except Exception as e:
            # If video ID extraction fails, return error info but continue program
            metadata = self._fetch_metadata(url)
            return {
                "url": url,
                "metadata": metadata,
                "content_markdown": f"Transcript not available: {e}"
            }

        metadata = self._fetch_metadata(url)
        try:
            ytt_api = YouTubeTranscriptApi()
            transcript = ytt_api.fetch(video_id, languages=[self.language])
            paragraph = " ".join(getattr(item, "text", str(item)) for item in transcript)
            messages = [ChatMessage(role="user", content=instructions_for_llm), ChatMessage(role="user", content=paragraph)]
            response = llm.chat(messages)
            markdown = response.message.content
        except Exception as e:
            markdown = f"Transcript not available: {e}"

        return {
            "url": url,
            "metadata": metadata,
            "content_markdown": markdown
        }


# Example usage
if __name__ == "__main__":
    yt_url = "https://www.youtube.com/watch?v=LtcHVLkkxjk"
    scraper = YouTubeTranscriptScraper()
    result = scraper.get_transcript(yt_url)

    print("Metadata:", result["metadata"])
    print("\nTranscript Paragraph:\n", result["content_markdown"][:500], "...")
