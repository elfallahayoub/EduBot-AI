import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (
    Embedding, LSTM, Bidirectional,
    Dense, Dropout, BatchNormalization
)
from tensorflow.keras.callbacks import (
    EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
)
from tensorflow.keras.regularizers import l2


def construire_lstm(taille_vocabulaire, nb_intentions):
    model = Sequential([
        Embedding(
            input_dim=taille_vocabulaire,
            output_dim=16,
            embeddings_regularizer=l2(0.01)
        ),
        Bidirectional(
            LSTM(
                16,
                return_sequences=True,
                dropout=0.5,
                recurrent_dropout=0.3,
                kernel_regularizer=l2(0.01)
            )
        ),
        BatchNormalization(),
        LSTM(
            8,
            dropout=0.5,
            recurrent_dropout=0.3,
            kernel_regularizer=l2(0.01)
        ),
        BatchNormalization(),
        Dropout(0.5),
        Dense(16, activation='relu', kernel_regularizer=l2(0.01)),
        BatchNormalization(),
        Dropout(0.4),
        Dense(nb_intentions, activation='softmax')
    ])

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.0005),
        loss=tf.keras.losses.SparseCategoricalCrossentropy(),
        metrics=['accuracy']
    )

    return model


def get_callbacks():
    return [
        EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True,
            verbose=1,
            min_delta=0.001
        ),
        ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.3,
            patience=5,
            min_lr=1e-7,
            verbose=1
        ),
        ModelCheckpoint(
            filepath='best_model.keras',
            monitor='val_loss',
            save_best_only=True,
            verbose=1
        )
    ]


def afficher_infos(model):
    model.build(input_shape=(None, 20))
    model.summary()
    print(f"Parametres totaux : {model.count_params():,}")
