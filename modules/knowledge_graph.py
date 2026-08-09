#knowledge_graph.py

import networkx as nx
from collections import defaultdict
import re

#----------------CLEAN TEXT----------------------
def clean_text(text):
    text = text.lower().strip() # normalize case + remove outer spaces

    # remove numbering (1., 1.1, etc.)
    text = re.sub(r"^\d+(\.\d+)*\s*", "", text)

    # remove special characters
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)

    # normalize spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()

#-------CHECK STRONG RELATION BETWEEN CONCEPTS------
def is_strong_related(a, b):
    a_words = set(a.split())
    b_words = set(b.split())

    # overlap check (filters noise relationships)
    common = a_words.intersection(b_words)
    
    return len(common) >= 2


#------------BUILD CO-OCCURRENCE MAP------------------------
def build_cooccurrence(page_text_dict, concepts):
    co_map = defaultdict(int)

    for text in page_text_dict.values():
        text = clean_text(text) #SPACE CLEANING
        
        # find concepts present in same page text
        present = [c for c in concepts if c in text]
        
        # create pair relationships
        for i in range(len(present)):
            for j in range(i + 1, len(present)):
                c1, c2 = present[i], present[j]
                co_map[(c1, c2)] += 1

    return co_map

# ----------------MAIN FUNCTION------------------
def build_knowledge_graph(classified, headings, page_text_dict):

    G = nx.DiGraph()

    # ROOT NODE
    root = "Knowledge Map"
    G.add_node(root, type="root", importance=10)

    # EXTRACT HEADINGS
    all_headings = []

    for page_heads in headings.values():
        if isinstance(page_heads, list):
            for h in page_heads:
                # clean heading text
                h_clean = clean_text(h)

                # remove useless headings
                if len(h_clean.split()) < 2:
                    continue
                if "no clear heading" in h_clean:
                    continue

                all_headings.append(h_clean)

    #remove duplicates + limit graph size
    all_headings = list(set(all_headings))[:8]

    #--------- ADD HEADINGS TO GRAPH----------------
    for h in all_headings:
        G.add_node(h, type="heading", importance=7)
        G.add_edge(root, h, relation="contains")

    # ---------------- CONCEPT EXTRACTION ----------------
    concepts = []
    score_map = {}

    for item in classified:
        concept = clean_text(item["concept"])

        # remove weak/noisy concepts
        if len(concept.split()) < 2:
            continue
        if len(concept.split()) > 5:
            continue
        if any(w in concept for w in ["example", "figure", "table", "data"]):
            continue

        concepts.append(concept)
        score_map[concept] = item["confidence"]

    # remove duplicates + limit
    concepts = list(set(concepts))[:12]

    #---------------- LINK CONCEPT → HEADINGS ----------------
    for concept in concepts:

        G.add_node(
            concept,
            type="concept",
            importance=score_map.get(concept, 1)
        )

        matched = False

        for h in all_headings:

            # strong semantic matching
            if concept in h or is_strong_related(concept, h):
                G.add_edge(h, concept, relation="has_topic")
                matched = True
                break

        if not matched:
            G.add_edge(root, concept, relation="general_topic")

    # ---------------- HEADING ↔ HEADING LINKS ----------------
    for i in range(len(all_headings)):
        for j in range(i + 1, len(all_headings)):

            h1 = all_headings[i]
            h2 = all_headings[j]

            if is_strong_related(h1, h2):
                G.add_edge(h1, h2, relation="related_heading")

    # ---------------- CONCEPT ↔ CONCEPT LINKS ----------------
    co_map = build_cooccurrence(page_text_dict, concepts)

    for (c1, c2), weight in co_map.items():

        #filter weak relationships (higher threshold = cleaner graph)
        if weight >= 2:
            G.add_edge(
                c1,
                c2,
                relation="related_to",
                weight=weight
            )

    return G