# ml_model.py
import joblib
import os

# Load the pre-trained model (once saved)
MODEL_PATH = "duration_model.pkl"

def load_model():
    if os.path.exists(MODEL_PATH):
        return joblib.load(MODEL_PATH)
    else:
        raise FileNotFoundError("Model not found. Train and save it first.")

def predict_duration(task_name):
    model = load_model()
    prediction = model.predict([task_name])
    return max(1, round(prediction[0], 1))  # Duration in hours
