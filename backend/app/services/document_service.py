"""
Document Processing Service
Handles OCR, document classification, and data extraction
Enhanced for Python 3.12 with full OCR support
"""
import os
import logging
import re
from typing import Dict, Any, Optional, List
from pathlib import Path
from decimal import Decimal
from datetime import datetime
from app.core.config import settings

# Try to import OCR dependencies
# Use basic logging here since logger might not be initialized yet
_logger = logging.getLogger(__name__)

try:
    from PIL import Image, ImageEnhance, ImageFilter
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    _logger.warning("PIL/Pillow not available. OCR features will be limited.")

try:
    import pytesseract
    HAS_TESSERACT = True
except (ImportError, AttributeError) as e:
    HAS_TESSERACT = False
    _logger.warning(f"pytesseract not available ({e}). OCR will use fallback mode.")

try:
    from pdf2image import convert_from_path
    HAS_PDF2IMAGE = True
except ImportError:
    HAS_PDF2IMAGE = False
    _logger.warning("pdf2image not available. PDF processing will be limited.")

class DocumentService:
    """Service for document processing and OCR with enhanced capabilities"""
    
    def __init__(self):
        self.upload_dir = Path("uploads/documents")
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.ocr_available = HAS_TESSERACT and HAS_PIL
        
        # Set Tesseract path if needed (Windows) and pytesseract is available
        if HAS_TESSERACT and os.name == 'nt':
            # Common Windows Tesseract paths
            tesseract_paths = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                r"C:\Users\{}\AppData\Local\Programs\Tesseract-OCR\tesseract.exe".format(os.getenv('USERNAME', '')),
            ]
            for path in tesseract_paths:
                if os.path.exists(path):
                    try:
                        pytesseract.pytesseract.tesseract_cmd = path
                        _logger.info(f"Tesseract found at: {path}")
                        break
                    except Exception as e:
                        _logger.warning(f"Could not set Tesseract path {path}: {e}")
        
        # Initialize AI service for enhanced classification
        try:
            from app.services.ai_service import AIService
            self.ai_service = AIService()
            self.ai_available = True
        except Exception as e:
            _logger.warning(f"AI service not available: {e}")
            self.ai_service = None
            self.ai_available = False
        
        # Initialize ML service for trained models
        try:
            from app.services.ml_service import ml_service
            self.ml_service = ml_service
            self.ml_available = True
        except Exception as e:
            _logger.warning(f"ML service not available: {e}")
            self.ml_service = None
            self.ml_available = False
    
    async def process_document(self, file_path: str, file_type: str) -> Dict[str, Any]:
        """Process uploaded document with enhanced OCR and AI classification"""
        try:
            from app.core.logging import logger
            logger.info(f"Processing document: {file_path}, type: {file_type}")
            
            # Extract text using OCR
            ocr_result = await self._extract_text(file_path, file_type)
            text = ocr_result.get("text", "")
            ocr_confidence = ocr_result.get("confidence", 0.0)
            
            # Classify document (with AI enhancement if available)
            classification_result = await self._classify_document(text, file_type)
            doc_type = classification_result.get("type", "general")
            classification_confidence = classification_result.get("confidence", 0.5)
            
            # Extract structured data
            extracted_data = await self._extract_data(text, doc_type)
            
            # Calculate overall confidence
            overall_confidence = (ocr_confidence * 0.6 + classification_confidence * 0.4)
            
            return {
                "success": True,
                "document_type": doc_type,
                "extracted_text": text,
                "extracted_data": extracted_data,
                "confidence": round(overall_confidence, 2),
                "ocr_confidence": round(ocr_confidence, 2),
                "classification_confidence": round(classification_confidence, 2),
                "ocr_available": self.ocr_available,
                "text_length": len(text),
            }
        except Exception as e:
            from app.core.logging import logger
            logger.error(f"Error processing document: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "ocr_available": self.ocr_available
            }
    
    async def _extract_text(self, file_path: str, file_type: str) -> Dict[str, Any]:
        """Extract text from document using enhanced OCR with confidence scoring"""
        try:
            # If OCR libraries are not available, return a message
            if not HAS_TESSERACT or not HAS_PIL:
                return {
                    "text": "[OCR not available: Please install pytesseract and Pillow. For now, document will be stored but text extraction is disabled.]",
                    "confidence": 0.0
                }
            
            if file_type == "application/pdf":
                if not HAS_PDF2IMAGE:
                    return {
                        "text": "[PDF processing not available: Please install pdf2image. For now, document will be stored but text extraction is disabled.]",
                        "confidence": 0.0
                    }
                # Convert PDF to images with higher DPI for better quality
                images = convert_from_path(file_path, dpi=300, fmt='png')
                text_parts = []
                confidences = []
                
                for idx, image in enumerate(images):
                    # Enhance image quality
                    image = self._enhance_image(image)
                    
                    # Extract text with confidence data
                    ocr_data = pytesseract.image_to_data(image, lang='eng', output_type=pytesseract.Output.DICT)
                    text = pytesseract.image_to_string(image, lang='eng')
                    text_parts.append(text)
                    
                    # Calculate confidence for this page
                    confs = [int(conf) for conf in ocr_data['conf'] if int(conf) > 0]
                    page_conf = sum(confs) / len(confs) / 100.0 if confs else 0.0
                    confidences.append(page_conf)
                
                # Average confidence across all pages
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
                
                return {
                    "text": "\n\n".join(text_parts),
                    "confidence": avg_confidence,
                    "pages": len(images)
                }
                
            elif file_type.startswith("image/"):
                # Process image directly with enhancement
                image = Image.open(file_path)
                image = self._enhance_image(image)
                
                # Extract text with confidence
                ocr_data = pytesseract.image_to_data(image, lang='eng', output_type=pytesseract.Output.DICT)
                text = pytesseract.image_to_string(image, lang='eng')
                
                # Calculate confidence
                confs = [int(conf) for conf in ocr_data['conf'] if int(conf) > 0]
                confidence = sum(confs) / len(confs) / 100.0 if confs else 0.0
                
                return {
                    "text": text,
                    "confidence": confidence,
                    "pages": 1
                }
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
        except Exception as e:
            from app.core.logging import logger
            logger.error(f"OCR extraction error: {e}", exc_info=True)
            # Return placeholder if OCR fails
            return {
                "text": f"[OCR processing failed: {str(e)}. Document uploaded successfully but text extraction failed.]",
                "confidence": 0.0
            }
    
    def _enhance_image(self, image: Image.Image) -> Image.Image:
        """Enhance image quality for better OCR results"""
        try:
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.5)
            
            # Enhance sharpness
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.2)
            
            # Apply slight denoising
            image = image.filter(ImageFilter.MedianFilter(size=3))
            
            return image
        except Exception as e:
            from app.core.logging import logger
            logger.warning(f"Image enhancement error: {e}, using original")
            return image
    
    async def _classify_document(self, text: str, file_type: str = None) -> Dict[str, Any]:
        """Classify document type with enhanced AI-based classification"""
        text_lower = text.lower()
        text_length = len(text)
        
        # Enhanced keyword-based classification with scoring
        scores = {
            "invoice": 0,
            "purchase_order": 0,
            "delivery_order": 0,
            "quotation": 0,
            "receipt": 0,
            "contract": 0,
            "general": 0
        }
        
        # Invoice indicators
        invoice_keywords = ["invoice", "bill", "payment due", "invoice number", "invoice #", 
                           "amount due", "total due", "billing address", "invoice date"]
        for keyword in invoice_keywords:
            if keyword in text_lower:
                scores["invoice"] += 2
        
        # Purchase Order indicators
        po_keywords = ["purchase order", "po number", "po #", "order number", "purchase order #",
                      "vendor", "supplier", "delivery date", "shipping address"]
        for keyword in po_keywords:
            if keyword in text_lower:
                scores["purchase_order"] += 2
        
        # Delivery Order indicators
        do_keywords = ["delivery order", "delivery note", "do number", "do #", "delivery receipt",
                      "received by", "delivered to", "delivery date"]
        for keyword in do_keywords:
            if keyword in text_lower:
                scores["delivery_order"] += 2
        
        # Quotation indicators
        quote_keywords = ["quotation", "quote", "estimate", "quotation number", "quote #",
                         "valid until", "quote date", "estimated cost"]
        for keyword in quote_keywords:
            if keyword in text_lower:
                scores["quotation"] += 2
        
        # Receipt indicators
        receipt_keywords = ["receipt", "paid", "payment received", "receipt number", "receipt #",
                           "thank you for your payment", "amount paid", "payment confirmation"]
        for keyword in receipt_keywords:
            if keyword in text_lower:
                scores["receipt"] += 2
        
        # Contract indicators
        contract_keywords = ["contract", "agreement", "terms and conditions", "party a", "party b",
                            "effective date", "signature", "witness"]
        for keyword in contract_keywords:
            if keyword in text_lower:
                scores["contract"] += 2
        
        # Find the document type with highest score
        max_score = max(scores.values())
        doc_type = max(scores, key=scores.get) if max_score > 0 else "general"
        
        # Calculate confidence based on score and text length
        confidence = min(0.95, max(0.3, max_score / 10.0))
        if text_length < 50:
            confidence *= 0.7  # Lower confidence for very short text
        
        # Try ML model classification first (if available)
        if self.ml_available and self.ml_service and text_length > 50:
            try:
                ml_result = self.ml_service.classify_document(text)
                if ml_result.get('method') == 'ml_model':
                    ml_type = ml_result.get('type')
                    ml_confidence = ml_result.get('confidence', 0.5)
                    
                    if ml_type in scores:
                        scores[ml_type] += 10  # Strong boost for ML model
                        doc_type = max(scores, key=scores.get)
                        confidence = max(confidence, ml_confidence)  # Use higher confidence
            except Exception as e:
                from app.core.logging import logger
                logger.warning(f"ML classification error: {e}")
        
        # Try AI-enhanced classification if available
        if self.ai_available and text_length > 100:
            try:
                ai_classification = await self._ai_classify_document(text)
                if ai_classification:
                    # Combine AI result with keyword-based result
                    ai_type = ai_classification.get("type")
                    ai_confidence = ai_classification.get("confidence", 0.5)
                    
                    if ai_type in scores:
                        scores[ai_type] += 5  # Boost AI-detected type
                        doc_type = max(scores, key=scores.get)
                        confidence = (confidence + ai_confidence) / 2
            except Exception as e:
                from app.core.logging import logger
                logger.warning(f"AI classification error: {e}")
        
        return {
            "type": doc_type,
            "confidence": confidence,
            "scores": scores
        }
    
    async def _ai_classify_document(self, text: str) -> Optional[Dict[str, Any]]:
        """Use AI service for document classification"""
        if not self.ai_available or not self.ai_service:
            return None
        
        try:
            prompt = f"""Classify this business document. Return only the document type and confidence (0-1).

Document text (first 1000 chars):
{text[:1000]}

Document types: invoice, purchase_order, delivery_order, quotation, receipt, contract, general

Return format: type: <type>, confidence: <0.0-1.0>"""
            
            response = await self.ai_service.generate_text(prompt)
            
            # Parse AI response
            if "type:" in response.lower() and "confidence:" in response.lower():
                import re
                type_match = re.search(r'type:\s*(\w+)', response, re.IGNORECASE)
                conf_match = re.search(r'confidence:\s*([\d.]+)', response, re.IGNORECASE)
                
                if type_match and conf_match:
                    return {
                        "type": type_match.group(1).lower(),
                        "confidence": float(conf_match.group(1))
                    }
        except Exception as e:
            from app.core.logging import logger
            logger.warning(f"AI classification error: {e}")
        
        return None
    
    async def _extract_data(self, text: str, doc_type: str) -> Dict[str, Any]:
        """Extract structured data from text with enhanced patterns"""
        extracted = {
            "vendor_name": None,
            "customer_name": None,
            "supplier_name": None,
            "document_number": None,
            "invoice_number": None,
            "po_number": None,
            "quotation_number": None,
            "date": None,
            "due_date": None,
            "amount": None,
            "subtotal": None,
            "tax": None,
            "total": None,
            "currency": None,
            "address": None,
            "email": None,
            "phone": None,
            "tax_id": None,
        }
        
        # Extract document numbers based on type
        if doc_type == "invoice":
            patterns = [
                r"invoice\s*#?\s*:?\s*([A-Z0-9\-]+)",
                r"invoice\s*number\s*:?\s*([A-Z0-9\-]+)",
                r"inv\s*#?\s*:?\s*([A-Z0-9\-]+)",
                r"invoice\s*no\.?\s*:?\s*([A-Z0-9\-]+)",
            ]
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    extracted["invoice_number"] = match.group(1).strip()
                    extracted["document_number"] = extracted["invoice_number"]
                    break
        
        elif doc_type == "purchase_order":
            patterns = [
                r"purchase\s*order\s*#?\s*:?\s*([A-Z0-9\-]+)",
                r"po\s*#?\s*:?\s*([A-Z0-9\-]+)",
                r"po\s*number\s*:?\s*([A-Z0-9\-]+)",
                r"order\s*#?\s*:?\s*([A-Z0-9\-]+)",
            ]
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    extracted["po_number"] = match.group(1).strip()
                    extracted["document_number"] = extracted["po_number"]
                    break
        
        elif doc_type == "quotation":
            patterns = [
                r"quotation\s*#?\s*:?\s*([A-Z0-9\-]+)",
                r"quote\s*#?\s*:?\s*([A-Z0-9\-]+)",
                r"quotation\s*number\s*:?\s*([A-Z0-9\-]+)",
            ]
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    extracted["quotation_number"] = match.group(1).strip()
                    extracted["document_number"] = extracted["quotation_number"]
                    break
        
        # Extract vendor/supplier/customer names
        vendor_patterns = [
            r"(?:vendor|supplier|from|bill\s*from)\s*:?\s*([A-Z][A-Za-z\s&,\.]+)",
            r"^([A-Z][A-Za-z\s&,\.]+)\s*(?:invoice|bill|statement)",
        ]
        for pattern in vendor_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                name = match.group(1).strip()
                if len(name) > 2 and len(name) < 100:
                    extracted["vendor_name"] = name
                    extracted["supplier_name"] = name
                    break
        
        # Extract amounts with better patterns
        amount_patterns = [
            r"total\s*(?:amount|due|payable)?\s*:?\s*\$?\s*([\d,]+\.?\d*)",
            r"amount\s*(?:due|payable)?\s*:?\s*\$?\s*([\d,]+\.?\d*)",
            r"grand\s*total\s*:?\s*\$?\s*([\d,]+\.?\d*)",
            r"\$\s*([\d,]+\.?\d*)\s*(?:total|amount)",
        ]
        for pattern in amount_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    amount = float(match.group(1).replace(",", ""))
                    if amount > 0:
                        extracted["total"] = amount
                        extracted["amount"] = amount
                        break
                except:
                    pass
        
        # Extract subtotal
        subtotal_patterns = [
            r"subtotal\s*:?\s*\$?\s*([\d,]+\.?\d*)",
            r"sub\s*total\s*:?\s*\$?\s*([\d,]+\.?\d*)",
        ]
        for pattern in subtotal_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    extracted["subtotal"] = float(match.group(1).replace(",", ""))
                    break
                except:
                    pass
        
        # Extract tax
        tax_patterns = [
            r"tax\s*(?:amount|total)?\s*:?\s*\$?\s*([\d,]+\.?\d*)",
            r"vat\s*:?\s*\$?\s*([\d,]+\.?\d*)",
            r"gst\s*:?\s*\$?\s*([\d,]+\.?\d*)",
        ]
        for pattern in tax_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    extracted["tax"] = float(match.group(1).replace(",", ""))
                    break
                except:
                    pass
        
        # Extract dates with better patterns
        date_patterns = [
            r"(?:invoice|bill|date)\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
            r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
            r"(\d{4}[/-]\d{1,2}[/-]\d{1,2})",
        ]
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                extracted["date"] = match.group(1)
                break
        
        # Extract due date
        due_date_patterns = [
            r"due\s*date\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
            r"payment\s*due\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
        ]
        for pattern in due_date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                extracted["due_date"] = match.group(1)
                break
        
        # Extract email
        email_pattern = r"\b([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b"
        email_match = re.search(email_pattern, text)
        if email_match:
            extracted["email"] = email_match.group(1)
        
        # Extract phone
        phone_patterns = [
            r"(\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})",
            r"(\d{3}[-.\s]?\d{3}[-.\s]?\d{4})",
        ]
        for pattern in phone_patterns:
            phone_match = re.search(pattern, text)
            if phone_match:
                extracted["phone"] = phone_match.group(1)
                break
        
        # Extract currency
        currency_match = re.search(r"currency\s*:?\s*([A-Z]{3})", text, re.IGNORECASE)
        if currency_match:
            extracted["currency"] = currency_match.group(1).upper()
        elif "$" in text or "USD" in text.upper():
            extracted["currency"] = "USD"
        
        # Extract tax ID
        tax_id_patterns = [
            r"tax\s*id\s*:?\s*([A-Z0-9\-]+)",
            r"ein\s*:?\s*([A-Z0-9\-]+)",
            r"vat\s*:?\s*([A-Z0-9\-]+)",
        ]
        for pattern in tax_id_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                extracted["tax_id"] = match.group(1).strip()
                break
        
        return extracted
    
    def save_uploaded_file(self, file_content: bytes, filename: str) -> str:
        """Save uploaded file and return path"""
        file_path = self.upload_dir / filename
        with open(file_path, "wb") as f:
            f.write(file_content)
        return str(file_path)

# Global document service instance
document_service = DocumentService()

