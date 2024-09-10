import cv2
import numpy as np
from PIL import Image
import pytesseract
import re

def load_image(image_path):
    """Load an image from the specified path."""
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Image at path {image_path} could not be loaded. Check the path and file.")
    return image

def resize_image(image, scale_factor=3):
    """Resize the image by a given scale factor."""
    width = int(image.shape[1] * scale_factor)
    height = int(image.shape[0] * scale_factor)
    dim = (width, height)
    resized_image = cv2.resize(image, dim, interpolation=cv2.INTER_CUBIC)
    return resized_image

def enhance_image(image):
    """Enhance the image by converting to grayscale, thresholding, and cleaning."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Adaptive Thresholding might work better for uneven lighting
    enhanced_image = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                           cv2.THRESH_BINARY_INV, 11, 2)
    kernel = np.ones((2, 2), np.uint8)
    cleaned_image = cv2.morphologyEx(enhanced_image, cv2.MORPH_CLOSE, kernel)
    return cleaned_image

def extract_text_from_image(image):
    """Extract text from the image using pytesseract."""
    # Convert the OpenCV image to PIL image for pytesseract
    pil_image = Image.fromarray(image)
    extracted_text = pytesseract.image_to_string(pil_image, config='--psm 8').strip()
    return extracted_text

def sanitize_text(text):
    """Sanitize text to only allow valid arithmetic expressions."""
    # Remove any non-numeric or operator characters
    sanitized_text = re.sub(r'[^0-9+\-*/]', '', text)
    return sanitized_text

def process_text(text):
    """Process the sanitized text as an arithmetic expression."""
    sanitized_text = sanitize_text(text)
    try:
        # Evaluate the arithmetic expression
        result = eval(sanitized_text)
    except Exception as e:
        print(f"Error evaluating expression: {e}")
        result = None
    return result

def process_image(image_path):
    """Process the image to extract and solve the arithmetic CAPTCHA."""
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    
    # Load the image
    image = load_image(image_path)
    
    # Resize the image to improve readability
    resized_image = resize_image(image)
    
    # Enhance the image quality
    enhanced_image = enhance_image(resized_image)
    
    # Extract text from the enhanced image
    text = extract_text_from_image(enhanced_image)
    
    return text

if __name__ == "__main__":
    # Path to your small image
    image_path = "captcha.png"
    
    # Process the image and extract text
    text = process_image(image_path)
    
    # Solve the arithmetic problem
    result = process_text(text)
    
    if result is not None:
        print(f"Extracted Text: {text}")
        print(f"Solved CAPTCHA result: {result}")
    else:
        print(f"Failed to solve the CAPTCHA. Extracted Text: {text}")
