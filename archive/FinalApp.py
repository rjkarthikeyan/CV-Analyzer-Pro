# ===============================
# Resume Classification App
# ===============================

# Importing Libraries
import os
import pandas as pd
import warnings
from gensim.parsing.preprocessing import remove_stopwords, stem_text
import re
import streamlit as st
import pickle
import docx2txt
from PyPDF2 import PdfReader
import numpy as np

warnings.filterwarnings("ignore")

# ===============================
# Load Model & Supporting Files
# ===============================

BASE_DIR = os.path.dirname(__file__)

# Load trained model
model_path = os.path.join(BASE_DIR, "finalmodel_xgboost.pkl")
classification_model = pickle.load(open(model_path, 'rb'))
print("Loaded model successfully")

# Load category-wise word frequencies
category_path = os.path.join(BASE_DIR, "category_word_frequencies.pkl")
with open(category_path, "rb") as f:
    category_word_frequencies = pickle.load(f)


# ===============================
# Text Preprocessing Function
# ===============================

def preprocess(text):
    text = text.strip()
    text = re.sub(r'\s+', " ", text)
    text = re.sub('[^a-zA-Z ]', '', text)
    text = text.lower()
    text = text.split()
    
    text = " ".join([remove_stopwords(word) for word in text])
    text = stem_text(text)
    
    return text


# ===============================
# Resume Classification Function
# ===============================

def classify_resume(text):
    text = preprocess(text)
    category_scores = {category: 0 for category in category_word_frequencies.keys()}
    
    for category, keywords in category_word_frequencies.items():
        for keyword in keywords:
            if keyword in text:
                category_scores[category] += 1
                
    predicted_category = max(category_scores, key=category_scores.get)
    return predicted_category


# ===============================
# Streamlit App
# ===============================

def main():
    st.title("Resume Classification Application")

    uploaded_files = st.file_uploader(
        "Upload Resume (.docx or .pdf)",
        type=["docx", "pdf"],
        accept_multiple_files=True
    )

    if st.button("Predict Resume Category"):

        if not uploaded_files:
            st.warning("Please upload at least one file.")
            return

        file_names = []
        resume_texts = []

        for uploaded_file in uploaded_files:

            # PDF handling
            if uploaded_file.type == "application/pdf":
                pdf_reader = PdfReader(uploaded_file)
                text = ""
                for page in pdf_reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted
            else:
                # DOCX handling
                text = docx2txt.process(uploaded_file)

            file_names.append(uploaded_file.name)
            resume_texts.append(text)

        # Create DataFrame
        resume_data = pd.DataFrame({
            "File_Name": file_names,
            "Resume_Text": resume_texts
        })

        # Predict category
        resume_data["Category"] = resume_data["Resume_Text"].apply(classify_resume)

        st.subheader("Prediction Results")
        for _, row in resume_data.iterrows():
            st.write(f"{row['File_Name']} → {row['Category']}")

        st.info("This application classifies resumes based on keyword frequency.")


if __name__ == "__main__":
    main()