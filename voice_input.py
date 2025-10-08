"""
Voice Input Module - Faster-Whisper Speech Recognition
"""

import logging
import os
import time
import wave

logger = logging.getLogger(__name__)


class FasterWhisperInput:
    """Voice input using Faster-Whisper with INT8 quantization for 4x faster CPU inference"""
    
    def __init__(self):
        self.model = None
        self.is_initialized = False
        self.microphone_active = False
        
    def initialize(self) -> bool:
        """Initialize Faster-Whisper model"""
        try:
            from faster_whisper import WhisperModel
            
            logger.info("Loading Faster-Whisper model with INT8 quantization...")
            # Use INT8 quantization for 4x faster CPU inference
            self.model = WhisperModel(
                "base", 
                device="cpu", 
                compute_type="int8",  # INT8 quantization for faster CPU inference
                download_root="./models"
            )
            logger.info("Faster-Whisper model loaded successfully")
            self.is_initialized = True
            return True
            
        except ImportError:
            logger.error("faster-whisper not installed. Install with: pip install faster-whisper")
            return False
        except Exception as e:
            logger.error(f"Error initializing Faster-Whisper: {e}")
            return False
    
    def start_microphone(self):
        """Start microphone for listening"""
        self.microphone_active = True
        logger.info("🎤 Microphone started")
    
    def stop_microphone(self):
        """Stop microphone"""
        self.microphone_active = False
        logger.info("🎤 Microphone stopped")
    
    def listen_for_command(self) -> str:
        """Listen for voice command using Faster-Whisper with proper microphone control"""
        try:
            if not self.model:
                return input("🎤 Enter command: ").strip()
            
            # Start microphone
            self.start_microphone()
            
            logger.info("🎤 Listening for voice command...")
            print("🎤 Listening... Speak now!")
            
            # Record audio using PyAudio
            import pyaudio
            
            CHUNK = 1024
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 16000
            RECORD_SECONDS = 3
            
            p = pyaudio.PyAudio()
            stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
            
            logger.info("🎤 Recording...")
            frames = []
            for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                data = stream.read(CHUNK)
                frames.append(data)
            
            # Stop microphone immediately after recording
            stream.stop_stream()
            stream.close()
            p.terminate()
            self.stop_microphone()
            
            # Save to temporary file
            temp_dir = os.path.join(os.getcwd(), "temp")
            os.makedirs(temp_dir, exist_ok=True)
            temp_path = os.path.join(temp_dir, f"voice_{int(time.time() * 1000)}.wav")
            
            wf = wave.open(temp_path, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
            wf.close()
            
            # Transcribe using Faster-Whisper
            logger.info("🎤 Processing audio with Faster-Whisper...")
            print("🎤 Processing...")
            
            segments, info = self.model.transcribe(temp_path, beam_size=1, language="en")
            text = " ".join([segment.text for segment in segments]).strip()
            
            # Clean up
            try:
                os.unlink(temp_path)
            except:
                pass
            
            logger.info(f"🎤 Heard: '{text}'")
            print(f"🎤 You said: '{text}'")
            
            return text
            
        except Exception as e:
            logger.error(f"Error with voice input: {e}")
            self.stop_microphone()  # Ensure microphone is stopped on error
            return input("🎤 Error with voice input. Enter command: ").strip()
    
    def release(self):
        """Release resources"""
        self.stop_microphone()
        self.model = None
        self.is_initialized = False
        logger.info("Faster-Whisper resources released")

