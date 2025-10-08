"""
Face Recognition Module - InsightFace Buffalo Model
"""

import os
import pickle
import numpy as np
import logging
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class InsightFaceRecognition:
    """Face recognition using InsightFace Buffalo model (CPU optimized)"""
    
    def __init__(self):
        self.app = None
        self.known_faces = {}
        self.known_embeddings = []
        self.known_names = []
        self.face_database_path = "data/face_database.pkl"
        self.is_initialized = False
        
    def initialize(self) -> bool:
        """Initialize InsightFace with Buffalo model"""
        try:
            from insightface.app import FaceAnalysis
            
            logger.info("Initializing InsightFace with Buffalo model...")
            
            # Initialize InsightFace with Buffalo model (optimized for CPU)
            self.app = FaceAnalysis(
                name='buffalo_l',  # Buffalo Large model - best for CPU
                providers=['CPUExecutionProvider']  # Force CPU usage
            )
            self.app.prepare(ctx_id=0, det_size=(640, 640))
            
            # Create data directory if it doesn't exist
            os.makedirs("data", exist_ok=True)
            
            # Load existing face database
            self.load_face_database()
            
            self.is_initialized = True
            logger.info("InsightFace Buffalo model initialized successfully")
            return True
            
        except ImportError:
            logger.error("insightface not installed. Install with: pip install insightface")
            return False
        except Exception as e:
            logger.error(f"Error initializing InsightFace: {e}")
            return False
    
    def load_face_database(self):
        """Load face database from file"""
        try:
            if os.path.exists(self.face_database_path):
                with open(self.face_database_path, 'rb') as f:
                    data = pickle.load(f)
                    self.known_faces = data.get('faces', {})
                    self.known_embeddings = data.get('embeddings', [])
                    self.known_names = data.get('names', [])
                logger.info(f"Loaded {len(self.known_faces)} known faces from database")
            else:
                logger.info("No existing face database found, starting fresh")
        except Exception as e:
            logger.error(f"Error loading face database: {e}")
            self.known_faces = {}
            self.known_embeddings = []
            self.known_names = []
    
    def save_face_database(self):
        """Save face database to file"""
        try:
            data = {
                'faces': self.known_faces,
                'embeddings': self.known_embeddings,
                'names': self.known_names
            }
            with open(self.face_database_path, 'wb') as f:
                pickle.dump(data, f)
            logger.info("Face database saved successfully")
        except Exception as e:
            logger.error(f"Error saving face database: {e}")
    
    def detect_faces(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """Detect faces and try to recognize known faces"""
        try:
            # Get faces from InsightFace
            faces = self.app.get(frame)
            
            face_list = []
            for face in faces:
                # Extract embedding
                embedding = face.embedding
                
                # Try to match with known faces
                name = "Unknown"
                confidence = 0.0
                
                if len(self.known_embeddings) > 0:
                    # Calculate similarity with known embeddings
                    similarities = np.dot(self.known_embeddings, embedding) / (
                        np.linalg.norm(self.known_embeddings, axis=1) * np.linalg.norm(embedding)
                    )
                    
                    # Find best match
                    best_match_idx = np.argmax(similarities)
                    best_similarity = similarities[best_match_idx]
                    
                    # Use threshold for recognition
                    if best_similarity > 0.6:  # Threshold for face recognition
                        name = self.known_names[best_match_idx]
                        confidence = best_similarity
                
                # Get face bounding box
                bbox = face.bbox.astype(int)
                
                face_list.append({
                    "name": name,
                    "confidence": confidence,
                    "bbox": bbox.tolist(),
                    "embedding": embedding
                })
            
            return face_list
            
        except Exception as e:
            logger.error(f"Error in face detection: {e}")
            return []
    
    def save_person(self, name: str, frame: np.ndarray) -> bool:
        """Save a person's face with their name"""
        try:
            # Normalize the name - remove punctuation and extra spaces, capitalize first letter
            name_clean = name.strip().rstrip('.,!?;:').strip()
            name_clean = ' '.join(name_clean.split())  # Remove extra spaces
            name_clean = name_clean.title()  # Capitalize first letter of each word
            
            # Get faces from InsightFace
            faces = self.app.get(frame)
            
            if len(faces) == 0:
                return False
            
            # Use the first (largest) face
            face = faces[0]
            embedding = face.embedding
            bbox = face.bbox.astype(int)
            
            # Save the face with clean name
            self.known_faces[name_clean] = {
                'embedding': embedding,
                'timestamp': datetime.now().isoformat(),
                'bbox': bbox.tolist()
            }
            
            self.known_embeddings.append(embedding)
            self.known_names.append(name_clean)
            
            # Save to database
            self.save_face_database()
            
            logger.info(f"Saved face for {name_clean}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving person: {e}")
            return False
    
    def delete_person(self, name: str) -> bool:
        """Delete a person from the database"""
        try:
            # Normalize the name - remove punctuation and convert to lowercase for matching
            name_normalized = name.strip().rstrip('.,!?;:').strip().lower()
            
            # Try to find the person with normalized matching
            found_name = None
            for saved_name in self.known_faces.keys():
                if saved_name.lower() == name_normalized:
                    found_name = saved_name
                    break
            
            if found_name:
                # Find and remove the person's embedding
                if found_name in self.known_names:
                    index = self.known_names.index(found_name)
                    self.known_embeddings.pop(index)
                    self.known_names.pop(index)
                
                # Remove from faces dictionary
                del self.known_faces[found_name]
                
                # Save updated database
                self.save_face_database()
                
                logger.info(f"Deleted {found_name} from face database")
                return True
            else:
                logger.info(f"Person {name} not found in database")
                logger.info(f"Available people: {list(self.known_faces.keys())}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting person: {e}")
            return False
    
    def list_known_people(self) -> List[str]:
        """Get list of known people"""
        return list(self.known_faces.keys())
    
    def release(self):
        """Release resources"""
        self.app = None
        self.is_initialized = False
        logger.info("InsightFace resources released")

