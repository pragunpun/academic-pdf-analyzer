#keywords.py

import re
from sklearn.feature_extraction.text import TfidfVectorizer
from modules.preprocessing import clean_text

# Common useless phrases to ignore
BAD_PHRASES = {
    "key points", "examples include", "example includes",
    "introduction", "conclusion", "summary",
    "chapter", "contents", "high level", "low level", "et al", "doi", "ieee"
}
# Weak/generic words (not useful as keywords)
WEAK_WORDS = {
    "system", "systems", "level", "levels",
    "type", "types", "part", "process", "use", "case",
    "design", "send", "area"
}

# Clean keyword phrase (normalize + remove repetition)
def clean_phrase(term):
    term = term.lower().strip()
    term = re.sub(r'\s+', ' ', term)
    # remove consecutive duplicate words
    words = term.split()
    words = [w for i, w in enumerate(words)
             if i == 0 or w != words[i-1]]
    return " ".join(words)

# Validate keyword quality
def is_valid_keyword(term):
    words = term.split()

    if len(words) < 2 or len(words) > 3:
        return False
    if len(set(words)) == 1:
        return False
    if term in BAD_PHRASES:
        return False
    if all(w in WEAK_WORDS for w in words):
        return False
    if re.search(r'\b(19|20)\d{2}\b', term):
        return False
    if any(char.isdigit() for char in term):
        return False

    return True

# MAIN
def extract_keywords(text, top_n=10):

    text = clean_text(text)

    # Remove short/noisy sentences
    sentences = text.split(".")
    filtered_text = " ".join([s for s in sentences if len(s.split()) > 5])

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),  # unigram + bigram
        max_features=800
    )

    X = vectorizer.fit_transform([filtered_text])
    terms = vectorizer.get_feature_names_out()
    scores = X.toarray()[0]
    
    # Sort terms by importance
    scored_terms = sorted(zip(terms, scores), key=lambda x: x[1], reverse=True)

    keywords = []
    seen = set()

    for term, score in scored_terms:

        term = clean_phrase(term)

        if term in seen:
            continue

        if is_valid_keyword(term):
            keywords.append(term)
            seen.add(term)

        if len(keywords) == top_n:
            break

    return keywords