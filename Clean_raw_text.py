
# Takes pages.json as input
# Removes unnecessary/noncontributing text
# Returns pages_clean.json

import json
import re

# --- Preprocessing Functions ---
def remove_headers_footers(text, header_patterns=None, footer_patterns=None):
    if header_patterns is None:
        header_patterns = [
            r'^President.*Company.*$',   # Example: "President - Company"
            r'^Menu.*$'                # Example: "Menu | About | Programs"
        ]
    if footer_patterns is None:
        footer_patterns = [
            r'^© 20\d{2} Company.*$', # Example: "© 2024 Company"
            r'^All rights reserved.*$'
        ]

    for pattern in header_patterns + footer_patterns:
        text = re.sub(pattern, '', text, flags=re.MULTILINE)

    return text.strip()

def clean_special_characters(text):
    safe_chars = r'[^\w\s\.,;:\'\"\?\!\-\(\)\/@]'
    text = re.sub(safe_chars, '', text)
    return text.strip()

def collapse_repeated_junk(text):
    text = re.sub(r'\.{2,}', '.', text)   # collapse "..."
    text = re.sub(r'[-=]{3,}', ' ', text) # collapse "-----" or "===="
    return text.strip()

def normalize_whitespace(text):
    text = re.sub(r'\r\n', '\n', text)        # unify line endings
    text = re.sub(r'\n{3,}', '\n\n', text)    # collapse 3+ newlines to 2
    text = re.sub(r'[ \t]+', ' ', text)       # collapse spaces/tabs
    return text.strip()

def preprocess_text(text):
    text = remove_headers_footers(text)
    text = clean_special_characters(text)
    text = collapse_repeated_junk(text)
    text = normalize_whitespace(text)
    return text

# --- Deduplication ---
def remove_duplicates(pages):
    seen = set()
    unique_pages = []
    for page in pages:
        cleaned_text = page["text"].strip()
        if cleaned_text not in seen:
            seen.add(cleaned_text)
            unique_pages.append(page)
    print(f"🧹 Removed {len(pages) - len(unique_pages)} duplicate entries.")
    return unique_pages

# --- JSON Cleaning Pipeline ---
def clean_json(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as f:
        pages = json.load(f)

    cleaned_pages = []
    for page in pages:
        url = page.get("url")
        content = page.get("text", "")
        cleaned_content = preprocess_text(content)
        cleaned_pages.append({
            "url": url,
            "text": cleaned_content
        })

    # Remove duplicates before saving
    cleaned_pages = remove_duplicates(cleaned_pages)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(cleaned_pages, f, indent=2, ensure_ascii=False)

    print(f"✅ Cleaned {len(cleaned_pages)} pages. Saved to {output_file}")

# --- Run ---
if __name__ == "__main__":
    clean_json("pages.json", "pages_clean.json")
