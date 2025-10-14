"""
Vision Module for Scene Description, VQA, and Feature Extraction
"""
import logging
from PIL import Image
from transformers import pipeline, AutoProcessor, AutoModel
import torch

logger = logging.getLogger(__name__)

class VisionModule:
    def __init__(self):
        self.captioner = None
        self.vqa_pipeline = None
        self.feature_extractor = None
        self.feature_model = None
        self.is_initialized = False

    def load_model(self):
        if self.is_initialized:
            return
        try:
            logger.info("Loading vision models (Captioner, VQA, and Feature Extractor)...")
            device = "cuda" if torch.cuda.is_available() else "cpu"
            
            # Captioner
            self.captioner = pipeline("image-to-text", 
                                      model="microsoft/git-base",
                                      device=device)
            
            # VQA
            self.vqa_pipeline = pipeline("visual-question-answering", 
                                         model="Salesforce/blip-vqa-base",
                                         device=device)

            # Feature Extractor for Embeddings
            feature_model_name = "microsoft/git-base"
            self.feature_extractor = AutoProcessor.from_pretrained(feature_model_name)
            self.feature_model = AutoModel.from_pretrained(feature_model_name).to(device)

            self.is_initialized = True
            logger.info("Vision models loaded successfully.")
        except Exception as e:
            logger.error(f"Error loading vision models: {e}")
            self.is_initialized = False

    def describe_scene(self, image: Image.Image) -> str:
        if not self.is_initialized or not self.captioner:
            return "Vision model not ready."
        
        results = self.captioner(image)
        return results[0]['generated_text']

    def answer_question(self, image: Image.Image, question: str) -> str:
        if not self.is_initialized or not self.vqa_pipeline:
            return "VQA model not ready."
            
        results = self.vqa_pipeline(image, question=question)
        return results[0]['answer']

    def get_image_embedding(self, image: Image.Image) -> list:
        """
        Generates a feature embedding for a given image.
        """
        if not self.is_initialized or not self.feature_model:
            logger.error("Feature extraction model not ready.")
            return None
        
        device = self.feature_model.device
        inputs = self.feature_extractor(images=image, return_tensors="pt").to(device)
        
        with torch.no_grad():
            image_features = self.feature_model.get_image_features(pixel_values=inputs.pixel_values)
        
        # Normalize the features
        image_features = image_features / image_features.norm(dim=-1, keepdim=True)

        # Return as a list
        return image_features.cpu().numpy().flatten().tolist()
