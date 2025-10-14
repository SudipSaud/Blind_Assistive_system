"""
Object Detection Module - YOLOv9 + MIDAS Depth Estimation
"""
import cv2
import numpy as np
import torch
import logging
from typing import List, Dict, Any
from ultralytics import YOLO
from config import YOLO_MODEL_PATH, MIDAS_MODEL_TYPE

logger = logging.getLogger(__name__)

class ObjectDetector:
    def __init__(self):
        self.yolo_model = None
        self.midas_model = None
        self.midas_transform = None
        self.device = None
        self.is_initialized = False

    def load_model(self):
        """Initialize YOLOv9 and MIDAS models"""
        if self.is_initialized:
            return
        try:
            logger.info(f"Loading YOLO model from {YOLO_MODEL_PATH}...")
            self.yolo_model = YOLO(YOLO_MODEL_PATH)
            logger.info("YOLO model loaded successfully")

            logger.info(f"Loading MIDAS {MIDAS_MODEL_TYPE} model...")
            self.device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
            self.midas_model = torch.hub.load("intel-isl/MiDaS", MIDAS_MODEL_TYPE, trust_repo=True).to(self.device)
            self.midas_model.eval()

            midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms", trust_repo=True)
            self.midas_transform = midas_transforms.dpt_transform if MIDAS_MODEL_TYPE in ["DPT_Large", "DPT_Hybrid"] else midas_transforms.small_transform
            
            logger.info(f"MIDAS model loaded successfully on {self.device}")
            self.is_initialized = True
            logger.info("ObjectDetector initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing ObjectDetector: {e}")
            self.is_initialized = False

    def check_for_immediate_threats(self, frame: np.ndarray, threat_distance: float = 1.0) -> tuple[bool, float]:
        """
        A high-speed, low-latency check for immediate obstacles using only the depth map.
        This is the "Fast Path" for safety.
        Returns a tuple: (is_threat, distance_of_closest_threat)
        """
        if not self.is_initialized:
            return False, float('inf')

        try:
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

            # Find the minimum depth value in the central region of the map
            h, w = depth_map.shape
            center_w_start = int(w * 0.25)
            center_w_end = int(w * 0.75)
            center_region = depth_map[:, center_w_start:center_w_end]
            
            min_depth = np.min(center_region) if center_region.size > 0 else float('inf')

            # MiDaS outputs inverse depth, so a higher value means a closer object.
            # We need to convert this to real-world distance.
            # This is a placeholder conversion. A more accurate calibration would be needed.
            # For now, let's assume a simple inverse relationship for threat detection.
            # A more robust implementation would calibrate this value.
            # Let's find the minimum non-zero value to avoid division by zero
            min_inverse_depth = np.min(center_region[np.nonzero(center_region)])
            closest_distance = 1 / min_inverse_depth if min_inverse_depth > 0 else float('inf')

            # This is a simplified distance metric. For now, we'll use the raw output for comparison.
            # Let's find the closest point (highest value in inverse depth map)
            max_inverse_depth = np.max(depth_map) # Higher value = closer object
            
            # This threshold will need to be calibrated based on real-world testing.
            # Let's set a hypothetical threshold for now.
            # For DPT_Large, higher values are closer.
            THREAT_THRESHOLD = 10.0 # This is a guess and needs calibration.

            if max_inverse_depth > THREAT_THRESHOLD:
                # A more sophisticated approach would be to calculate the actual distance.
                # For now, we'll just signal a threat.
                # A proper distance calculation would be: distance = focal_length * real_height / pixel_height
                # Since we don't have that, we'll use the inverse depth value as a proxy.
                # Let's find the closest distance in meters for a more intuitive result.
                # The MiDaS output is not in meters. It's a relative inverse depth.
                # To get metric distance, we need a scale and shift factor, which are model-dependent.
                # output = scale * disparity + shift
                # For now, let's find the minimum value in the disparity map which corresponds to the farthest object
                # and the max value which is the closest.
                
                # Let's refine the logic. The output of MiDaS is a relative inverse depth map.
                # To get absolute distance, we need to calibrate.
                # However, for a simple threat detector, we can check if a significant portion
                # of the depth map is "close" (has a high value).
                
                h, w = depth_map.shape
                center_region = depth_map[int(h*0.3):int(h*0.7), int(w*0.3):int(w*0.7)]
                average_center_depth = np.mean(center_region)

                # This threshold is arbitrary and needs to be calibrated.
                # Let's assume a higher average value in the center means a large close object.
                if average_center_depth > 5.0: # Calibrate this value!
                    # For simplicity, we can't return meters yet without calibration.
                    # We will return the raw average depth value.
                    return True, average_center_depth

            return False, float('inf')

        except Exception as e:
            logger.error(f"Error in immediate threat check: {e}")
            return False, float('inf')

    def calculate_object_depth(self, depth_map, box):
        """Calculate depth of a detected object."""
        try:
            x1, y1, x2, y2 = map(int, box)
            depth_region = depth_map[y1:y2, x1:x2]
            return np.mean(depth_region) if depth_region.size > 0 else 0
        except Exception as e:
            logger.error(f"Error calculating object depth: {e}")
            return 0

    def detect(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """Detect objects with depth estimation."""
        if not self.is_initialized:
            return []
        
        try:
            # YOLOv9 object detection
            results = self.yolo_model(frame, imgsz=640, verbose=False)
            
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

            detected_objects = []
            boxes = results[0].boxes.xyxy.cpu().tolist()
            classes = results[0].boxes.cls.cpu().tolist()
            confidences = results[0].boxes.conf.cpu().tolist()
            names = results[0].names

            for box, cls, conf in zip(boxes, classes, confidences):
                if conf > 0.3:
                    depth = self.calculate_object_depth(depth_map, box)
                    detected_objects.append({
                        "name": names.get(cls, "Unknown"),
                        "confidence": conf,
                        "box": box,
                        "depth_m": float(depth) 
                    })
            
            return detected_objects
        except Exception as e:
            logger.error(f"Error in object detection: {e}")
            return []
