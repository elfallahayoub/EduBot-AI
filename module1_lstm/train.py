import numpy as np
import json
import pickle
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from model import construire_lstm, get_callbacks, afficher_infos


# Load dataset
with open("dataset_complet.json", "r", encoding="utf-8") as f:
    dataset = json.load(f)

phrases    = []
intentions = []

for intention, exemples in dataset.items():
    for phrase in exemples:
        phrases.append(phrase)
        intentions.append(intention)

print(f"{len(phrases):,} phrases chargees")

# Shuffle before splitting to avoid label ordering bias
combined = list(zip(phrases, intentions))
np.random.shuffle(combined)
phrases, intentions = zip(*combined)
phrases    = list(phrases)
intentions = list(intentions)

# Tokenize
tokenizer = Tokenizer(num_words=2000, oov_token="<OOV>")
tokenizer.fit_on_texts(phrases)
sequences = tokenizer.texts_to_sequences(phrases)
X = pad_sequences(sequences, maxlen=20, padding='post')

le = LabelEncoder()
y  = le.fit_transform(intentions)

print(f"Vocabulaire : {len(tokenizer.word_index) + 1} mots")
print(f"Classes     : {list(le.classes_)}")

# Split 70% train / 15% validation / 15% test
X_train, X_temp, y_train, y_temp = train_test_split(
    X, y, test_size=0.30, random_state=42, stratify=y
)
X_val, X_test, y_val, y_test = train_test_split(
    X_temp, y_temp, test_size=0.50, random_state=42, stratify=y_temp
)

total = len(X)
print(f"Train      : {len(X_train):,} ({len(X_train)/total*100:.0f}%)")
print(f"Validation : {len(X_val):,}  ({len(X_val)/total*100:.0f}%)")
print(f"Test       : {len(X_test):,}  ({len(X_test)/total*100:.0f}%)")

# Build model
taille_vocab  = len(tokenizer.word_index) + 1
nb_intentions = len(le.classes_)

model = construire_lstm(taille_vocab, nb_intentions)
afficher_infos(model)

# Train
history = model.fit(
    X_train, y_train,
    epochs=70,
    batch_size=300,
    validation_data=(X_val, y_val),
    callbacks=get_callbacks(),
    verbose=1,
    shuffle=True
)

# Final evaluation on held-out test set
loss, acc = model.evaluate(X_test, y_test, verbose=0)
print(f"Precision finale : {acc*100:.2f}%")
print(f"Loss finale      : {loss:.4f}")

# Save model and preprocessing artifacts
model.save('edubot_lstm.keras')

with open('tokenizer.pkl', 'wb') as f:
    pickle.dump(tokenizer, f)

with open('label_encoder.pkl', 'wb') as f:
    pickle.dump(le, f)

print("Sauvegarde : edubot_lstm.keras | tokenizer.pkl | label_encoder.pkl")
