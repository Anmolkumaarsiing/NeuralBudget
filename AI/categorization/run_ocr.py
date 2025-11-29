import os
import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv

# Load env
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")


if api_key:
    genai.configure(api_key=api_key)
else:
    print("Warning: GEMINI_API_KEY or GOOGLE_API_KEY not found in environment variables.")

def get_ocr_text(image_path):
    """
    Extracts text from an image using Google Gemini 1.5 Flash.
    """
    # Check if the file exists
    if not os.path.isfile(image_path):
        print(f"Error: File '{image_path}' not found! Check the path.")
        return ""

    if not api_key:
        print("Error: API key not configured. Cannot run Gemini OCR.")
        return ""

    print("Processing OCR with Gemini...")
    try:

        model = genai.GenerativeModel(gemini-flash-lite-latest)
        
        # Use context manager to ensure file is closed
        with Image.open(image_path) as img:
            # Prompt for pure text extraction
            response = model.generate_content(["Check whether the image is for screenshot of a trancastion via any UPI app. If yes then, extract all text from this image verbatim. Do not add any markdown formatting or explanations, just the raw text. If no, Just repond Not a screenshot.", img])
            
            if response.text:
                cleaned_text = response.text.strip()
                # Check for the specific rejection phrase from the prompt
                if "Not a screenshot" in cleaned_text:
                    print("Gemini rejected image: Not a transaction screenshot.")
                    return ""
                return cleaned_text
            else:
                print("Gemini returned empty response.")
                return ""
            
    except Exception as e:
        print(f"Error during Gemini OCR: {e}")
        return ""