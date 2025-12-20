"""
Document Upload and Processing Endpoints
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
from typing import List, Optional
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_active_user
from app.database.connection import get_db
from app.database.models import User, Document
from app.services.document_service import document_service
from app.core.logging import logger
import uuid
from datetime import datetime
import json

router = APIRouter()

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    save_to_db: bool = Query(True, description="Save document metadata to database")
):
    """
    Upload a document for OCR processing
    
    Supported formats: PDF, JPEG, PNG, TIFF
    
    Features:
    - Automatic OCR text extraction
    - Document classification (Invoice, PO, Receipt, etc.)
    - Structured data extraction
    - Confidence scoring
    - Optional database storage
    """
    try:
        # Validate file type
        allowed_types = [
            "application/pdf",
            "image/jpeg",
            "image/jpg",
            "image/png",
            "image/tiff"
        ]
        
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file.content_type}. Allowed: PDF, JPEG, PNG, TIFF"
            )
        
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)
        
        # Generate unique filename
        file_ext = file.filename.split(".")[-1] if "." in file.filename else "pdf"
        unique_filename = f"{uuid.uuid4()}.{file_ext}"
        
        # Save file
        file_path = document_service.save_uploaded_file(file_content, unique_filename)
        
        # Process document with enhanced OCR
        result = await document_service.process_document(file_path, file.content_type)
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Processing failed"))
        
        # Save to database if requested
        doc_id = None
        if save_to_db:
            try:
                # Determine document category
                doc_type = result.get("document_type", "other")
                category_map = {
                    "invoice": "invoice",
                    "purchase_order": "purchase_order",
                    "delivery_order": "delivery_order",
                    "quotation": "quotation",
                    "receipt": "receipt",
                    "contract": "contract"
                }
                category = category_map.get(doc_type, "other")
                
                # Create document record
                doc = Document(
                    id=uuid.uuid4(),
                    company_id=current_user.company_id,
                    document_type=doc_type,
                    document_category=category,
                    file_name=file.filename,
                    file_path=str(file_path),
                    file_size=file_size,
                    mime_type=file.content_type,
                    ocr_status="completed" if result.get("ocr_available") else "failed",
                    ocr_processed_at=datetime.utcnow() if result.get("ocr_available") else None,
                    ocr_confidence_score=result.get("ocr_confidence"),
                    extracted_data=result.get("extracted_data"),
                    validation_status="pending",
                    uploaded_by=current_user.id
                )
                db.add(doc)
                db.commit()
                db.refresh(doc)
                doc_id = str(doc.id)
            except Exception as db_error:
                logger.warning(f"Failed to save document to database: {db_error}")
                # Continue even if DB save fails
        
        # Prepare response
        extracted_text = result.get("extracted_text", "")
        text_preview = extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text
        
        response_data = {
            "success": True,
            "message": "Document processed successfully",
            "document_id": doc_id,
            "file_id": unique_filename,
            "filename": file.filename,
            "document_type": result.get("document_type"),
            "extracted_text_preview": text_preview,
            "extracted_text_length": len(extracted_text),
            "extracted_data": result.get("extracted_data"),
            "confidence": result.get("confidence"),
            "ocr_confidence": result.get("ocr_confidence"),
            "classification_confidence": result.get("classification_confidence"),
            "ocr_available": result.get("ocr_available", False),
            "uploaded_at": datetime.utcnow().isoformat(),
            "uploaded_by": current_user.email
        }
        
        return JSONResponse(response_data)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document upload error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@router.post("/upload/bulk")
async def upload_multiple_documents(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_active_user)
):
    """
    Upload multiple documents at once
    """
    results = []
    
    for file in files:
        try:
            # Validate file type
            allowed_types = [
                "application/pdf",
                "image/jpeg",
                "image/jpg",
                "image/png",
                "image/tiff"
            ]
            
            if file.content_type not in allowed_types:
                results.append({
                    "filename": file.filename,
                    "success": False,
                    "error": f"Unsupported file type: {file.content_type}"
                })
                continue
            
            # Read and save file
            file_content = await file.read()
            file_ext = file.filename.split(".")[-1] if "." in file.filename else "pdf"
            unique_filename = f"{uuid.uuid4()}.{file_ext}"
            file_path = document_service.save_uploaded_file(file_content, unique_filename)
            
            # Process document
            result = await document_service.process_document(file_path, file.content_type)
            
            if result.get("success"):
                results.append({
                    "filename": file.filename,
                    "file_id": unique_filename,
                    "success": True,
                    "document_type": result.get("document_type"),
                    "extracted_data": result.get("extracted_data")
                })
            else:
                results.append({
                    "filename": file.filename,
                    "success": False,
                    "error": result.get("error", "Processing failed")
                })
        
        except Exception as e:
            logger.error(f"Error processing {file.filename}: {e}")
            results.append({
                "filename": file.filename,
                "success": False,
                "error": str(e)
            })
    
    return JSONResponse({
        "success": True,
        "total_files": len(files),
        "processed": sum(1 for r in results if r.get("success")),
        "failed": sum(1 for r in results if not r.get("success")),
        "results": results
    })

@router.get("/list")
async def list_documents(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    document_type: Optional[str] = Query(None, description="Filter by document type"),
    category: Optional[str] = Query(None, description="Filter by category"),
    use_db: bool = Query(True, description="Use database records if available")
):
    """
    List uploaded documents with enhanced metadata
    """
    try:
        files = []
        
        # Try to get from database first
        if use_db:
            try:
                query = db.query(Document).filter(
                    Document.company_id == current_user.company_id
                )
                
                if document_type:
                    query = query.filter(Document.document_type == document_type)
                if category:
                    query = query.filter(Document.document_category == category)
                
                db_docs = query.order_by(Document.created_at.desc()).offset(offset).limit(limit).all()
                
                for doc in db_docs:
                    files.append({
                        "document_id": str(doc.id),
                        "filename": doc.file_name,
                        "document_type": doc.document_type,
                        "category": doc.document_category,
                        "size": doc.file_size,
                        "ocr_status": doc.ocr_status,
                        "ocr_confidence": float(doc.ocr_confidence_score) if doc.ocr_confidence_score else None,
                        "extracted_data": doc.extracted_data,
                        "uploaded_at": doc.created_at.isoformat() if doc.created_at else None,
                        "processed_at": doc.ocr_processed_at.isoformat() if doc.ocr_processed_at else None,
                        "source": "database"
                    })
                
                if files:
                    return JSONResponse({
                        "success": True,
                        "total": len(files),
                        "files": files,
                        "source": "database"
                    })
            except Exception as db_error:
                logger.warning(f"Database query failed, falling back to file system: {db_error}")
        
        # Fallback to file system listing
        upload_dir = document_service.upload_dir
        
        if upload_dir.exists():
            for file_path in sorted(upload_dir.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
                if file_path.is_file():
                    stat = file_path.stat()
                    files.append({
                        "filename": file_path.name,
                        "size": stat.st_size,
                        "uploaded_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "source": "filesystem"
                    })
        
        return JSONResponse({
            "success": True,
            "total": len(files),
            "files": files[offset:offset+limit],
            "source": "filesystem"
        })
    
    except Exception as e:
        logger.error(f"Error listing documents: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{document_id}")
async def get_document(
    document_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    include_text: bool = Query(False, description="Include full extracted text")
):
    """
    Get document details by ID
    """
    try:
        doc = db.query(Document).filter(
            Document.id == uuid.UUID(document_id),
            Document.company_id == current_user.company_id
        ).first()
        
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        response_data = {
            "success": True,
            "document_id": str(doc.id),
            "filename": doc.file_name,
            "document_type": doc.document_type,
            "category": doc.document_category,
            "size": doc.file_size,
            "mime_type": doc.mime_type,
            "ocr_status": doc.ocr_status,
            "ocr_confidence": float(doc.ocr_confidence_score) if doc.ocr_confidence_score else None,
            "extracted_data": doc.extracted_data,
            "validation_status": doc.validation_status,
            "uploaded_at": doc.created_at.isoformat() if doc.created_at else None,
            "processed_at": doc.ocr_processed_at.isoformat() if doc.ocr_processed_at else None,
        }
        
        # Optionally include full text (can be large)
        if include_text and doc.extracted_data:
            # Try to read from file if path exists
            try:
                from pathlib import Path
                file_path = Path(doc.file_path)
                if file_path.exists():
                    # Re-process to get text (or store text separately in future)
                    result = await document_service.process_document(str(file_path), doc.mime_type or "application/pdf")
                    if result.get("success"):
                        response_data["extracted_text"] = result.get("extracted_text", "")
            except Exception as e:
                logger.warning(f"Could not load full text: {e}")
        
        return JSONResponse(response_data)
    
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid document ID format")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

