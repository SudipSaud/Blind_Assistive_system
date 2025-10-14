# Server Implementation Guide for Scout1 Blind Assistant App

**Version:** 1.0  
**Date:** October 11, 2025  
**Client Team:** Scout1 Mobile App (React Native + Expo)  
**Purpose:** Complete technical specification for server-side implementation

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Application Modes](#2-application-modes)
3. [Intent System](#3-intent-system)
4. [API Endpoints](#4-api-endpoints)
5. [Room Mapping System](#5-room-mapping-system)
6. [Data Structures](#6-data-structures)
7. [Model Requirements](#7-model-requirements)
8. [Database Schema](#8-database-schema)
9. [Real-Time Communication](#9-real-time-communication)
10. [Error Handling](#10-error-handling)

---

## 1. System Overview

### 1.1 Application Purpose

Scout1 is a voice-first AI assistant for blind and visually impaired users. It operates in three intelligent modes:

- **On-Demand Mode**: User asks questions, AI responds
- **Proactive Sentry Mode**: AI watches for important events and alerts user
- **Room Mapping Mode**: AI builds 3D spatial maps with object relationships

### 1.2 Technology Stack (Client)

```json
{
  "framework": "React Native (Expo SDK 54)",
  "state_management": "Zustand",
  "camera": "expo-camera v17.0.8",
  "sensors": "expo-sensors v14.0.0 (compass, accelerometer, gyroscope)",
  "video_encoding": "ffmpeg-kit-react-native v6.0.2",
  "wake_word": "Picovoice Porcupine (wake word: 'Bumblebee')",
  "tts": "expo-speech v14.0.7",
  "networking": "axios v1.12.2"
}
```

### 1.3 Client Capabilities

The mobile app can provide:
- **Video**: H.264 encoded MP4 files (10-15 seconds typical)
- **Images**: JPEG, base64-encoded
- **Sensor Data**: 
  - Compass heading (0-360°)
  - Device orientation (pitch, roll, yaw)
  - Accelerometer data
  - Position estimates (step counting)
- **User Context**: Previous interactions, feedback history

---

## 2. Application Modes

### 2.1 On-Demand Mode (Reactive)

**User Behavior**: User says "Bumblebee" + command  
**Client Action**: Captures single image, sends to server  
**Server Response**: Text description (spoken via TTS)

**Example Flow**:
```
User: "Bumblebee, describe the scene"
Client → Server: Single image + task='describe_scene'
Server → Client: "You're in a living room with a gray couch..."
Client: Speaks response to user
```

### 2.2 Proactive Sentry Mode (Stationary)

**User Behavior**: User says "Bumblebee, activate sentry mode"  
**Client Action**: Continuously buffers video frames, detects motion, sends video on events  
**Server Response**: Alert text only if something important detected

**Example Flow**:
```
[Client is buffering frames at 10 FPS]
[Motion detected - local object movement, not head movement]
Client → Server: 10-second video + metadata
Server analyzes: "Unknown person entered room"
Server → Client: { alert_text: "Someone just entered the room" }
Client: INTERRUPTS current activity, speaks alert immediately
```

**Key Difference**: Server must ONLY return alert_text for **significant events**:
- ✅ Unknown person detected
- ✅ Known person enters/leaves
- ✅ Significant object change (new object, object moved)
- ✅ Potential safety hazard
- ❌ Normal room activity (person sitting, minor movements)
- ❌ No change detected

### 2.3 Room Mapping Mode (Scan Mode)

**User Behavior**: User says "Bumblebee, map this room"  
**Client Action**: Records video while user walks around room, collects sensor data  
**Server Response**: Complete 3D room map with all object positions and relationships

**Example Flow**:
```
User: "Bumblebee, map this room"
Client: "Walk around the room slowly. I'll guide you."
[Records 60-90 second video with compass headings]
Client → Server: Video + sensor_data array + room_name
Server: Processes video, extracts frames, builds 3D map
Server → Client: Complete room map with object positions
Client: Saves map locally, tells user: "I've mapped 15 objects in a 12x10 foot room"
```

---

## 3. Intent System

### 3.1 Complete Intent List

The client recognizes these intents and sends appropriate requests:

#### Visual Intents (Require Camera)
```typescript
1. 'describe_scene'       // "What do you see?"
2. 'read_text'           // "Read this document"
3. 'find_object'         // "Where is my phone?" (query_text provided)
4. 'answer_question'     // "What color is this?" (query_text provided)
5. 'face_detect'         // "Who is this person?"
6. 'save_face'           // "Remember this person as John" (person_name provided)
```

#### Non-Visual Intents (Client Handles)
```typescript
7. 'time'                    // Client responds with current time
8. 'date'                    // Client responds with current date
9. 'weather'                 // Client responds (requires weather API integration)
10. 'set_city'              // Client stores city preference
11. 'help'                  // Client explains capabilities
12. 'battery_level'         // Client reads battery status
13. 'general_conversation'  // Client responds with preset messages
```

#### Mode Control Intents (Client Handles)
```typescript
14. 'activate_sentry_mode'    // Starts proactive video monitoring
15. 'deactivate_sentry_mode'  // Stops proactive monitoring
```

#### Feedback Intents (Client Handles Partially)
```typescript
16. 'submit_feedback'         // "That was wrong" - triggers correction flow
17. 'feedback_correction'     // User's correction sent to server
```

#### Room Mapping Intents (New - To Be Implemented)
```typescript
18. 'map_room'               // Start room mapping
19. 'find_object_in_room'    // "Where is my couch?" (uses saved map)
20. 'navigate_to'            // "Guide me to the table"
21. 'whats_around_me'        // "What's near me?" (uses saved map + current position)
22. 'distance_to'            // "How far is the door?"
23. 'whats_between_me_and'   // "What's between me and the kitchen?"
24. 'recall_room'            // Load previously saved room map
```

### 3.2 Intent Recognition Examples

```typescript
// Client-side pattern matching (simplified)
"what do you see" → { task: 'describe_scene' }
"read this text" → { task: 'read_text' }
"where is my keys" → { task: 'find_object', query_text: 'keys' }
"what color is this" → { task: 'answer_question', query_text: 'what color is this' }
"who is this" → { task: 'face_detect' }
"remember this person as Mom" → { task: 'save_face', person_name: 'Mom' }
"that was wrong" → { task: 'submit_feedback' }
"map this room" → { task: 'map_room' }
```

---

## 4. API Endpoints

### 4.1 POST `/process_data` (On-Demand Requests)

**Purpose**: Handle single-image reactive requests

**Request Format**:
```json
{
  "task": "describe_scene",
  "image_data": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
  "query_text": "optional - only for find_object and answer_question"
}
```

**Response Format**:
```json
{
  "result_text": "You are in a living room with a gray couch on the left...",
  "structured_data": {
    // Optional: additional metadata
    "objects_detected": ["couch", "table", "tv"],
    "confidence": 0.92
  }
}
```

**Task-Specific Behaviors**:

1. **describe_scene**: General scene description
2. **read_text**: OCR text extraction
3. **find_object**: Look for specific object from `query_text`
4. **answer_question**: Answer specific question from `query_text`
5. **face_detect**: Identify person (match against known faces)
6. **save_face**: Save face embedding with `person_name`

---

### 4.2 POST `/analyze_event` (Proactive Sentry)

**Purpose**: Analyze video clips for significant events

**Request Format** (multipart/form-data):
```
POST /analyze_event
Content-Type: multipart/form-data

Fields:
- video: [MP4 file, ~5-10 MB, 10-15 seconds]
- timestamp_utc: "2025-10-11T14:30:45.123Z"
- event_type: "motion_detected"
- video_format: "mp4"
```

**Response Format**:
```json
{
  "alert_text": "Someone just entered the room",
  "event_id": "evt_abc123xyz",
  "confidence": 0.89,
  "details": {
    "event_type": "unknown_person",
    "timestamp": "2025-10-11T14:30:45.123Z",
    "objects_changed": ["person_unknown"]
  }
}
```

**OR** (if nothing significant):
```json
{
  "alert_text": null,
  "event_id": "evt_abc123xyz",
  "details": {
    "event_type": "no_significant_change"
  }
}
```

**Critical**: Only return `alert_text` for truly significant events!

**Significant Events**:
- Unknown person enters
- Known person enters/leaves
- New object appears
- Object disappears
- Object moved significantly
- Potential hazard (fire, water, etc.)

**Not Significant**:
- Person already in room moves slightly
- Normal room activity
- Lighting changes only
- Minor shadows/reflections

---

### 4.3 POST `/submit_feedback` (User Corrections)

**Purpose**: Collect user corrections for ML training

**Request Format**:
```json
{
  "timestamp": "2025-10-11T14:30:45.123Z",
  "task": "describe_scene",
  "user_query": "what do you see",
  "system_response": "There is a blue bottle on the table",
  "user_correction": "There is a red cup on the table",
  "image_data": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
  "event_id": "evt_abc123xyz"  // Optional: for proactive events
}
```

**Response Format**:
```json
{
  "status": "success",
  "message": "Feedback recorded for training",
  "feedback_id": "fb_xyz789"
}
```

**Server Action**: Store feedback in database for future model retraining

---

### 4.4 POST `/map_room` (Room Mapping - New)

**Purpose**: Process video to build 3D room map with spatial relationships

**Request Format** (multipart/form-data):
```
POST /map_room
Content-Type: multipart/form-data

Fields:
- video: [MP4 file, 30-90 seconds]
- sensor_data: JSON string (see below)
- room_name: "Living Room"
- existing_map_id: "room_123abc" (optional - for updating existing map)
```

**sensor_data Format**:
```json
[
  {
    "frame_index": 0,
    "timestamp": 1697123456789,
    "heading": 45.5,
    "tilt": { "x": 0.02, "y": -0.15, "z": 0.0 },
    "estimated_position": { "x": 0.0, "y": 0.0 },
    "step_count": 0
  },
  {
    "frame_index": 30,
    "timestamp": 1697123457789,
    "heading": 92.3,
    "tilt": { "x": 0.01, "y": 0.05, "z": 0.0 },
    "estimated_position": { "x": 1.2, "y": 0.5 },
    "step_count": 2
  }
  // ... one entry per second or every 30 frames
]
```

**Response Format**:
```json
{
  "room_id": "room_123abc",
  "room_name": "Living Room",
  "map": {
    "dimensions": {
      "width": 5.0,
      "depth": 4.5,
      "height": 2.7
    },
    "objects": [
      {
        "id": "obj_couch_1",
        "type": "couch",
        "position": { "x": 2.5, "y": 1.0, "z": 0.4 },
        "dimensions": { "width": 2.0, "height": 0.8, "depth": 0.9 },
        "heading": 0,
        "confidence": 0.95
      },
      {
        "id": "obj_table_1",
        "type": "coffee_table",
        "position": { "x": 3.0, "y": 2.5, "z": 0.0 },
        "dimensions": { "width": 1.0, "height": 0.5, "depth": 0.6 },
        "heading": 45,
        "confidence": 0.89
      }
    ],
    "boundaries": [
      {
        "type": "wall",
        "start": { "x": 0, "y": 0 },
        "end": { "x": 5, "y": 0 },
        "height": 2.7
      },
      {
        "type": "door",
        "position": { "x": 2.5, "y": 4.5 },
        "width": 0.9,
        "height": 2.1
      }
    ],
    "relationships": {
      "obj_couch_1": {
        "obj_table_1": {
          "distance": 1.58,
          "direction": "southeast",
          "clear_path": true,
          "path_length": 1.58
        }
      }
    }
  },
  "coverage": 85.5,
  "unexplored_regions": [
    {
      "center": { "x": 0.5, "y": 3.5 },
      "size": 1.2,
      "direction": "northwest",
      "suggested_heading": 315
    }
  ],
  "next_instruction": "Turn northwest and walk 2 meters to complete mapping"
}
```

---

### 4.5 POST `/navigate_query` (Navigation Assistance - New)

**Purpose**: Answer spatial queries about saved rooms

**Request Format**:
```json
{
  "room_id": "room_123abc",
  "query_type": "navigate_to",
  "user_position": { "x": 1.0, "y": 1.0 },
  "user_heading": 90,
  "target": "table"
}
```

**Query Types**:
- `navigate_to`: Get turn-by-turn directions
- `distance_to`: Get distance to object
- `whats_around_me`: List nearby objects
- `whats_between_me_and`: Analyze path between two points

**Response Format** (navigate_to example):
```json
{
  "target_object": {
    "id": "obj_table_1",
    "type": "coffee_table",
    "position": { "x": 3.0, "y": 2.5, "z": 0.0 }
  },
  "distance": 2.55,
  "obstacles_in_path": ["obj_couch_1"],
  "instructions": [
    {
      "action": "turn_left",
      "amount": 30,
      "text": "Turn 30 degrees to your left"
    },
    {
      "action": "walk_forward",
      "distance": 1.5,
      "text": "Walk straight for 1.5 meters"
    },
    {
      "action": "turn_right",
      "amount": 15,
      "text": "Turn slightly right"
    },
    {
      "action": "walk_forward",
      "distance": 1.2,
      "text": "Walk straight for 1.2 meters to reach the table"
    }
  ],
  "estimated_time": "15 seconds"
}
```

---

## 5. Room Mapping System

### 5.1 Concept: "Clear the Black Box"

The room starts as completely unknown (a "black box"). As the user walks around with video recording:

1. **Server extracts frames** from video (e.g., 1 frame per second)
2. **For each frame**:
   - Get compass heading from sensor_data
   - Run object detection (YOLOv9c)
   - Estimate depth for each object
   - Transform to world coordinates using heading
   - Mark regions as "explored"
3. **Build 3D map**:
   - Track all object positions
   - Calculate distances between all objects
   - Identify boundaries (walls, doors)
   - Find unexplored regions
4. **Generate guidance**:
   - Identify largest unexplored region
   - Calculate heading user should walk
   - Return instruction

### 5.2 Coordinate System

```
Origin (0, 0): User's starting position when mapping begins
X-axis: Increases to the East
Y-axis: Increases to the North
Z-axis: Height from floor (0 = floor level)

Heading (degrees):
  0° = East
  90° = North
  180° = West
  270° = South
```

### 5.3 Depth Estimation

**Options**:
1. **YOLOv9c built-in depth** (if available)
2. **Separate monocular depth model** (MiDaS, ZoeDepth)
3. **Size-based estimation** (known object sizes)

**Required Output**: Distance in meters from camera for each detected object

### 5.4 Coordinate Transformation

```python
# Pseudo-code
def transform_to_world_coords(object_bbox, depth, heading, frame_width):
    # Calculate object angle relative to camera center
    bbox_center_x = (object_bbox['x1'] + object_bbox['x2']) / 2
    camera_fov = 60  # degrees (typical phone camera)
    angle_offset = (bbox_center_x / frame_width - 0.5) * camera_fov
    
    # Absolute world angle
    world_angle = heading + angle_offset
    
    # Convert polar to Cartesian
    world_x = depth * cos(radians(world_angle))
    world_y = depth * sin(radians(world_angle))
    
    return { "x": world_x, "y": world_y }
```

### 5.5 Distance Matrix Calculation

For every pair of objects, calculate:
- **Euclidean distance**: `sqrt((x2-x1)² + (y2-y1)²)`
- **Direction**: Cardinal direction from obj1 to obj2
- **Clear path**: Check if line segment intersects other objects
- **Path length**: If no clear path, use A* pathfinding

### 5.6 Unexplored Region Detection

Create a 2D occupancy grid:
- 0 = unexplored (black box)
- 1 = explored (camera has seen this area)

Algorithm:
1. For each frame, mark cone-shaped region as explored based on:
   - Heading
   - Depth range visible
   - Camera FOV
2. After processing all frames, find clusters of 0s (unexplored regions)
3. Return largest cluster's center as next target

---

## 6. Data Structures

### 6.1 Object Detection Output

```python
{
    "class": "couch",
    "bbox": [x1, y1, x2, y2],  # Pixel coordinates in image
    "confidence": 0.95,
    "depth": 2.5,  # meters from camera
    "world_position": {
        "x": 2.5,  # meters from origin
        "y": 1.0,  # meters from origin
        "z": 0.4   # height from floor
    },
    "dimensions": {
        "width": 2.0,   # meters
        "height": 0.8,  # meters
        "depth": 0.9    # meters
    }
}
```

### 6.2 Room Map Structure

```python
{
    "room_id": "room_123abc",
    "room_name": "Living Room",
    "created_at": "2025-10-11T14:30:00Z",
    "last_updated": "2025-10-11T14:45:00Z",
    "dimensions": {
        "width": 5.0,   # meters
        "depth": 4.5,   # meters
        "height": 2.7   # meters
    },
    "objects": [...],  # Array of objects (see above)
    "boundaries": [...],  # Walls, doors, windows
    "relationships": {...},  # Distance matrix
    "exploration_grid": [[0,1,1,...], [0,0,1,...]],  # 2D array
    "coverage": 85.5  # Percentage explored
}
```

---

## 7. Model Requirements

### 7.1 Object Detection

**Recommended**: YOLOv9c or YOLOv8-medium

**Requirements**:
- Real-time inference (< 100ms per frame on GPU)
- Detect common household objects (COCO dataset classes minimum)
- Return bounding boxes with confidence scores

**Optional Enhancements**:
- Built-in depth estimation
- 3D bounding boxes

### 7.2 Depth Estimation

**Recommended**: MiDaS-small or ZoeDepth-NK

**Requirements**:
- Monocular depth (single image input)
- Fast inference (< 150ms per frame)
- Reasonable accuracy (±0.3m at 3m distance acceptable)

**GPU Requirements**: 4GB VRAM sufficient if models run sequentially

### 7.3 Face Recognition

**Requirements**:
- Face detection (MTCNN or RetinaFace)
- Face embedding extraction (FaceNet, ArcFace, or InsightFace)
- Similarity matching (cosine similarity > 0.85 threshold)

### 7.4 OCR (Text Reading)

**Recommended**: EasyOCR or Tesseract

**Requirements**:
- Multi-language support (English minimum)
- Handle various text orientations
- Return text with confidence scores

### 7.5 Scene Understanding

**Recommended**: CLIP (OpenAI) or BLIP-2

**Requirements**:
- Generate natural language descriptions
- Answer visual questions
- Handle "find object" queries semantically

---

## 8. Database Schema

### 8.1 Known Faces

```json
{
  "faces": {
    "person_uuid_1": {
      "name": "John",
      "embedding": [0.123, -0.456, ...],  // 128 or 512 dimensions
      "saved_at": "2025-10-11T14:30:00Z",
      "last_seen": "2025-10-11T15:45:00Z",
      "image_path": "/storage/faces/john.jpg"
    }
  }
}
```

### 8.2 Saved Rooms

```json
{
  "rooms": {
    "room_123abc": {
      // Full RoomMap structure (see 6.2)
    }
  }
}
```

### 8.3 Feedback Log

```json
{
  "feedback": [
    {
      "feedback_id": "fb_xyz789",
      "timestamp": "2025-10-11T14:30:00Z",
      "task": "describe_scene",
      "system_response": "...",
      "user_correction": "...",
      "image_path": "/storage/feedback/img_xyz.jpg",
      "event_id": "evt_abc123"
    }
  ]
}
```

---

## 9. Real-Time Communication

### 9.1 Current Implementation (HTTP)

All current endpoints use standard HTTP POST requests.

**Timeouts**:
- Client timeout: 30 seconds
- Server should respond within 10 seconds for `/process_data`
- Server should respond within 15 seconds for `/analyze_event`
- Server should respond within 30 seconds for `/map_room`

### 9.2 Future: WebSocket for Live Guidance (Phase 2)

**Use Case**: Real-time navigation with live frame streaming

**Flow**:
```
1. Client opens WebSocket connection
2. Client streams frames at 2 fps
3. Server processes each frame
4. Server sends back navigation instructions every 2 seconds
5. Client speaks instructions via TTS
```

**Not implemented yet** - stick with HTTP for now.

---

## 10. Error Handling

### 10.1 HTTP Status Codes

```
200: Success
400: Bad request (invalid parameters)
413: Payload too large (video > 50MB)
422: Unprocessable entity (corrupt video, invalid image)
500: Server error (model failed, unexpected exception)
503: Service unavailable (server overloaded)
```

### 10.2 Error Response Format

```json
{
  "error": "InvalidImageFormat",
  "message": "Could not decode base64 image data",
  "code": 400
}
```

### 10.3 Client Retry Logic

Client will:
- Retry on 503 (server busy) after 5 seconds
- Retry on network timeout after 10 seconds
- NOT retry on 400, 413, 422 (client error)
- Give up after 3 retry attempts

---

## 11. Performance Benchmarks

### 11.1 Expected Latency

| Endpoint | Expected Latency | Max Acceptable |
|----------|------------------|----------------|
| `/process_data` (describe_scene) | 2-3 seconds | 10 seconds |
| `/process_data` (read_text) | 1-2 seconds | 8 seconds |
| `/analyze_event` | 5-8 seconds | 15 seconds |
| `/map_room` | 20-40 seconds | 60 seconds |
| `/navigate_query` | < 500ms | 2 seconds |

### 11.2 Hardware Requirements

**Minimum**:
- GPU: 4GB VRAM (GTX 1650 or equivalent)
- CPU: 4 cores
- RAM: 8GB system RAM
- Storage: 50GB for models + data

**Recommended**:
- GPU: 8GB VRAM (RTX 3060 or equivalent)
- CPU: 8 cores
- RAM: 16GB system RAM
- Storage: 100GB SSD

---

## 12. Testing & Validation

### 12.1 Sample Test Data

Client will provide:
- 10 sample images for each task type
- 5 sample videos for proactive mode testing
- 3 sample room scanning videos with sensor data

### 12.2 Integration Testing Checklist

- [ ] `/process_data` with describe_scene
- [ ] `/process_data` with read_text
- [ ] `/process_data` with find_object
- [ ] `/process_data` with face_detect
- [ ] `/process_data` with save_face
- [ ] `/analyze_event` with significant event
- [ ] `/analyze_event` with no significant event
- [ ] `/submit_feedback` endpoint
- [ ] `/map_room` with sensor data
- [ ] `/navigate_query` with saved map

---

## 13. Security & Privacy

### 13.1 Data Storage

- All face embeddings: Encrypted at rest
- All feedback images: Stored securely, auto-delete after 90 days
- Room maps: User-owned, stored locally on device (client-side)

### 13.2 Network Security

- All endpoints: HTTPS required in production
- API authentication: Bearer token (to be implemented)

---

## 14. Deployment Architecture

### 14.1 Recommended Setup

```
┌─────────────┐
│ Mobile App  │
│ (Client)    │
└──────┬──────┘
       │ HTTPS
       ↓
┌─────────────┐
│ Load        │
│ Balancer    │
└──────┬──────┘
       │
    ┌──┴──┐
    │     │
┌───↓─┐ ┌─↓───┐
│ API │ │ API │  (FastAPI instances)
└──┬──┘ └──┬──┘
   │       │
   └───┬───┘
       ↓
┌─────────────┐
│ GPU Server  │  (Model inference)
│ - YOLO      │
│ - Depth     │
│ - CLIP      │
└─────────────┘
       │
       ↓
┌─────────────┐
│ Database    │  (SQLite or PostgreSQL)
└─────────────┘
```

---

## 15. Contact & Collaboration

### 15.1 Communication Channels

- **Documentation**: This file + Q&A document
- **Issue Tracking**: GitHub Issues
- **API Testing**: Postman collection (to be provided)

### 15.2 Next Steps

1. Server team answers questions in Q&A document
2. Client team provides sample test data
3. Both teams agree on API contract
4. Implementation begins
5. Integration testing
6. User acceptance testing

---

**Document Version**: 1.0  
**Last Updated**: October 11, 2025  
**Next Review**: After Q&A responses received

