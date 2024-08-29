# api/handlers/pdf_handler.py

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status

from app.dependencies import get_pdf_service
from app.models.file_model import FileModel
from app.services.pdf_service import PDFService

router = APIRouter()


@router.post("/lift/upload_pdf", status_code=status.HTTP_202_ACCEPTED)
async def upload_pdf(file: UploadFile = File(...), pdf_service: PDFService = Depends(get_pdf_service)):
    file_content = await file.read()
    file_model = FileModel(filename=file.filename, content=file_content)

    if not file_model.is_pdf():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File must be a PDF")

    try:
        result = await pdf_service.process_lift_pdf(file_model)
        return {"message": "PDF file processed successfully", "result": result}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
