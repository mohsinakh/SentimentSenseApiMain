from tensorflow.keras.models import load_model, save_model

model = load_model("/Users/mohsinabbas/Downloads/code/Main Project/backend copy/API/models/face_model.h5")
save_model(model, "/Users/mohsinabbas/Downloads/code/Main Project/backend copy/API/models/emotion_model.h5", include_optimizer=False)
