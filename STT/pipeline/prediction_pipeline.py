
import os, sys
import tensorflow as tf

from STT.models.model import Transformer
from STT.utils import path_to_audio
from STT.models.data_utils import VectorizeChar
from STT.constants import MAX_TARGET_LENGTH
from STT.logger import logging
from STT.exceptions import STTException


def calculate_wer(reference, prediction):
    """
    Calculate the Word Error Rate (WER) between the reference and the prediction.
    WER is the number of word-level errors divided by the total number of words in the reference.

    Args:
        reference (str): The ground truth transcription.
        prediction (str): The model's predicted transcription.

    Returns:
        float: The WER for the given reference and prediction.
    """
    # Split the reference and prediction into words
    reference_words = reference.split()
    prediction_words = prediction.split()

    # Create a matrix to calculate the Levenshtein distance
    d = [[0] * (len(prediction_words) + 1) for _ in range(len(reference_words) + 1)]

    # Initialize the matrix
    for i in range(len(reference_words) + 1):
        d[i][0] = i
    for j in range(len(prediction_words) + 1):
        d[0][j] = j

    # Populate the matrix
    for i in range(1, len(reference_words) + 1):
        for j in range(1, len(prediction_words) + 1):
            if reference_words[i - 1] == prediction_words[j - 1]:
                d[i][j] = d[i - 1][j - 1]
            else:
                d[i][j] = min(
                    d[i - 1][j] + 1,     # deletion
                    d[i][j - 1] + 1,     # insertion
                    d[i - 1][j - 1] + 1  # substitution
                )

    # The WER is the total edit distance divided by the number of words in the reference
    wer = d[-1][-1] / len(reference_words)
    return wer
class Prediction:
    def __init__(self, audio_path, model_path, reference_text):
        try:
            self.vectorizer = VectorizeChar(MAX_TARGET_LENGTH)
            self.audio_path = audio_path
            self.model_path = model_path
            self.reference_text = reference_text  # Reference transcription for WER calculation
        except Exception as e:
            raise STTException(e, sys)
    
    def prediction(self):
        try:
            idx_to_char = self.vectorizer.get_vocabulary()

            logging.info("Vocabulary created")

            model = Transformer(
                num_hid=200,
                num_head=2,
                num_feed_forward=400,
                target_maxlen=MAX_TARGET_LENGTH,
                num_layers_enc=4,
                num_layers_dec=1,
                num_classes=34,
            )

            logging.info("Model instance created")

            model.load_weights(self.model_path)
            logging.info("Model weights loaded")

            # Load and process the audio to make predictions
            audio_features = tf.expand_dims(path_to_audio(path=self.audio_path), axis=0)
            preds = model.generate(audio_features, target_start_token_idx=2)

            preds = preds.numpy()

            # Convert prediction indices to characters
            prediction = ""
            for idx in preds[0]:
                prediction += idx_to_char[idx]
                if idx_to_char[idx] == '>':
                    break
            
            logging.info("Prediction completed")
            
            # Calculate WER
            wer = calculate_wer(self.reference_text, prediction)
            logging.info(f"Word Error Rate (WER): {wer}")

            return str(prediction), wer
        except Exception as e:
            raise STTException(e, sys)
        

