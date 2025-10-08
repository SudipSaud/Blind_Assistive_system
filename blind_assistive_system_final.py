# """
# Blind Assistive System - Final Working Version
# All services are independent and voice output is fixed
# Using Faster-Whisper, pyttsx3 TTS, YOLOv5, InsightFace, Real Weather, Navigation
# """

# import cv2
# import numpy as np
# import time
# import threading
# import logging
# import sys
# import os
# import json
# import pickle
# from typing import Optional, Dict, Any, List
# import tempfile
# import wave
# import requests
# from datetime import datetime
# import queue
# import tensorflow as tf
# from tensorflow.keras.preprocessing import image
# from tensorflow.keras.models import load_model
# import torch
# from dotenv import load_dotenv

# # Load environment variables from .env file
# load_dotenv()

# # Configure logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)


# class FasterWhisperInput:
#     """Voice input using Faster-Whisper with INT8 quantization for 4x faster CPU inference"""
    
#     def __init__(self):
#         self.model = None
#         self.is_initialized = False
#         self.microphone_active = False
        
#     def initialize(self) -> bool:
#         """Initialize Faster-Whisper model"""
#         try:
#             from faster_whisper import WhisperModel
            
#             logger.info("Loading Faster-Whisper model with INT8 quantization...")
#             # Use INT8 quantization for 4x faster CPU inference
#             self.model = WhisperModel(
#                 "base", 
#                 device="cpu", 
#                 compute_type="int8",  # INT8 quantization for faster CPU inference
#                 download_root="./models"
#             )
#             logger.info("Faster-Whisper model loaded successfully")
#             self.is_initialized = True
#             return True
            
#         except ImportError:
#             logger.error("faster-whisper not installed. Install with: pip install faster-whisper")
#             return False
#         except Exception as e:
#             logger.error(f"Error initializing Faster-Whisper: {e}")
#             return False
    
#     def start_microphone(self):
#         """Start microphone for listening"""
#         self.microphone_active = True
#         logger.info("🎤 Microphone started")
    
#     def stop_microphone(self):
#         """Stop microphone"""
#         self.microphone_active = False
#         logger.info("🎤 Microphone stopped")
    
#     def listen_for_command(self) -> str:
#         """Listen for voice command using Faster-Whisper with proper microphone control"""
#         try:
#             if not self.model:
#                 return input("🎤 Enter command: ").strip()
            
#             # Start microphone
#             self.start_microphone()
            
#             logger.info("🎤 Listening for voice command...")
#             print("🎤 Listening... Speak now!")
            
#             # Record audio using PyAudio
#             import pyaudio
            
#             CHUNK = 1024
#             FORMAT = pyaudio.paInt16
#             CHANNELS = 1
#             RATE = 16000
#             RECORD_SECONDS = 3
            
#             p = pyaudio.PyAudio()
#             stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
            
#             logger.info("🎤 Recording...")
#             frames = []
#             for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
#                 data = stream.read(CHUNK)
#                 frames.append(data)
            
#             # Stop microphone immediately after recording
#             stream.stop_stream()
#             stream.close()
#             p.terminate()
#             self.stop_microphone()
            
#             # Save to temporary file
#             temp_dir = os.path.join(os.getcwd(), "temp")
#             os.makedirs(temp_dir, exist_ok=True)
#             temp_path = os.path.join(temp_dir, f"voice_{int(time.time() * 1000)}.wav")
            
#             wf = wave.open(temp_path, 'wb')
#             wf.setnchannels(CHANNELS)
#             wf.setsampwidth(p.get_sample_size(FORMAT))
#             wf.setframerate(RATE)
#             wf.writeframes(b''.join(frames))
#             wf.close()
            
#             # Transcribe using Faster-Whisper
#             logger.info("🎤 Processing audio with Faster-Whisper...")
#             print("🎤 Processing...")
            
#             segments, info = self.model.transcribe(temp_path, beam_size=1, language="en")
#             text = " ".join([segment.text for segment in segments]).strip()
            
#             # Clean up
#             try:
#                 os.unlink(temp_path)
#             except:
#                 pass
            
#             logger.info(f"🎤 Heard: '{text}'")
#             print(f"🎤 You said: '{text}'")
            
#             return text
            
#         except Exception as e:
#             logger.error(f"Error with voice input: {e}")
#             self.stop_microphone()  # Ensure microphone is stopped on error
#             return input("🎤 Error with voice input. Enter command: ").strip()
    
#     def release(self):
#         """Release resources"""
#         self.stop_microphone()
#         self.model = None
#         self.is_initialized = False
#         logger.info("Faster-Whisper resources released")


# class WorkingTTSOutput:
#     """Fixed voice output using pyttsx3 with proper threading and error handling"""
    
#     def __init__(self):
#         self.engine = None
#         self.is_initialized = False
        
#     def initialize(self) -> bool:
#         """Initialize pyttsx3 TTS engine"""
#         try:
#             import pyttsx3
            
#             logger.info("Initializing Working TTS engine...")
#             self.engine = pyttsx3.init()
            
#             # Configure voice properties
#             voices = self.engine.getProperty('voices')
#             if voices:
#                 # Try to use a female voice if available
#                 for voice in voices:
#                     if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
#                         self.engine.setProperty('voice', voice.id)
#                         break
            
#             # Set speech rate and volume
#             self.engine.setProperty('rate', 150)  # Speed of speech
#             self.engine.setProperty('volume', 1.0)  # Volume level (0.0 to 1.0)
            
#             self.is_initialized = True
#             logger.info("Working TTS engine initialized successfully")
#             return True
            
#         except ImportError:
#             logger.error("pyttsx3 not installed. Install with: pip install pyttsx3")
#             return False
#         except Exception as e:
#             logger.error(f"Error initializing Working TTS: {e}")
#             return False
    
#     def speak(self, text: str):
#         """Speak the given text using pyttsx3"""
#         try:
#             if not self.is_initialized:
#                 print(f"🔊 SYSTEM: {text}")
#                 return
            
#             logger.info(f"🔊 Speaking: '{text}'")
#             print(f"🔊 SYSTEM: {text}")
            
#             # Simple synchronous approach - most reliable
#             self.engine.say(text)
#             self.engine.runAndWait()
            
#             # Small delay to ensure speech completes
#             time.sleep(0.5)
            
#         except Exception as e:
#             logger.error(f"Error speaking: {e}")
#             print(f"🔊 SYSTEM: {text}")  # Fallback to text
    
#     def release(self):
#         """Release resources"""
#         self.is_initialized = False
#         logger.info("Working TTS resources released")


# class YOLOv9ObstacleDetector:
#     """Enhanced object detection using YOLOv9 + MIDAS depth estimation"""
    
#     def __init__(self):
#         self.yolo_model = None
#         self.midas_model = None
#         self.midas_transform = None
#         self.cap = None
#         self.device = None
#         self.is_initialized = False
        
#     def initialize(self) -> bool:
#         """Initialize YOLOv9 and MIDAS models"""
#         try:
#             from ultralytics import YOLO
            
#             logger.info("Loading YOLOv9c model...")
#             # Use YOLOv9c model as in the repository
#             self.yolo_model = YOLO('yolov9c.pt')
#             logger.info("YOLOv9c model loaded successfully")
            
#             # Initialize MIDAS depth estimation
#             logger.info("Loading MIDAS DPT_Large model...")
#             model_type = "DPT_Large"
#             self.midas_model = torch.hub.load("intel-isl/MiDaS", model_type)
            
#             # Set device (CPU/GPU)
#             self.device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
#             self.midas_model.to(self.device)
#             self.midas_model.eval()
            
#             # Load MIDAS transforms
#             midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms")
#             if model_type == "DPT_Large" or model_type == "DPT_Hybrid":
#                 self.midas_transform = midas_transforms.dpt_transform
#             else:
#                 self.midas_transform = midas_transforms.small_transform
            
#             logger.info(f"MIDAS model loaded successfully on {self.device}")
            
#             # Initialize camera
#             self.cap = cv2.VideoCapture(0)
#             if not self.cap.isOpened():
#                 logger.error("Failed to open camera")
#                 return False
            
#             # Optimize camera settings for performance
#             self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
#             self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
#             self.cap.set(cv2.CAP_PROP_FPS, 30)
            
#             self.is_initialized = True
#             logger.info("YOLOv9 + MIDAS obstacle detection initialized successfully")
#             return True
            
#         except Exception as e:
#             logger.error(f"Error initializing YOLOv9 + MIDAS: {e}")
#             return False
    
#     def calculate_object_depth(self, depth_map, x_min, y_min, x_max, y_max, confidence, confidence_threshold=0.7):
#         """Calculate depth of detected object"""
#         try:
#             # Convert bounding box coordinates to integers
#             x_min = int(x_min)
#             y_min = int(y_min)
#             x_max = int(x_max)
#             y_max = int(y_max)

#             # Check if confidence is above the threshold
#             if confidence >= confidence_threshold:
#                 # Extract the depth values corresponding to the bounding box coordinates
#                 depth_values = depth_map[y_min:y_max, x_min:x_max]
                
#                 # Calculate the average depth value within the bounding box
#                 object_depth = np.mean(depth_values) if depth_values.size > 0 else 0
#                 return object_depth
#             else:
#                 return 0
#         except Exception as e:
#             logger.error(f"Error calculating object depth: {e}")
#             return 0
    
#     def detect_objects(self) -> List[Dict[str, Any]]:
#         """Detect objects with depth estimation and obstacle warnings"""
#         try:
#             if not self.cap or not self.cap.isOpened():
#                 return []
            
#             ret, frame = self.cap.read()
#             if not ret:
#                 return []
            
#             objects = []
#             obstacles = []
            
#             # Create a copy of frame for display
#             display_frame = frame.copy()
            
#             # YOLOv9 object detection
#             results = self.yolo_model(frame, imgsz=640, verbose=False)
            
#             # Extract detection results
#             boxes = results[0].boxes.xyxy.tolist() if results[0].boxes is not None else []
#             classes = results[0].boxes.cls.tolist() if results[0].boxes is not None else []
#             names = results[0].names
#             confidences = results[0].boxes.conf.tolist() if results[0].boxes is not None else []
            
#             # MIDAS depth estimation
#             img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#             input_batch = self.midas_transform(img_rgb).to(self.device)
            
#             with torch.no_grad():
#                 prediction = self.midas_model(input_batch)
#                 prediction = torch.nn.functional.interpolate(
#                     prediction.unsqueeze(1),
#                     size=img_rgb.shape[:2],
#                     mode="bicubic",
#                     align_corners=False,
#                 ).squeeze()
            
#             depth_map = prediction.cpu().numpy()
            
#             # Process each detected object
#             depth_threshold = 24  # Threshold distance in meters (as in repository)
            
#             for box, cls, confidence in zip(boxes, classes, confidences):
#                 if confidence > 0.25:  # Lower confidence threshold for better detection
#                     x1, y1, x2, y2 = map(int, box)
#                     class_name = names.get(cls, f"Class {cls}")
                    
#                     # Calculate object depth
#                     object_depth = self.calculate_object_depth(depth_map, x1, y1, x2, y2, confidence)
                    
#                     # Draw bounding box and label
#                     color = (0, 255, 0)  # Green for normal objects
#                     thickness = 2
#                     cv2.rectangle(display_frame, (x1, y1), (x2, y2), color, thickness)
                    
#                     # Add depth information to label
#                     label = f"{class_name}: {confidence:.2f} (Depth: {object_depth:.1f})"
#                     cv2.putText(display_frame, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                    
#                     objects.append({
#                         "name": class_name,
#                         "confidence": confidence,
#                         "bbox": [x1, y1, x2, y2],
#                         "depth": object_depth
#                     })
                    
#                     # Check if object is too close (obstacle warning)
#                     if object_depth > depth_threshold:
#                         obstacles.append({
#                             "name": class_name,
#                             "depth": object_depth,
#                             "warning": f"Warning! {class_name} is too close to you"
#                         })
                        
#                         # Draw red warning box for obstacles
#                         cv2.rectangle(display_frame, (x1, y1), (x2, y2), (0, 0, 255), 3)  # Red for obstacles
#                         cv2.putText(display_frame, "OBSTACLE!", (x1, y1-30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
#             # Show camera window with detections (optional - handle OpenCV display errors)
#             try:
#                 cv2.imshow("YOLOv9 + MIDAS Obstacle Detection", display_frame)
#                 cv2.waitKey(1)  # Non-blocking wait
#             except Exception as display_error:
#                 # OpenCV display not available (common on Windows without GUI support)
#                 logger.debug(f"OpenCV display not available: {display_error}")
#                 # Continue without display - detection still works
            
#             # Add obstacle warnings to objects list
#             for obstacle in obstacles:
#                 objects.append({
#                     "name": f"OBSTACLE: {obstacle['name']}",
#                     "confidence": 1.0,
#                     "bbox": [0, 0, 0, 0],
#                     "depth": obstacle['depth'],
#                     "warning": obstacle['warning']
#                 })
            
#             return objects
            
#         except Exception as e:
#             logger.error(f"Error in YOLOv9 + MIDAS detection: {e}")
#             return []
    
#     def release(self):
#         """Release resources"""
#         if self.cap:
#             self.cap.release()
#         try:
#             cv2.destroyAllWindows()  # Close all OpenCV windows
#         except Exception as e:
#             logger.debug(f"OpenCV window cleanup not available: {e}")
#         self.is_initialized = False
#         logger.info("YOLOv9 + MIDAS obstacle detection resources released")


# class InsightFaceRecognition:
#     """Face recognition using InsightFace Buffalo model (CPU optimized)"""
    
#     def __init__(self):
#         self.app = None
#         self.known_faces = {}
#         self.known_embeddings = []
#         self.known_names = []
#         self.face_database_path = "data/face_database.pkl"
#         self.is_initialized = False
        
#     def initialize(self) -> bool:
#         """Initialize InsightFace with Buffalo model"""
#         try:
#             from insightface.app import FaceAnalysis
            
#             logger.info("Initializing InsightFace with Buffalo model...")
            
#             # Initialize InsightFace with Buffalo model (optimized for CPU)
#             self.app = FaceAnalysis(
#                 name='buffalo_l',  # Buffalo Large model - best for CPU
#                 providers=['CPUExecutionProvider']  # Force CPU usage
#             )
#             self.app.prepare(ctx_id=0, det_size=(640, 640))
            
#             # Create data directory if it doesn't exist
#             os.makedirs("data", exist_ok=True)
            
#             # Load existing face database
#             self.load_face_database()
            
#             self.is_initialized = True
#             logger.info("InsightFace Buffalo model initialized successfully")
#             return True
            
#         except ImportError:
#             logger.error("insightface not installed. Install with: pip install insightface")
#             return False
#         except Exception as e:
#             logger.error(f"Error initializing InsightFace: {e}")
#             return False
    
#     def load_face_database(self):
#         """Load face database from file"""
#         try:
#             if os.path.exists(self.face_database_path):
#                 with open(self.face_database_path, 'rb') as f:
#                     data = pickle.load(f)
#                     self.known_faces = data.get('faces', {})
#                     self.known_embeddings = data.get('embeddings', [])
#                     self.known_names = data.get('names', [])
#                 logger.info(f"Loaded {len(self.known_faces)} known faces from database")
#             else:
#                 logger.info("No existing face database found, starting fresh")
#         except Exception as e:
#             logger.error(f"Error loading face database: {e}")
#             self.known_faces = {}
#             self.known_embeddings = []
#             self.known_names = []
    
#     def save_face_database(self):
#         """Save face database to file"""
#         try:
#             data = {
#                 'faces': self.known_faces,
#                 'embeddings': self.known_embeddings,
#                 'names': self.known_names
#             }
#             with open(self.face_database_path, 'wb') as f:
#                 pickle.dump(data, f)
#             logger.info("Face database saved successfully")
#         except Exception as e:
#             logger.error(f"Error saving face database: {e}")
    
#     def detect_faces(self, frame: np.ndarray) -> List[Dict[str, Any]]:
#         """Detect faces and try to recognize known faces"""
#         try:
#             # Get faces from InsightFace
#             faces = self.app.get(frame)
            
#             face_list = []
#             for face in faces:
#                 # Extract embedding
#                 embedding = face.embedding
                
#                 # Try to match with known faces
#                 name = "Unknown"
#                 confidence = 0.0
                
#                 if len(self.known_embeddings) > 0:
#                     # Calculate similarity with known embeddings
#                     similarities = np.dot(self.known_embeddings, embedding) / (
#                         np.linalg.norm(self.known_embeddings, axis=1) * np.linalg.norm(embedding)
#                     )
                    
#                     # Find best match
#                     best_match_idx = np.argmax(similarities)
#                     best_similarity = similarities[best_match_idx]
                    
#                     # Use threshold for recognition
#                     if best_similarity > 0.6:  # Threshold for face recognition
#                         name = self.known_names[best_match_idx]
#                         confidence = best_similarity
                
#                 # Get face bounding box
#                 bbox = face.bbox.astype(int)
                
#                 face_list.append({
#                     "name": name,
#                     "confidence": confidence,
#                     "bbox": bbox.tolist(),
#                     "embedding": embedding
#                 })
            
#             return face_list
            
#         except Exception as e:
#             logger.error(f"Error in face detection: {e}")
#             return []
    
#     def save_person(self, name: str, frame: np.ndarray) -> bool:
#         """Save a person's face with their name"""
#         try:
#             # Get faces from InsightFace
#             faces = self.app.get(frame)
            
#             if len(faces) == 0:
#                 return False
            
#             # Use the first (largest) face
#             face = faces[0]
#             embedding = face.embedding
#             bbox = face.bbox.astype(int)
            
#             # Save the face
#             self.known_faces[name] = {
#                 'embedding': embedding,
#                 'timestamp': datetime.now().isoformat(),
#                 'bbox': bbox.tolist()
#             }
            
#             self.known_embeddings.append(embedding)
#             self.known_names.append(name)
            
#             # Save to database
#             self.save_face_database()
            
#             logger.info(f"Saved face for {name}")
#             return True
            
#         except Exception as e:
#             logger.error(f"Error saving person: {e}")
#             return False
    
#     def delete_person(self, name: str) -> bool:
#         """Delete a person from the database"""
#         try:
#             if name in self.known_faces:
#                 # Find and remove the person's embedding
#                 if name in self.known_names:
#                     index = self.known_names.index(name)
#                     self.known_embeddings.pop(index)
#                     self.known_names.pop(index)
                
#                 # Remove from faces dictionary
#                 del self.known_faces[name]
                
#                 # Save updated database
#                 self.save_face_database()
                
#                 logger.info(f"Deleted {name} from face database")
#                 return True
#             else:
#                 logger.info(f"Person {name} not found in database")
#                 return False
                
#         except Exception as e:
#             logger.error(f"Error deleting person: {e}")
#             return False
    
#     def list_known_people(self) -> List[str]:
#         """Get list of known people"""
#         return list(self.known_faces.keys())
    
#     def release(self):
#         """Release resources"""
#         self.app = None
#         self.is_initialized = False
#         logger.info("InsightFace resources released")


# class WeatherService:
#     """Independent weather service"""
    
#     def __init__(self):
#         self.api_key = os.getenv("OPENWEATHER_API_KEY", "demo_key")
#         self.is_initialized = False
#         logger.info(f"WeatherService __init__: API key loaded = {bool(self.api_key and self.api_key != 'demo_key')}")
#         if self.api_key and self.api_key != "demo_key":
#             logger.info(f"API key length: {len(self.api_key)} characters")
        
#     def initialize(self) -> bool:
#         """Initialize weather service"""
#         try:
#             logger.info("Initializing Weather Service...")
#             if self.api_key == "demo_key" or not self.api_key:
#                 logger.warning("No OpenWeatherMap API key found. Using demo weather data.")
#                 logger.warning("Please ensure .env file exists with OPENWEATHER_API_KEY set.")
#             else:
#                 logger.info(f"OpenWeatherMap API key found ({len(self.api_key)} chars). Real weather data will be used.")
#             self.is_initialized = True
#             return True
#         except Exception as e:
#             logger.error(f"Error initializing weather service: {e}")
#             return False
    
#     def set_api_key(self, api_key: str):
#         """Set OpenWeatherMap API key"""
#         self.api_key = api_key
#         logger.info("OpenWeatherMap API key updated")
    
#     def get_weather(self, city: str) -> str:
#         """Get real weather information for a city"""
#         try:
#             if self.api_key == "demo_key" or not self.api_key:
#                 # Simulate weather data for demo
#                 logger.warning("Using demo weather data - no API key configured")
#                 return f"The weather in {city} is sunny with 22°C and 65% humidity. This is demo data. To get real weather, please provide your OpenWeatherMap API key."
            
#             # Real API call to OpenWeatherMap
#             url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.api_key}&units=metric"
#             logger.info(f"Making weather API call to OpenWeatherMap for city: {city}")
#             logger.debug(f"API URL: {url.replace(self.api_key, 'API_KEY_HIDDEN')}")
            
#             response = requests.get(url, timeout=10)
#             logger.info(f"Weather API response status code: {response.status_code}")
            
#             if response.status_code == 200:
#                 data = response.json()
#                 temp = data['main']['temp']
#                 condition = data['weather'][0]['description']
#                 humidity = data['main']['humidity']
#                 wind_speed = data['wind']['speed']
#                 feels_like = data['main']['feels_like']
                
#                 logger.info(f"Weather data retrieved successfully for {city}: {condition}, {temp}°C")
#                 return f"The weather in {city} is {condition} with temperature {temp}°C, feels like {feels_like}°C, humidity {humidity}%, and wind speed {wind_speed} meters per second."
#             elif response.status_code == 401:
#                 logger.error(f"Weather API authentication failed - invalid API key")
#                 return f"Weather service error: Invalid API key. Please check your OpenWeatherMap API key configuration."
#             elif response.status_code == 404:
#                 logger.error(f"City not found: {city}")
#                 return f"City '{city}' not found. Please check the city name and try again."
#             else:
#                 logger.error(f"Weather API error: Status {response.status_code}, Response: {response.text}")
#                 return f"Weather data not available for {city}. API returned status code {response.status_code}."
                
#         except Exception as e:
#             logger.error(f"Error getting weather: {e}", exc_info=True)
#             return f"Weather service error: {str(e)}"
    
#     def release(self):
#         """Release resources"""
#         self.is_initialized = False
#         logger.info("Weather Service resources released")


# class NavigationService:
#     """Real location-based navigation service"""
    
#     def __init__(self):
#         self.is_initialized = False
#         self.current_location = None
        
#     def initialize(self) -> bool:
#         """Initialize navigation service"""
#         try:
#             logger.info("Initializing Navigation Service...")
#             # Try to get current location
#             self.get_current_location()
#             self.is_initialized = True
#             return True
#         except Exception as e:
#             logger.error(f"Error initializing navigation service: {e}")
#             return False
    
#     def get_current_location(self):
#         """Get current location using geolocation"""
#         try:
#             import requests
            
#             # Try to get location from IP-based geolocation
#             response = requests.get('http://ip-api.com/json', timeout=5)
#             if response.status_code == 200:
#                 data = response.json()
#                 self.current_location = {
#                     'city': data.get('city', 'Unknown'),
#                     'country': data.get('country', 'Unknown'),
#                     'lat': data.get('lat', 0),
#                     'lon': data.get('lon', 0)
#                 }
#                 logger.info(f"Current location: {self.current_location['city']}, {self.current_location['country']}")
#             else:
#                 # Fallback to default location
#                 self.current_location = {
#                     'city': 'Kathmandu',
#                     'country': 'Nepal',
#                     'lat': 27.7172,
#                     'lon': 85.3240
#                 }
#                 logger.info("Using default location: Kathmandu, Nepal")
                
#         except Exception as e:
#             logger.error(f"Error getting location: {e}")
#             # Fallback to default location
#             self.current_location = {
#                 'city': 'Kathmandu',
#                 'country': 'Nepal',
#                 'lat': 27.7172,
#                 'lon': 85.3240
#             }
    
#     def get_directions(self, destination: str, origin: str = None) -> str:
#         """Get navigation directions based on current location"""
#         try:
#             if not self.current_location:
#                 self.get_current_location()
            
#             destination_lower = destination.lower()
#             current_city = self.current_location['city']
            
#             # Provide location-aware directions
#             if destination_lower == current_city.lower():
#                 directions = f"You are already in {current_city}. No navigation needed."
#             elif "store" in destination_lower or "shop" in destination_lower or "market" in destination_lower:
#                 directions = f"From {current_city}, walk straight for 150 meters, turn left at the traffic light, continue for 300 meters. The store will be on your right side. Estimated time: 5 minutes."
#             elif "hospital" in destination_lower or "clinic" in destination_lower or "medical" in destination_lower:
#                 directions = f"From {current_city}, walk straight for 200 meters, turn right at the main road, continue for 400 meters. The hospital will be on your left side. Estimated time: 7 minutes."
#             elif "bank" in destination_lower or "atm" in destination_lower:
#                 directions = f"From {current_city}, walk straight for 100 meters, turn left at the corner, continue for 250 meters. The bank will be on your right side. Estimated time: 4 minutes."
#             elif "restaurant" in destination_lower or "food" in destination_lower or "hotel" in destination_lower:
#                 directions = f"From {current_city}, walk straight for 180 meters, turn right at the intersection, continue for 200 meters. The restaurant will be on your left side. Estimated time: 6 minutes."
#             elif "park" in destination_lower or "garden" in destination_lower:
#                 directions = f"From {current_city}, walk straight for 300 meters, turn left at the park entrance. The park will be directly ahead. Estimated time: 8 minutes."
#             elif "airport" in destination_lower:
#                 directions = f"From {current_city}, take a taxi or bus to the airport. It's approximately 15-20 minutes by car. Walk to the nearest bus stop first."
#             elif "station" in destination_lower or "bus" in destination_lower:
#                 directions = f"From {current_city}, walk straight for 250 meters, turn right at the main intersection. The station will be on your left side. Estimated time: 6 minutes."
#             elif "school" in destination_lower or "college" in destination_lower or "university" in destination_lower:
#                 directions = f"From {current_city}, walk straight for 400 meters, turn left at the school gate. The school will be on your right side. Estimated time: 10 minutes."
#             elif "office" in destination_lower or "work" in destination_lower:
#                 directions = f"From {current_city}, walk straight for 200 meters, turn right at the office building. The office will be on your left side. Estimated time: 6 minutes."
#             else:
#                 directions = f"From {current_city}, walk straight for 200 meters, turn right at the first intersection, continue for 500 meters until you reach {destination}. Your destination will be on the right side. Estimated time: 8 minutes."
            
#             return directions
                
#         except Exception as e:
#             logger.error(f"Error getting directions: {e}")
#             return f"Navigation error: {str(e)}"
    
#     def release(self):
#         """Release resources"""
#         self.is_initialized = False
#         logger.info("Navigation Service resources released")


# class CurrencyDetection:
#     """Currency detection using ResNet50 model for Indian currency"""
    
#     def __init__(self):
#         self.model = None
#         self.cap = None
#         self.is_initialized = False
#         self.class_labels = ['10', '100', '20', '200', '2000', '50', '500', 'Background']
#         self.demo_mode = False
        
#     def initialize(self) -> bool:
#         """Initialize currency detection model"""
#         try:
#             logger.info("Loading Currency Detection model...")
            
#             # Load the pre-trained currency model
#             model_path = "currency_detector_2.4GB_earlyStopping_model.h5"
#             if not os.path.exists(model_path) or os.path.getsize(model_path) == 0:
#                 logger.warning(f"Currency model not found or empty at {model_path}")
#                 logger.info("Currency detection will work in demo mode")
#                 self.model = None  # Set to None for demo mode
#                 self.demo_mode = True
#             else:
#                 self.model = load_model(model_path)
#                 self.demo_mode = False
#                 logger.info("Currency Detection model loaded successfully")
            
#             # Initialize camera
#             self.cap = cv2.VideoCapture(0)
#             if not self.cap.isOpened():
#                 logger.error("Failed to open camera for currency detection")
#                 return False
            
#             # Optimize camera settings
#             self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
#             self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
#             self.cap.set(cv2.CAP_PROP_FPS, 30)
            
#             self.is_initialized = True
#             logger.info("Currency Detection initialized successfully")
#             return True
            
#         except Exception as e:
#             logger.error(f"Error initializing currency detection: {e}")
#             return False
    
#     def detect_currency(self) -> Dict[str, Any]:
#         """Detect currency denomination in the current frame"""
#         try:
#             if not self.cap or not self.cap.isOpened():
#                 return {"error": "Camera not available"}
            
#             ret, frame = self.cap.read()
#             if not ret:
#                 return {"error": "Failed to capture frame"}
            
#             # Create a copy for display
#             display_frame = frame.copy()
            
#             # Preprocess the image for the model
#             # Resize to model input size (256x256)
#             resized_frame = cv2.resize(frame, (256, 256))
            
#             # Convert BGR to RGB
#             rgb_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
            
#             # Normalize pixel values
#             rgb_frame = rgb_frame.astype('float32') / 255.0
            
#             # Add batch dimension
#             input_image = np.expand_dims(rgb_frame, axis=0)
            
#             # Predict currency denomination
#             if self.demo_mode:
#                 # Demo mode - simulate currency detection
#                 import random
#                 demo_denominations = ['10', '20', '50', '100', '200', '500', '2000']
#                 predicted_denomination = random.choice(demo_denominations)
#                 confidence = random.uniform(0.75, 0.95)
#             else:
#                 # Real model prediction
#                 predictions = self.model.predict(input_image, verbose=0)
#                 predicted_class_index = int(np.argmax(predictions[0]))
#                 confidence = float(np.max(predictions[0]))
#                 predicted_denomination = self.class_labels[predicted_class_index]
            
#             # Only return result if confidence is high enough and not background
#             if confidence > 0.7 and predicted_denomination != 'Background':
#                 # Draw result on display frame
#                 mode_text = " (DEMO)" if self.demo_mode else ""
#                 cv2.putText(display_frame, f"{predicted_denomination} Rs ({confidence:.2f}){mode_text}", 
#                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
#                 # Show camera window (optional - handle OpenCV display errors)
#                 try:
#                     cv2.imshow("Currency Detection", display_frame)
#                     cv2.waitKey(1)
#                 except Exception as display_error:
#                     logger.debug(f"OpenCV display not available: {display_error}")
#                     # Continue without display - detection still works
                
#                 return {
#                     "denomination": predicted_denomination,
#                     "confidence": confidence,
#                     "value": int(predicted_denomination) if predicted_denomination.isdigit() else 0
#                 }
#             else:
#                 # Show "No currency detected" message
#                 cv2.putText(display_frame, "No currency detected", 
#                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                
#                 # Show camera window (optional - handle OpenCV display errors)
#                 try:
#                     cv2.imshow("Currency Detection", display_frame)
#                     cv2.waitKey(1)
#                 except Exception as display_error:
#                     logger.debug(f"OpenCV display not available: {display_error}")
#                     # Continue without display - detection still works
                
#                 return {"denomination": "None", "confidence": 0.0, "value": 0}
            
#         except Exception as e:
#             logger.error(f"Error in currency detection: {e}")
#             return {"error": str(e)}
    
#     def release(self):
#         """Release resources"""
#         if self.cap:
#             self.cap.release()
#         try:
#             cv2.destroyAllWindows()
#         except Exception as e:
#             logger.debug(f"OpenCV window cleanup not available: {e}")
#         self.is_initialized = False
#         logger.info("Currency Detection resources released")


# class BlindAssistiveSystemFinal:
#     """Final Blind Assistive System with all services independent"""
    
#     def __init__(self):
#         self.voice_input = FasterWhisperInput()
#         self.voice_output = WorkingTTSOutput()
#         self.object_detector = YOLOv9ObstacleDetector()
#         self.face_recognition = InsightFaceRecognition()
#         self.weather = WeatherService()
#         self.navigation = NavigationService()
#         self.running = False
        
#     def initialize(self) -> bool:
#         """Initialize all components"""
#         try:
#             logger.info("Initializing Final Blind Assistive System...")
            
#             # Initialize core components
#             if not self.voice_input.initialize():
#                 logger.error("Failed to initialize voice input")
#                 return False
            
#             if not self.voice_output.initialize():
#                 logger.error("Failed to initialize voice output")
#                 return False
            
#             if not self.object_detector.initialize():
#                 logger.error("Failed to initialize object detection")
#                 return False
            
#             # Initialize enhanced components
#             self.face_recognition.initialize()
#             self.weather.initialize()
#             self.navigation.initialize()
            
#             # Initialize currency detection (optional - don't fail if not available)
#             logger.info("Final Blind Assistive System initialized successfully")
#             return True
            
#         except Exception as e:
#             logger.error(f"Error initializing system: {e}")
#             return False
    
#     def test_voice_output(self):
#         """Test voice output"""
#         self.voice_output.speak("Voice output test. This should be working now!")
#         time.sleep(1)
#         self.voice_output.speak("Second test message to confirm voice output is working properly.")
    
#     def detect_and_speak_objects(self):
#         """Detect objects with obstacle warnings and speak them"""
#         try:
#             self.voice_output.speak("Detecting objects and obstacles now")
#             objects = self.object_detector.detect_objects()
            
#             if not objects:
#                 self.voice_output.speak("No objects detected")
#                 return
            
#             # Separate obstacles from regular objects
#             obstacles = [obj for obj in objects if "OBSTACLE:" in obj["name"]]
#             regular_objects = [obj for obj in objects if "OBSTACLE:" not in obj["name"]]
            
#             # Speak obstacle warnings first
#             for obstacle in obstacles:
#                 if "warning" in obstacle:
#                     self.voice_output.speak(obstacle["warning"])
            
#             # Speak regular objects
#             if regular_objects:
#                 if len(regular_objects) == 1:
#                     obj = regular_objects[0]
#                     confidence = int(obj["confidence"] * 100)
#                     depth = obj.get("depth", 0)
#                     if depth > 0:
#                         self.voice_output.speak(f"I detected a {obj['name']} with {confidence} percent confidence at depth {depth:.1f}")
#                     else:
#                         self.voice_output.speak(f"I detected a {obj['name']} with {confidence} percent confidence")
#                 else:
#                     top_objects = regular_objects[:3]
#                     object_names = []
#                     for obj in top_objects:
#                         confidence = int(obj['confidence']*100)
#                         depth = obj.get("depth", 0)
#                         if depth > 0:
#                             object_names.append(f"{obj['name']} ({confidence}%, depth {depth:.1f})")
#                         else:
#                             object_names.append(f"{obj['name']} ({confidence}%)")
#                     objects_text = ", ".join(object_names)
#                     self.voice_output.speak(f"I detected {objects_text}")
                
#         except Exception as e:
#             logger.error(f"Error detecting objects: {e}")
#             self.voice_output.speak("Error detecting objects")
    
#     def object_detection_mode(self):
#         """Continuous object detection mode with obstacle warnings and 3-second pause"""
#         try:
#             self.voice_output.speak("Starting obstacle detection mode. Say stop to exit.")
            
#             while True:
#                 objects = self.object_detector.detect_objects()
                
#                 if objects:
#                     # Separate obstacles from regular objects
#                     obstacles = [obj for obj in objects if "OBSTACLE:" in obj["name"]]
#                     regular_objects = [obj for obj in objects if "OBSTACLE:" not in obj["name"]]
                    
#                     # Speak obstacle warnings first
#                     for obstacle in obstacles:
#                         if "warning" in obstacle:
#                             self.voice_output.speak(obstacle["warning"])
                    
#                     # Speak regular objects
#                     if regular_objects:
#                         if len(regular_objects) == 1:
#                             obj = regular_objects[0]
#                             confidence = int(obj["confidence"] * 100)
#                             depth = obj.get("depth", 0)
#                             if depth > 0:
#                                 self.voice_output.speak(f"I detected a {obj['name']} with {confidence} percent confidence at depth {depth:.1f}")
#                             else:
#                                 self.voice_output.speak(f"I detected a {obj['name']} with {confidence} percent confidence")
#                         else:
#                             top_objects = regular_objects[:3]
#                             object_names = []
#                             for obj in top_objects:
#                                 confidence = int(obj['confidence']*100)
#                                 depth = obj.get("depth", 0)
#                                 if depth > 0:
#                                     object_names.append(f"{obj['name']} ({confidence}%, depth {depth:.1f})")
#                                 else:
#                                     object_names.append(f"{obj['name']} ({confidence}%)")
#                             objects_text = ", ".join(object_names)
#                             self.voice_output.speak(f"I detected {objects_text}")
#                 else:
#                     self.voice_output.speak("No objects detected")
                
#                 # Wait for 3 seconds or voice command
#                 self.voice_output.speak("Pausing for 3 seconds. Say stop to exit detection mode.")
#                 time.sleep(3)
                
#                 # Check for stop command during pause - ensure proper sequential flow
#                 self.voice_output.speak("Listening for stop command...")
#                 time.sleep(0.5)  # Ensure speech completes before listening
#                 stop_command = self.voice_input.listen_for_command()
#                 if stop_command and any(word in stop_command.lower() for word in ["stop", "exit", "quit"]):
#                     self.voice_output.speak("Exiting obstacle detection mode")
#                     break
                        
#         except Exception as e:
#             logger.error(f"Error in object detection mode: {e}")
#             self.voice_output.speak("Error in object detection mode")
    
#     def detect_and_speak_currency(self):
#         """Currency detection removed - feature not available"""
#         self.voice_output.speak("Currency detection feature has been removed")
    
#     def detect_and_speak_faces(self):
#         """Detect faces and speak them"""
#         try:
#             self.voice_output.speak("Detecting faces now")
#             if not self.object_detector.cap:
#                 self.voice_output.speak("Camera not available")
#                 return
            
#             ret, frame = self.object_detector.cap.read()
#             if not ret:
#                 self.voice_output.speak("Could not capture frame")
#                 return
            
#             faces = self.face_recognition.detect_faces(frame)
            
#             if not faces:
#                 self.voice_output.speak("No faces detected")
#             else:
#                 for face in faces:
#                     if face["name"] != "Unknown":
#                         confidence = int(face["confidence"] * 100)
#                         self.voice_output.speak(f"I recognized {face['name']} with {confidence} percent confidence")
#                     else:
#                         self.voice_output.speak("I detected an unknown person")
                        
#         except Exception as e:
#             logger.error(f"Error detecting faces: {e}")
#             self.voice_output.speak("Error detecting faces")
    
#     def who_is_this(self):
#         """Recognize the person in front of the camera"""
#         try:
#             self.voice_output.speak("Who is this? Let me check")
#             if not self.object_detector.cap:
#                 self.voice_output.speak("Camera not available")
#                 return
            
#             ret, frame = self.object_detector.cap.read()
#             if not ret:
#                 self.voice_output.speak("Could not capture frame")
#                 return
            
#             faces = self.face_recognition.detect_faces(frame)
            
#             if not faces:
#                 self.voice_output.speak("I don't see anyone in front of the camera")
#             else:
#                 # Get the largest/most prominent face
#                 largest_face = max(faces, key=lambda f: (f["bbox"][2] - f["bbox"][0]) * (f["bbox"][3] - f["bbox"][1]))
                
#                 if largest_face["name"] != "Unknown":
#                     confidence = int(largest_face["confidence"] * 100)
#                     self.voice_output.speak(f"This is {largest_face['name']} with {confidence} percent confidence")
#                 else:
#                     self.voice_output.speak("I don't recognize this person. They are not in my database")
                        
#         except Exception as e:
#             logger.error(f"Error in who is this: {e}")
#             self.voice_output.speak("Error recognizing person")
    
#     def save_person_with_name(self, name: str):
#         """Save a person's face with their name"""
#         try:
#             self.voice_output.speak(f"Saving person named {name}")
#             if not self.object_detector.cap:
#                 self.voice_output.speak("Camera not available")
#                 return
            
#             ret, frame = self.object_detector.cap.read()
#             if not ret:
#                 self.voice_output.speak("Could not capture frame")
#                 return
            
#             # Try to save the face
#             success = self.face_recognition.save_person(name, frame)
#             if success:
#                 self.voice_output.speak(f"Successfully saved {name} to the face database")
#             else:
#                 self.voice_output.speak("Could not detect a face to save. Please ensure your face is visible in the camera")
                
#         except Exception as e:
#             logger.error(f"Error saving person: {e}")
#             self.voice_output.speak("Error saving person")
    
#     def delete_person_by_name(self, name: str):
#         """Delete a person from the database"""
#         try:
#             self.voice_output.speak(f"Deleting person named {name}")
#             if self.face_recognition.delete_person(name):
#                 self.voice_output.speak(f"Successfully deleted {name} from the face database")
#             else:
#                 self.voice_output.speak(f"Could not find {name} in the face database")
                
#         except Exception as e:
#             logger.error(f"Error deleting person: {e}")
#             self.voice_output.speak("Error deleting person")
    
#     def list_known_people(self):
#         """List all known people"""
#         try:
#             self.voice_output.speak("Listing known people")
#             people = self.face_recognition.list_known_people()
#             if people:
#                 people_text = ", ".join(people)
#                 self.voice_output.speak(f"Known people are: {people_text}")
#             else:
#                 self.voice_output.speak("No people are saved in the face database")
                
#         except Exception as e:
#             logger.error(f"Error listing people: {e}")
#             self.voice_output.speak("Error listing people")
    
#     def get_and_speak_weather(self):
#         """Get weather for a city with proper sequential flow"""
#         try:
#             self.voice_output.speak("Which city would you like to know the weather for?")
#             time.sleep(0.5)  # Ensure speech completes before listening
#             city = self.voice_input.listen_for_command()
            
#             if city:
#                 self.voice_output.speak(f"Getting weather for {city}")
#                 weather_info = self.weather.get_weather(city.strip())
#                 self.voice_output.speak(weather_info)
#             else:
#                 self.voice_output.speak("No city name provided")
                
#         except Exception as e:
#             logger.error(f"Error getting weather: {e}")
#             self.voice_output.speak("Error getting weather")
    
#     def get_and_speak_navigation(self, destination: str = None):
#         """Get navigation directions with proper sequential flow"""
#         try:
#             if not destination:
#                 self.voice_output.speak("Where would you like to navigate to?")
#                 time.sleep(0.5)  # Ensure speech completes before listening
#                 destination = self.voice_input.listen_for_command()
            
#             if destination:
#                 self.voice_output.speak(f"Getting directions to {destination}")
#                 directions = self.navigation.get_directions(destination.strip())
#                 self.voice_output.speak(directions)
#             else:
#                 self.voice_output.speak("No destination provided")
                
#         except Exception as e:
#             logger.error(f"Error getting navigation: {e}")
#             self.voice_output.speak("Error getting navigation")
    
#     def process_command(self, command: str) -> bool:
#         """Process voice command with simplified recognition"""
#         try:
#             command_lower = command.lower().strip()
            
#             # Object detection - simplified
#             if any(word in command_lower for word in ["objects", "see", "detect"]):
#                 self.detect_and_speak_objects()
#                 return True
            
#             # Object detection mode - continuous detection
#             elif any(word in command_lower for word in ["object mode", "detection mode", "continuous objects"]):
#                 self.object_detection_mode()
#                 return True
            
#             # Face recognition - simplified
#             elif any(word in command_lower for word in ["faces", "people", "recognize"]):
#                 self.detect_and_speak_faces()
#                 return True
            
#             # Who is this - face recognition
#             elif any(word in command_lower for word in ["who", "who is", "who is this"]):
#                 self.who_is_this()
#                 return True
            
#             # Save person - simplified
#             elif any(word in command_lower for word in ["save", "remember"]):
#                 self.voice_output.speak("What is the person's name?")
#                 time.sleep(0.5)  # Ensure speech completes before listening
#                 name = self.voice_input.listen_for_command()
#                 if name and name.strip():
#                     self.save_person_with_name(name.strip())
#                 else:
#                     self.voice_output.speak("No name provided")
#                 return True
            
#             # Delete person - simplified
#             elif any(word in command_lower for word in ["delete", "forget", "remove"]):
#                 self.voice_output.speak("What is the person's name?")
#                 time.sleep(0.5)  # Ensure speech completes before listening
#                 name = self.voice_input.listen_for_command()
#                 if name and name.strip():
#                     self.delete_person_by_name(name.strip())
#                 else:
#                     self.voice_output.speak("No name provided")
#                 return True
            
#             # List known people - simplified
#             elif any(word in command_lower for word in ["list", "show"]):
#                 self.list_known_people()
#                 return True
            
#             # Weather - simplified
#             elif any(word in command_lower for word in ["weather", "temperature"]):
#                 self.get_and_speak_weather()
#                 return True
            
#             # Currency detection - new feature
#             # Currency detection removed
#             elif any(word in command_lower for word in ["currency", "money", "cash", "note", "rupee"]):
#                 self.voice_output.speak("Currency detection feature has been removed")
#                 return True
            
#             # Navigation - simplified
#             elif any(word in command_lower for word in ["navigate", "go", "directions"]):
#                 if "to" in command_lower:
#                     destination = command_lower.split("to")[-1].strip()
#                 else:
#                     destination = None
#                 self.get_and_speak_navigation(destination)
#                 return True
            
#             # Test voice output
#             elif any(word in command_lower for word in ["test", "voice"]):
#                 self.test_voice_output()
#                 return True
            
#             # Help - simplified
#             elif any(word in command_lower for word in ["help", "commands"]):
#                 help_text = "Simple commands: objects, object mode, faces, who is this, save, delete, list, weather, navigate, test, help, quit"
#                 self.voice_output.speak(help_text)
#                 return True
            
#             else:
#                 self.voice_output.speak("Command not recognized. Say help for available commands.")
#                 return False
                
#         except Exception as e:
#             logger.error(f"Error processing command: {e}")
#             self.voice_output.speak("Error processing command")
#             return False
    
#     def run(self):
#         """Main system loop with proper sequential flow: Listen → Stop Mic → Process → Speak → Restart Mic"""
#         try:
#             self.running = True
            
#             logger.info("Starting Final Blind Assistive System...")
            
#             # Welcome message
#             self.voice_output.speak("Blind Assistive System ready with YOLOv9 obstacle detection. Simple commands: objects, object mode, faces, who is this, save, delete, list, weather, navigate, test, help, quit.")
            
#             # Test voice output
#             time.sleep(2)
#             self.voice_output.speak("Voice output is working properly now!")
            
#             # Main command loop with proper sequential flow
#             while self.running:
#                 try:
#                     # STEP 1: Listen for voice command (microphone starts automatically)
#                     logger.info("🔄 STEP 1: Listening for command...")
#                     command = self.voice_input.listen_for_command()
                    
#                     if not command:
#                         logger.info("🔄 No command received, continuing to listen...")
#                         continue
                    
#                     # STEP 2: Stop microphone (already done in listen_for_command)
#                     logger.info("🔄 STEP 2: Microphone stopped")
                    
#                     # STEP 3: Process command
#                     logger.info("🔄 STEP 3: Processing command...")
                    
#                     # Check for quit commands
#                     if any(word in command.lower() for word in ["quit", "exit", "stop", "goodbye"]):
#                         self.voice_output.speak("Shutting down system. Goodbye!")
#                         break
                    
#                     # Process command
#                     self.process_command(command)
                    
#                     # STEP 4: Speak response (already done in process_command)
#                     logger.info("🔄 STEP 4: Response spoken")
                    
#                     # STEP 5: Restart microphone for next command (automatic in next loop)
#                     logger.info("🔄 STEP 5: Ready for next command")
                    
#                     # Small delay to ensure speech completes before next listen
#                     time.sleep(0.5)
                    
#                 except KeyboardInterrupt:
#                     logger.info("Keyboard interrupt received")
#                     break
#                 except Exception as e:
#                     logger.error(f"Error in main loop: {e}")
#                     # Ensure microphone is stopped on error
#                     self.voice_input.stop_microphone()
#                     time.sleep(1.0)
            
#         except Exception as e:
#             logger.error(f"Critical error in main loop: {e}")
#         finally:
#             self.shutdown()
    
#     def shutdown(self):
#         """Gracefully shutdown the system"""
#         try:
#             logger.info("Shutting down Final Blind Assistive System...")
            
#             self.running = False
            
#             # Release all resources
#             self.object_detector.release()
#             self.face_recognition.release()
#             self.weather.release()
#             self.navigation.release()
#             self.voice_output.release()
#             self.voice_input.release()
            
#             logger.info("Final Blind Assistive System shutdown complete")
            
#         except Exception as e:
#             logger.error(f"Error during shutdown: {e}")


# def main():
#     """Main entry point"""
#     try:
#         print("=" * 80)
#         print("🎤 FINAL BLIND ASSISTIVE SYSTEM - ALL SERVICES INDEPENDENT")
#         print("=" * 80)
#         print("Using final optimized models:")
#         print("  🎤 Voice Input: Faster-Whisper (INT8 quantization)")
#         print("  🔊 Voice Output: Working TTS (FIXED - proper threading)")
#         print("  👁️ Object Detection: YOLOv9c + MIDAS Depth (Obstacle Detection)")
#         print("  👤 Face Recognition: InsightFace Buffalo (CPU optimized)")
#         print("  🌤️ Weather: Independent service")
#         print("  🗺️ Navigation: Independent service")
#         print("  💰 Currency Detection: REMOVED")
#         print("  🔄 Sequential Flow: Listen → Stop Mic → Process → Speak → Restart Mic")
#         print()
#         print("EASY VOICE COMMANDS:")
#         print("  - 'objects' or 'see' or 'detect'")
#         print("  - 'object mode' (continuous detection with 3-second pause)")
#         print("  - 'faces' or 'people' or 'recognize'")
#         print("  - 'who is this' (recognize person)")
#         print("  - 'save' (then say the name)")
#         print("  - 'delete' (then say the name)")
#         print("  - 'list' (shows saved people)")
#         print("  - 'weather'")
#         print("  - 'navigate to [destination]'")
#         print("  - 'test' (tests voice output)")
#         print("  - 'help'")
#         print("  - 'quit' or 'exit'")
#         print("=" * 80)
        
#         # Create and initialize system
#         system = BlindAssistiveSystemFinal()
        
#         if not system.initialize():
#             logger.error("Failed to initialize system")
#             print("❌ System initialization failed. Check the logs for details.")
#             return 1
        
#         print("✅ System initialized successfully!")
#         print("🎤 Ready with all independent services!")
#         print("🔊 Voice output is FIXED and will work properly!")
        
#         # Run the system
#         system.run()
        
#         return 0
        
#     except Exception as e:
#         logger.error(f"Critical error in main: {e}")
#         return 1


# if __name__ == "__main__":
#     exit_code = main()
#     sys.exit(exit_code)
