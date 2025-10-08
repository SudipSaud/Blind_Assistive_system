"""
Voice Output Module - Text-to-Speech using pyttsx3
"""

import logging
import time

logger = logging.getLogger(__name__)


class WorkingTTSOutput:
    """Fixed voice output using pyttsx3 with proper threading and error handling"""
    
    def __init__(self):
        self.engine = None
        self.is_initialized = False
        
    def initialize(self) -> bool:
        """Initialize pyttsx3 TTS engine"""
        try:
            import pyttsx3
            
            logger.info("Initializing Working TTS engine...")
            self.engine = pyttsx3.init()
            
            # Configure voice properties
            voices = self.engine.getProperty('voices')
            if voices:
                # Try to use a female voice if available
                for voice in voices:
                    if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                        self.engine.setProperty('voice', voice.id)
                        break
            
            # Set speech rate and volume
            self.engine.setProperty('rate', 150)  # Speed of speech
            self.engine.setProperty('volume', 1.0)  # Volume level (0.0 to 1.0)
            
            self.is_initialized = True
            logger.info("Working TTS engine initialized successfully")
            return True
            
        except ImportError:
            logger.error("pyttsx3 not installed. Install with: pip install pyttsx3")
            return False
        except Exception as e:
            logger.error(f"Error initializing Working TTS: {e}")
            return False
    
    def speak(self, text: str):
        """Speak the given text using pyttsx3"""
        try:
            if not self.is_initialized:
                print(f"🔊 SYSTEM: {text}")
                return
            
            logger.info(f"🔊 Speaking: '{text}'")
            print(f"🔊 SYSTEM: {text}")
            
            # Simple synchronous approach - most reliable
            self.engine.say(text)
            self.engine.runAndWait()
            
            # Small delay to ensure speech completes
            time.sleep(0.5)
            
        except Exception as e:
            logger.error(f"Error speaking: {e}")
            print(f"🔊 SYSTEM: {text}")  # Fallback to text
    
    def release(self):
        """Release resources"""
        self.is_initialized = False
        logger.info("Working TTS resources released")

