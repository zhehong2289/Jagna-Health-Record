# utils/ocr.py - Add this function
import pytesseract
import cv2
import numpy as np
import re

def extract_text_from_roi(roi, field_name=None):
    """
    Extract text from a region of interest (ROI) in an image using OCR
    Args:
        roi: numpy array, the image region to process
        field_name: str, optional, the field name for custom OCR config
    Returns:
        str: extracted text from the region
    """
    # Guard: empty or invalid ROI
    if roi is None:
        return ""
    if getattr(roi, 'size', 0) == 0:
        return ""

    # Convert to grayscale if the image is in color
    if len(roi.shape) == 3:
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    else:
        gray = roi

    # Apply adaptive thresholding for better handling of different lighting conditions
    binary = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11,
        2
    )

    # Apply some noise reduction
    kernel = np.ones((1, 1), np.uint8)
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

    # Save ROI for debugging if systolic/diastolic
    if field_name in ['systolic', 'diastolic']:
        cv2.imwrite(f'debug_roi_{field_name}.png', binary)

    # Use tesseract with specific configuration for better number recognition
    if field_name in ['systolic', 'diastolic']:
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789'
    else:
        custom_config = r'--oem 3 --psm 6'
    try:
        text = pytesseract.image_to_string(binary, config=custom_config).strip()
    except Exception:
        return ""
    return text

def clean_extracted_text(text, field_name):
    """Clean up extracted text by removing field labels"""
    # Remove common field labels
    patterns = {
        'name': r'(?i)(name\s*:?\s*)',
        'age': r'(?i)(age\s*:?\s*)', 
        'feedback': r'(?i)(feedback\s*:?\s*)'
    }
    
    if field_name in patterns:
        text = re.sub(patterns[field_name], '', text)
    
    # Special handling for feedback to preserve meaningful spacing
    if field_name == 'feedback':
        # Replace multiple newlines (3 or more) with double newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        # Clean up any remaining multiple spaces within lines
        text = re.sub(r'([^\n]) +', r'\1 ', text)
        # Remove spaces at the start of lines
        text = re.sub(r'(?m)^ +', '', text)
        # Remove spaces at the end of lines
        text = re.sub(r'(?m) +$', '', text)
        # Ensure consistent paragraph breaks
        text = re.sub(r'\n\n+', '\n\n', text)
        text = text.strip()
    else:
        # For other fields, collapse all whitespace to single spaces
        text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def extract_fields(image, field_config):
    """Extract all fields from form based on configuration"""
    results = {}
    
    # Validate image
    if image is None:
        raise ValueError("Input image is None. Check image decoding (cv2.imdecode) in the caller.")

    img_h, img_w = image.shape[:2]

    for field_name, coords in field_config.items():
        # Validate coords structure
        if not isinstance(coords, dict):
            results[field_name] = ""
            continue

        # Ensure required keys exist
        try:
            x = int(coords['x'])
            y = int(coords['y'])
            w = int(coords['width'])
            h = int(coords['height'])
        except Exception:
            # missing or invalid coords - skip
            results[field_name] = ""
            continue

        # Clamp coordinates to image bounds
        if x < 0:
            x = 0
        if y < 0:
            y = 0
        if w < 0 or h < 0:
            results[field_name] = ""
            continue

        x2 = min(x + w, img_w)
        y2 = min(y + h, img_h)

        # If ROI is empty after clamping, skip
        if x >= x2 or y >= y2:
            results[field_name] = ""
            continue

        # This block should be inside the loop - fixing indentation
        roi = image[y:y2, x:x2]
        
        # Save ROI for debugging - now saving for all fields
        cv2.imwrite(f'debug_roi_{field_name}.png', roi)
        
        # Safely extract text (extract_text_from_roi now handles empty ROI)
        text = extract_text_from_roi(roi, field_name)

        # Clean the extracted text
        cleaned_text = clean_extracted_text(text, field_name)
        results[field_name] = cleaned_text
    
    return results


