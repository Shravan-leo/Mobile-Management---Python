
from pathlib import Path

from fastapi import  HTTPException
from fastapi.responses import FileResponse


# PDF location
PDF_FILE = Path(__file__).resolve().parent.parent / "data" / "sample.pdf"

def download_pdf():
    if not PDF_FILE.exists():
        raise HTTPException(
            status_code=404,
            detail="PDF file not found"
        )

    return FileResponse(
        path=str(PDF_FILE),
        media_type="application/pdf",
        filename="sample.pdf",
        content_disposition_type="attachment"
    )

