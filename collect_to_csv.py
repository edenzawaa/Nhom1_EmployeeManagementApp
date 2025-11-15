import cv2
import os
import time
from deepface import DeepFace
import csv

# --- Configuration ---
CSV_FILE = "face_embeddings.csv"
NUM_IMAGES_PER_PERSON = 5
MODEL_NAME = "ArcFace"
VECTOR_LENGTH = 512
# --- THIS IS THE FIX ---
# We will use the powerful 'mtcnn' detector for the REAL encoding
DETECTOR_BACKEND = "mtcnn" 

# --- Initialize CSV ---
def initialize_csv(file_path):
    if not os.path.exists(file_path):
        headers = ['label'] + [f'vec_{i}' for i in range(VECTOR_LENGTH)]
        with open(file_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
    print(f"Using CSV file: {file_path}")

# --- Get User Name (Replaced tkinter) ---
def get_user_name():
    name = input("Enter name for this person: ")
    if name:
        return "_".join(name.strip().split())
    else:
        return None

# --- Main ---
initialize_csv(CSV_FILE)

try:
    print(f"Building and loading model: {MODEL_NAME}...")
    DeepFace.build_model(MODEL_NAME)
    print("Model built successfully.")
except Exception as e:
    print(f"CRITICAL ERROR: Could not build model. {e}")
    exit()

# --- Get user name from terminal BEFORE opening the camera ---
user_name = get_user_name()

if not user_name:
    print("No name entered. Exiting.")
    exit()

cap = cv2.VideoCapture(0)
print(f"--- Enrolling new person: {user_name} ---")
print("Position your face in the box and press 'c' to capture.")
print("!!! IMPORTANT: Make sure your face is well-lit and centered. !!!")

frames_recorded = 0
# This 'haar_cascade' is ONLY for the fast PREVIEW box.
# It is NOT used for the final, high-quality encoding.
preview_detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

while cap.isOpened() and frames_recorded < NUM_IMAGES_PER_PERSON:
    success, frame = cap.read()
    if not success:
        continue

    image_to_show = frame.copy()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # This just draws the "guide" box
    faces = preview_detector.detectMultiScale(gray, 1.3, 5)

    cv2.putText(image_to_show, "Press 'c' to capture, 'q' to quit", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    status_text = f"Capture {frames_recorded + 1} of {NUM_IMAGES_PER_PERSON}"
    cv2.putText(image_to_show, status_text, (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    if len(faces) > 0:
        (x, y, w, h) = faces[0]
        cv2.rectangle(image_to_show, (x, y), (x+w, y+h), (0, 255, 0), 2) # The guide box

    cv2.imshow('Manual Enrollment (MTCNN)', image_to_show)
    key = cv2.waitKey(5) & 0xFF

    if key == ord('q'):
        break
    
    if key == ord('c'):
        # We don't care if the 'preview' detector saw a face.
        # We will now run the HEAVY, ACCURATE detector.
            
        print(f"Capturing image {frames_recorded + 1}...")
        
        try:
            # --- THIS IS THE ROBUST LOGIC ---
            # We pass the ENTIRE frame to DeepFace
            # We command it to use the powerful 'mtcnn' detector
            embedding_objs = DeepFace.represent(
                img_path=frame,  # <-- Pass the FULL color frame
                model_name=MODEL_NAME,
                enforce_detection=True, # Force it to find a face
                detector_backend=DETECTOR_BACKEND # Use 'mtcnn'
            )
            
            # mtcnn will find the best face, ArcFace will encode it.
            embedding = embedding_objs[0]["embedding"]
            
            with open(CSV_FILE, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([user_name] + embedding)
            
            frames_recorded += 1
            print(f"Saved! {NUM_IMAGES_PER_PERSON - frames_recorded} remaining.")
            print("Please change your pose slightly and press 'c' again.")
            time.sleep(1.0) # Pause to avoid double capture

        except ValueError as e:
            # This will print "Face could not be detected" if mtcnn fails
            print(f"Capture failed: {e}. Try better lighting or a clearer position.")
        except Exception as e:
            print(f"An error occurred: {e}")

print(f"Enrollment complete for {user_name}.")
cap.release()
cv2.destroyAllWindows()