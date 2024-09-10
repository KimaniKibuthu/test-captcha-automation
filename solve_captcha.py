import cv2
import numpy as np
from PIL import Image
import pytesseract

class CaptchaSolver:
    def __init__(self, image_path):
        self.image = cv2.imread(image_path)
        if self.image is None:
            raise ValueError(f"Image at path {image_path} could not be loaded. Check the path and file.")
        print(f"Original image shape: {self.image.shape}")

    def resize_image(self, image, scale_factor=2):
        """Resize the image by a given scale factor."""
        width = int(image.shape[1] * scale_factor)
        height = int(image.shape[0] * scale_factor)
        dim = (width, height)
        resized_image = cv2.resize(image, dim, interpolation=cv2.INTER_CUBIC)
        return resized_image

    def enhance_legibility(self, image):
        """Enhance the legibility of the image."""
        if image is None or image.size == 0:
            raise ValueError("Empty or invalid image passed for enhancement.")
        print(f"Enhancing image with shape: {image.shape}")
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Apply thresholding
        _, thresh_image = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
        # Apply morphological operations to clean up noise
        cleaned_image = cv2.morphologyEx(thresh_image, cv2.MORPH_CLOSE, self.kernel)
        return cleaned_image

    def extract_text(self, image_path):
        """Extract text from image using pytesseract."""
        img = Image.open(image_path)
        extracted_text = pytesseract.image_to_string(img, config='--psm 7').strip()
        return extracted_text

    def math_operation(self, left_number, right_number):
        """Perform mathematical operation."""
        if right_number.isdigit():
            return eval(f"{left_number} + {right_number}")
        return None

    def resolve(self, left_image_path, right_image_path, left_image_twice_path, right_image_twice_path):
        """Resolve CAPTCHA by extracting and computing numbers."""
        left_number_text = self.extract_text(left_image_twice_path)
        print(f"Extracted left number (twice): {left_number_text}")
        if left_number_text.isdigit():
            left_number = int(left_number_text)
            right_number_text = self.extract_text(right_image_twice_path)
            print(f"Extracted right number (twice): {right_number_text}")
            if right_number_text.isdigit() and int(right_number_text) > 10:
                return self.math_operation(left_number, right_number_text)
            else:
                right_number_text = self.extract_text(right_image_path)
                print(f"Extracted right number (unit): {right_number_text}")
                return self.math_operation(left_number, right_number_text)
        else:
            left_number_text = self.extract_text(left_image_path)
            print(f"Extracted left number (unit): {left_number_text}")
            if left_number_text.isdigit():
                right_number_text = self.extract_text(right_image_path)
                print(f"Extracted right number (unit): {right_number_text}")
                return self.math_operation(left_number_text, right_number_text)

    def solve_captcha(self):
        """Solve the CAPTCHA image and return the result."""
        positions = {'left': 5, 'right_unit': 57, 'right_twice': 71}
        dimensions = {'width_twice': 31, 'width_unit': 19, 'height': 20}

        # Crop images for each number
        left_image_for_unit_number = self.image[7:30, positions['left']:positions['left'] + dimensions['width_unit']]
        left_image_for_twice_number = self.image[7:30, positions['left']:positions['left'] + dimensions['width_twice']]
        right_image_for_left_twice_number = self.image[7:30, positions['right_twice']:positions['right_twice'] + dimensions['width_twice']]
        right_image_for_left_unit_number = self.image[7:30, positions['right_unit']:positions['right_unit'] + dimensions['width_twice']]

        # Check if cropped images are empty
        for img, name in zip([left_image_for_unit_number, left_image_for_twice_number, right_image_for_left_twice_number, right_image_for_left_unit_number], 
                             ['left_image_for_unit_number', 'left_image_for_twice_number', 'right_image_for_left_twice_number', 'right_image_for_left_unit_number']):
            if img.size == 0:
                raise ValueError(f"Cropped image {name} is empty. Check cropping coordinates.")

        # Resize and enhance images
        left_image_for_unit_number = self.resize_image(left_image_for_unit_number)
        left_image_for_twice_number = self.resize_image(left_image_for_twice_number)
        right_image_for_left_twice_number = self.resize_image(right_image_for_left_twice_number)
        right_image_for_left_unit_number = self.resize_image(right_image_for_left_unit_number)

        left_enhanced = self.enhance_legibility(left_image_for_unit_number)
        left_enhanced_for_twice_number = self.enhance_legibility(left_image_for_twice_number)
        right_enhanced = self.enhance_legibility(right_image_for_left_unit_number)
        right_enhanced_for_twice_number = self.enhance_legibility(right_image_for_left_twice_number)

        # Save enhanced images
        cv2.imwrite('left_number.png', left_enhanced)
        cv2.imwrite('left_image_for_twice_number.png', left_enhanced_for_twice_number)
        cv2.imwrite('right_number.png', right_enhanced)
        cv2.imwrite('right_image_for_twice_number.png', right_enhanced_for_twice_number)

        return self.resolve('left_number.png', 'right_number.png', 'left_image_for_twice_number.png', 'right_image_for_twice_number.png')

if __name__ == '__main__':
    solver = CaptchaSolver("captcha.png")
    result = solver.solve_captcha()
    if result is not None:
        print(f"CAPTCHA solved successfully: {result}")
    else:
        print("Failed to solve CAPTCHA.")