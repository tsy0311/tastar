"""
ML Service for loading and using trained models
"""
from pathlib import Path
from typing import Dict, Any, Optional
import pickle
import json
from app.core.logging import logger

class MLService:
    """Service for loading and using trained ML models"""
    
    def __init__(self):
        self.models_dir = Path(__file__).parent.parent.parent / 'ml' / 'models'
        self._document_classifier = None
        self._vectorizer = None
        self._sentiment_analyzer = None
    
    def _load_document_classifier(self):
        """Lazy load document classifier"""
        if self._document_classifier is None:
            try:
                model_dir = self.models_dir / 'document_classifier'
                if (model_dir / 'model.pkl').exists():
                    with open(model_dir / 'model.pkl', 'rb') as f:
                        self._document_classifier = pickle.load(f)
                    with open(model_dir / 'vectorizer.pkl', 'rb') as f:
                        self._vectorizer = pickle.load(f)
                    logger.info("Document classifier loaded successfully")
                else:
                    logger.warning("Document classifier not found. Train model first.")
            except Exception as e:
                logger.error(f"Error loading document classifier: {e}")
        
        return self._document_classifier, self._vectorizer
    
    def classify_document(self, text: str) -> Dict[str, Any]:
        """
        Classify document type using trained model
        
        Args:
            text: Document text (from OCR or manual input)
            
        Returns:
            Dict with 'type', 'confidence', and 'probabilities'
        """
        model, vectorizer = self._load_document_classifier()
        
        if model is None or vectorizer is None:
            # Fallback to rule-based (synchronous)
            from app.services.document_service import document_service
            import asyncio
            try:
                result = asyncio.run(document_service._classify_document(text))
                return {
                    'type': result.get('type', 'general'),
                    'confidence': result.get('confidence', 0.5),
                    'method': 'rule_based'
                }
            except:
                return {
                    'type': 'general',
                    'confidence': 0.5,
                    'method': 'rule_based_fallback'
                }
        
        try:
            # Vectorize text
            text_vec = vectorizer.transform([text])
            
            # Predict
            prediction = model.predict(text_vec)[0]
            probabilities = model.predict_proba(text_vec)[0]
            confidence = max(probabilities)
            
            # Get class names
            classes = model.classes_
            prob_dict = {cls: float(prob) for cls, prob in zip(classes, probabilities)}
            
            return {
                'type': prediction,
                'confidence': float(confidence),
                'probabilities': prob_dict,
                'method': 'ml_model'
            }
        except Exception as e:
            logger.error(f"Error classifying document: {e}")
            return {
                'type': 'general',
                'confidence': 0.0,
                'error': str(e),
                'method': 'error'
            }
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment using trained model
        
        Args:
            text: Text to analyze
            
        Returns:
            Dict with 'sentiment' and 'score'
        """
        # TODO: Load sentiment model when available
        # For now, use rule-based from AI service
        from app.services.ai_service import ai_service
        import asyncio
        
        try:
            result = asyncio.run(ai_service.analyze_sentiment(text))
            result['method'] = 'rule_based'
            return result
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {
                'sentiment': 'neutral',
                'score': 0.5,
                'error': str(e),
                'method': 'error'
            }
    
    def extract_entities(self, text: str) -> Dict[str, Any]:
        """
        Extract entities using trained NER model
        
        Args:
            text: Text to extract entities from
            
        Returns:
            Dict with extracted entities
        """
        # TODO: Load NER model when available
        # For now, use regex-based from AI service
        from app.services.ai_service import ai_service
        import asyncio
        
        try:
            result = asyncio.run(ai_service.extract_entities(text))
            result['method'] = 'regex_based'
            return result
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            return {
                'entities': {},
                'error': str(e),
                'method': 'error'
            }

# Global ML service instance
ml_service = MLService()

