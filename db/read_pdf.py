
from pathlib import Path
from pypdf import PdfReader

# Locate the PDF inside the data folder
pdf_file = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "empty_pdf.pdf"
)

try:
    # Read the PDF
    reader = PdfReader(str(pdf_file))

    print("Total pages:", len(reader.pages))

    # Extract and print text from every page
    for page_number, page in enumerate(reader.pages, start=1):
        print(f"\n--- Page {page_number} ---")

        text = page.extract_text()

        if text:
            print(text)
        else:
            print("No extractable text found on this page.")

except FileNotFoundError:
    print(f"PDF file not found: {pdf_file}")

except Exception as error:
    print("Error reading PDF:", error)
