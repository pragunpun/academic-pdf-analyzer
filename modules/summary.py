#summary.py

import re
import pandas as pd

# SPLIT TEXT INTO SECTIONS USING HEADINGS
def split_by_heading(text, headings):
    sections = {}

    if not headings:
        return sections

    for i, heading in enumerate(headings):
        
        # split text at heading
        parts = re.split(re.escape(heading), text, maxsplit=1)
        if len(parts) < 2:
            continue

        content = parts[1]

        # stop at next heading
        if i + 1 < len(headings):
            next_h = headings[i + 1]
            content = re.split(re.escape(next_h), content)[0]
            
        # SPACE CLEANING 
        content = re.sub(r'\s+', ' ', content).strip()
        
        # ignore very small sections
        if len(content.split()) > 20:
            sections[heading] = content

    return sections

#------------SUMMARY-----------------------
def simple_summary(text, max_sentences=4):
    # SPACE CLEANING 
    text = re.sub(r'\s+', ' ', text)

    sentences = re.split(r'(?<=[.!?])\s+', text)

    cleaned = []

    for s in sentences:
        s = s.strip()

        # remove short junk sentences
        if len(s.split()) < 8:
            continue
        # remove incomplete lines
        if s.endswith(":"):
            continue

        cleaned.append(s)

    # remove duplicates while preserving order
    unique = list(dict.fromkeys(cleaned))

    return " ".join(cleaned[:max_sentences])

#--------------CLEAN TABLES FROM PDF-------------
def clean_tables(tables):

    cleaned_tables = []

    for table in tables:

        try:
            if not table or len(table) < 2:
                continue

            # clean header row
            header = [str(h).strip() if h else f"col_{i}" 
                      for i, h in enumerate(table[0])]

            # remove duplicate column names
            seen = set()
            unique_header = []
            
            for h in header:
                if h in seen:
                    h = h + "_dup"
                seen.add(h)
                unique_header.append(h)

            # clean rows
            rows = []
            
            for r in table[1:]:
                if not isinstance(r, list):
                    continue

                # fix row length mismatch
                r = r[:len(unique_header)]
                r += [""] * (len(unique_header) - len(r))

                rows.append(r)

            df = pd.DataFrame(rows, columns=unique_header)

            cleaned_tables.append(df)

        except:
            continue

    return cleaned_tables

#---------------MAIN SUMMARY PIPELINE------------------
def generate_summary(page_text_dict, page_line_data, page_tables_dict, headings_dict):

    final_output = {}

    for page_num, text in page_text_dict.items():

        headings = headings_dict.get(page_num, [])
        if not headings:
            continue

        # split page text into sections
        sections = split_by_heading(text, headings)

        page_blocks = []
        
        #TEXT BLOCKS 
        for heading, content in sections.items():

            summary = simple_summary(content)

            page_blocks.append({
                "type": "text",
                "heading": heading,
                "content": summary
            })

        # TABLE BLOCKS
        tables = clean_tables(page_tables_dict.get(page_num, []))

        for table in tables:
            page_blocks.append({
                "type": "table",
                "data": table
            })

        final_output[page_num] = page_blocks

    return final_output