#question_generator.py

import random
import re

# CLEAN CONCEPT 
def clean_concept(text: str) -> str:
    text = re.sub(r"^\d+(\.\d+)*\s*", "", text) # remove 1., 1.1 etc
    # remove leading dot cases like ". Smart Agriculture"
    text = re.sub(r"^\.\s*", "", text) 
    text = text.strip() # remove extra spaces
    return text.strip()

# MAIN FUNCTION
def generate_exam_questions(classified_concepts, max_questions=15):

    if not classified_concepts:
        return []

    templates = {
        "🔥 HIGH": [
            "Discuss {} in detail.",
            "Explain {} with advantages and disadvantages.",
            "Write a short note on {}."
        ],
        "⚡ MEDIUM": [
            "Explain {} with an example.",
            "Why is {} important?",
            "Describe {} briefly."
        ],
        "🟡 LOW": [
            "What is {}?",
            "Define {}."
        ]
    }

    questions = []
    used_concepts = set()

    for item in classified_concepts:
        
        # Extract and clean concept
        raw_concept = item.get("concept", "")
        
        # clean numbering like 1. 2. 3. 4.
        concept = clean_concept(raw_concept)

        # Skip empty or duplicate concepts
        if not concept or concept.lower() in used_concepts:
            continue

        used_concepts.add(concept.lower())

        # Get level (default LOW if missing)
        level = item.get("level", "🟡 LOW")
        if level not in templates:
            level = "🟡 LOW"
            
        # Generate question
        question_template = random.choice(templates[level])
        question = question_template.format(concept)

        questions.append(question)

        # Limit number of questions
        if len(questions) >= max_questions:
            break

    return questions