# Technical Design: Room Mapping & Spatial Memory

*Status: Proposed*
*Last Updated: 2025-10-11*

## 1. Overview

This document outlines the technical design for the "Room Mapping" feature. The goal is to give the assistive system a persistent memory of a user's environment, enabling advanced spatial awareness and object-finding capabilities.

The core concept involves two phases:
1.  **Mapping Phase:** The user scans a room, and the server builds a structured, descriptive map of it.
2.  **Relocalization & Guidance Phase:** When the user re-enters a mapped room, the system recognizes it and can use the map to provide intelligent guidance (e.g., "Your keys are on the coffee table to your left").

## 2. Proposed API Endpoint: `/map_room`

A new endpoint will be created to handle the mapping process.

*   **Endpoint:** `POST /map_room`
*   **Content-Type:** `multipart/form-data`

### 2.1. Request Payload

The client will initiate a "scan mode" and send a collection of images captured during a slow panoramic sweep of the room.

| Part Name | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `room_name` | Text | A user-provided name for the room (e.g., "Living Room", "Office"). This will serve as the primary identifier. | **Yes** |
| `image_files` | File Array | An array of high-resolution image files from the scan. These should be sequential frames from the video stream. | **Yes** |
| `timestamp_utc`| Text | The UTC timestamp of when the scan was initiated, formatted as an ISO 8601 string. | **Yes** |

### 2.2. Response Payload

Upon successful processing, the server will return a structured JSON object representing the room map. The client will be responsible for persisting this map on the device.

**Proposed JSON Structure:**

```json
{
  "room_id": "user1_living_room",
  "room_name": "Living Room",
  "description": "A rectangular living room with a large window on the right wall and a door on the left. A couch is against the back wall with a coffee table in front of it.",
  "landmarks": [
    {
      "landmark_id": "lm_1",
      "type": "door",
      "position_description": "on the left wall",
      "vector_from_center": [-1.0, 0.0, 0.5] // Example: [x, y, z] coordinates
    },
    {
      "landmark_id": "lm_2",
      "type": "window",
      "position_description": "on the right wall",
      "vector_from_center": [1.0, 0.0, 0.0]
    }
  ],
  "objects": [
    {
      "object_id": "obj_1",
      "name": "couch",
      "position_description": "against the back wall",
      "last_seen_timestamp": "2025-10-11T10:00:00Z"
    },
    {
      "object_id": "obj_2",
      "name": "coffee table",
      "position_description": "in the center of the room, in front of the couch",
      "last_seen_timestamp": "2025-10-11T10:00:00Z"
    },
    {
      "object_id": "obj_3",
      "name": "keys",
      "position_description": "on the coffee table",
      "last_seen_timestamp": "2025-10-11T10:00:00Z"
    }
  ]
}
```

## 3. Server-Side Processing Logic

The `/map_room` endpoint will trigger a complex, multi-step pipeline:

1.  **Image Stitching:**
    *   Receive the array of `image_files`.
    *   Use a computer vision library (e.g., OpenCV's `Stitcher` class) to create a single panoramic image of the room. This will be the primary visual reference.

2.  **Object & Landmark Detection:**
    *   Run the `ObjectDetector` (YOLOv9) on the panoramic image to identify all general objects (couch, table, window, door, etc.).
    *   Identify key architectural features as "landmarks" (doors, windows).

3.  **Spatial Relationship Analysis:**
    *   This is the most complex step. The server will analyze the positions of objects relative to each other and the landmarks.
    *   It will generate simple descriptive phrases like "on the coffee table," "to the left of the door," "against the back wall."

4.  **Descriptive Summary Generation:**
    *   Use a Vision Language Model (like the one in `VisionModule`) to generate a high-level, human-readable `description` of the room based on the panoramic image and the detected objects.

5.  **Map Assembly:**
    *   Combine the `room_name`, the generated `description`, and the lists of `landmarks` and `objects` into the final JSON structure.
    *   Save this map to a new `room_maps` collection in the database, linked to the user.

## 4. Integration with "Find Object" Feature

Once a room is mapped, the `find_object` task is fundamentally enhanced.

**New Workflow for `find_object`:**

1.  **User Query:** "Where are my keys?"
2.  **System Check:** The system checks if the user is in a known, mapped room (this requires a future "relocalization" step). Let's assume the user is in the "Living Room."
3.  **Database Lookup:** The server queries the "Living Room" map for "keys."
4.  **Memory Recall:** The map returns: "keys, last seen on the coffee table."
5.  **Guided Response:** The system provides a spatially aware response: "Your keys are in the Living Room. They were last seen on the coffee table. The coffee table is in the center of the room, to your right."

## 5. Future Considerations (Phase 2)

*   **Relocalization:** The ability for the server to determine which mapped room a user is in from a single image frame. This is non-trivial and may require techniques like visual place recognition.
*   **Map Updates:** A mechanism to update a room map when objects are moved or added, without requiring a full rescan.
*   **3D Reconstruction:** For true metric guidance ("5 steps forward"), a full 3D point cloud or mesh of the room would be needed, likely requiring a SLAM (Simultaneous Localization and Mapping) approach. This is significantly more complex than 2D image stitching.

This design provides a solid foundation for the Room Mapping feature, starting with a descriptive 2D map that can be expanded upon in the future.
