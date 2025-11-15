import cv2
import os
import csv
import numpy as np
from scipy.spatial.distance import cosine
from deepface import DeepFace
import math
import threading
import queue

# --- Configuration ---
CSV_FILE = "face_embeddings.csv"
MODEL_NAME = "ArcFace"
VECTOR_LENGTH = 512
THRESHOLD = 0.68  # ArcFace threshold
# This is the "lock-on" distance. If a face moves less than 75 pixels,
# we assume it's the same person and don't re-run recognition.
TRACKING_THRESHOLD = 75 

# --- Queues for Thread-Safe Communication ---
job_queue = queue.Queue(maxsize=1) 
result_queue = queue.Queue(maxsize=1)

# --- 1. Load Known Faces ---
def load_known_faces(csv_file):
    known_embeddings = []
    known_labels = []
    
    if not os.path.exists(csv_file):
        print(f"Error: CSV file not found at {csv_file}")
        return [], []

    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        try:
            # Try to read header to check for 'label'
            header = next(reader)
            if 'label' not in header[0]:
                print("No header found. Reading from start.")
                f.seek(0) # Rewind file to read first row as data
        except StopIteration:
            return [], [] # File is empty
            
        for row in reader:
            if not row: continue
            try:
                known_labels.append(row[0])
                embedding = np.array([float(x) for x in row[1:]])
                known_embeddings.append(embedding)
            except (IndexError, ValueError) as e:
                print(f"Skipping malformed row: {row}. Error: {e}")
                
    if not known_labels:
        print("CSV file was read, but no data was loaded.")
        print("Please delete the CSV and re-enroll faces.")
        return [], []

    # Verify vector length from the first loaded embedding
    if len(known_embeddings[0]) != VECTOR_LENGTH:
        print(f"CRITICAL ERROR: CSV vectors have {len(known_embeddings[0])} dims, but model needs {VECTOR_LENGTH}.")
        print("Please delete your CSV and re-enroll all users.")
        return [], []

    print(f"Loaded {len(known_labels)} known embeddings ({VECTOR_LENGTH}-dim) for {len(set(known_labels))} people.")
    return known_labels, known_embeddings

# --- 2. The Worker Thread Function (DeepFace) ---
def recognition_worker(known_labels, known_embeddings):
    """This function runs in the background thread."""
    try:
        DeepFace.build_model(MODEL_NAME)
        print("Recognition worker: Model built successfully.")
    except Exception as e:
        print(f"Worker Error: Could not build model. {e}")
        return

    while True:
        try:
            cropped_face, current_bbox = job_queue.get()

            embedding_objs = DeepFace.represent(
                img_path=cropped_face,
                model_name=MODEL_NAME,
                enforce_detection=False, # We already cropped it
                detector_backend='skip'    # Skip detection, just encode
            )
            
            live_encoding = embedding_objs[0]["embedding"]
            name = "Unknown"
            dist_str = ""

            distances = [cosine(live_encoding, known_vec) for known_vec in known_embeddings]
            
            best_match_index = np.argmin(distances)
            min_distance = distances[best_match_index]

            if min_distance <= THRESHOLD:
                name = known_labels[best_match_index]
            
            dist_str = f"({min_distance:.2f})"
            
            try: result_queue.get_nowait() 
            except queue.Empty: pass
            result_queue.put((name, dist_str, current_bbox))

        except Exception as e:
            # This 'e' often says 'Face could not be detected' if the crop is bad
            print(f"Worker error: {e}. Face might be too small or blurry.")
            try: result_queue.get_nowait() 
            except queue.Empty: pass
            result_queue.put(("Unknown", "(?)", current_bbox))

# --- Helper Functions ---
def get_box_center(bbox):
    x, y, w, h = bbox
    return (x + w / 2, y + h / 2)

def get_center_distance(center1, center2):
    return math.sqrt((center1[0] - center2[0])**2 + (center1[1] - center2[1])**2)

# --- 3. Initialize System ---
known_face_labels, known_face_embeddings = load_known_faces(CSV_FILE)
if not known_face_labels:
    print("No faces loaded from CSV. Exiting.")
    exit()

cap = cv2.VideoCapture(0)
# --- This is the OpenCV detector (replaces MediaPipe) ---
haar_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

### CONSISTENCY: These variables store the "locked-on" person
last_known_bbox = None
last_known_name = ""
last_known_distance_str = ""

# --- 4. Start the Worker Thread ---
worker_thread = threading.Thread(
    target=recognition_worker, 
    args=(known_face_labels, known_face_embeddings), 
    daemon=True
)
worker_thread.start()

# --- 5. Main Loop ---
print("Starting automatic recognition... Press 'q' to quit.")
while cap.isOpened():
    success, frame = cap.read()
    if not success:
        continue

    image_to_show = frame.copy()
    
    # --- Check for results from the worker ---
    try:
        ### CONSISTENCY: A new result just came in from the worker
        name, dist_str, bbox = result_queue.get_nowait()
        # We "lock on" to this new person
        last_known_name = name
        last_known_distance_str = dist_str
        last_known_bbox = bbox
        with job_queue.mutex:
            job_queue.queue.clear() # Clear old jobs
    except queue.Empty:
        pass # No new results, keep using the old "locked-on" name

    # --- 6. Run Fast Detection (Main Thread) ---
    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = haar_cascade.detectMultiScale(gray, 1.3, 5)

    current_face_found = False
    
    if len(faces) > 0:
        (x, y, w, h) = faces[0]
        
        padding_x = int(w * 0.1)
        padding_y = int(h * 0.2)
        x_pad = max(0, x - padding_x)
        y_pad = max(0, y - padding_y)
        w_pad = w + (padding_x * 2)
        h_pad = h + (padding_y * 2)
        
        current_bbox = (x_pad, y_pad, w_pad, h_pad)
        current_center = get_box_center(current_bbox)
        current_face_found = True
        
        is_tracked = False
        
        # --- 7. Tracking Logic (Main Thread) ---
        ### CONSISTENCY: This is the core logic you asked for
        if last_known_bbox is not None:
            last_center = get_box_center(last_known_bbox)
            dist = get_center_distance(current_center, last_center)
            
            # If the new face box is close to the old one...
            if dist < TRACKING_THRESHOLD:
                # ...we assume it's the same person.
                is_tracked = True
                last_known_bbox = current_bbox # Update the box position
                # We DO NOT send a new job. We keep the old name.

        # --- 8. Hand Off Job (Main Thread) ---
        # ### CONSISTENCY: We only run recognition if it's NOT tracked
        if not is_tracked:
            if job_queue.empty(): # Is the worker free?
                print("New face, sending to recognition worker...")
                
                (x,y,w,h) = current_bbox
                cropped_face = image_rgb[y:y+h, x:x+w]
                
                if cropped_face.size > 0:
                    job_queue.put((cropped_face, current_bbox))
                else:
                    print("Skipping empty crop.")
            
    if not current_face_found:
        ### CONSISTENCY: If the face disappears, clear the "lock"
        last_known_bbox = None
        last_known_name = ""

    # --- 9. Draw Last Known Result ---
    ### CONSISTENCY: This just draws the "locked-on" name every frame
    if last_known_name and last_known_bbox:
        (x, y, w, h) = last_known_bbox
        color = (0, 255, 0) if last_known_name != "Unknown" else (0, 0, 255)
        if last_known_name == "Error":
            color = (0, 255, 255) # Yellow for error
        
        cv2.rectangle(image_to_show, (x, y), (x + w, y + h), color, 2)
        label = f"{last_known_name} {last_known_distance_str}"
        cv2.putText(image_to_show, label, (x, y - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    cv2.imshow('Face Recognition', image_to_show)
    key = cv2.waitKey(5) & 0xFF
    
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()