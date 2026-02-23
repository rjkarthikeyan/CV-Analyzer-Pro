import os
import pickle
import re
import PyPDF2
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from gensim.parsing.preprocessing import remove_stopwords, stem_text
from django.contrib.auth.decorators import login_required

@login_required(login_url='login')  # This redirects them if they aren't logged in
def home(request):
    # ... your existing home code here ...
# Load models safely
 def load_models():
    # This looks in your main 'core' folder for the files
    model = pickle.load(open("finalmodel_xgboost.pkl", 'rb'))
    vectorizer = pickle.load(open("vector.pkl", 'rb'))
    with open("category_word_frequencies.pkl", "rb") as f:
        freq = pickle.load(f)
    return model, vectorizer, freq

def home(request):
    context = {}
    if request.method == 'POST' and request.FILES.get('resume'):
        try:
            # 1. Load the "Brain"
            model, vectorizer, category_word_frequencies = load_models()
            
            # 2. File handling
            resume_file = request.FILES['resume']
            fs = FileSystemStorage()
            filename = fs.save(resume_file.name, resume_file)
            file_path = fs.path(filename)
            
            # 3. PDF Text Extraction (The new way)
            reader = PyPDF2.PdfReader(file_path)
            raw_text = ""
            for page in reader.pages:
                raw_text += page.extract_text()

            # 4. Cleaning Logic (Matching your FinalApp.py)
            cleaned = raw_text.strip().lower()
            cleaned = re.sub(r'\s+', " ", cleaned)
            cleaned = re.sub('[^a-zA-Z ]', '', cleaned)
            cleaned = " ".join([remove_stopwords(w) for w in cleaned.split()])
            final_text = stem_text(cleaned)

            # 5. Prediction
            # Calculate scores based on your word frequencies pkl
            category_scores = {cat: 0 for cat in category_word_frequencies.keys()}
            for cat, keywords in category_word_frequencies.items():
                for word in keywords:
                    if word in final_text:
                        category_scores[cat] += 1
            
            predicted_category = max(category_scores, key=category_scores.get)
            
            # 6. ATS Score Calculation (Simple version)
            ats_score = min(len(final_text.split()) // 5, 100) 

            context = {
                'status': predicted_category,
                'score': ats_score,
                'user_name': request.POST.get('name'),
            }
        except Exception as e:
            # This will show you exactly what is wrong on the webpage
            context['status'] = f"Error: {str(e)}"
            
    return render(request, 'home.html', context)