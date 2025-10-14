# Questions for App-Side Team: Server-Side Review Complete

*Date: 2025-10-11*
*Server Team: Complete codebase review finished*

## Executive Summary

After thoroughly reviewing all server-side code, I have completed the following:

1. ✅ **Face Recognition Database Integration**: Migrated from `known_faces.pkl` to persistent database
2. ✅ **Proactive Agent Intelligence**: Enhanced to detect unknown people AND significant object changes
3. ✅ **User Feedback System**: Implemented `/submit_feedback` endpoint for AI corrections
4. ✅ **API Contract Documentation**: Created `CLIENT_SERVER_CONTRACT.md` for `/analyze_event`
5. ✅ **Room Mapping Design**: Created `FEATURE_DESIGN_ROOM_MAPPING.md` for future implementation

The server is now production-ready for **Stationary Mode** (Proactive Sentry) integration.

---

## Section 1: Critical Integration Questions

### 1.1 Video Upload Implementation Status

**Context**: The `/analyze_event` endpoint is ready and expects multipart/form-data with a video file.

**Questions**:
1. Have you successfully implemented the `multipart/form-data` request with the video file + metadata fields (`event_type`, `timestamp_utc`, `video_format`)?
2. Are you using a specific library for video encoding (e.g., `ffmpeg-kit-react-native`)? If so, what version?
3. What is the typical file size of the 10-15 second video clips you're sending? (This helps us optimize server memory allocation)

### 1.2 Motion Detection Improvements

**Context**: You mentioned improving motion detection to filter out head movements using Optical Flow.

**Questions**:
1. Have you started implementing the Optical Flow solution? If yes, which algorithm are you using (e.g., Farneback, Lucas-Kanade)?
2. What is your current false-positive rate for motion detection? (Approximate percentage)
3. Do you need any server-side assistance with motion analysis, or is this purely client-side preprocessing?

### 1.3 Error Handling & Network Failures

**Context**: The mobile app operates in real-world conditions with potential network interruptions.

**Questions**:
1. How are you handling network failures during video upload to `/analyze_event`?
   - Do you retry the request?
   - Do you queue failed uploads for later transmission?
2. What timeout value have you set for the `/analyze_event` request? (The server processes videos in ~3-5 seconds on average)
3. How do you handle the case where the server returns an empty `alert_text` (no significant event)? Do you log this silently or provide any UI feedback?

---

## Section 2: Transit Mode (Real-Time Navigator) - Future Work

**Context**: The server's "Fast Path" for immediate obstacle detection is implemented but not yet integrated with the app.

### 2.1 Continuous Image Streaming

**Questions**:
1. Have you started planning the implementation for sending continuous image frames (1-2 fps) to the `/process_data` endpoint when the user is walking?
2. What strategy will you use for image compression to minimize bandwidth while maintaining object detection accuracy?
3. Will you implement any client-side buffering or frame-skipping logic if the server response is slower than the capture rate?

### 2.2 Obstacle Avoidance UX

**Questions**:
1. When the server returns an `immediate_alert` (obstacle detected), how quickly can your app provide audio feedback to the user?
2. Do you plan to use haptic feedback (vibration) in addition to audio alerts for immediate threats?
3. Should the server provide directional information in the alert (e.g., "Obstacle on your left")? This would require additional development on our end.

---

## Section 3: Personal Object Learning & Finding

**Context**: The server has fully implemented the `learn_personal_object` and enhanced `find_object` features using image embeddings.

### 3.1 Object Learning Workflow

**Questions**:
1. Have you designed the UX flow for when a user wants to teach the system about a personal object (e.g., "Learn my keys")?
   - Voice command trigger?
   - Step-by-step guidance for the user?
2. Do you capture a single image or multiple images from different angles when learning an object?
3. Should the server provide confirmation feedback about the quality of the captured image before saving the embedding?

### 3.2 Object Finding Accuracy

**Questions**:
1. The server currently uses a similarity threshold of `0.85` for matching personal objects. Have you encountered any false positives or false negatives in testing?
2. Would it be helpful for the server to return a "confidence score" along with the found object?
3. If an object is not found in the current view, should the server suggest actions (e.g., "Try scanning the room more slowly")?

---

## Section 4: Face Recognition Integration

**Context**: Face recognition is now fully integrated with the database. The old `known_faces.pkl` file has been deleted.

### 4.1 Face Saving Workflow

**Questions**:
1. How do you guide the user to capture a good face image when using the `save_face` task?
   - Do you provide real-time feedback about face detection?
   - Do you enforce a minimum face size or quality threshold on the client side?
2. What happens if the user accidentally saves the same person with a different name? Should the server prevent duplicates based on face similarity?
3. Do you need a way for users to *delete* or *rename* saved faces? (This functionality is not yet implemented on the server)

### 4.2 Face Recognition in Proactive Mode

**Questions**:
1. When the agent announces "An unknown person has just entered the room," do you want to provide the user with an option to immediately save that face?
   - Example workflow: Alert → User says "Save this face as John" → System captures and saves
2. Should the agent announce *every* unknown person, or only the first unknown detection in a session to avoid repetitive alerts?

---

## Section 5: User Feedback System (`/submit_feedback`)

**Context**: The `/submit_feedback` endpoint is ready to receive detailed user corrections.

### 5.1 Feedback Collection UX

**Questions**:
1. What is the exact voice command trigger for initiating feedback? (e.g., "Bumblebee, that was wrong")
2. After the trigger, how do you prompt the user for their correction?
   - Specific question like "What should I have said?"
   - Open-ended listening?
3. How do you handle cases where the user's correction is unclear or incomplete?

### 5.2 Feedback Data Linking

**Questions**:
1. For proactive alerts (from `/analyze_event`), the server generates an `event_id`. Can your app capture and store this `event_id` temporarily so it can be sent with the feedback?
2. For reactive tasks (like `describe_scene`), you don't currently have an `event_id`. Should the server start returning an `event_id` for all `/process_data` responses to enable feedback on those tasks too?
3. Do you want a way to view or manage the feedback history on the client side?

---

## Section 6: Mode Detection & Switching

**Context**: The three modes (Stationary, Transit, Vehicle) are designed to be detected by the client app based on sensor data.

### 6.1 Sensor Integration

**Questions**:
1. Have you integrated with the device's accelerometer and GPS to detect the user's movement state?
2. What thresholds have you chosen for distinguishing between the modes?
   - Stationary: Speed < ? m/s, Accelerometer variance < ?
   - Transit: Speed between ? and ? m/s
   - Vehicle: Speed > ? m/s
3. How do you handle edge cases like:
   - User is stationary on a moving train (GPS moving but accelerometer stable)?
   - User is in a slow-moving vehicle in traffic?

### 6.2 Mode Transition Handling

**Questions**:
1. When transitioning between modes (e.g., from Stationary to Transit), do you:
   - Stop current operations immediately?
   - Wait for the current task to complete?
2. Do you provide any feedback to the user when the mode changes (e.g., "Switching to walking mode")?
3. How do you prevent rapid mode switching if the sensors are noisy?

---

## Section 7: Performance & Resource Management

### 7.1 Battery & Data Usage

**Questions**:
1. Have you measured the battery consumption of the app in each mode?
   - Stationary Mode (periodic video uploads)
   - Transit Mode (continuous image streaming - future)
2. Do you provide users with options to adjust the quality/frequency of uploads to save data or battery?
3. Have you tested the app's behavior on a cellular connection (not just WiFi)?

### 7.2 Server Response Handling

**Questions**:
1. What is the maximum acceptable latency for a server response in each mode?
   - Stationary: ? seconds for video analysis
   - Transit: ? milliseconds for immediate threat detection
2. Do you implement any client-side caching or prediction to handle temporary server unavailability?
3. Should the server provide status updates for long-running operations (e.g., "Analyzing video... 50% complete")?

---

## Section 8: Database & Privacy Concerns

### 8.1 Local vs. Server Storage

**Context**: The server stores face embeddings and personal object embeddings in a local `memory.json` database.

**Questions**:
1. Is the server expected to run on the user's own local machine/laptop, or on a remote cloud server?
2. If it's a cloud-based deployment, do we need to implement multi-user support with user authentication?
3. Should face embeddings and personal objects be encrypted at rest in the database for additional privacy?

### 8.2 Data Synchronization

**Questions**:
1. If a user has multiple devices (e.g., phone and smart glasses), do you need a way to sync the learned faces and objects between devices?
2. Should the server provide endpoints to export/import the database for backup purposes?

---

## Section 9: Testing & Validation

### 9.1 Integration Testing

**Questions**:
1. Do you have a test suite for the client-server integration?
2. What is your process for testing with real video data? Do you have sample videos we can use for server-side testing?
3. Are you conducting user testing with visually impaired individuals? If so, what is the most common feedback you're receiving?

### 9.2 Edge Cases

**Questions**:
1. How does the app handle:
   - Very low-light conditions where the camera can't capture usable images?
   - Crowded environments with many people/objects?
   - Rapidly changing scenes (e.g., user walking through a busy street)?
2. Should the server provide a "confidence score" or "quality indicator" for its responses to help the app decide whether to trust the result?

---

## Section 10: Documentation & Next Steps

### 10.1 API Documentation

**Questions**:
1. Do you need more detailed API documentation beyond what's in `CLIENT_SERVER_CONTRACT.md` and `README.md`?
2. Should I create example request/response payloads with actual base64-encoded images and videos for easier integration testing?
3. Do you need documentation on the expected error codes and how to handle them?

### 10.2 Collaboration Tools

**Questions**:
1. What is the best way for our teams to communicate about issues or changes?
   - Shared documentation (e.g., Google Docs)?
   - Issue tracker (e.g., GitHub Issues)?
   - Regular sync meetings?
2. Should I create a **Postman collection** or **OpenAPI/Swagger spec** for easier API testing on your end?
3. Do you need access to server logs for debugging integration issues?

---

## Summary of Immediate Action Items for App Team

Based on the questions above, here are the immediate clarifications I need to continue server-side development effectively:

1. **Video Upload Status**: Confirm that multipart/form-data upload is working
2. **Error Handling**: Clarify retry logic and timeout values
3. **Face Recognition UX**: Define the workflow for saving faces
4. **Feedback System**: Confirm voice command trigger and correction prompt
5. **Mode Detection**: Share sensor thresholds for mode switching
6. **Testing Data**: Provide sample video clips for server-side testing

Please prioritize answering these questions so I can optimize the server for your specific client implementation.

---

*Server Team: Ready for integration testing and eager to collaborate!*
