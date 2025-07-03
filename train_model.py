# train_model.py
import pandas as pd
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
import joblib

# Task templates
tasks = [
    ("prepare for exam", 3),
    ("study data structures", 4),
    ("complete thesis", 12),
    ("write report", 6),
    ("make presentation", 4),
    ("revise for test", 2),
    ("project documentation", 5),
    ("code final project", 8),
    ("read research paper", 3),
    ("debug code", 2),
    ("practice interview", 3),
    ("record presentation", 1),
    ("edit thesis", 7),
    ("design poster", 2),
    ("analyze results", 4),
    ("work on literature review", 6),
    ("review notes", 2),
    ("draft research proposal", 5),
    ("prepare viva questions", 3),
    ("build prototype", 9),
]

# Generate data
data = []
for _ in range(500):
    task, base = random.choice(tasks)
    noise = random.uniform(-1.0, 1.5)
    final = max(1, round(base + noise, 1))
    data.append((task, final))

df = pd.DataFrame(data, columns=["task", "duration"])

# Train model
pipeline = Pipeline([
    ("tfidf", TfidfVectorizer()),
    ("regressor", LinearRegression())
])

pipeline.fit(df["task"], df["duration"])

# Save model
joblib.dump(pipeline, "duration_model.pkl")
print("Model trained and saved as duration_model.pkl")
