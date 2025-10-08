"""
OCR Service Module - Text extraction using RapidOCR
"""

import logging
import cv2
import numpy as np
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class OCRService:
    """OCR service using RapidOCR for text extraction"""
    
    def __init__(self):
        self.ocr_engine = None
        self.is_initialized = False
        
    def initialize(self) -> bool:
        """Initialize RapidOCR engine"""
        try:
            from rapidocr_onnxruntime import RapidOCR
            
            logger.info("Initializing OCR Service with RapidOCR...")
            
            # Initialize RapidOCR with ONNX runtime for CPU optimization
            self.ocr_engine = RapidOCR(
                use_angle_cls=True,  # Enable text angle classification
                use_text_det=True,   # Enable text detection
                use_text_rec=True,   # Enable text recognition
                text_score=0.5,      # Text confidence threshold
                det_db_thresh=0.3,   # Detection threshold
                det_db_box_thresh=0.5,  # Detection box threshold
                det_db_unclip_ratio=1.6,  # Detection unclip ratio
                det_model_dir=None,  # Use default models
                rec_model_dir=None,  # Use default models
                cls_model_dir=None,  # Use default models
                print_verbose=False  # Reduce verbose output
            )
            
            self.is_initialized = True
            logger.info("OCR Service initialized successfully with RapidOCR")
            return True
            
        except ImportError:
            logger.error("RapidOCR not installed. Install with: pip install rapidocr-onnxruntime")
            return False
        except Exception as e:
            logger.error(f"Error initializing OCR Service: {e}")
            return False
    
    def extract_text_from_image(self, image: np.ndarray) -> List[Dict]:
        """
        Extract text from image using RapidOCR
        
        Args:
            image: Input image as numpy array
            
        Returns:
            List of dictionaries containing text, confidence, and bounding box
        """
        try:
            if not self.is_initialized or not self.ocr_engine:
                logger.error("OCR Service not initialized")
                return []
            
            logger.info("Extracting text from image using RapidOCR...")
            
            # Perform OCR on the image
            result, _ = self.ocr_engine(image)
            
            if not result:
                logger.info("No text detected in image")
                return []
            
            # Format results
            text_results = []
            for item in result:
                if len(item) >= 2:
                    bbox = item[0]  # Bounding box coordinates
                    text = item[1]   # Extracted text
                    confidence = item[2] if len(item) > 2 else 1.0  # Confidence score
                    
                    text_results.append({
                        'text': text.strip(),
                        'confidence': float(confidence),
                        'bbox': bbox
                    })
            
            logger.info(f"OCR extracted {len(text_results)} text elements")
            return text_results
            
        except Exception as e:
            logger.error(f"Error extracting text from image: {e}")
            return []
    
    def extract_text_from_camera(self, camera_capture) -> List[Dict]:
        """
        Capture image from camera and extract text
        
        Args:
            camera_capture: OpenCV camera capture object
            
        Returns:
            List of dictionaries containing extracted text information
        """
        try:
            if not camera_capture:
                logger.error("Camera not available")
                return []
            
            # Capture frame from camera
            ret, frame = camera_capture.read()
            if not ret:
                logger.error("Could not capture frame from camera")
                return []
            
            logger.info("Captured frame for OCR processing")
            
            # Extract text from captured frame
            return self.extract_text_from_image(frame)
            
        except Exception as e:
            logger.error(f"Error capturing and processing camera image: {e}")
            return []
    
    def format_text_for_speech(self, text_results: List[Dict]) -> str:
        """
        Format OCR results into a speech-friendly string
        
        Args:
            text_results: List of OCR results
            
        Returns:
            Formatted string for text-to-speech
        """
        try:
            if not text_results:
                return "No text detected in the image"
            
            # Extract just the text content
            texts = [result['text'] for result in text_results if result['text'].strip()]
            
            if not texts:
                return "No readable text found"
            
            # Join all text with proper spacing
            combined_text = " ".join(texts)
            
            # Clean up the text for better speech
            combined_text = combined_text.replace('\n', ' ')
            combined_text = ' '.join(combined_text.split())  # Remove extra spaces
            
            logger.info(f"Formatted text for speech: {len(combined_text)} characters")
            return combined_text
            
        except Exception as e:
            logger.error(f"Error formatting text for speech: {e}")
            return "Error processing extracted text"
    
    def get_detailed_text_info(self, text_results: List[Dict]) -> str:
        """
        Get detailed information about detected text
        
        Args:
            text_results: List of OCR results
            
        Returns:
            Detailed string describing detected text
        """
        try:
            if not text_results:
                return "No text detected in the image"
            
            total_texts = len(text_results)
            high_confidence_texts = [r for r in text_results if r['confidence'] > 0.8]
            
            info_parts = [f"Detected {total_texts} text elements"]
            
            if high_confidence_texts:
                info_parts.append(f"{len(high_confidence_texts)} with high confidence")
            
            # Add some sample text if available
            sample_texts = [r['text'] for r in text_results[:3] if r['text'].strip()]
            if sample_texts:
                sample_text = " ".join(sample_texts)
                if len(sample_text) > 100:
                    sample_text = sample_text[:100] + "..."
                info_parts.append(f"Sample text: {sample_text}")
            
            return ". ".join(info_parts)
            
        except Exception as e:
            logger.error(f"Error getting detailed text info: {e}")
            return "Error analyzing detected text"
    
    def release(self):
        """Release OCR resources"""
        try:
            self.ocr_engine = None
            self.is_initialized = False
            logger.info("OCR Service resources released")
            
        except Exception as e:
            logger.error(f"Error releasing OCR resources: {e}")
