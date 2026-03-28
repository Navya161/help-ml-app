import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
import tensorflow as tf
from tensorflow.keras import layers

# dataset
data = {
    "fever":[1,0,1,1,0],
    "injury":[0,1,1,0,0],
    "bleeding":[0,1,1,0,0],
    "unconscious":[0,0,1,0,0],
    "breathing":[0,1,1,0,0],
    "text":["normal","minor injury","heavy bleeding","mild","normal"],
    "level":[0,1,2,0,0]
}

df = pd.DataFrame(data)

# NLP
vectorizer = CountVectorizer()
text_features = vectorizer.fit_transform(df["text"]).toarray()

# combine
symptoms = df[["fever","injury","bleeding","unconscious","breathing"]].values
X = np.concatenate((symptoms, text_features), axis=1)
y = df["level"].values

# model
model = tf.keras.Sequential([
    layers.Dense(16, activation='relu', input_shape=(X.shape[1],)),
    layers.Dense(3, activation='softmax')
])

model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

model.fit(X, y, epochs=20)

# save
model.save("model.h5")
import pickle

# save vectorizer
with open("vectorizer.pkl", "wb") as f:
    pickle.dump(vectorizer, f)