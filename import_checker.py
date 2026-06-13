import sys
print(f"Python Executable: {sys.executable}")
print("-" * 40)

try:
    import spacy
    print(f"[SUCCESS] spaCy imported successfully! Version: {spacy.__version__}")
    
    try:
        nlp = spacy.load("en_core_web_md")
        print("[SUCCESS] Loaded 'en_core_web_md' spaCy model!")
    except Exception as e:
        print(f"[ERROR] Could not load 'en_core_web_md' model: {e}")
except ImportError as e:
    print(f"[ERROR] Failed to import spaCy: {e}")

print("-" * 40)

try:
    from thefuzz import fuzz
    print(f"[SUCCESS] thefuzz imported successfully!")
    
    # Test a quick fuzzy match
    score = fuzz.ratio("test", "test")
    if score == 100:
        print("[SUCCESS] thefuzz is working correctly!")
except ImportError as e:
    print(f"[ERROR] Failed to import thefuzz: {e}")

print("-" * 40)
print("Checker finished.")
