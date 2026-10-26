from fastapi import FastAPI, HTTPException, UploadFile, File
from models_service import models
from pydantic import BaseModel, Field
import db.mobile_models_repo
import db.export_pdf_to_endpoint
from fastapi.responses import Response


class Mobile(BaseModel):
    id: int = Field(..., gt=0)
    name: str = Field(..., min_length=3, max_length=15)
    price: int = Field(..., gt=0)
app = FastAPI()

base_path = "/api"

@app.get("/welcome")
def welcome_message():
    return {
        "message": "Welcome to my API"
    }

@app.get("/greeting")
def greeting_message():
    return {
        "message": "Welcome to Shravan API"
    }

@app.get("/models")
def get_mobile_models():
    return models

@app.get("/models/{model_id}")
def get_mobile_models_by_id(model_id: int):

     model = models.get(model_id)

     if model is None:
         raise HTTPException(
             status_code=404,
             detail="Model not found"
         )

     return model

@app.get(f"{base_path}/models")
def get_all_mobile_models():
    return db.mobile_models_repo.get_all_models()

@app.post(f"{base_path}/model",status_code=201)
def insert_mobile_model(model: Mobile):
    return db.mobile_models_repo.insert_models(model)

@app.delete(f"{base_path}/model/{{model_id}}/delete")
def delete_mobile_model_by_id(model_id: int):
    return db.mobile_models_repo.delete_model_by_id(model_id)

@app.get("/api/reports/pdf", tags=["Reports"])
def export_pdf():
    return db.export_pdf_to_endpoint.download_pdf()

@app.on_event("startup")
def initialize_database_schema():
    db.mobile_models_repo.ensure_file_data_column()


@app.post("/api/models/{model_id}/pdf")
async def upload_model_pdf(
    model_id: int,
    file: UploadFile = File(...)
):
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )

    pdf_bytes = await file.read()

    # Check the PDF file signature.
    if not pdf_bytes.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=400,
            detail="Invalid PDF file"
        )

    saved = db.mobile_models_repo.save_pdf_to_model(
        model_id,
        pdf_bytes
    )

    if not saved:
        raise HTTPException(
            status_code=404,
            detail="Mobile model not found"
        )

    return {
        "success": True,
        "message": "PDF stored successfully",
        "model_id": model_id,
        "file_size_bytes": len(pdf_bytes)
    }


@app.get("/api/models/{model_id}/pdf")
def download_model_pdf(model_id: int):
    pdf_bytes = db.mobile_models_repo.get_pdf_from_model(
        model_id
    )

    if pdf_bytes is None:
        raise HTTPException(
            status_code=404,
            detail="Model or PDF not found"
        )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                f'attachment; filename="model_{model_id}.pdf"'
        }
    )
