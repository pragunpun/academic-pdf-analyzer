#exam_analyzer.py

from collections import defaultdict
import re

#------------------CLEAN CONCEPT--------------
def clean_concept(text: str) -> str:
    text = text.lower().strip()  # normalize case + remove outer spaces

    # remove numbering like 1., 1.1, 2.3 etc
    text = re.sub(r"^\d+(\.\d+)*\s*", "", text)

    # remove bracket content (like (AI), (2020))
    text = re.sub(r"\(.*?\)", "", text)

    # remove special characters
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)

    # REMOVE EXTRA SPACES
    text = re.sub(r"\s+", " ", text)

    return text.strip()

#--------REMOVE NOISE / BAD CONCEPTS----------
def is_valid_concept(concept):

    words = concept.split()

    # too short or too long
    if len(words) < 2 or len(words) > 5:
        return False

    # reject sentence-like concepts
    if any(w in concept for w in [
        "is", "are", "was", "were", "this", "that",
        "known as", "defined as", "it is"
    ]):
        return False

    # junk words filter
    bad = [
        "no clear heading", "example", "figure",
        "table", "data", "raw", "etc"
    ]
    if any(b in concept for b in bad):
        return False

    return True
     
#-----------------MERGE SIMILAR CONCEPTS-----------------
def normalize_concept(concept):

    # remove "the", "a"
    concept = re.sub(r"^(the|a|an)\s+", "", concept)

    words = concept.split()
    
    # remove duplicate words
    unique = []
    for w in words:
        if w not in unique:
            unique.append(w)

    return " ".join(unique)

# -----------------------------
# 1. CONCEPT SCORING
# -----------------------------
def compute_concept_scores(keywords, headings, page_text_dict):

    concept_scores = defaultdict(float)

    # flatten headings
    all_headings = []
    for page in headings.values():
        if isinstance(page, list):
            all_headings.extend(page)

    # CLEAN + NORMALIZE HEADINGS 
    all_headings = [clean_concept(h) for h in all_headings]
    
    # CLEAN KEYWORDS
    keywords = [clean_concept(k) for k in keywords]
    
    # merge full text
    full_text = clean_concept(" ".join(page_text_dict.values()))

    # combine
    raw_concepts = list(set(keywords + all_headings))

    for concept in raw_concepts:

        c = normalize_concept(clean_concept(concept))

        if not is_valid_concept(c):
            continue

        # scoring system
        h_score = sum(1 for h in all_headings if c in h)
        k_score = sum(1 for k in keywords if c in k)
        t_score = full_text.count(c)

        # bonus boost for important topics
        bonus = 0
        if any(w in c for w in ["architecture", "layer", "model", "system"]):
            bonus += 2

        score = (h_score * 3) + (k_score * 2) + (t_score * 0.3) + bonus

        concept_scores[c] = round(score, 2)

    return dict(concept_scores)

# -----------------------------
# 2. CLASSIFICATION
# -----------------------------
def classify_exam_probability(score_map, top_n=15):

    if not score_map:
        return []

    # sort concepts by score
    sorted_items = sorted(
        score_map.items(),
        key=lambda x: x[1],
        reverse=True
    )

    max_score = sorted_items[0][1] if sorted_items else 1

    classified = []

    for concept, score in sorted_items:

        norm = score / max_score
        confidence = round(norm * 100, 2)

        # classification logic
        if norm >= 0.6:
            level = "🔥 HIGH"
            reason = "Core concept (very important)"
        elif norm >= 0.3:
            level = "⚡ MEDIUM"
            reason = "Important supporting topic"
        else:
            level = "🟡 LOW"
            reason = "Less frequent topic"

        classified.append({
            "concept": concept,
            "score": score,
            "level": level,
            "confidence": confidence,
            "reasons": [reason]

            
        })

    return classified