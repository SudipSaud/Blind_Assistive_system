"""
Object Detection Module - YOLOv9 + MIDAS Depth Estimation
"""

import cv2
import numpy as np
import torch
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class YOLOv9ObstacleDetector:
    """Enhanced object detection using YOLOv9 + MIDAS depth estimation"""
    
    def __init__(self):
        self.yolo_model = None
        self.midas_model = None
        self.midas_transform = None
        self.cap = None
        self.device = None
        self.is_initialized = False
        
    def initialize(self) -> bool:
        """Initialize YOLOv9 and MIDAS models"""
        try:
            from ultralytics import YOLO
            
            logger.info("Loading YOLOv9c model...")
            # Use YOLOv9c model as in the repository
            self.yolo_model = YOLO('yolov9c.pt')
            logger.info("YOLOv9c model loaded successfully")
            
            # Initialize MIDAS depth estimation
            logger.info("Loading MIDAS DPT_Large model...")
            model_type = "DPT_Large"
            self.midas_model = torch.hub.load("intel-isl/MiDaS", model_type)
            
            # Set device (CPU/GPU)
            self.device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
            self.midas_model.to(self.device)
            self.midas_model.eval()
            
            # Load MIDAS transforms
            midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms")
            if model_type == "DPT_Large" or model_type == "DPT_Hybrid":
                self.midas_transform = midas_transforms.dpt_transform
            else:
                self.midas_transform = midas_transforms.small_transform
            
            logger.info(f"MIDAS model loaded successfully on {self.device}")
            
            # Initialize camera
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                logger.error("Failed to open camera")
                return False
            
            # Optimize camera settings for performance
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            self.is_initialized = True
            logger.info("YOLOv9 + MIDAS obstacle detection initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing YOLOv9 + MIDAS: {e}")
            return False
    
    def calculate_object_depth(self, depth_map, x_min, y_min, x_max, y_max, confidence, confidence_threshold=0.7):
        """Calculate depth of detected object"""
        try:
            # Convert bounding box coordinates to integers
            x_min = int(x_min)
            y_min = int(y_min)
            x_max = int(x_max)
            y_max = int(y_max)

            # Check if confidence is above the threshold
            if confidence >= confidence_threshold:
                # Extract the depth values corresponding to the bounding box coordinates
                depth_values = depth_map[y_min:y_max, x_min:x_max]
                
                # Calculate the average depth value within the bounding box
                object_depth = np.mean(depth_values) if depth_values.size > 0 else 0
                return object_depth
            else:
                return 0
        except Exception as e:
            logger.error(f"Error calculating object depth: {e}")
            return 0
    
    def detect_objects(self) -> List[Dict[str, Any]]:
        """Detect objects with depth estimation and obstacle warnings"""
        try:
            if not self.cap or not self.cap.isOpened():
                return []
            
            ret, frame = self.cap.read()
            if not ret:
                return []
            
            objects = []
            obstacles = []
            
            # Create a copy of frame for display
            display_frame = frame.copy()
            
            # YOLOv9 object detection
            results = self.yolo_model(frame, imgsz=640, verbose=False)
            
            # Extract detection results
            boxes = results[0].boxes.xyxy.tolist() if results[0].boxes is not None else []
            classes = results[0].boxes.cls.tolist() if results[0].boxes is not None else []
            names = results[0].names
            confidences = results[0].boxes.conf.tolist() if results[0].boxes is not None else []
            
            # MIDAS depth estimation
            img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            input_batch = self.midas_transform(img_rgb).to(self.device)
            
            with torch.no_grad():
                prediction = self.midas_model(input_batch)
                prediction = torch.nn.functional.interpolate(
                    prediction.unsqueeze(1),
                    size=img_rgb.shape[:2],
                    mode="bicubic",
                    align_corners=False,
                ).squeeze()
            
            depth_map = prediction.cpu().numpy()
            
            # Process each detected object
            depth_threshold = 24  # Threshold distance in meters (as in repository)
            
            for box, cls, confidence in zip(boxes, classes, confidences):
                if confidence > 0.25:  # Lower confidence threshold for better detection
                    x1, y1, x2, y2 = map(int, box)
                    class_name = names.get(cls, f"Class {cls}")
                    
                    # Calculate object depth
                    object_depth = self.calculate_object_depth(depth_map, x1, y1, x2, y2, confidence)
                    
                    # Draw bounding box and label
                    color = (0, 255, 0)  # Green for normal objects
                    thickness = 2
                    cv2.rectangle(display_frame, (x1, y1), (x2, y2), color, thickness)
                    
                    # Add depth information to label
                    label = f"{class_name}: {confidence:.2f} (Depth: {object_depth:.1f})"
                    cv2.putText(display_frame, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                    
                    objects.append({
                        "name": class_name,
                        "confidence": confidence,
                        "bbox": [x1, y1, x2, y2],
                        "depth": object_depth
                    })
                    
                    # Check if object is too close (obstacle warning)
                    if object_depth > depth_threshold:
                        obstacles.append({
                            "name": class_name,
                            "depth": object_depth,
                            "warning": f"Warning! {class_name} is too close to you"
                        })
                        
                        # Draw red warning box for obstacles
                        cv2.rectangle(display_frame, (x1, y1), (x2, y2), (0, 0, 255), 3)  # Red for obstacles
                        cv2.putText(display_frame, "OBSTACLE!", (x1, y1-30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # Show camera window with detections (optional - handle OpenCV display errors)
            try:
                cv2.imshow("YOLOv9 + MIDAS Obstacle Detection", display_frame)
                cv2.waitKey(1)  # Non-blocking wait
            except Exception as display_error:
                # OpenCV display not available (common on Windows without GUI support)
                logger.debug(f"OpenCV display not available: {display_error}")
                # Continue without display - detection still works
            
            # Add obstacle warnings to objects list
            for obstacle in obstacles:
                objects.append({
                    "name": f"OBSTACLE: {obstacle['name']}",
                    "confidence": 1.0,
                    "bbox": [0, 0, 0, 0],
                    "depth": obstacle['depth'],
                    "warning": obstacle['warning']
                })
            
            return objects
            
        except Exception as e:
            logger.error(f"Error in YOLOv9 + MIDAS detection: {e}")
            return []
    
    def release(self):
        """Release resources"""
        if self.cap:
            self.cap.release()
        try:
            cv2.destroyAllWindows()  # Close all OpenCV windows
        except Exception as e:
            logger.debug(f"OpenCV window cleanup not available: {e}")
        self.is_initialized = False
        logger.info("YOLOv9 + MIDAS obstacle detection resources released")

