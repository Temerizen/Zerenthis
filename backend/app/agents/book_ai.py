# C:\AI_BRAIN\book_reader\book_ai.py

from pypdf import PdfReader

file = input("Enter PDF path (inside books folder): ")
reader = PdfReader(file)
text = ""

for page in reader.pages:
    text += page.extract_text() or ""

print("\nFirst 2000 characters of the book:\n")
print(text[:2000])