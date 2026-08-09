#headings.py

import re
import numpy as np

# ---------------- CONFIG ----------------
IMPORTANT_HINT_WORDS = {
    "model", "analysis", "system", "method", "approach",
    "learning", "network", "data", "algorithm", "design",
    "architecture", "framework", "evaluation", "process",
    "introduction", "database", "software", "language"
}

BAD_PATTERNS = [
    r'©', r'issn', r'volume', r'issue',
    r'arxiv', r'\[\d+\]', r'http', r'www',
    r'figure', r'table', r'ijirt', r'international journal',
    r'copyright'
]

# ---------------- HELPERS ----------------
# 1. Strong numbered headings: 1. 2. 3.
def is_numbered(line):
    return bool(re.match(r'^\d+\.\s+[A-Z]', line))

# 2. Section headings: A) B) I.
def is_section_pattern(line):
    return bool(re.match(r'^([A-Z]\)|[IVX]+\.)\s+[A-Z]', line))

# 3. Title Case
def is_title_case(line):
    words = line.split()
    if len(words) < 2 or len(words) > 10:
        return False
    caps = sum(1 for w in words if w[0].isupper())
    return caps / len(words) > 0.6

# 4. ALL CAPS
def is_all_caps(line):
    return line.isupper() and len(line.split()) >= 2

# 5. Keyword hint
def has_keywords(line):
    return any(k in line.lower() for k in IMPORTANT_HINT_WORDS)



# ---------------- NOISE FILTER ----------------
def is_noise(line):

    line = line.strip()
    words = line.split()

    # NEVER treat numbered headings as noise
    if re.match(r'^\d+\.', line):
        return False

    # NEVER block numbered headings
    if re.match(r'^\d+\.', line):
        return False

     # Remove bullet points
    if line.startswith(("•", "-", "*")):
        return True

    # Remove table rows
    if "|" in line:
        return True

    # Too short or too long
    if len(words) < 2 or len(words) > 12:
        return True
        
    # sentence-like text
    if re.search(r'\b(is|are|was|were|has|have|had|can|will|should|may|might|include|provides|contains|uses|allows|helps|supports)\b', line.lower()):
        return True

    # Ending like sentence
    if line.endswith('.') or line.endswith(','):
        return True

    # long sentence logic
    if len(words) > 10 and re.search(r'\b(and|or|because|that|which|with|for)\b', line.lower()):
        return True

    # Too many digits
    if sum(c.isdigit() for c in line) > 4:
        return True

    # Code / symbols
    if re.search(r'[{}<>/=;:$%#@]', line):
        return True

    # Function-like text
    if re.search(r'\w+\(.*\)', line):
        return True

    # empty junk lines
    if re.fullmatch(r'[-–—\s]+', line):
        return True

    # Bad patterns
    for p in BAD_PATTERNS:
        if re.search(p, line.lower()):
            return True

    return False

# ---------------- FINAL FILTER ----------------
def is_valid_heading(text):
    text = text.strip()

    # REMOVE Unit / Chapter
    if re.match(r'^(unit|chapter)\b', text.lower()): 
        return False
   
    # reject incomplete phrases
    if text.lower().startswith(("and ", "or ", "of ","for ", "with ")):
        return False

    if len(text) < 2:
        return False
    
    # must start with letter or number
    if not (text[0].isupper() or text[0].isdigit()):
        return False

    return True

# ---------------- MAIN ----------------
def detect_headings(page_line_data):

    headings_dict = {}

    for page, lines in page_line_data.items():

        if not lines:
            headings_dict[page] = ["No clear heading found"] 
            continue

        # -------- FONT ANALYSIS (KEY STEP) --------
        fonts = [l["font_size"] for l in lines]
        avg_font = np.mean(fonts)
        max_font = max(fonts)

        heading_threshold = avg_font * 1.2

        final = []
        seen = set()

        # PROCESS LINES IN PDF ORDER
        for item in lines:

            text = item["text"].strip()
            font = item["font_size"]

            if not text:
                continue

            # FORCE numbered headings FIRST
            if is_numbered(text) and is_valid_heading(text):
                key = text.lower()
                if key not in seen:
                    final.append(text)
                    seen.add(key)
                continue

            # noise filter for important headings
            if is_noise(text) and not is_numbered(text):
                continue

            score = 0


            # FONT priority
            if font >= heading_threshold:
                score += 3

            if font >= max_font * 0.9:
                score += 5

            # STRUCTURE priority
            if is_section_pattern(text):
                score += 8

            if is_title_case(text):
                score += 3

            if is_all_caps(text):
                score += 2

            if has_keywords(text):
                score += 1

            if len(text.split()) <= 6:
                score += 1

            # FINAL DECISION
            if score >= 5:
                key = text.lower()

                if key not in seen and is_valid_heading(text):
                    final.append(text)
                    seen.add(key)

        # FALLBACK (if no headings found)
        if not final:
            fallback = sorted(lines, key=lambda x: -x["font_size"])

            for item in fallback:
                t = item["text"].strip()

                if not is_noise(t) and is_valid_heading(t):
                    final.append(t)

                if len(final) >= 3:
                    break

        headings_dict[page] = final[:6] if final else ["No clear heading found"]

    return headings_dict