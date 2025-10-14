"""
Face Recognition Module - InsightFace Buffalo Model
"""
import os
import numpy as np
import logging
from typing import List, Dict, Any
from insightface.app import FaceAnalysis
from config import INSIGHTFACE_MODEL
from modules.database import DatabaseManager # Import DatabaseManager

logger = logging.getLogger(__name__)

class FaceRecognizer:
    def __init__(self, db_manager: DatabaseManager):
        self.app = None
        self.known_embeddings = []
        self.known_names = []
        self.db_manager = db_manager # Use the database manager
        self.is_initialized = False

    def load_model(self):
        if self.is_initialized:
            return
        try:
            logger.info("Initializing InsightFace with Buffalo model...")
            self.app = FaceAnalysis(name=INSIGHTFACE_MODEL, providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
            self.app.prepare(ctx_id=0, det_size=(640, 640))
            self._load_database()
            self.is_initialized = True
            logger.info("InsightFace model initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing InsightFace: {e}")
            self.is_initialized = False

    def _load_database(self):
        """Loads known faces from the MongoDB database."""
        all_people = self.db_manager.get_all_people()
        if all_people:
            self.known_names = [person['name'] for person in all_people]
            # Ensure embeddings are numpy arrays for calculations
            self.known_embeddings = [np.array(person['face_embedding']) for person in all_people]
            logger.info(f"Loaded {len(self.known_names)} known faces from database.")
        else:
            logger.info("No existing face database found.")

    def recognize(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        if not self.is_initialized:
            return []
        
        faces = self.app.get(frame)
        recognized_faces = []
        
        if not self.known_embeddings:
            for face in faces:
                 recognized_faces.append({"name": "Unknown", "confidence": 0.0, "box": face.bbox.astype(int).tolist()})
            return recognized_faces

        for face in faces:
            embedding = face.embedding
            # Using cosine similarity
            # Ensure known_embeddings is a 2D numpy array for this operation
            sims = np.dot(np.array(self.known_embeddings), embedding) / (np.linalg.norm(self.known_embeddings, axis=1) * np.linalg.norm(embedding))
            best_match_idx = np.argmax(sims)
            confidence = sims[best_match_idx]

            if confidence > 0.6: # Recognition threshold
                name = self.known_names[best_match_idx]
            else:
                name = "Unknown"
            
            recognized_faces.append({
                "name": name,
                "confidence": float(confidence),
                "box": face.bbox.astype(int).tolist()
            })
        return recognized_faces

    def save_face(self, name: str, frame: np.ndarray) -> bool:
        if not self.is_initialized:
            return False
        
        faces = self.app.get(frame)
        if not faces:
            logger.warning("No face detected in frame to save.")
            return False
        
        # Use the largest face found in the frame
        largest_face = max(faces, key=lambda face: (face.bbox[2] - face.bbox[0]) * (face.bbox[3] - face.bbox[1]))
        embedding = largest_face.embedding
        
        # Normalize name
        clean_name = name.strip().title()

        # Save to database via DatabaseManager
        success = self.db_manager.add_person(clean_name, embedding.tolist()) # Store as list

        if success:
            # Reload the in-memory database to include the new face immediately
            self._load_database()
            logger.info(f"Successfully saved face for {clean_name}.")
            return True
        else:
            logger.error(f"Failed to save face for {clean_name} to the database.")
            return False
