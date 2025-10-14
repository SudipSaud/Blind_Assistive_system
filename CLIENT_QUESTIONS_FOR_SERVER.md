# Client Questions for Server Team

**Date:** October 11, 2025  
**From:** Scout1 Mobile App Team  
**To:** Server Implementation Team  
**Purpose:** Clarify requirements and resolve black boxes before implementation

---

## Context

We've completed the **Server Implementation Guide** that details the entire system architecture. Before we proceed with implementing the client-side room mapping components, we need your input on several critical technical decisions that will affect both our implementations.

Please read the **SERVER_IMPLEMENTATION_GUIDE.md** first, then answer these questions.

---

## Section 1: Architecture & Modes

### Q1.1: Mode Detection Responsibility

**Background**: The app operates in three modes (On-Demand, Proactive Sentry, Room Mapping).

**Question**: Should mode transitions be:
- **Option A**: Client-controlled (client decides when to activate sentry mode)
- **Option B**: Server-suggested (server recommends mode based on user patterns)
- **Current assumption**: Option A - client has full control

**Your preference**: _____

**Reasoning**: _____

---

### Q1.2: Proactive Event Filtering Logic

**Background**: In Sentry Mode, we want to minimize false alerts while catching important events.

**Question**: What approach will you use for determining "significant events"?
- **Option A**: Rule-based (if unknown_person OR object_disappeared → alert)
- **Option B**: ML-based classifier (train model on "alert-worthy" vs "normal" events)
- **Option C**: Confidence threshold (only alert if event confidence > 90%)
- **Option D**: Combination of above

**Your choice**: _____

**Question**: Should the client send you ALL motion-detected videos, or should we implement client-side pre-filtering to reduce bandwidth?

**Your preference**: _____

---

## Section 2: Room Mapping - Technical Decisions

### Q2.1: Depth Estimation Model Choice

**Background**: Room mapping requires accurate depth estimation to build 3D maps.

**Question**: Which depth model will you use?
- **Option A**: MiDaS-small (fast, ~150ms/frame, ±0.5m accuracy)
- **Option B**: ZoeDepth-NK (better, ~300ms/frame, ±0.3m accuracy)
- **Option C**: YOLOv9c built-in depth (if available)
- **Option D**: Other: _____

**Your choice**: _____

**Follow-up**: What is the expected depth range accuracy at various distances?
- At 1 meter: ±_____ cm
- At 3 meters: ±_____ cm
- At 5 meters: ±_____ cm

---

### Q2.2: Coordinate System Confirmation

**Background**: We proposed this coordinate system in the guide:
```
Origin (0,0): User's starting position
X-axis: East (+X), West (-X)
Y-axis: North (+Y), South (-Y)
Z-axis: Height from floor

Heading: 0° = East, 90° = North, 180° = West, 270° = South
```

**Question**: Do you agree with this convention?
- ✅ Yes, we'll use this system
- ❌ No, we propose: _____

**Rationale**: _____

---

### Q2.3: Video Processing Strategy

**Background**: Client will send 30-90 second videos for room mapping.

**Question**: How will you process the video?
- **Option A**: Extract keyframes (e.g., 1 frame per second = 30-90 frames)
- **Option B**: Extract frames on scene change (adaptive sampling)
- **Option C**: Process every Nth frame (e.g., every 30 frames at 30fps)
- **Option D**: Other: _____

**Your choice**: _____

**Follow-up**: What is the optimal frame rate for us to record?
- Client should record at: _____ fps
- You'll process: _____ frames per second of video

---

### Q2.4: Object Persistence & Tracking

**Background**: The same object (e.g., "couch") will appear in multiple frames from different angles.

**Question**: How will you handle object deduplication?
- **Option A**: Cluster similar detections using IOU (intersection over union)
- **Option B**: Track objects across frames (using optical flow or SORT)
- **Option C**: 3D position-based clustering (merge objects within 0.5m radius)
- **Option D**: Other: _____

**Your choice**: _____

**Follow-up**: If the user maps the same room twice (updating the map), should we:
- Merge new detections with old map
- Replace old map entirely
- Keep both as separate versions

**Your preference**: _____

---

### Q2.5: Boundary Detection (Walls, Doors)

**Background**: The guide mentions detecting "boundaries" like walls and doors.

**Question**: How will you detect room boundaries?
- **Option A**: Depth discontinuities (sudden depth changes = wall)
- **Option B**: Dedicated wall/door detection model
- **Option C**: Assume rectangular room based on explored area
- **Option D**: Use object positions to infer walls (e.g., objects stop at walls)
- **Option E**: Don't detect boundaries initially (future enhancement)

**Your choice**: _____

**Reasoning**: _____

---

### Q2.6: Unexplored Region ("Black Box") Tracking

**Background**: Core concept is guiding users to map unexplored regions.

**Question**: What resolution should the occupancy grid be?
- **Option A**: 0.5m x 0.5m cells (coarse, fast)
- **Option B**: 0.25m x 0.25m cells (medium)
- **Option C**: 0.1m x 0.1m cells (fine, slower)
- **Option D**: Adaptive resolution based on object density

**Your choice**: _____

**Follow-up**: How will you calculate camera field-of-view coverage?
- Assume fixed FOV (60°)?
- Extract FOV from video metadata?
- Let client provide camera FOV in sensor_data?

**Your approach**: _____

---

## Section 3: Spatial Reasoning & Navigation

### Q3.1: Distance Calculation Between Objects

**Background**: Client needs distance matrix between ALL objects for "What's between me and X?" queries.

**Question**: For a room with 20 objects, that's 190 pairwise distances. Should we:
- **Option A**: Pre-calculate all distances when map is built (fast queries, more storage)
- **Option B**: Calculate distances on-demand when user asks (slower queries, less storage)
- **Option C**: Pre-calculate only between "important" objects (furniture), on-demand for small objects

**Your choice**: _____

**Follow-up**: What constitutes a "clear path" between two objects?
- No other objects intersecting the line segment
- Sufficient space (e.g., > 0.6m width for person to walk)
- Other criteria: _____

---

### Q3.2: Pathfinding Algorithm

**Background**: For "Navigate to X" queries, we need obstacle-aware pathfinding.

**Question**: Which algorithm will you implement?
- **Option A**: A* (optimal path, standard choice)
- **Option B**: Dijkstra (simpler, slower for large maps)
- **Option C**: RRT (Rapidly-exploring Random Tree - good for dynamic obstacles)
- **Option D**: Simple waypoints (straight line with obstacle flagging)

**Your choice**: _____

**Follow-up**: Should paths avoid objects by a safety margin?
- Margin size: _____ cm from object boundaries

---

### Q3.3: Real-Time Position Tracking

**Background**: Client will track user position using step counting + compass heading.

**Question**: Should the server:
- **Option A**: Trust client's position estimate completely
- **Option B**: Refine position based on visible objects in live camera feed (Phase 2 feature)
- **Option C**: Provide "position confidence" feedback if estimate seems wrong

**Your choice**: _____

**Follow-up**: How should client handle position drift (accumulating error)?
- Suggest re-scanning room every X minutes?
- Provide "recalibration points" (e.g., "touch the table to reset position")?

**Your recommendation**: _____

---

### Q3.4: Turn-by-Turn Instruction Format

**Background**: Server will return navigation instructions like "Turn left 30°, walk 2m".

**Question**: Should instructions be:
- **Option A**: Absolute (based on compass: "Turn to heading 45°")
- **Option B**: Relative (based on user's current facing: "Turn 30° to your left")
- **Option C**: Contextual (based on landmarks: "Turn left at the couch, then walk straight")

**Your preference**: _____

**Reasoning**: _____

---

## Section 4: Object Detection & Recognition

### Q4.1: Object Classification Granularity

**Background**: YOLO models can detect "chair" but not distinguish "office chair" vs "dining chair".

**Question**: For room mapping, what level of detail do you plan to provide?
- **Option A**: Generic classes only (chair, table, couch, tv, etc.)
- **Option B**: Sub-classes where possible (dining table, coffee table, office desk)
- **Option C**: Allow user to rename objects ("That's my gaming chair")

**Your approach**: _____

**Follow-up**: If Option C, how should client trigger renaming?
- Voice command: "Call that object my work desk"
- Requires identifying which object user is referring to

**Your proposal**: _____

---

### Q4.2: Small Object Handling

**Background**: Small objects (phone, keys, remote) are important but harder to detect/track.

**Question**: Should room maps include small objects?
- **Option A**: Yes, track everything detected
- **Option B**: Only track stationary furniture (tables, chairs, couch)
- **Option C**: Track small objects but mark them as "movable" / less reliable

**Your choice**: _____

**Reasoning**: _____

---

### Q4.3: Dynamic Objects (People, Pets)

**Background**: People and pets move around - they're not static room features.

**Question**: Should detected people/pets be:
- **Option A**: Excluded from room map entirely
- **Option B**: Noted as "dynamic obstacles" (present during mapping, ignored later)
- **Option C**: Tracked separately as "current occupants" (updated in real-time)

**Your choice**: _____

---

## Section 5: API Design & Data Formats

### Q5.1: Sensor Data Frequency

**Background**: Client will record video + sensor data (compass, accelerometer).

**Question**: How often should we sample and send sensor data?
- **Option A**: Every frame (30 fps = 30 readings/second)
- **Option B**: Once per second (1 Hz)
- **Option C**: Only when heading changes > 10°
- **Option D**: Other: _____

**Your preference**: _____

**Reasoning**: _____

---

### Q5.2: Video Format & Compression

**Background**: Room mapping videos will be 30-90 seconds, potentially large files.

**Question**: What video format/codec is optimal for your processing pipeline?
- **Current plan**: H.264 encoded MP4
- **Alternative**: Motion JPEG (easier to extract frames, but larger)
- **Your preference**: _____

**Follow-up**: Should we apply client-side compression?
- Target bitrate: _____ kbps
- Resolution: _____ (e.g., 1280x720, 1920x1080)
- Frame rate: _____ fps

---

### Q5.3: Response Size Concerns

**Background**: A room with 20 objects has a large JSON response (~50KB+ with all relationships).

**Question**: Should we optimize the response size?
- **Option A**: Send full map every time (simple, redundant)
- **Option B**: Send only "changed" objects if updating existing map
- **Option C**: Compress response (gzip at HTTP level)
- **Option D**: Split into multiple endpoints (get map summary, then get details)

**Your choice**: _____

---

### Q5.4: Error Cases & Fallbacks

**Background**: Room mapping might fail (poor lighting, featureless room, etc.).

**Question**: What should server return if mapping fails?
- **Option A**: HTTP 422 with error message "Insufficient features detected"
- **Option B**: Partial map with low coverage percentage + warning
- **Option C**: Suggest user actions: "Please turn on lights and try again"

**Your approach**: _____

**Follow-up**: What minimum requirements should we enforce?
- Minimum video length: _____ seconds
- Minimum number of frames: _____
- Minimum detected objects: _____

---

## Section 6: Performance & Scalability

### Q6.1: Processing Time Expectations

**Background**: User will wait while server processes room mapping video.

**Question**: What is realistic processing time for 60-second video?
- **Your estimate**: _____ seconds
- **Breakdown**:
  - Frame extraction: _____ sec
  - Object detection (per frame): _____ ms × _____ frames = _____ sec
  - Depth estimation (per frame): _____ ms × _____ frames = _____ sec
  - Map building: _____ sec
  - Relationship calculation: _____ sec
  - **Total**: _____ sec

**Question**: Should client show progress updates?
- If yes, can server send partial updates (e.g., "50% complete")?
- Or should we just show generic "Processing..." message?

---

### Q6.2: Concurrent Request Handling

**Background**: In proactive mode, server might receive motion-detected videos frequently.

**Question**: How many concurrent video processing requests can your server handle?
- **Your capacity**: _____ concurrent requests
- **Should client implement request queuing?**
  - Yes / No
- **Should client drop frames if server is busy?**
  - Yes / No

---

### Q6.3: Model Loading & Memory

**Background**: Multiple ML models running simultaneously.

**Question**: Will models be:
- **Option A**: Loaded once at startup (faster inference, more RAM)
- **Option B**: Loaded on-demand (slower first request, less RAM)
- **Option C**: Different models on different endpoints (e.g., YOLO always loaded, depth loaded only for /map_room)

**Your approach**: _____

**Follow-up**: What is total expected memory usage?
- YOLO model: _____ GB
- Depth model: _____ GB
- Face recognition: _____ GB
- CLIP/BLIP: _____ GB
- **Peak memory**: _____ GB

---

## Section 7: User Feedback System

### Q7.1: Feedback Storage Duration

**Background**: `/submit_feedback` endpoint stores user corrections for training.

**Question**: How long should feedback data be retained?
- **Option A**: Forever (for long-term learning)
- **Option B**: 90 days (privacy-conscious)
- **Option C**: Until next model retraining, then delete
- **Option D**: User-configurable

**Your choice**: _____

---

### Q7.2: Feedback Integration into Training

**Background**: Collected feedback should improve model accuracy.

**Question**: When will feedback be used for retraining?
- **Option A**: Continuous learning (model updates daily)
- **Option B**: Batch retraining (manual trigger when enough feedback collected)
- **Option C**: Future feature (just collect for now)

**Your choice**: _____

**Follow-up**: Should client notify user when model has improved based on their feedback?

---

## Section 8: Face Recognition Specifics

### Q8.1: Face Detection Confidence Threshold

**Background**: Not every detected face should be compared against database.

**Question**: What confidence threshold for face detection?
- Only process faces with confidence > _____ %

**Follow-up**: In proactive mode, should server announce:
- Every unknown person detected
- Only the first unknown person in a session
- Only if unknown person is close to camera (< 2m distance)

**Your preference**: _____

---

### Q8.2: Face Similarity Threshold

**Background**: You mentioned 0.85 threshold in your original questions document.

**Question**: Is 0.85 still the planned threshold, or do you want it configurable?
- **Fixed at 0.85**
- **Configurable** (client sends threshold in request)
- **Adaptive** (threshold adjusts based on lighting conditions)

**Your choice**: _____

---

## Section 9: Testing & Validation

### Q9.1: Test Data Requirements

**Background**: We need sample data to test integration.

**Question**: What test data do you need from us?
- [ ] 10 sample images for each task type (describe_scene, read_text, etc.)
- [ ] 5 sample videos for proactive sentry mode
- [ ] 3 sample room mapping videos with sensor data
- [ ] Sample face images for recognition testing
- [ ] Other: _____

**Your needs**: _____

**Follow-up**: Should test data include "edge cases"?
- Poor lighting
- Motion blur
- Extreme camera angles
- Empty rooms
- Very cluttered rooms

---

### Q9.2: Integration Testing Timeline

**Background**: Both teams need to coordinate testing.

**Question**: What is your preferred testing approach?
1. **Option A**: You build endpoints first, we test against them
2. **Option B**: We create mock server, you match the interface
3. **Option C**: Parallel development, integration testing at milestones

**Your preference**: _____

**Follow-up**: How should we report bugs/issues?
- GitHub Issues
- Shared document
- Direct communication (email/chat)

---

## Section 10: Future Enhancements (Phase 2)

### Q10.1: Real-Time WebSocket Streaming

**Background**: Phase 2 might include live frame streaming for real-time navigation.

**Question**: Do you have experience with WebSocket video streaming?
- Yes / No
- If yes, preferred protocol: _____

**Question**: Should we plan for this now (even if not implementing yet)?
- **Yes** - design API with WebSocket in mind
- **No** - focus on HTTP, refactor later if needed

**Your preference**: _____

---

### Q10.2: Multi-User / Multi-Device Support

**Background**: Users might want to sync data across devices.

**Question**: Should server support multiple users?
- **Option A**: Single user per server instance (user runs server locally)
- **Option B**: Multi-user with authentication
- **Option C**: Not needed (privacy-first, local only)

**Your choice**: _____

---

### Q10.3: Cloud Deployment

**Background**: Running server locally vs. cloud-hosted.

**Question**: What is the expected deployment model?
- **Option A**: User runs server on their own computer (localhost)
- **Option B**: User deploys to their own cloud instance (AWS/GCP)
- **Option C**: We provide hosted service (SaaS)
- **Option D**: Hybrid (local for privacy-sensitive tasks, cloud for heavy processing)

**Your target**: _____

**Follow-up**: If cloud-based, what regions should we optimize for?

---

## Section 11: Open Questions & Concerns

### Q11.1: Anything We Missed?

**Question**: After reading the Server Implementation Guide, what critical topics did we NOT cover that you need clarification on?

**Your concerns**: _____

---

### Q11.2: Scope Creep Prevention

**Background**: Room mapping is a complex feature with potential for infinite enhancement.

**Question**: What should be the **minimum viable product (MVP)** for room mapping?
- **Your MVP definition**:
  - [ ] Basic object detection (furniture only)
  - [ ] Distance calculations between objects
  - [ ] Navigate-to functionality
  - [ ] Unexplored region detection
  - [ ] Other: _____

**What can be deferred to Phase 2?**
- [ ] Boundary detection (walls/doors)
- [ ] Small object tracking
- [ ] Real-time position refinement
- [ ] Advanced pathfinding
- [ ] Other: _____

---

### Q11.3: Development Timeline

**Background**: Both teams need to coordinate schedules.

**Question**: What is your estimated timeline?
- **Phase 1 (On-Demand + Proactive Sentry)**: _____ weeks
- **Phase 2 (Room Mapping MVP)**: _____ weeks
- **Phase 3 (Real-time Navigation)**: _____ weeks

**Our timeline**:
- Client-side room mapping components: ~2 weeks
- Integration testing: ~1 week
- User testing: ~1 week

**Question**: Does this align with your schedule?

---

## Section 12: Final Sign-Off

### Q12.1: API Contract Approval

**Question**: After reading SERVER_IMPLEMENTATION_GUIDE.md, do you approve the API contracts for:
- [ ] `/process_data` endpoint
- [ ] `/analyze_event` endpoint
- [ ] `/submit_feedback` endpoint
- [ ] `/map_room` endpoint (new)
- [ ] `/navigate_query` endpoint (new)

**Any requested changes**: _____

---

### Q12.2: Ready to Implement?

**Question**: Are you confident you have enough information to start implementation?
- ✅ Yes, we're ready
- ⚠️ Almost, but we need clarification on: _____
- ❌ No, we need more discussion

**Your status**: _____

---

## Response Deadline

**Please respond by**: _____ (Date)

**Preferred response format**:
- Fill in this document with your answers
- Send back as `SERVER_RESPONSES.md`
- Or schedule a call to discuss together

---

## Summary of Critical Questions (TL;DR)

If you're short on time, these are the **MUST-ANSWER** questions:

1. **Q2.1**: Which depth estimation model? (MiDaS, ZoeDepth, other?)
2. **Q2.3**: How will you process room mapping videos? (frame extraction strategy)
3. **Q2.5**: How will you detect room boundaries? (walls, doors)
4. **Q2.6**: What occupancy grid resolution for black box tracking?
5. **Q3.2**: Which pathfinding algorithm? (A*, Dijkstra, RRT, simple?)
6. **Q5.2**: Video format requirements (codec, resolution, fps, bitrate)
7. **Q6.1**: Expected processing time for 60-second room mapping video?
8. **Q9.2**: Integration testing approach (we test your API, or you match our mocks?)
9. **Q11.2**: What's your MVP definition for room mapping?
10. **Q11.3**: What's your development timeline?

---

**Thank you for your collaboration! 🚀**

*Scout1 Client Team*

