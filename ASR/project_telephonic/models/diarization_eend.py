# project_telephonic/models/diarization_eend.py
import logging
from pyannote.audio import Pipeline
from project_telephonic.config import EEND_MODEL_ID, HF_TOKEN

"""
A placeholder for using an overlap-aware EEND approach.
pyannote/speaker-diarization-3.1 is already an EEND-like pipeline that can handle overlaps.
To truly integrate SA-EEND or EEND-SAD, you may need specialized code.
Below is a minimal usage of the pyannote pipeline with forced two-speaker if needed.
"""

class EENDDiarizationModel:
    def __init__(self, min_speakers=None, max_speakers=None):
        self.min_speakers = min_speakers
        self.max_speakers = max_speakers
        self.pipeline = self.load_model()

    def load_model(self):
        logging.info("Loading EEND diarization pipeline '%s'...", EEND_MODEL_ID)
        diar_pipeline = Pipeline.from_pretrained(
            EEND_MODEL_ID,
            use_auth_token=HF_TOKEN
        )
        logging.info("Diarization pipeline loaded successfully.")
        return diar_pipeline

    def diarize(self, wav_file: str):
        logging.info("Running EEND diarization on '%s'...", wav_file)
        # Force two speakers if you always expect exactly 2 on telephonic calls:
        result = self.pipeline(
            {"audio": wav_file},
            min_speakers=self.min_speakers or 2,
            max_speakers=self.max_speakers or 2
        )
        logging.info("EEND diarization completed.")
        return result
