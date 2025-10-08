"""
Blind Assistive System - Main Orchestrator
Modular architecture with separate services for each feature
"""

import logging
import sys
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import all service modules
from voice_input import FasterWhisperInput
from voice_output import WorkingTTSOutput
from object_detection import YOLOv9ObstacleDetector
from face_recognition_service import InsightFaceRecognition
from weather_service import WeatherService
from navigation_service import NavigationService
from ocr_service import OCRService

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class BlindAssistiveSystem:
    """Main Blind Assistive System orchestrator"""
    
    def __init__(self):
        self.voice_input = FasterWhisperInput()
        self.voice_output = WorkingTTSOutput()
        self.object_detector = YOLOv9ObstacleDetector()
        self.face_recognition = InsightFaceRecognition()
        self.weather = WeatherService()
        self.navigation = NavigationService()
        self.ocr_service = OCRService()
        self.running = False
        
    def initialize(self) -> bool:
        """Initialize all components"""
        try:
            logger.info("Initializing Blind Assistive System...")
            
            # Initialize core components
            if not self.voice_input.initialize():
                logger.error("Failed to initialize voice input")
                return False
            
            if not self.voice_output.initialize():
                logger.error("Failed to initialize voice output")
                return False
            
            if not self.object_detector.initialize():
                logger.error("Failed to initialize object detection")
                return False
            
            # Initialize enhanced components
            self.face_recognition.initialize()
            self.weather.initialize()
            self.navigation.initialize()
            self.ocr_service.initialize()
            
            logger.info("Blind Assistive System initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing system: {e}")
            return False
    
    def test_voice_output(self):
        """Test voice output"""
        self.voice_output.speak("Voice output test. This should be working now!")
        time.sleep(1)
        self.voice_output.speak("Second test message to confirm voice output is working properly.")
    
    def detect_and_speak_objects(self):
        """Detect objects with obstacle warnings and speak them"""
        try:
            self.voice_output.speak("Detecting objects and obstacles now")
            objects = self.object_detector.detect_objects()
            
            if not objects:
                self.voice_output.speak("No objects detected")
                return
            
            # Separate obstacles from regular objects
            obstacles = [obj for obj in objects if "OBSTACLE:" in obj["name"]]
            regular_objects = [obj for obj in objects if "OBSTACLE:" not in obj["name"]]
            
            # Speak obstacle warnings first
            for obstacle in obstacles:
                if "warning" in obstacle:
                    self.voice_output.speak(obstacle["warning"])
            
            # Speak regular objects
            if regular_objects:
                if len(regular_objects) == 1:
                    obj = regular_objects[0]
                    confidence = int(obj["confidence"] * 100)
                    depth = obj.get("depth", 0)
                    if depth > 0:
                        self.voice_output.speak(f"I detected a {obj['name']} with {confidence} percent confidence at depth {depth:.1f}")
                    else:
                        self.voice_output.speak(f"I detected a {obj['name']} with {confidence} percent confidence")
                else:
                    top_objects = regular_objects[:3]
                    object_names = []
                    for obj in top_objects:
                        confidence = int(obj['confidence']*100)
                        depth = obj.get("depth", 0)
                        if depth > 0:
                            object_names.append(f"{obj['name']} ({confidence}%, depth {depth:.1f})")
                        else:
                            object_names.append(f"{obj['name']} ({confidence}%)")
                    objects_text = ", ".join(object_names)
                    self.voice_output.speak(f"I detected {objects_text}")
                
        except Exception as e:
            logger.error(f"Error detecting objects: {e}")
            self.voice_output.speak("Error detecting objects")
    
    def object_detection_mode(self):
        """Continuous object detection mode with obstacle warnings and 3-second pause"""
        try:
            self.voice_output.speak("Starting obstacle detection mode. Say stop to exit.")
            
            while True:
                objects = self.object_detector.detect_objects()
                
                if objects:
                    # Separate obstacles from regular objects
                    obstacles = [obj for obj in objects if "OBSTACLE:" in obj["name"]]
                    regular_objects = [obj for obj in objects if "OBSTACLE:" not in obj["name"]]
                    
                    # Speak obstacle warnings first
                    for obstacle in obstacles:
                        if "warning" in obstacle:
                            self.voice_output.speak(obstacle["warning"])
                    
                    # Speak regular objects
                    if regular_objects:
                        if len(regular_objects) == 1:
                            obj = regular_objects[0]
                            confidence = int(obj["confidence"] * 100)
                            depth = obj.get("depth", 0)
                            if depth > 0:
                                self.voice_output.speak(f"I detected a {obj['name']} with {confidence} percent confidence at depth {depth:.1f}")
                            else:
                                self.voice_output.speak(f"I detected a {obj['name']} with {confidence} percent confidence")
                        else:
                            top_objects = regular_objects[:3]
                            object_names = []
                            for obj in top_objects:
                                confidence = int(obj['confidence']*100)
                                depth = obj.get("depth", 0)
                                if depth > 0:
                                    object_names.append(f"{obj['name']} ({confidence}%, depth {depth:.1f})")
                                else:
                                    object_names.append(f"{obj['name']} ({confidence}%)")
                            objects_text = ", ".join(object_names)
                            self.voice_output.speak(f"I detected {objects_text}")
                else:
                    self.voice_output.speak("No objects detected")
                
                # Wait for 3 seconds or voice command
                self.voice_output.speak("Pausing for 3 seconds. Say stop to exit detection mode.")
                time.sleep(3)
                
                # Check for stop command during pause
                self.voice_output.speak("Listening for stop command...")
                time.sleep(0.5)
                stop_command = self.voice_input.listen_for_command()
                if stop_command and any(word in stop_command.lower() for word in ["stop", "exit", "quit"]):
                    self.voice_output.speak("Exiting obstacle detection mode")
                    break
                        
        except Exception as e:
            logger.error(f"Error in object detection mode: {e}")
            self.voice_output.speak("Error in object detection mode")
    
    def detect_and_speak_faces(self):
        """Detect faces and speak them"""
        try:
            self.voice_output.speak("Detecting faces now")
            if not self.object_detector.cap:
                self.voice_output.speak("Camera not available")
                return
            
            ret, frame = self.object_detector.cap.read()
            if not ret:
                self.voice_output.speak("Could not capture frame")
                return
            
            faces = self.face_recognition.detect_faces(frame)
            
            if not faces:
                self.voice_output.speak("No faces detected")
            else:
                for face in faces:
                    if face["name"] != "Unknown":
                        confidence = int(face["confidence"] * 100)
                        self.voice_output.speak(f"I recognized {face['name']} with {confidence} percent confidence")
                    else:
                        self.voice_output.speak("I detected an unknown person")
                        
        except Exception as e:
            logger.error(f"Error detecting faces: {e}")
            self.voice_output.speak("Error detecting faces")
    
    def who_is_this(self):
        """Recognize the person in front of the camera"""
        try:
            self.voice_output.speak("Who is this? Let me check")
            if not self.object_detector.cap:
                self.voice_output.speak("Camera not available")
                return
            
            ret, frame = self.object_detector.cap.read()
            if not ret:
                self.voice_output.speak("Could not capture frame")
                return
            
            faces = self.face_recognition.detect_faces(frame)
            
            if not faces:
                self.voice_output.speak("I don't see anyone in front of the camera")
            else:
                # Get the largest/most prominent face
                largest_face = max(faces, key=lambda f: (f["bbox"][2] - f["bbox"][0]) * (f["bbox"][3] - f["bbox"][1]))
                
                if largest_face["name"] != "Unknown":
                    confidence = int(largest_face["confidence"] * 100)
                    self.voice_output.speak(f"This is {largest_face['name']} with {confidence} percent confidence")
                else:
                    self.voice_output.speak("I don't recognize this person. They are not in my database")
                        
        except Exception as e:
            logger.error(f"Error in who is this: {e}")
            self.voice_output.speak("Error recognizing person")
    
    def save_person_with_name(self, name: str):
        """Save a person's face with their name"""
        try:
            # Clean the name for display
            name_clean = name.strip().rstrip('.,!?;:').strip().title()
            
            self.voice_output.speak(f"Saving person named {name_clean}")
            if not self.object_detector.cap:
                self.voice_output.speak("Camera not available")
                return
            
            ret, frame = self.object_detector.cap.read()
            if not ret:
                self.voice_output.speak("Could not capture frame")
                return
            
            success = self.face_recognition.save_person(name, frame)
            if success:
                self.voice_output.speak(f"Successfully saved {name_clean} to the face database")
            else:
                self.voice_output.speak("Could not detect a face to save. Please ensure your face is visible in the camera")
                
        except Exception as e:
            logger.error(f"Error saving person: {e}")
            self.voice_output.speak("Error saving person")
    
    def delete_person_by_name(self, name: str):
        """Delete a person from the database"""
        try:
            # Clean the name for display
            name_clean = name.strip().rstrip('.,!?;:').strip().title()
            
            self.voice_output.speak(f"Deleting person named {name_clean}")
            if self.face_recognition.delete_person(name):
                self.voice_output.speak(f"Successfully deleted {name_clean} from the face database")
            else:
                self.voice_output.speak(f"Could not find {name_clean} in the face database")
                
        except Exception as e:
            logger.error(f"Error deleting person: {e}")
            self.voice_output.speak("Error deleting person")
    
    def list_known_people(self):
        """List all known people"""
        try:
            self.voice_output.speak("Listing known people")
            people = self.face_recognition.list_known_people()
            if people:
                people_text = ", ".join(people)
                self.voice_output.speak(f"Known people are: {people_text}")
            else:
                self.voice_output.speak("No people are saved in the face database")
                
        except Exception as e:
            logger.error(f"Error listing people: {e}")
            self.voice_output.speak("Error listing people")
    
    def get_and_speak_weather(self):
        """Get weather for a city"""
        try:
            self.voice_output.speak("Which city would you like to know the weather for?")
            time.sleep(0.5)
            city = self.voice_input.listen_for_command()
            
            if city:
                self.voice_output.speak(f"Getting weather for {city}")
                weather_info = self.weather.get_weather(city.strip())
                self.voice_output.speak(weather_info)
            else:
                self.voice_output.speak("No city name provided")
                
        except Exception as e:
            logger.error(f"Error getting weather: {e}")
            self.voice_output.speak("Error getting weather")
    
    def get_and_speak_navigation(self, destination: str = None):
        """Get navigation directions"""
        try:
            if not destination:
                self.voice_output.speak("Where would you like to navigate to?")
                time.sleep(0.5)
                destination = self.voice_input.listen_for_command()
            
            if destination:
                self.voice_output.speak(f"Getting directions to {destination}")
                directions = self.navigation.get_directions(destination.strip())
                self.voice_output.speak(directions)
            else:
                self.voice_output.speak("No destination provided")
                
        except Exception as e:
            logger.error(f"Error getting navigation: {e}")
            self.voice_output.speak("Error getting navigation")
    
    def read_text_from_camera(self):
        """Capture image and read text using OCR"""
        try:
            self.voice_output.speak("Capturing image to read text")
            
            if not self.object_detector.cap:
                self.voice_output.speak("Camera not available")
                return
            
            # Extract text from camera
            text_results = self.ocr_service.extract_text_from_camera(self.object_detector.cap)
            
            if not text_results:
                self.voice_output.speak("No text detected in the image")
                return
            
            # Format and speak the extracted text
            formatted_text = self.ocr_service.format_text_for_speech(text_results)
            self.voice_output.speak(f"Reading text: {formatted_text}")
            
            # Also provide detailed info
            detailed_info = self.ocr_service.get_detailed_text_info(text_results)
            self.voice_output.speak(detailed_info)
            
        except Exception as e:
            logger.error(f"Error reading text from camera: {e}")
            self.voice_output.speak("Error reading text from image")
    
    def process_command(self, command: str) -> bool:
        """Process voice command"""
        try:
            command_lower = command.lower().strip()
            
            # Object detection
            if any(word in command_lower for word in ["objects", "see", "detect"]):
                self.detect_and_speak_objects()
                return True
            
            # Object detection mode
            elif any(word in command_lower for word in ["object mode", "detection mode", "continuous objects"]):
                self.object_detection_mode()
                return True
            
            # Face recognition
            elif any(word in command_lower for word in ["faces", "people", "recognize"]):
                self.detect_and_speak_faces()
                return True
            
            # Who is this
            elif any(word in command_lower for word in ["who", "who is", "who is this"]):
                self.who_is_this()
                return True
            
            # Save person
            elif any(word in command_lower for word in ["save", "remember"]):
                self.voice_output.speak("What is the person's name?")
                time.sleep(0.5)
                name = self.voice_input.listen_for_command()
                if name and name.strip():
                    self.save_person_with_name(name.strip())
                else:
                    self.voice_output.speak("No name provided")
                return True
            
            # Delete person
            elif any(word in command_lower for word in ["delete", "forget", "remove"]):
                self.voice_output.speak("What is the person's name?")
                time.sleep(0.5)
                name = self.voice_input.listen_for_command()
                if name and name.strip():
                    self.delete_person_by_name(name.strip())
                else:
                    self.voice_output.speak("No name provided")
                return True
            
            # List known people
            elif any(word in command_lower for word in ["list", "show"]):
                self.list_known_people()
                return True
            
            # Weather
            elif any(word in command_lower for word in ["weather", "temperature"]):
                self.get_and_speak_weather()
                return True
            
            # Navigation
            elif any(word in command_lower for word in ["navigate", "go", "directions"]):
                if "to" in command_lower:
                    destination = command_lower.split("to")[-1].strip()
                else:
                    destination = None
                self.get_and_speak_navigation(destination)
                return True
            
            # OCR - Read text from camera
            elif any(word in command_lower for word in ["read", "ocr", "text", "scan"]):
                self.read_text_from_camera()
                return True
            
            # Test voice
            elif any(word in command_lower for word in ["test", "voice"]):
                self.test_voice_output()
                return True
            
            # Help
            elif any(word in command_lower for word in ["help", "commands"]):
                help_text = "Simple commands: objects, object mode, faces, who is this, save, delete, list, weather, navigate, read text, test, help, quit"
                self.voice_output.speak(help_text)
                return True
            
            else:
                self.voice_output.speak("Command not recognized. Say help for available commands.")
                return False
                
        except Exception as e:
            logger.error(f"Error processing command: {e}")
            self.voice_output.speak("Error processing command")
            return False
    
    def run(self):
        """Main system loop"""
        try:
            self.running = True
            
            logger.info("Starting Blind Assistive System...")
            
            # Welcome message
            self.voice_output.speak("Blind Assistive System ready with YOLOv9 obstacle detection and OCR text reading. Simple commands: objects, object mode, faces, who is this, save, delete, list, weather, navigate, read text, test, help, quit.")
            
            # Test voice output
            time.sleep(2)
            self.voice_output.speak("Voice output is working properly now!")
            
            # Main command loop
            while self.running:
                try:
                    # Listen for command
                    logger.info("🔄 STEP 1: Listening for command...")
                    command = self.voice_input.listen_for_command()
                    
                    if not command:
                        logger.info("🔄 No command received, continuing to listen...")
                        continue
                    
                    logger.info("🔄 STEP 2: Microphone stopped")
                    logger.info("🔄 STEP 3: Processing command...")
                    
                    # Check for quit commands
                    if any(word in command.lower() for word in ["quit", "exit", "stop", "goodbye"]):
                        self.voice_output.speak("Shutting down system. Goodbye!")
                        break
                    
                    # Process command
                    self.process_command(command)
                    
                    logger.info("🔄 STEP 4: Response spoken")
                    logger.info("🔄 STEP 5: Ready for next command")
                    
                    # Small delay
                    time.sleep(0.5)
                    
                except KeyboardInterrupt:
                    logger.info("Keyboard interrupt received")
                    break
                except Exception as e:
                    logger.error(f"Error in main loop: {e}")
                    self.voice_input.stop_microphone()
                    time.sleep(1.0)
            
        except Exception as e:
            logger.error(f"Critical error in main loop: {e}")
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Gracefully shutdown the system"""
        try:
            logger.info("Shutting down Blind Assistive System...")
            
            self.running = False
            
            # Release all resources
            self.object_detector.release()
            self.face_recognition.release()
            self.weather.release()
            self.navigation.release()
            self.ocr_service.release()
            self.voice_output.release()
            self.voice_input.release()
            
            logger.info("Blind Assistive System shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


def main():
    """Main entry point"""
    try:
        print("=" * 80)
        print("🎤 BLIND ASSISTIVE SYSTEM - MODULAR ARCHITECTURE")
        print("=" * 80)
        print("Using modular components:")
        print("  🎤 Voice Input: voice_input.py")
        print("  🔊 Voice Output: voice_output.py")
        print("  👁️ Object Detection: object_detection.py")
        print("  👤 Face Recognition: face_recognition_service.py")
        print("  🌤️ Weather: weather_service.py")
        print("  🗺️ Navigation: navigation_service.py (Real API Integration!)")
        print("  📖 OCR: ocr_service.py (RapidOCR Text Recognition!)")
        print()
        print("EASY VOICE COMMANDS:")
        print("  - 'objects' or 'see' or 'detect'")
        print("  - 'object mode' (continuous detection)")
        print("  - 'faces' or 'people' or 'recognize'")
        print("  - 'who is this'")
        print("  - 'save' (then say the name)")
        print("  - 'delete' (then say the name)")
        print("  - 'list'")
        print("  - 'weather'")
        print("  - 'navigate to [destination]'")
        print("  - 'read text' or 'ocr' or 'scan' (NEW!)")
        print("  - 'test'")
        print("  - 'help'")
        print("  - 'quit' or 'exit'")
        print("=" * 80)
        
        # Create and initialize system
        system = BlindAssistiveSystem()
        
        if not system.initialize():
            logger.error("Failed to initialize system")
            print("❌ System initialization failed. Check the logs for details.")
            return 1
        
        print("✅ System initialized successfully!")
        print("🎤 Ready with all independent services!")
        print("🗺️ Navigation now uses REAL OpenStreetMap APIs!")
        
        # Run the system
        system.run()
        
        return 0
        
    except Exception as e:
        logger.error(f"Critical error in main: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

