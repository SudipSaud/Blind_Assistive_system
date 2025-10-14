# Client-Server API Contract: Proactive Sentry Mode

This document outlines the agreed-upon contract between the mobile client application and the server for the "Proactive Sentry" feature, specifically concerning the `/analyze_event` endpoint.

*Last Updated: 2025-10-11*

## Endpoint: `/analyze_event`

The server will expose the `/analyze_event` endpoint to receive and analyze video clips of motion events detected by the client.

### Request Format

The client will send a `POST` request using the `multipart/form-data` content type. The request will contain the following parts:

| Part Name | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `video_file` | File | The video clip of the motion event. The video must be an **MP4 container (.mp4)** with the video stream encoded using the **libx264 (H.264)** codec and a pixel format of **yuv420p**. | **Yes** |
| `event_type` | Text | A string describing the event that triggered the capture. For now, this will be a generic string like `"motion_detected"`. | **Yes** |
| `timestamp_utc`| Text | The UTC timestamp of when the event was captured, formatted as an **ISO 8601 string**. | **Yes** |
| `video_format` | Text | The format of the video file (e.g., `"mp4"`). | **Yes** |

### Server-Side Logic

1.  The server will receive the multipart request.
2.  It will save the `video_file` temporarily to disk.
3.  The `Agent` module will analyze the video to determine if a significant event occurred (e.g., a known person entering the frame).
4.  The event details will be logged to the `Scene History` collection in the database, using the provided `timestamp_utc`.

### Response Format

The server will respond with a JSON object.

#### On Significant Event

If a meaningful event is detected (e.g., a person enters), the server will return a JSON object with a single key, `alert_text`, containing a human-readable description of the event.

```json
{
  "alert_text": "Sarah has just entered the room."
}
```

#### On No Significant Event

If the motion is determined to be insignificant (e.g., lighting changes, minor movements), the server will return a JSON object with an empty `alert_text`.

```json
{
  "alert_text": ""
}
```

The client application will check for the presence of text in the `alert_text` field. If it is not empty, the app will speak the contents to the user.
