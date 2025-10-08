import requests
from urllib.parse import urlparse

def read_github_file(github_url):
    """
    Read content from a GitHub file URL and return the text content.
    
    Args:
        github_url (str): GitHub file URL
        
    Returns:
        str: File content or None if error
    """
    try:
        # Convert GitHub blob URL to raw URL
        if 'github.com' in github_url and '/blob/' in github_url:
            raw_url = github_url.replace('github.com', 'raw.githubusercontent.com').replace('/blob/', '/')
        else:
            raw_url = github_url
            
        # Make HTTP request to get file content
        response = requests.get(raw_url)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        return response.text
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching file: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def main():
    # GitHub repository README.md URL
    github_url = "https://github.com/RMCV-Rajapaksha/A2A-Project/blob/main/README.md"
    
    print("Fetching README.md content from GitHub repository...")
    print(f"URL: {github_url}")
    print("-" * 80)
    
    # Read the file content
    content = read_github_file(github_url)
    
    if content:
        print("README.md Content:")
        print("=" * 80)
        print(content)
        print("=" * 80)
        print(f"Total characters: {len(content)}")
    else:
        print("Failed to fetch the file content.")

if __name__ == "__main__":
    main()