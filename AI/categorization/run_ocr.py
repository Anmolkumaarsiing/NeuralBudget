import os
import logging
from paddleocr import PaddleOCR

# Suppress PaddleOCR logging
logging.getLogger('ppocr').setLevel(logging.ERROR)

# Initialize OCR
ocr = PaddleOCR(use_angle_cls=True, lang="en", show_log=False)

def get_ocr_text(image_path):
    # Check if the file exists
    if not os.path.isfile(image_path):
        print(f"Error: File '{image_path}' not found! Check the path.")
        return ""  # Return empty if file doesn't exist

    # Run OCR if the file exists
    print("Processing OCR")
    res_text = ""
    result = ocr.ocr(image_path, cls=True)

    # The result is a list containing one element for the single image processed.
    # It can be None or contain None if no text is found.
    if not result or not result[0]:
        return ""

    image_result = result[0]
    
    extracted_texts = []
    for line in image_result:
        # Each line is a list containing the bounding box and a tuple of (text, confidence)
        if line and len(line) > 1 and isinstance(line[1], tuple) and len(line[1]) > 0:
            extracted_texts.append(line[1][0])

    return "\n".join(extracted_texts).strip()