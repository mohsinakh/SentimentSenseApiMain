import cv2,base64,uuid,asyncio
import numpy as np
import logging
from fastapi import WebSocket, WebSocketDisconnect, APIRouter ,HTTPException,BackgroundTasks
from pathlib import Path
import os,time
import tensorflow as tf
from fastapi.responses import JSONResponse,FileResponse
from pydantic import BaseModel


TIMEOUT = 5


router = APIRouter(prefix="/emotion", tags=["emotion"])
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class EmotionDetector:
    def __init__(self):
        self.model = None
        self.class_names = ['Angry', 'Disgusted', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.model_path = Path(__file__).parent.parent / "models" / "face_model.h5"

    def initialize(self):
        if self.model is None:
            try:
                self.model = tf.keras.models.load_model(str(self.model_path), compile=False)
                logger.info("✅ Model loaded successfully.")
            except Exception as e:
                logger.error(f"❌ Model loading failed: {str(e)}")
                raise

    def predict(self, face_image):
        if self.model is None:
            raise Exception("Model not loaded.")

        face_image = np.expand_dims(face_image, axis=0)  # Reshape for model input
        predictions = self.model.predict(face_image)
        emotion = self.class_names[np.argmax(predictions)]  
        return emotion
    



emotion_detector = EmotionDetector()
emotion_detector.initialize()  # Load model at startup

@router.websocket("/detection/")
async def emotion_detection(websocket: WebSocket):
    await websocket.accept()
    logger.info("✅ WebSocket connection accepted.")

    try:
        while True:
            data = await websocket.receive_bytes()
            frame = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
            if frame is None:
                continue

            # Resize to speed up face detection
            small_frame = cv2.resize(frame, (320, 240))  
            gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
            faces = emotion_detector.face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(30, 30))

            emotions = []
            for (x, y, w, h) in faces:
                face_roi = small_frame[y:y+h, x:x+w]
                face_image = cv2.resize(face_roi, (48, 48))
                face_image = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
                face_image = np.expand_dims(face_image, axis=0)

                prediction = emotion_detector.model.predict(face_image)
                detected_emotion = emotion_detector.class_names[np.argmax(prediction)]
                emotions.append(detected_emotion)

                # Draw rectangles and label faces
                cv2.rectangle(frame, (x*2, y*2), (x*2 + w*2, y*2 + h*2), (0, 255, 0), 2)
                cv2.putText(frame, detected_emotion, (x*2, y*2 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            # Convert frame to JPEG for faster transmission
            _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
            await websocket.send_bytes(buffer.tobytes())
            await websocket.send_json({"emotions": emotions, "timestamp": time.time()})

    except WebSocketDisconnect:
        logger.info("🔌 Client disconnected.")
    except Exception as e:
        logger.error(f"❌ WebSocket error: {str(e)}")





# Define the request body model
class ImageRequest(BaseModel):
    base64_image: str



# HTTP route for emotion detection from base64 image
@router.post("/detect-from-image/")
async def detect_emotions_from_base64(request: ImageRequest):
    try:
        base64_image = request.base64_image

        emotion_detector.initialize()


        # Decode base64 string into bytes
        image_data = base64.b64decode(base64_image)
        nparr = np.frombuffer(image_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if frame is None:
            logger.error("❌ Image could not be decoded.")
            return JSONResponse(status_code=400, content={"error": "Image could not be decoded"})

        # Convert to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = emotion_detector.face_cascade.detectMultiScale(
            gray, scaleFactor=1.3, minNeighbors=5, minSize=(30, 30)
        )

        if len(faces) == 0:
            logger.info("👤 No faces detected in the image.")
            return JSONResponse(status_code=200, content={"emotions": []})

        emotions = []
        for (x, y, w, h) in faces:
            try:
                face_roi = frame[y:y+h, x:x+w]
                face_image = cv2.resize(face_roi, (48, 48))
                face_image = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
                face_image = np.expand_dims(face_image, axis=0)

                # Predict emotions
                predictions = emotion_detector.model.predict(face_image)
                emotion = emotion_detector.class_names[np.argmax(predictions)]
                emotions.append(emotion)

            except Exception as e:
                logger.error(f"❌ Face processing error: {str(e)}")
                continue

        # Return the detected emotions
        return JSONResponse(status_code=200, content={"emotions": emotions})

    except Exception as e:
        logger.error(f"❌ Error processing image: {str(e)}")
        return JSONResponse(status_code=500, content={"error": "Error processing image"})
    




class VideoRequest(BaseModel):
    base64_video: str

async def process_video(background_tasks: BackgroundTasks, base64_video: str):
    try:
        # Decode base64 video
        video_data = base64.b64decode(base64_video)
        unique_id = str(uuid.uuid4())
        tmp_video_path = f"temp_{unique_id}.mp4"
        processed_video_path = f"processed_{unique_id}.mp4"

        # Save uploaded video
        with open(tmp_video_path, "wb") as tmp_video_file:
            tmp_video_file.write(video_data)

        cap = cv2.VideoCapture(tmp_video_path)
        if not cap.isOpened():
            raise HTTPException(status_code=400, detail="Error opening video file")

        # Reduce FPS for optimization
        target_fps = 10  # Lower FPS to optimize performance
        original_fps = cap.get(cv2.CAP_PROP_FPS)
        frame_skip = int(original_fps / target_fps) if original_fps > target_fps else 1

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(processed_video_path, fourcc, target_fps, (640, 480))

        frame_count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Process every nth frame to reduce FPS
            if frame_count % frame_skip == 0:
                frame_resized = cv2.resize(frame, (640, 480))
                gray = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)
                
                # Detect faces
                faces = emotion_detector.face_cascade.detectMultiScale(gray, 1.3, 5)
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame_resized, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    face_roi = frame_resized[y:y + h, x:x + w]
                    face_image = cv2.resize(face_roi, (48, 48))
                    face_image = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
                    face_image = np.expand_dims(face_image, axis=0)

                    # Predict emotion
                    predictions = emotion_detector.model.predict(face_image)
                    emotion = emotion_detector.class_names[np.argmax(predictions)]

                    # Display emotion
                    cv2.putText(frame_resized, emotion, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

                out.write(frame_resized)

            frame_count += 1

        cap.release()
        out.release()
        os.remove(tmp_video_path)

        # Schedule deletion of processed video
        background_tasks.add_task(delete_file_with_delay, processed_video_path)

        return processed_video_path

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing video: {str(e)}")


async def delete_file_with_delay(file_path: str):
    await asyncio.sleep(30)
    if os.path.exists(file_path):
        os.remove(file_path)

@router.post("/detect-from-video/")
async def detect_emotions_from_video(request: VideoRequest, background_tasks: BackgroundTasks):
    processed_video_path = await process_video(background_tasks, request.base64_video)
    return FileResponse(processed_video_path, media_type="video/mp4", filename="processed_video.mp4")
