# 🚀 Blind Assistive System - Complete Setup Guide

## 📋 Table of Contents
1. [System Requirements](#system-requirements)
2. [Installation Steps](#installation-steps)
3. [Required Models](#required-models)
4. [Environment Configuration](#environment-configuration)
5. [Running the System](#running-the-system)
6. [Troubleshooting](#troubleshooting)

---

## 🖥️ System Requirements

### Hardware Requirements
- **CPU**: Modern multi-core processor (Intel i5/AMD Ryzen 5 or better)
- **RAM**: Minimum 8GB (16GB recommended)
- **Storage**: 5GB free space for models and dependencies
- **Webcam**: Required for object detection and face recognition
- **Microphone**: Required for voice commands
- **GPU**: Optional (NVIDIA GPU with CUDA for faster processing)

### Software Requirements
- **Operating System**: Windows 10/11, Linux, or macOS
- **Python**: Version 3.8, 3.9, 3.10, 3.11, or 3.12
- **Internet Connection**: Required for initial setup and navigation features

---

## 📥 Installation Steps

### Step 1: Clone the Repository
```bash
git clone <your-repository-url>
cd blind_assistive_system
```

### Step 2: Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Python Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Note**: Installation may take 10-15 minutes depending on your internet speed.

### Step 4: Install System Dependencies

#### Windows:
- Install Visual C++ Redistributable (required for some packages)
- Download from: https://aka.ms/vs/17/release/vc_redist.x64.exe

#### Linux (Ubuntu/Debian):
```bash
sudo apt-get update
sudo apt-get install -y python3-dev python3-pip
sudo apt-get install -y portaudio19-dev python3-pyaudio
sudo apt-get install -y libopencv-dev
```

#### macOS:
```bash
brew install portaudio
brew install opencv
```

---

## 🤖 Required Models

### 1. YOLOv9 Model (Already Included)
- **File**: `yolov9c.pt` (49MB)
- **Location**: Root directory
- **Status**: ✅ Already in repository
- **Purpose**: Object detection and obstacle avoidance

### 2. Faster-Whisper Model (Auto-downloaded)
- **Model**: `Systran/faster-whisper-base`
- **Size**: ~150MB
- **Location**: `models/models--Systran--faster-whisper-base/`
- **Status**: ✅ Auto-downloads on first run
- **Purpose**: Speech-to-text for voice commands

### 3. InsightFace Model (Auto-downloaded)
- **Model**: `buffalo_l`
- **Size**: ~200MB
- **Location**: `~/.insightface/models/`
- **Status**: ✅ Auto-downloads on first run
- **Purpose**: Face recognition

### 4. RapidOCR Models (Auto-downloaded)
- **Models**: ONNX models for text recognition
- **Size**: ~50MB
- **Status**: ✅ Auto-downloads when OCR is first used
- **Purpose**: Text reading from camera

### Total Download Size
- **First-time setup**: ~450MB (models auto-download)
- **With repository**: ~500MB total

---

## ⚙️ Environment Configuration

### Create `.env` File
Create a file named `.env` in the root directory:

```bash
# Weather Service API Key (Get from https://openweathermap.org/api)
OPENWEATHER_API_KEY=your_api_key_here

# Optional: Custom configuration
NAVIGATION_GPS_UPDATE_INTERVAL=1.0
NAVIGATION_VOICE_VOLUME=1.0
NAVIGATION_VOICE_RATE=150
```

### Get OpenWeatherMap API Key (FREE)
1. Go to https://openweathermap.org/api
2. Click "Sign Up" (it's FREE)
3. Verify your email
4. Go to "API keys" section
5. Copy your API key
6. Paste it in `.env` file

**Note**: Free tier allows 60 calls/minute, which is more than enough!

---

## 🎮 Running the System

### Quick Start
```bash
# Activate virtual environment (if not already activated)
# Windows: venv\Scripts\activate
# Linux/macOS: source venv/bin/activate

# Run the main system
python main.py
```

### System Startup
1. System initializes all components (~10-15 seconds)
2. Camera opens for object detection
3. Voice recognition starts listening
4. You'll hear: "Blind Assistive System ready..."

### Available Voice Commands

#### 🔍 Object Detection
- **"objects"** / **"see"** / **"detect"** - Detect objects once
- **"object mode"** - Continuous object detection

#### 👤 Face Recognition
- **"faces"** / **"people"** - Detect faces
- **"who is this"** - Recognize person in front of camera
- **"save"** - Save a new person (then say their name)
- **"delete"** - Delete a person (then say their name)
- **"list"** - List all known people

#### 🌤️ Weather
- **"weather"** - Get weather for your location (then say city name)

#### 🗺️ Navigation
- **"navigate to [destination]"** - Start navigation
- **"where am I"** - Get current location
- **"navigation status"** - Check navigation progress
- **"stop navigation"** - Cancel navigation

#### 📖 OCR (Text Reading)
- **"read text"** / **"ocr"** / **"scan"** - Read text from camera

#### 🔧 System Commands
- **"test"** - Test voice output
- **"help"** - List all commands
- **"quit"** / **"exit"** - Shut down system

---

## 🐛 Troubleshooting

### Problem: "ModuleNotFoundError"
**Solution**: Reinstall requirements
```bash
pip install -r requirements.txt --force-reinstall
```

### Problem: Camera not working
**Solutions**:
1. Check camera permissions in system settings
2. Close other apps using the camera
3. Try different camera index:
   - Edit `object_detection.py`, line 35: Change `cv2.VideoCapture(0)` to `cv2.VideoCapture(1)`

### Problem: Microphone not detected
**Solutions**:
1. Check microphone permissions
2. Test microphone:
   ```bash
   python -c "import pyaudio; p=pyaudio.PyAudio(); print(f'Devices: {p.get_device_count()}')"
   ```
3. Install audio drivers

### Problem: Voice recognition not working
**Solutions**:
1. Speak clearly and loudly
2. Reduce background noise
3. Check microphone levels in system settings
4. Increase microphone gain

### Problem: Models not downloading
**Solutions**:
1. Check internet connection
2. Disable VPN/proxy temporarily
3. Run with administrator/sudo privileges
4. Manually download models (see documentation)

### Problem: "CUDA not available" warning
**Note**: This is normal! System works on CPU.
- For GPU acceleration, install CUDA toolkit and GPU-enabled PyTorch
- Not required - CPU mode works fine!

### Problem: Weather service not working
**Solutions**:
1. Check `.env` file exists
2. Verify API key is correct
3. Wait 10-15 minutes after API key creation (activation time)
4. Check internet connection

### Problem: Navigation not working
**Solutions**:
1. Check internet connection (required for routing)
2. Try more specific destination names
3. Add country name (e.g., "Kathmandu, Nepal")

### Problem: Face delete not working
**Solution**: This is FIXED! Make sure you have the latest code.
- Names are now case-insensitive
- Punctuation is automatically removed
- "John Doe!" will match "John Doe"

---

## 📊 Performance Tips

### For Faster Performance:
1. **Close unnecessary applications**
2. **Use GPU if available**:
   ```bash
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
   ```
3. **Reduce camera resolution** (edit `object_detection.py`):
   ```python
   self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
   self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
   ```

### For Better Voice Recognition:
1. Use a good quality microphone
2. Minimize background noise
3. Speak clearly at normal volume
4. Wait for "Listening..." prompt before speaking

### For Better Object Detection:
1. Ensure good lighting
2. Point camera at objects clearly
3. Avoid shaky movements
4. Keep objects within 2-5 meters

---

## 📁 Project Structure

```
blind_assistive_system/
├── main.py                          # Main entry point
├── voice_input.py                   # Speech recognition
├── voice_output.py                  # Text-to-speech
├── object_detection.py              # YOLO object detection
├── face_recognition_service.py      # Face recognition
├── weather_service.py               # Weather API
├── navigation_service.py            # Navigation API
├── ocr_service.py                   # Text reading
├── requirements.txt                 # Python dependencies
├── .env                            # Environment variables (create this)
├── .gitignore                      # Git ignore rules
├── README.md                       # Project documentation
├── yolov9c.pt                      # YOLO model (49MB)
├── data/                           # Face database
│   └── face_database.pkl           # Saved faces
├── logs/                           # System logs
├── models/                         # Auto-downloaded models
│   └── models--Systran--faster-whisper-base/
└── temp/                           # Temporary files
```

---

## 🔒 Privacy & Security

### Data Storage
- **Face Database**: Stored locally in `data/face_database.pkl`
- **Logs**: Stored locally in `logs/` directory
- **No cloud uploads**: All processing is local

### API Keys
- Keep `.env` file private
- Never commit API keys to git
- Use free tiers for testing

### Permissions Required
- **Camera**: For object detection and face recognition
- **Microphone**: For voice commands
- **Internet**: For weather and navigation APIs (optional)

---

## 🤝 Getting Help

### Common Issues
1. Check this guide first
2. Read error messages carefully
3. Check logs in `logs/` directory

### Error Logs
Located in: `logs/navigation.log`
```bash
# View recent errors (Windows)
type logs\navigation.log | findstr ERROR

# View recent errors (Linux/macOS)
tail -f logs/navigation.log | grep ERROR
```

### System Test
Run a quick system test:
```bash
python -c "from main import BlindAssistiveSystem; print('✅ System imports successfully')"
```

---

## 🎯 Quick Test Checklist

After installation, test each feature:

- [ ] System starts without errors
- [ ] Camera opens
- [ ] Voice recognition works ("test")
- [ ] Object detection works ("objects")
- [ ] Face recognition works ("faces")
- [ ] Weather works ("weather")
- [ ] Navigation works ("navigate to [place]")
- [ ] OCR works ("read text")
- [ ] Voice output is clear
- [ ] All commands respond correctly

---

## 📝 Notes

1. **First Run**: May take 2-3 minutes to download models
2. **GPU Support**: Optional, system works fine on CPU
3. **Internet**: Required for navigation and weather only
4. **Privacy**: All face data stored locally
5. **Free APIs**: Using free tiers of all services

---

## ✅ System is Ready!

If you can run `python main.py` and hear the welcome message, you're all set! 🎉

**Enjoy using the Blind Assistive System!**

For questions, check the troubleshooting section or review the code documentation.

---

**Last Updated**: October 2025  
**Version**: 1.0  
**License**: MIT
