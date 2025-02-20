# project_telephonic/models/vad.py
import logging
from pyannote.audio import Pipeline
from project_telephonic.config import HF_TOKEN, VAD_MODEL_ID
from pydub import AudioSegment

class VADModel:
    """
    Use a PyAnnote VAD pipeline to detect speech vs. silence.
    We can then split audio on these boundaries for sub-chunks.
    """
    def __init__(self):
        self.pipeline = self.load_model()

    def load_model(self):
        logging.info("Loading VAD pipeline '%s'...", VAD_MODEL_ID)
        vad_pipeline = Pipeline.from_pretrained(
            VAD_MODEL_ID,
            use_auth_token=HF_TOKEN
        )
        logging.info("VAD pipeline loaded successfully.")
        return vad_pipeline

    def apply_vad(self, wav_file: str):
        logging.info("Applying VAD on '%s'...", wav_file)
        result = self.pipeline({"audio": wav_file})
        audio = AudioSegment.from_file(wav_file)
        duration_sec = len(audio) / 1000.0

        segments = []
        for segment, _, label in result.itertracks(yield_label=True):
            if label == "SPEECH":
                segments.append({
                    "type": "speech",
                    "start": segment.start,
                    "end": segment.end
                })

        # If no speech is found, label entire audio as silence
        if not segments:
            return [{
                "type": "silence",
                "start": 0.0,
                "end": duration_sec
            }]

        # Merge / fill gaps for final segment list
        segments.sort(key=lambda x: x["start"])
        final_segments = []

        # leading silence
        if segments[0]["start"] > 0:
            final_segments.append({
                "type": "silence",
                "start": 0.0,
                "end": segments[0]["start"]
            })

        for i, seg in enumerate(segments):
            final_segments.append(seg)
            if i < len(segments) - 1:
                gap_start = seg["end"]
                gap_end = segments[i+1]["start"]
                if gap_end > gap_start:
                    final_segments.append({
                        "type": "silence",
                        "start": gap_start,
                        "end": gap_end
                    })

        # trailing silence
        if segments[-1]["end"] < duration_sec:
            final_segments.append({
                "type": "silence",
                "start": segments[-1]["end"],
                "end": duration_sec
            })

        logging.info("VAD produced %d segments.", len(final_segments))
        return final_segments
