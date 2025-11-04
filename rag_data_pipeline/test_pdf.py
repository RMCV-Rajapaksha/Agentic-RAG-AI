"""
Test Script - Convert Local PDF to Markdown

This script tests the convert_document_to_markdown() function
from the Google Drive Document Reader module by using a locally
stored PDF file in the same directory.
"""

from pathlib import Path
from src.drive_reader.drive_reader import convert_document_to_markdown

def test_local_pdf_conversion():
    # Specify the local PDF file (must be in the same folder as this script)
    pdf_file = Path(__file__).parent / "A2A vs ACP.pdf"

    # Check if the file exists
    if not pdf_file.exists():
        print(f"❌ File not found: {pdf_file}")
        return

    print(f"✅ Found PDF file: {pdf_file}")
    print("Converting PDF to Markdown...\n")

    # Perform the conversion
    markdown_content = convert_document_to_markdown(str(pdf_file))

    # Display results
    if markdown_content.strip():
        print("✅ Conversion successful!")
        print("\n--- Markdown Output Preview ---\n")
        print(markdown_content)  # Print first 1000 chars only
        print("\n--- End of Preview ---")
    else:
        print("❌ Conversion failed or no text extracted from PDF.")


if __name__ == "__main__":
    test_local_pdf_conversion()
