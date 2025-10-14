# Project Vision: The Proactive Personal Assistant

This document outlines the long-term vision for the Blind Assistive System, evolving it from a reactive tool into a proactive, context-aware personal assistant.

## 1. The Core Problem to Solve

A blind user cannot know *what* to ask about in their environment. The current system is reactive; it waits for a specific command from the user (e.g., "describe the scene"). This puts the burden on the user to constantly query their surroundings.

The future system must be **proactive**, capable of understanding the scene and anticipating the user's needs by providing relevant information automatically, without being asked.

## 2. The "Digital Nurse" Agent

The heart of the new system will be a proactive, always-on agent that functions like a helpful assistant or a "digital nurse." This agent will observe the environment through the camera and provide unsolicited, important updates.

### Key Proactive Capabilities:
- **Person Recognition & Arrival:** The agent will announce when a known person enters the user's view.
  - *Example: "Your mom just entered the room."*
- **Emotional Context (Advanced Future Goal):** The system could eventually be trained to recognize basic facial expressions.
  - *Example: "She seems to be happy."*
- **Environmental Changes:** The agent will notify the user of significant changes in the environment.
  - *Example: "The delivery person left a package on the table."*

## 3. The "Memory" Database Architecture

To achieve true personalization and proactivity, the system will build and maintain a persistent "memory" of the user's world. This database will be structured into three main collections.

### 3.1. The "People" Collection
This collection stores information about known individuals, replacing the simple `known_faces.pkl` file.
- **`person_id`**: A unique identifier (e.g., "person_1").
- **`name`**: The person's name (e.g., "Sarah").
- **`face_embedding`**: The unique mathematical signature of their face from the InsightFace model.
- **`metadata`**: Additional context, such as relationship ("mom") or the date first seen.

### 3.2. The "Personal Objects" Collection
This collection will store information about the user's important personal items.
- **`object_id`**: A unique identifier (e.g., "item_keys").
- **`name`**: The object's name (e.g., "my keys", "my wallet").
- **`visual_embedding`**: The unique visual signature of the object, captured via a dedicated "learn this object" function.

### 3.3. The "Scene History" Log
This is the core component for enabling proactivity. Every image from the app will be processed and its summary stored here.
- **`timestamp`**: When the image was captured.
- **`detected_objects`**: A list of all objects found by YOLOv9 (e.g., `['cup', 'laptop', 'book']`).
- **`detected_people`**: A list of names of recognized people in the scene (e.g., `['Sarah']`).
- **`image_summary`**: A brief text description from the image captioning model.

**How it enables proactivity:** The agent will constantly compare the latest entry in the Scene History with the previous one. If a new person appears, or a significant object is added, the agent can generate a proactive alert.

## 4. The Multi-Modal Agentic Architecture

To create a system that is intelligent, efficient, and context-aware, we will implement a multi-modal architecture. The app will be responsible for detecting the user's current state and switching the system's behavior accordingly. The three primary operating modes are: **Stationary**, **Transit**, and **Vehicle**.

### 4.1. Stationary Mode: The Proactive Sentry
- **When Active:** When the user is still (e.g., sitting in a room, standing in line). Detected by low GPS speed and low accelerometer variance.
- **App's Role:**
    - Runs a lightweight, on-device motion detection algorithm (e.g., frame differencing).
    - When a new, discrete motion event occurs, it sends a **10-15 second video clip** to the server's `/analyze_event` endpoint.
- **Server's Role:**
    - Receives the video clip and performs a deep, contextual analysis to identify the event (e.g., a person entering, a package being delivered).
    - Provides a rich, proactive summary of the event.
- **Goal:** To make the user aware of meaningful changes in their stable environment.

### 4.2. Transit Mode: The Real-Time Navigator
- **When Active:** When the user is walking. Detected by GPS speed > 0.7 m/s or high accelerometer variance.
- **App's Role:**
    - Disables motion detection.
    - Sends a **continuous stream of still images (1-2 fps)** to the server's main `/process_data` endpoint.
- **Server's Role:**
    - For every frame, it executes the **"Fast Path"** reflexive safety check using the depth model for immediate obstacle avoidance.
    - It can also use the "Slow Path" to provide a running commentary of the surroundings (e.g., "Approaching a crosswalk").
- **Goal:** To provide continuous, low-latency safety warnings and navigational awareness.

### 4.3. Vehicle Mode: The On-Demand Analyst
- **When Active:** When the user is in a car. Detected by the OS's Activity Recognition API or a sustained GPS speed > 5 m/s (18 km/h).
- **App's Role:**
    - Disables all proactive triggers (no video stream, no motion detection).
    - The system becomes purely **reactive**, waiting for a voice command.
- **Server's Role:**
    - Remains idle until a request is made.
    - When the user asks a question (e.g., "Read that sign"), the app sends a single, high-quality image to `/process_data` for on-demand analysis. The "Fast Path" is bypassed.
- **Goal:** To conserve resources and provide specific, user-initiated information in a rapidly changing environment.

This multi-modal design ensures the system's behavior is always appropriate to the user's real-world context, maximizing both safety and efficiency.

## 5. Human-Like, Actionable Guidance

The system's responses will evolve from simple, robotic data points into natural, intuitive, and actionable guidance that helps the user navigate their space.

### Response Evolution:
- **Old Response (Data-centric):**
  - User: "Where are my keys?"
  - System: `"keys at 0.9 meters."`
- **New Response (Agentic & Human-like):**
  - User: "Where are my keys?"
  - System: `"Your keys are on the coffee table, just to your right, near the TV remote. If you turn slightly to your right, I can guide you closer."`

This vision transforms the project from a set of disconnected AI tools into a cohesive, intelligent agent that truly understands and assists its user in their daily life.

## 6. Agent Learning via Voice Feedback

To ensure the proactive alerts are genuinely useful and to improve the agent's intelligence over time, a non-visual, voice-based feedback loop will be implemented.

- **Purpose:** To gather user feedback on the quality and relevance of proactive alerts in a hands-free manner.
- **How it works:**
    1. After the system provides a proactive alert (e.g., "Sarah has just entered the room"), the app will immediately ask a follow-up question: **"Was that helpful?"**
    2. The app will listen for a simple **"Yes"** or **"No"** response.
    3. This feedback will be sent to a dedicated `/feedback` endpoint on the server, linked to the specific event that triggered the alert.
- **Goal:** To create a data stream of user-validated events, which can be used in the future to fine-tune the agent's decision-making logic, reduce false positives, and help it learn what is most important to the user.

## 7. Future Vision: Advanced Capabilities

Once the core multi-modal agent is stable and functional, the following advanced features can be explored to further enhance the system's capabilities.

### 7.1. Scene Reconstruction (SLAM)
This feature would allow the system to build and remember a 3D map of the user's frequent environments, like their home or office, enabling a new level of spatial awareness.

- **Mapping Phase:** On command, or when the system detects a new environment, the user would be prompted to scan the room by turning their head. The app would capture a video stream of this process.
- **Server-Side Processing:** The server would receive the video and use advanced computer vision techniques (Simultaneous Localization and Mapping - SLAM) to "stitch" the frames together, creating a 3D point cloud or map of the room. Key landmarks (doors, windows, large furniture) would be identified and stored.
- **Relocalization Phase:** The next time the user enters a mapped room, the server can "relocalize" them with just a single frame, understanding their exact position and orientation within that known space.
- **Enhanced Guidance:** With this spatial context, the agent can provide truly intelligent guidance, such as "The kitchen table is about 5 steps forward and to your left," or "You are walking towards the wall; the exit is behind you."
