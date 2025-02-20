# project_telephonic/processors/eend_segmenter.py
"""
Example of a specialized "EENDSegmenter" that uses the EENDDiarizationModel
to create speaker-labeled segments, handling overlaps if they exist.
"""
import logging

class EENDSegmenter:
    def __init__(self, eend_model):
        self.eend_model = eend_model

    def segment(self, wav_file: str):
        logging.info("Running EEND-based segmentation on '%s'...", wav_file)
        diarization_result = self.eend_model.diarize(wav_file)
        # You can do additional overlap merging or keep them separate

        segments = []
        # Extract segments from the diarization_result
        for turn, _, speaker in diarization_result.itertracks(yield_label=True):
            # Overlap is possible; some frameworks store them differently
            segments.append({
                "type": "speech",
                "start": turn.start,
                "end": turn.end,
                "speaker": speaker
            })
        return segments
