import os
from pypdf import PdfReader
from knowledge_base import knowledge_db
import time

# Path to your incoming_books folder
BOOKS_FOLDER = "book_reader/incoming_books"
PROCESSED_FOLDER = "book_reader/books"

# Make sure processed folder exists
if not os.path.exists(PROCESSED_FOLDER):
    os.makedirs(PROCESSED_FOLDER)

print("Self-learning AI started. Watching for new books...")

while True:
    for filename in os.listdir(BOOKS_FOLDER):
        if filename.endswith(".pdf"):
            path = os.path.join(BOOKS_FOLDER, filename)
            reader = PdfReader(path)
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                if text:
                    knowledge_db.add_document(text, source=filename, page=i)
            # Move processed PDF to main books folder
            os.rename(path, os.path.join(PROCESSED_FOLDER, filename))
            print(f"Processed {filename} and added to knowledge DB.")
    
    # Wait 10 minutes before checking again
    time.sleep(600)
