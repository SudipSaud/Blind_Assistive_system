from fastapi import FastAPI, HTTPException, File, Form, UploadFile
from pydantic import BaseModel
from typing import List, Optional, Literal
import base64
from PIL import Image
import io
import uvicorn
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
import datetime
import numpy as np
import cv2

# --- Helper function for similarity calculation ---
def calculate_cosine_similarity(embedding1, embedding2):
    """Calculates the cosine similarity between two embeddings."""
    vec1 = np.array(embedding1)
    vec2 = np.array(embedding2)
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

# Import the new modular services
from modules.vision import VisionModule
from modules.object_detection import ObjectDetector
from modules.face_recognition import FaceRecognizer
from modules.ocr import OCRReader
from modules.agent import Agent
from modules.database import DatabaseManager

# --- Global instances of our services ---
vision_service = VisionModule()
object_service = ObjectDetector()
db_manager = DatabaseManager() # Initialize the database manager first
face_service = FaceRecognizer(db_manager=db_manager) # Pass the db_manager to the FaceRecognizer
ocr_service = OCRReader()
# The agent uses other services, so it's initialized with them
agent_service = Agent(face_recognizer=face_service, object_detector=object_service, db_manager=db_manager)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load all AI models on startup
    print("Loading all AI models...")
    vision_service.load_model()
    object_service.load_model()
    face_service.load_model()
    ocr_service.load_model()
    agent_service.load_model() # Initialize the agent
    print("All models loaded.")
    yield
    # Close the database connection when the app shuts down
    db_manager.close()

app = FastAPI(lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConversationTurn(BaseModel):
    role: str
    content: str

class ProcessRequest(BaseModel):
    task: Literal[
        'describe_scene', 
        'read_text', 
        'find_object',
        'answer_question', 
        'recognize_face',
        'save_face',
        'learn_personal_object'
    ]
    image_data: Optional[str] = None
    query_text: Optional[str] = None # Used for VQA, find_object, save_face, and learn_personal_object
    conversation_history: Optional[List[ConversationTurn]] = None

class ProcessResponse(BaseModel):
    result_text: str
    structured_data: Optional[dict] = None
    immediate_alert: Optional[str] = None

# --- Updated model for the /analyze_event endpoint response ---
class AnalyzeEventResponse(BaseModel):
    alert_text: str

# --- New model for the /submit_feedback endpoint ---
class SubmitFeedbackRequest(BaseModel):
    event_id: Optional[str] = None # event_id or original_image_data should be present
    original_image_data: Optional[str] = None
    incorrect_ai_response: str
    user_correction_text: str
    timestamp_utc: str

# --- New Models for the /feedback endpoint ---
class FeedbackRequest(BaseModel):
    event_id: str
    feedback: Literal["Yes", "No"]

@app.post("/process_data", response_model=ProcessResponse)
async def process_data(request: ProcessRequest):
    """
    Processes a request containing an image and a task using the new modular services.
    Implements a "Fast Path" for immediate threat detection.
    """
    print(f"Received task: {request.task}")

    image = None
    cv_image = None
    if request.image_data:
        try:
            image_bytes = base64.b64decode(request.image_data)
            # Convert to numpy array for OpenCV compatibility
            nparr = np.frombuffer(image_bytes, np.uint8)
            cv_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            # Convert to PIL Image for vision models
            image = Image.fromarray(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid image data: {e}")

    result_text = ""
    structured_data = None
    immediate_alert = None

    # --- Fast Path: Immediate Threat Detection ---
    if cv_image is not None:
        is_threat, threat_details = object_service.check_for_immediate_threats(cv_image)
        if is_threat:
            # Threat detected, return an immediate alert and stop further processing.
            # NOTE: The 'threat_details' is a raw proximity value and needs calibration.
            alert_message = f"Immediate obstacle detected! Proximity level: {threat_details:.2f}"
            return ProcessResponse(result_text="", immediate_alert=alert_message)

    # --- Slow Path: Full Analysis (only if no immediate threat was found) ---
    try:
        if request.task == 'describe_scene':
            if not image:
                raise HTTPException(status_code=400, detail="Image data is required for describe_scene")
            result_text = vision_service.describe_scene(image)

        elif request.task == 'read_text':
            if not image:
                raise HTTPException(status_code=400, detail="Image data is required for read_text")
            ocr_results = ocr_service.read(np.array(image))
            result_text = " ".join([res['text'] for res in ocr_results]) if ocr_results else "No text found."
            structured_data = {"ocr_results": ocr_results}

        elif request.task == 'find_object':
            if not image:
                raise HTTPException(status_code=400, detail="Image data is required for find_object")
            
            # The new object detector finds all objects. We decide how to report them.
            detected_objects = object_service.detect(np.array(image))

            # --- New Logic: Find a SPECIFIC personal object ---
            if request.query_text:
                target_object_name = request.query_text.lower()
                
                # 1. Get the learned embedding for the target object
                learned_object = db_manager.get_personal_object_by_name(target_object_name)
                if not learned_object:
                    result_text = f"I haven't learned what '{target_object_name}' looks like yet. Please show it to me first."
                else:
                    learned_embedding = learned_object['embedding']
                    found_match = False
                    
                    # 2. Compare against all detected objects in the scene
                    best_match_score = 0
                    best_match_object = None

                    for detected_obj in detected_objects:
                        # Crop the image to the detected object's bounding box
                        box = detected_obj['box']
                        cropped_image = image.crop((box[0], box[1], box[2], box[3]))
                        
                        # Get embedding for the cropped object
                        current_embedding = vision_service.get_image_embedding(cropped_image)
                        if not current_embedding:
                            continue

                        # Calculate similarity
                        similarity = calculate_cosine_similarity(learned_embedding, current_embedding)
                        
                        if similarity > best_match_score:
                            best_match_score = similarity
                            best_match_object = detected_obj

                    # 3. Report the best match if it's above a threshold
                    SIMILARITY_THRESHOLD = 0.85 # This may need tuning
                    if best_match_score > SIMILARITY_THRESHOLD:
                        found_match = True
                        # We can add directional info later (e.g., "to your left")
                        result_text = f"I found your {target_object_name}! It is about {best_match_object['depth_m']:.1f} meters away."
                        structured_data = {"found_object": best_match_object}
                    
                    if not found_match:
                        result_text = f"I looked, but I could not find your '{target_object_name}' in the current view."

            # --- Old Logic: General object detection ---
            else:
                if detected_objects:
                    summary = []
                    for obj in detected_objects[:5]: # Report top 5
                        summary.append(f"{obj['name']} at {obj['depth_m']:.1f} meters")
                    result_text = "I see: " + ", ".join(summary)
                else:
                    result_text = "I could not detect any objects."
                structured_data = {"objects": detected_objects}

        elif request.task == 'answer_question':
            if not image or not request.query_text:
                raise HTTPException(status_code=400, detail="Image data and query_text are required")
            result_text = vision_service.answer_question(image, request.query_text)

        elif request.task == 'recognize_face':
            if not image:
                raise HTTPException(status_code=400, detail="Image data is required for recognize_face")
            recognized_persons = face_service.recognize(np.array(image))
            if recognized_persons:
                known_persons = [p['name'] for p in recognized_persons if p['name'] != 'Unknown']
                if known_persons:
                    result_text = f"Detected persons: {', '.join(known_persons)}"
                else:
                    result_text = "I see a face, but I don't recognize them."
            else:
                result_text = "No faces detected."
            structured_data = {"faces": recognized_persons}

        elif request.task == 'save_face':
            if not image or not request.query_text:
                raise HTTPException(status_code=400, detail="Image and a name (in query_text) are required to save a face.")
            success = face_service.save_face(request.query_text, np.array(image))
            if success:
                result_text = f"Successfully saved face for {request.query_text}."
            else:
                result_text = f"Could not save face for {request.query_text}. Make sure a face is clearly visible."

        elif request.task == 'learn_personal_object':
            if not image or not request.query_text:
                raise HTTPException(status_code=400, detail="Image and a name (in query_text) are required to learn an object.")
            
            # 1. Get the embedding for the object in the image
            embedding = vision_service.get_image_embedding(image)
            if not embedding:
                raise HTTPException(status_code=500, detail="Could not generate an embedding for the image.")

            # 2. Save the embedding to the database
            success = db_manager.learn_personal_object(request.query_text, embedding)
            if success:
                result_text = f"I've learned what '{request.query_text}' looks like."
            else:
                result_text = f"Sorry, I had a problem learning '{request.query_text}'."

        else:
            raise HTTPException(status_code=400, detail="Invalid task")
            
    except HTTPException:
        # Re-raise HTTP errors raised intentionally above so they keep their original status codes
        raise
    except Exception as e:
        import traceback
        traceback_str = traceback.format_exc()
        print(f"Unexpected error in /process_data: {traceback_str}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

    if not result_text and not immediate_alert:
        result_text = "I'm sorry, I couldn't process the request."

    return ProcessResponse(result_text=result_text, structured_data=structured_data, immediate_alert=immediate_alert)

# --- Refactored Endpoint for Proactive Event Analysis ---
@app.post("/analyze_event", response_model=AnalyzeEventResponse)
async def analyze_event(
    event_type: str = Form(...),
    timestamp_utc: str = Form(...),
    video_format: str = Form(...),
    video_file: UploadFile = File(...)
):
    """
    Receives a video clip via multipart/form-data, analyzes it for significant events,
    and returns a simple alert text.
    """
    import uuid
    import os
    
    # Although not in the response model, event_id is needed for feedback logging
    event_id = str(uuid.uuid4())
    temp_video_path = f"temp_event_{event_id}.{video_format}"
    
    try:
        # Save the uploaded video file temporarily
        video_bytes = await video_file.read()
        with open(temp_video_path, "wb") as f:
            f.write(video_bytes)
            
        # Analyze the video using the agent service
        # The agent now needs to know the timestamp for logging
        analysis_result = agent_service.analyze_video_event(
            video_path=temp_video_path,
            timestamp_utc=timestamp_utc
        )
        
        # The agent service directly returns the alert text
        alert_text = analysis_result.get("alert_text", "")
        
        return AnalyzeEventResponse(alert_text=alert_text)

    except HTTPException:
        # Re-raise intentional HTTPExceptions
        raise
    except Exception as e:
        import traceback
        traceback_str = traceback.format_exc()
        print(f"Unexpected error in /analyze_event: {traceback_str}")
        # Ensure cleanup happens even if there's an error
        raise HTTPException(status_code=500, detail=f"Error analyzing event: {e}")
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_video_path):
            os.remove(temp_video_path)

# --- New Endpoint for Detailed AI Correction Feedback ---
@app.post("/submit_feedback")
async def submit_feedback(request: SubmitFeedbackRequest):
    """
    Receives detailed feedback from a user about an incorrect AI response.
    """
    try:
        # We need to link this feedback to an event. The client might send
        # an event_id from a proactive alert, or the image from a reactive task.
        # For now, we'll pass event_id directly if it exists.
        # A more robust solution might involve storing the image and generating an ID.
        
        event_identifier = request.event_id or f"img_{request.timestamp_utc}"

        feedback_id = db_manager.add_ai_correction_feedback(
            event_id=event_identifier,
            incorrect_ai_response=request.incorrect_ai_response,
            user_correction_text=request.user_correction_text,
            timestamp_utc=request.timestamp_utc
        )
        
        if feedback_id:
            return {"status": "Feedback submitted successfully", "feedback_id": feedback_id}
        else:
            raise HTTPException(status_code=500, detail="Failed to store feedback.")

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback_str = traceback.format_exc()
        print(f"Unexpected error in /submit_feedback: {traceback_str}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")


# --- New Endpoint for Voice-Based Feedback ---
@app.post("/feedback")
async def receive_feedback(request: FeedbackRequest):
    """
    Receives user feedback on a proactive alert and logs it to the database.
    """
    try:
        timestamp = datetime.datetime.utcnow().isoformat()
        feedback_id = db_manager.add_feedback(
            event_id=request.event_id,
            feedback=request.feedback,
            timestamp=timestamp
        )
        print(f"Logged feedback {feedback_id} for event {request.event_id}: {request.feedback}")
        return {"status": "Feedback received successfully"}
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback_str = traceback.format_exc()
        print(f"Unexpected error in /feedback: {traceback_str}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
