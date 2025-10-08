# Blind Assistive System - CPU-Optimized Multi-Agent Architecture

A comprehensive voice-enabled blind assistive system that runs entirely on CPU using specialized AI agents for object detection, face recognition, weather analysis, and navigation.

## Features

- **Voice Input/Output**: Whisper STT and Coqui TTS for natural voice interaction
- **Object Detection**: Real-time YOLOv5 object detection with background monitoring
- **Face Recognition**: DeepFace-based face recognition with MediaPipe detection
- **Weather Analysis**: OpenWeatherMap integration for outdoor navigation advice
- **Navigation**: OpenStreetMap-based pedestrian routing with turn-by-turn instructions
- **LLM Orchestration**: TinyLLaMA-1.1B for intelligent command parsing and routing

## System Requirements

- Python 3.8 or higher
- 4GB+ RAM (8GB recommended)
- CPU with 4+ cores
- Webcam
- Microphone
- Speakers/Headphones

## Quick Start

1. **Clone and Setup**:
   ```bash
   git clone <repository>
   cd blind_assistive_system
   python setup.py
   ```

2. **Download Models**:
   - Download TinyLLaMA-1.1B GGUF model from [Hugging Face](https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF)
   - Place `tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf` in `./models/tinyllama-1.1b-q4_k_m.gguf`

3. **Configure API Keys**:
   - Set your OpenWeatherMap API key in `config.py`
   - Get free API key at [OpenWeatherMap](https://openweathermap.org/api)

4. **Run the System**:
   ```bash
   python main.py
   ```

## Voice Commands

### Object Detection
- "What do you see around me?"
- "What's in front of me?"
- "Describe what you see"

### Face Recognition
- "Who is this person?"
- "Recognize this face"
- "Save this face" (then provide name)
- "Delete face for [name]"

### Weather
- "What's the weather like?"
- "Tell me about the temperature"
- "Is it raining?"

### Navigation
- "Take me to [destination]"
- "Navigate to [location]"
- "How do I get to [place]?"

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Voice Input   │───▶│  LLM Orchestrator│───▶│  Voice Output   │
│   (Whisper)     │    │  (TinyLLaMA)     │    │   (Coqui TTS)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                    ┌───────────┼───────────┐
                    │           │           │
            ┌───────▼──┐ ┌──────▼──┐ ┌──────▼──┐ ┌─────────┐
            │  Object  │ │  Face   │ │ Weather │ │Navigation│
            │Detection │ │Recognition│ │Analysis │ │  Agent  │
            │ (YOLOv5) │ │(DeepFace)│ │(OpenWM) │ │ (OSMnx) │
            └──────────┘ └─────────┘ └─────────┘ └─────────┘
```

## Components

### Core System
- **main.py**: Main orchestration system with threading
- **voice_input.py**: Whisper-based speech-to-text
- **voice_output.py**: Coqui TTS text-to-speech
- **llm_orchestrator.py**: Command parsing and routing

### Specialized Agents
- **agents/object_detection.py**: YOLOv5 object detection
- **agents/face_recognition.py**: DeepFace face recognition
- **agents/weather.py**: Weather analysis and advice
- **agents/navigation.py**: Pedestrian navigation

### Utilities
- **utils/camera.py**: Camera management and frame processing
- **utils/audio.py**: Audio recording and playback
- **utils/location.py**: GPS and geolocation services

## Configuration

Key settings in `config.py`:

```python
# API Keys
OPENWEATHER_API_KEY = "your_api_key_here"

# Model Paths
LLM_MODEL_PATH = "./models/tinyllama-1.1b-q4_k_m.gguf"
WHISPER_MODEL_SIZE = "tiny"  # or "base"

# Detection Settings
OBJECT_DETECTION_FPS = 10
OBJECT_CONFIDENCE_THRESHOLD = 0.5
FACE_RECOGNITION_THRESHOLD = 0.4
```

## Performance Optimization

- **CPU-Only**: All models optimized for CPU execution
- **Threading**: Background object detection in separate thread
- **Rate Limiting**: Configurable FPS for object detection
- **Caching**: Face embeddings and weather data cached
- **Memory Management**: Efficient model loading and cleanup

## Troubleshooting

### Common Issues

1. **Camera not found**: Check camera index in config.py
2. **Microphone issues**: Ensure microphone permissions are granted
3. **Model loading errors**: Verify model files are in correct locations
4. **API errors**: Check API keys and internet connection

### Performance Issues

- Reduce `OBJECT_DETECTION_FPS` for lower CPU usage
- Use `WHISPER_MODEL_SIZE = "tiny"` for faster STT
- Close other applications to free up memory

## Development

### Adding New Agents

1. Create agent class in `agents/` directory
2. Implement required methods: `initialize()`, `release()`, and main functionality
3. Add routing logic in `main.py` `_route_command()` method
4. Update LLM orchestrator with new action keywords

### Testing

Run individual component tests:
```bash
python -c "from voice_input import VoiceInput; VoiceInput().test_microphone()"
python -c "from voice_output import VoiceOutput; VoiceOutput().test_speech()"
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues and questions:
- Check the troubleshooting section
- Review system logs in `./logs/`
- Open an issue on GitHub

## Acknowledgments

- OpenAI Whisper for speech recognition
- Ultralytics for YOLOv5 object detection
- DeepFace for face recognition
- Coqui TTS for text-to-speech
- OpenStreetMap for navigation data
- TinyLLaMA for lightweight language understanding
