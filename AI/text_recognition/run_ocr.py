import os
from paddleocr import PaddleOCR

# Initialize OCR
ocr = PaddleOCR(use_angle_cls=True, lang="en")

def get_ocr_text(image_path):
    # Check if the file exists
    if not os.path.isfile(image_path):
        print(f"Error: File '{image_path}' not found! Check the path.")
        return ""  # Return empty if file doesn't exist

    # Run OCR if the file exists
    res_text = ""
    result = ocr.ocr(image_path, cls=True)

    extracted_text = [word[1][0] for line in result for word in line]
    for line in extracted_text:
        res_text += line + "\n"

    return res_text.strip()  # Return without trailing newline

# For standalone testing (remove if you're importing this module elsewhere)
if __name__ == "__main__":
    text = get_ocr_text("image.png")
    print(text)
