#pdf_reader.py

import fitz  # PyMuPDF

# Extract text, headings (with font) and tables from PDF
def extract_pdf_text(file_bytes):
    full_text = ""       # Full document text
    page_text_dict = {}  # Page-wise text storage
    page_line_data = {}  # stores line + font size
    page_tables_dict = {} # Extracted tables per page

    # Open PDF from memory
    doc = fitz.open(stream=file_bytes, filetype="pdf")

    # Loop through each pages
    for page_num, page in enumerate(doc, start=1):
        page_text = ""        # Text for current page
        lines_with_fonts = [] # Store lines with font info
        
        # Extract tables 
        tables = page.find_tables()
        extracted_tables = []
        
        for table in tables:
            extracted_tables.append(table.extract())

        blocks = page.get_text("dict")["blocks"]

        for block in blocks:
            if "lines" not in block:
                continue

            for line in block["lines"]:
                line_text = ""
                font_sizes = []

                for span in line["spans"]:
                    line_text += span["text"]
                    font_sizes.append(span["size"])

                line_text = line_text.strip()

                if len(line_text) < 2:
                    continue

                # Average font size (used for heading detection)
                avg_font = sum(font_sizes) / len(font_sizes)

                # Store structured line data
                lines_with_fonts.append({
                    "text": line_text,
                    "font_size": avg_font
                })
                #reduce extra spacing (single newline only)
                page_text += line_text + "\n"
                
        # store per page
        page_text_dict[page_num] = page_text
        page_line_data[page_num] = lines_with_fonts
        page_tables_dict[page_num] = extracted_tables  
        
        # build full text
        full_text += page_text + "\n"

    total_pages = len(doc)
    doc.close()

    return full_text, page_text_dict, page_line_data, total_pages, page_tables_dict