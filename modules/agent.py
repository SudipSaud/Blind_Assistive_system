"""
The Agent Module
This module contains the core logic for the proactive agent, including the analysis of video events.
"""
import logging
import cv2
import numpy as np
import datetime
from modules.face_recognition import FaceRecognizer
from modules.object_detection import ObjectDetector
from modules.database import DatabaseManager

logger = logging.getLogger(__name__)

class Agent:
    def __init__(self, face_recognizer: FaceRecognizer, object_detector: ObjectDetector, db_manager: DatabaseManager):
        self.is_initialized = False
        self.face_recognizer = face_recognizer
        self.object_detector = object_detector
        self.db_manager = db_manager
        # Define a set of objects considered significant for proactive alerts
        self.significant_objects = {'box', 'package', 'bag', 'backpack', 'suitcase', 'bottle'}
        logger.info("Agent module created.")

    def load_model(self):
        # The agent uses models loaded by other services, so no new models to load here.
        self.is_initialized = True
        logger.info("Agent initialized.")

    def analyze_video_event(self, video_path: str, timestamp_utc: str) -> dict:
        """
        Analyzes a video clip to identify a key event, logs the scene to the database,
        and generates a simple alert text for the client.

        Args:
            video_path: The path to the temporary video file.
            timestamp_utc: The ISO 8601 timestamp from the client.

        Returns:
            A dictionary with a single key "alert_text".
        """
        if not self.is_initialized:
            return {"alert_text": ""}

        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                logger.error(f"Could not open video file: {video_path}")
                return {"alert_text": "Error processing video."}

            frame_count = 0
            all_recognized_people_per_frame = []
            all_detected_objects = set()

            # --- Get the last known scene from the database for comparison ---
            last_scene = self.db_manager.get_last_scene()
            people_in_last_scene = set(last_scene.get('detected_people', [])) if last_scene else set()
            objects_in_last_scene = set(last_scene.get('detected_objects', [])) if last_scene else set()
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Analyze every Nth frame to be efficient
                if frame_count % 5 == 0:
                    # Recognize faces and store all results (known and unknown)
                    recognized_persons_in_frame = self.face_recognizer.recognize(frame)
                    all_recognized_people_per_frame.append(recognized_persons_in_frame)

                    # Detect objects
                    detected_objects = self.object_detector.detect(frame)
                    for obj in detected_objects:
                        all_detected_objects.add(obj['name'])

                frame_count += 1
            
            cap.release()

            # --- Process the final frame's results for logging and comparison ---
            final_recognized_people = all_recognized_people_per_frame[-1] if all_recognized_people_per_frame else []
            
            # Get sets of names for comparison logic
            current_known_people = {p['name'] for p in final_recognized_people if p['name'] != 'Unknown'}
            current_has_unknown = any(p['name'] == 'Unknown' for p in final_recognized_people)
            current_objects = all_detected_objects

            # --- Log the current scene to the database ---
            self.db_manager.add_scene(
                timestamp=timestamp_utc,
                detected_people=list(current_known_people), # Log only known people for history
                detected_objects=list(current_objects),
                image_summary="Video event analysis"
            )

            # --- Event Classification Logic ---
            alert_text = "" # Default to no alert

            # 1. Check for newly entered KNOWN people (highest priority)
            newly_entered_known_people = current_known_people - people_in_last_scene
            if newly_entered_known_people:
                person_name = list(newly_entered_known_people)[0]
                alert_text = f"{person_name} has just entered the room."
            
            # 2. If no known person entered, check for UNKNOWN people
            elif current_has_unknown and not people_in_last_scene:
                # This logic triggers if the last scene had no one, and now there's an unknown person.
                alert_text = "An unknown person has just entered the room."

            # 3. If no person-related events, check for significant OBJECT changes
            if not alert_text:
                newly_added_objects = current_objects - objects_in_last_scene
                significant_new_objects = newly_added_objects.intersection(self.significant_objects)
                
                if significant_new_objects:
                    # Announce the first significant new object found
                    new_object_name = list(significant_new_objects)[0]
                    alert_text = f"A {new_object_name} has been placed in the area."

            if alert_text:
                logger.info(f"Generated alert: {alert_text}")
            else:
                logger.info("Motion detected, but no new significant event was identified.")

            return {"alert_text": alert_text}

        except Exception as e:
            logger.error(f"An error occurred during video event analysis: {e}")
            return {"alert_text": "An error occurred during analysis."}

