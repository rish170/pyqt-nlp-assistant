import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from thefuzz import fuzz
from PyQt6.QtCore import QObject, pyqtSignal, QRunnable, pyqtSlot
from services.faq_service import FAQService
import numpy as np
import logging

logger = logging.getLogger(__name__)

# Global cache to prevent recalculation
_FAQ_CACHE = {
    'ids': [],
    'questions': [],
    'tfidf_matrix': None,
    'spacy_docs': [],
    'is_dirty': True
}

class NLPEngine:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(NLPEngine, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance

    def initialize(self):
        self.nlp = None
        self.vectorizer = TfidfVectorizer(stop_words='english')
        
        # Load spaCy
        try:
            self.nlp = spacy.load("en_core_web_md")
            logger.info("Loaded en_core_web_md")
        except OSError:
            logger.warning("en_core_web_md not found, falling back to en_core_web_sm")
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                logger.error("No spaCy model found!")
                self.nlp = None
                
        self.faq_service = FAQService()

    def _preprocess(self, text):
        if not self.nlp: return text.lower()
        doc = self.nlp(text)
        tokens = [token.lemma_.lower() for token in doc if not token.is_stop and not token.is_punct]
        return " ".join(tokens)

    def mark_dirty(self):
        _FAQ_CACHE['is_dirty'] = True

    def build_index(self):
        if not _FAQ_CACHE['is_dirty']:
            return

        faqs = self.faq_service.get_all_faqs()
        _FAQ_CACHE['ids'] = [f.id for f in faqs]
        _FAQ_CACHE['questions'] = [f.question for f in faqs]
        
        if not faqs:
            _FAQ_CACHE['tfidf_matrix'] = None
            _FAQ_CACHE['spacy_docs'] = []
            _FAQ_CACHE['is_dirty'] = False
            return

        # Prepare combined text for TF-IDF and Semantic to include answers
        combined_texts = [f"{f.question} {f.answer}" for f in faqs]

        # Prepare text for TF-IDF
        processed_qs = [self._preprocess(text) for text in combined_texts]
        
        # TF-IDF
        _FAQ_CACHE['tfidf_matrix'] = self.vectorizer.fit_transform(processed_qs)
        
        # SpaCy Docs for semantic similarity
        # CRITICAL: Use processed_qs (no stopwords) to prevent inflated similarity scores
        if self.nlp:
            _FAQ_CACHE['spacy_docs'] = list(self.nlp.pipe(processed_qs))
            
        _FAQ_CACHE['is_dirty'] = False
        logger.info(f"Built index for {len(faqs)} FAQs")

    def query(self, user_question: str, threshold: float = 70.0):
        self.build_index()
        
        if not _FAQ_CACHE['ids']:
            return {"status": "error", "message": "No FAQs in database."}

        # 1. TF-IDF
        processed_query = self._preprocess(user_question)
        query_vec = self.vectorizer.transform([processed_query])
        tfidf_scores = cosine_similarity(query_vec, _FAQ_CACHE['tfidf_matrix'])[0]
        
        # 2. Semantic Similarity
        semantic_scores = np.zeros(len(_FAQ_CACHE['ids']))
        if self.nlp and len(self.nlp.vocab.vectors) > 0:
            query_doc = self.nlp(processed_query) # Use processed query (no stopwords)
            for i, doc in enumerate(_FAQ_CACHE['spacy_docs']):
                # Prevent warnings on empty docs
                if query_doc.vector_norm > 0 and doc.vector_norm > 0:
                    semantic_scores[i] = query_doc.similarity(doc)
                else:
                    semantic_scores[i] = 0.0
        
        # 3. Fuzzy Matching (keep against raw question for typo detection)
        fuzzy_scores = np.array([fuzz.token_set_ratio(user_question, q) / 100.0 for q in _FAQ_CACHE['questions']])
        
        # Combine Scores: 
        # Since we removed stop words, the semantic similarity is well-calibrated.
        # We should trust whichever model is MOST confident.
        combined_scores = np.maximum(semantic_scores, tfidf_scores)
        
        # If fuzzy score is very high (e.g. >0.8), it should override everything
        combined_scores = np.maximum(combined_scores, fuzzy_scores * 0.9)
        
        best_idx = np.argmax(combined_scores)
        best_score = combined_scores[best_idx] * 100
        
        faqs = self.faq_service.get_all_faqs() # Simple fetch to get full FAQ objects
        faq_dict = {f.id: f for f in faqs}
        
        if best_score >= threshold:
            best_faq = faq_dict[_FAQ_CACHE['ids'][best_idx]]
            return {
                "status": "success",
                "faq": best_faq,
                "score": best_score
            }
            
        # Get top 3
        top_3_idx = np.argsort(combined_scores)[-3:][::-1]
        suggestions = [faq_dict[_FAQ_CACHE['ids'][i]] for i in top_3_idx if combined_scores[i] > 0]
        return {
            "status": "low_confidence",
            "score": best_score,
            "suggestions": suggestions
        }
            
    def get_suggestions(self, partial_query: str, limit=5):
        self.build_index()
        if not _FAQ_CACHE['ids'] or not partial_query.strip():
            return []
            
        fuzzy_scores = np.array([fuzz.partial_ratio(partial_query.lower(), q.lower()) for q in _FAQ_CACHE['questions']])
        top_idx = np.argsort(fuzzy_scores)[-limit:][::-1]
        
        faqs = self.faq_service.get_all_faqs()
        faq_dict = {f.id: f for f in faqs}
        return [faq_dict[_FAQ_CACHE['ids'][i]] for i in top_idx if fuzzy_scores[i] > 50]


class NLPQueryWorker(QRunnable):
    """Worker thread for running NLP queries without blocking UI"""
    class Signals(QObject):
        finished = pyqtSignal(dict)
        error = pyqtSignal(str)
        
    def __init__(self, query: str, threshold: float):
        super().__init__()
        self.query_text = query
        self.threshold = threshold
        self.signals = self.Signals()
        self.engine = NLPEngine()
        
    @pyqtSlot()
    def run(self):
        try:
            result = self.engine.query(self.query_text, self.threshold)
            self.signals.finished.emit(result)
        except Exception as e:
            logger.error(f"NLP error: {e}")
            self.signals.error.emit(str(e))
