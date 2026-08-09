#app

# Import modules
import streamlit as st
from modules.pdf_reader import extract_pdf_text
from modules.preprocessing import clean_text
from modules.keywords import extract_keywords
from modules.headings import detect_headings
from modules.summary import generate_summary
from modules.exam_analyzer import (
    compute_concept_scores,
    classify_exam_probability
)
from modules.question_generator import generate_exam_questions
from modules.knowledge_graph import build_knowledge_graph
from pyvis.network import Network
import streamlit.components.v1 as components

# ---------------- PAGE LAYOUT CONFIGURE ----------------
st.set_page_config(page_title="Academic PDF Analyzer", layout="wide")
st.title("📚 Academic PDF Analyzer")

# ---------------- Sidebar navigation ----------------
option = st.sidebar.radio(
    "Navigation",
    ["Headings / Topics", "Summary", "Exam Preparation"]
)

# ---------------- FILE UPLOAD ----------------
uploaded_file = st.file_uploader("Upload Academic PDF", type=["pdf"])

if uploaded_file:
    with st.spinner("Processing PDF..."):
        file_bytes = uploaded_file.read()

        # Extract text
        full_text, page_text_dict, page_line_data, total_pages, page_tables_dict = extract_pdf_text(file_bytes)

        # Clean text
        cleaned_text = clean_text(full_text)

        if len(cleaned_text) < 100:
            st.error("PDF has very little readable content.")
            st.stop()

        # Run NLP pipeline (keywords, headings, scoring)
        keywords = extract_keywords(cleaned_text)
        headings = detect_headings(page_line_data)
        score_map = compute_concept_scores(keywords, headings, page_text_dict)
        classified = classify_exam_probability(score_map)
        questions = generate_exam_questions(classified)

        word_count = len(cleaned_text.split())

    # ---------------- METRICS ----------------
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📄 Pages", total_pages)

    with col2:
        st.metric("📝 Words", word_count)

    with col3:
        st.subheader("🔑 Keywords")
        for k in keywords:
            st.write("•", k)

    # ---------------- HEADINGS / TOPICS ----------------
    if option == "Headings / Topics":
        st.subheader("📌 Headings / Topics")

        for page, heads in headings.items():
            if heads:
                st.write(f"### Page {page}")
                for h in heads:
                    st.write("•", h)

    # ---------------- SUMMARY ----------------
    elif option == "Summary":
        st.subheader("📚 Summary")
        
        result = generate_summary(
            page_text_dict,
            page_line_data,
            page_tables_dict,
            headings
        )
        
        for page, blocks in result.items():
            
            for block in blocks:
                
                if block["type"] == "text":
                    st.markdown(f"### {block['heading']}")
                    st.write(block["content"])
                    
                elif block["type"] == "table":
                    st.dataframe(block["data"])
                    
    # ---------------- EXAM PREPARATION ----------------
    elif option == "Exam Preparation":
        st.subheader("🎯 Exam Preparation Dashboard")

        # Tabs inside Exam Preparation
        tab1, tab2, tab3 = st.tabs([
            "❓ Questions",
            "📊 Exam Prediction",
            "🧠 Knowledge Graph"
        ])

        # -------- QUESTIONS --------
        with tab1:
            st.subheader("Important Questions")
            for q in questions:
                st.write("•", q)

        # -------- EXAM PREDICTION --------
        with tab2:
            st.subheader("Exam Probability Analysis")

            for item in classified:
                st.write(f"{item['level']} → {item['concept']}")
                st.caption(", ".join(item["reasons"]))
                st.progress(item["confidence"] / 100)

        # -------- KNOWLEDGE GRAPH --------
        with tab3:
            st.subheader("Concept Relationship Graph")
            
            G = build_knowledge_graph(classified, headings, page_text_dict)
            net = Network(height="650px", width="100%", directed=True)
             
            # Nodes
            for node, data in G.nodes(data=True):
                size = 10 + data.get("importance", 1) * 0.5
                net.add_node(
                    node,
                    label=node,
                    size=size,
                    title=f"{node} ({data.get('type')})"
                )
                
            # Edges   
            for u, v, data in G.edges(data=True):
                label = data.get("relation", "")
                net.add_edge(u, v)  
            
            net.repulsion(
                node_distance=250,
                central_gravity=0.3,
                spring_length=200,
                spring_strength=0.05
            )
            
            net.write_html("graph.html")
            with open("graph.html", "r", encoding="utf-8") as f:
                html = f.read()
    
            components.html(html, height=650)