import numpy as np
import re
import easyocr
import cv2
import numpy as np
from .models import Manuals
from difflib import SequenceMatcher
from sqlalchemy import select, or_
from sqlalchemy.orm import Session
import uuid


def resize_image(image, max_width=800):
    """Resizes the image (from memory Numpy array) for faster excecution, using the cv2 library.
    Resize only occurs if the image width is larger than 800 pixels
    Inparameter image
    Returns: an image to memory as numpy array (not any readable image format)"""
    h, w = image.shape[:2]
    if w > max_width:
        ratio = max_width / w
        new_h = int(h * ratio)
        return cv2.resize(image, (max_width, new_h))
    else:
        return image


def validate_content_in_image(image_data):
    """Does som adjustments and scanns the image with easyocr, 
    returns: words_numbers_found - a list of found words and numbercombinations from the image
      raises: ValueError if image cant be decoded  """
    # Create reader with English language, gpu can be set to true if the server has a gpu for faster processing

    # Convert bytes to numpy array
    nparr = np.frombuffer(image_data, np.uint8)

    # Decodes the image data directly
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if image is None:
        raise ValueError("Failed to decode image data - no image")

    image = resize_image(image)  # Resize to 800px width max

    # Create reader with English language
    reader = easyocr.Reader(['en'], gpu=False)

    # Optional: Apply some preprocessing to enhance text
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply thresholding to make text more visible
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

    # Optional: You can try different preprocessing techniques
    # blur = cv2.GaussianBlur(gray, (5, 5), 0)
    # thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    # Use both the original and preprocessed images
    result1 = reader.readtext(image, detail=1, paragraph=False,
                              allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789:',
                              contrast_ths=0.1, adjust_contrast=0.5)
    result2 = reader.readtext(thresh, detail=1, paragraph=False,
                              allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789:',
                              contrast_ths=0.1, adjust_contrast=0.5)

    # Combine results
    result = result1 + result2

    words_numbers_found = []
    for detection in result:
        word = str(detection[1])
        confidence = detection[2]  # Confidence score
        print(f"Detected: {word}, Confidence: {confidence}")  # ta bort sedan
        word = word.replace("\n", "")
        words_numbers_found.append(word)

    # Additional check specifically for model number
    model_pattern = r'[A-Z]{2}\d{1,2}[A-Z]\d{1,4}[A-Z]{1,2}'
    for word in words_numbers_found:
        if re.search(model_pattern, word):
            print(f"Found potential model number: {word}")

    # Try to specifically find the model number section
    for i, detection in enumerate(result):
        if "MODEL" in detection[1]:
            # If we find the word "MODEL", look at nearby text
            print(f"Found MODEL label at detection {i}")
            # Check the next few detections for potential model numbers
            for j in range(i+1, min(i+5, len(result))):
                print(f"Potential model value: {result[j][1]}")

    return words_numbers_found

# functions that supports search page


def check_for_perfect_match(search_words: list, device_type_id: uuid.UUID, brand_id: uuid.UUID, db: Session):
    """Support function for search - in parameter searchwords, id for device and brand.
     returns: a list of dictionaries where each hit is a dictionary. """
    result = []
    added_file_ids = []
    for search_word in search_words:
        stmt = (
            select(
                Manuals.brand_id,
                Manuals.device_type_id,
                Manuals.modelnumber,
                Manuals.modelname,
                Manuals.id,
            )
            .where(
                Manuals.brand_id == brand_id,
                Manuals.device_type_id == device_type_id,
                or_(Manuals.modelnumber == search_word,
                    Manuals.modelname == search_word)
            )
        )
        perfect_match = db.execute(stmt).all()
        if perfect_match:
            for match in perfect_match:
                if match.id not in added_file_ids:
                    added_file_ids.append(match.id)
                    result.append({
                        "brand_id": match.brand_id,
                        "device_type_id": match.device_type_id,
                        "model_numbers": match.modelnumber,
                        "modelname": match.modelname,
                        "file_id": match.id,
                        "match": "perfect match",
                    })
    return result  # Return just the list


def check_for_partial_match(search_words: list, type_id: uuid.UUID, brand_id: uuid.UUID, db: Session):
    """Support function for search. In parameter searchwords, id for device and brand.
     returns: a list of dictionaries where each hit is a dictionary. """
    stmt = (
        select(
            Manuals.brand_id,
            Manuals.device_type_id,
            Manuals.modelnumber,
            Manuals.modelname,
            Manuals.id,
        )
        .where(
            Manuals.brand_id == brand_id,
            Manuals.device_type_id == type_id,
        )
    )

    pot_manuals_from_db = db.execute(stmt).all()

    # Use a dictionary to track best match for each manual ID
    best_matches = {}

    for search_word in search_words:
        for manual in pot_manuals_from_db:
            # Check similarity with modelnumber
            similarity1 = SequenceMatcher(
                None, search_word, manual.modelnumber).ratio()

            # Check similarity with modelname
            similarity2 = SequenceMatcher(
                None, search_word, manual.modelname).ratio()

            # Use the higher similarity score
            max_similarity = max(similarity1, similarity2)

            if max_similarity >= 0.7:
                # Update best match if this is better than previous match for this manual
                manual_id = manual.id
                if manual_id not in best_matches or max_similarity > best_matches[manual_id][1]:
                    best_matches[manual_id] = (manual, max_similarity)

    # Convert dictionary to list and sort by similarity
    result = list(best_matches.values())
    result.sort(key=lambda x: x[1], reverse=True)

    formatted_result = []
    # Take only top 20 results
    for manual, similarity in result[:20]:
        formatted_result.append({
            "brand_id": manual.brand_id,
            "device_type_id": manual.device_type_id,
            "model_numbers": manual.modelnumber,
            "modelname": manual.modelname,
            "file_id": manual.id,
            "match": f"partial match ({similarity:.2f})",
        })

    return formatted_result
