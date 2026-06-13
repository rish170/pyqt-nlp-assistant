# 🧠 FAQ Intelligence Assistant

A production-grade, desktop-based intelligent FAQ chatbot and knowledge base manager built with **Python**, **PyQt6**, **spaCy**, and **scikit-learn**. 

Designed to mimic the polished aesthetics of enterprise applications (like Notion, Zendesk, or Microsoft Fluent Design), this assistant operates completely offline while providing lightning-fast, highly accurate conversational responses based on your proprietary data.

---

## ✨ Key Features

- **Triple-Threat NLP Engine**: Utilizes a sophisticated ensemble algorithm combining Semantic Similarity (`spaCy` word vectors), Keyword Overlap (TF-IDF), and Typo Detection (Fuzzy Matching).
- **Offline & Secure**: Runs 100% locally on your machine. No API keys, no cloud dependencies, and complete privacy for your internal data.
- **Dynamic Theming**: Beautiful Light and Dark modes with smooth transitions and transparent, glitch-free UI components.
- **Full Knowledge Management**: Built-in CRUD interface to add, edit, delete, import, and export your FAQs in CSV, JSON, or Excel formats.
- **Aggressive Caching**: Vectors and TF-IDF matrices are calculated strictly when the database changes, ensuring instant, real-time typing suggestions and sub-millisecond query responses.
- **Analytics Dashboard**: Tracks usage statistics so you know exactly which questions your users are asking the most.

---

## 📂 Project Structure

```text
faq_assistant/
│
├── assets/                 # SVGs, images, and visual assets
│   └── icons.py            # Programmatic SVG rendering for dynamic theming
│
├── database/               # Local data persistence layer
│   └── database.py         # SQLite initialization and connection pooling
│
├── services/               # Core business and backend logic
│   ├── faq_service.py      # Handles CRUD ops and file imports/exports
│   ├── history_service.py  # Logs questions and analytics
│   ├── nlp_engine.py       # 🧠 The brains: spaCy + TF-IDF ensemble matching
│   └── theme_manager.py    # Manages light/dark state and settings
│
├── styles/                 # QSS (Qt Style Sheets) for Fluent Design
│   ├── dark.qss            
│   └── light.qss           
│
├── ui/                     # PyQt6 User Interface components
│   ├── components/         # Reusable widgets (e.g., custom Toast notifications)
│   ├── analytics_view.py   # Charts and usage metrics
│   ├── chat_widget.py      # Conversational interface with smooth scrolling
│   ├── faq_manager.py      # The database management table
│   ├── main_window.py      # The primary application shell and sidebar navigation
│   └── settings_dialog.py  # User-configurable NLP thresholds and preferences
│
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
└── README.md               # You are here!
```

---

## 🧠 Deep Dive: The NLP Engine

The core magic of this application lives inside `services/nlp_engine.py`. Matching user questions to pre-written FAQs is notoriously difficult because humans paraphrase heavily. To solve this, the engine employs a **Max-with-Bonus** ensemble architecture:

### 1. Stopword Removal & Preprocessing
Before any math happens, both the user's question and the stored FAQs are stripped of punctuation and grammatical "noise" (words like *is, it, to, the, are*). This prevents the AI from falsely assuming two sentences are similar just because they share basic English grammar.

### 2. Semantic Understanding (`spaCy`)
Using the `en_core_web_md` model, the engine understands the *meaning* of words. If a user asks *"Where do I get my money back?"*, the semantic model knows that "money back" is conceptually identical to "refund", even if the exact letters don't overlap.

### 3. Keyword Extraction (TF-IDF)
`scikit-learn`'s TF-IDF Vectorizer hunts for specific, rare keywords. If a user mentions a hyper-specific product name or error code, TF-IDF ensures that the exact keyword match heavily boosts the score.

### 4. Typo Tolerance (Fuzzy Matching)
Using `thefuzz`, the engine handles fat-finger mistakes. If a user types *"Hw do I rset my passwrd"*, the fuzzy token matcher detects the intended string and overrides the other models.

**The Algorithm:**
Rather than averaging the scores (which penalizes a perfect semantic match if there are no exact keywords), the engine calculates the **Maximum** score across all three models. If *any* of the models is highly confident, the question passes the threshold!

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.12+
- Git

### 1. Clone & Environment
```bash
git clone <repository_url>
cd faq_assistant

# Create and activate a virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Download the NLP Model
The application relies on spaCy's medium-sized English model for vector mathematics. You must download it before running:
```bash
python -m spacy download en_core_web_md
```

### 4. Run the Application
```bash
python main.py
```

---

## 🛠️ Usage Guide

1. **Populate the Database:** Navigate to the `FAQ Database` tab on the left sidebar. Click **Import** to load a CSV file, or use the **Add FAQ** button to manually create questions.
2. **Chat:** Go to the `Home` tab. Start typing your question. The engine will instantly process your text and search for the best match based on your configured confidence threshold.
3. **Adjust strictness:** Go to `Settings` (the gear icon top-right). You can adjust the **Confidence Threshold**. Lower it (e.g., 50%) to make the AI guess more aggressively, or raise it (e.g., 85%) if you only want it to answer when it is absolutely certain.
4. **View Analytics:** The `History` tab keeps track of total queries, successful matches vs. fallback failures, and the most frequently triggered FAQs.

---

## 🤝 Contributing & Future Roadmap
- **LLM Fallback:** Future versions could integrate local LLMs (like Llama.cpp) to dynamically generate conversational answers when the static database fails.
- **Multi-lingual Support:** Implementing `spaCy` multi-lingual models to automatically translate and map questions to English FAQs.

---
*Built with ❤️ utilizing PyQt6 and Modern Desktop Design Principles.*
