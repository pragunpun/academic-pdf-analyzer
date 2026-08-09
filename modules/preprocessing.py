# preprocessing.py

import re

# Clean and normalize extracted PDF text
def clean_text(text):

     # Convert to lowercase (helps in NLP processing)
    text = text.lower()

    # Remove page numbers like "Page 1"
    text = re.sub(r'page\s*\d+', '', text, flags=re.IGNORECASE)

    # Remove references like [1], [23]
    text = re.sub(r'\[\d+\]', '', text)

    # Remove year citations like (2020)
    text = re.sub(r'\(\d{4}\)', '', text)

    # Normalize spaces
    text = re.sub(r'\s+', ' ', text)

    # Remove unwanted characters (keep useful symbols)
    text = re.sub(r'[^a-zA-Z0-9.,;:%()\-\s]', '', text)

    return text.strip()