# project_telephonic/processors/audio_processor.py
import os
import logging
import threading
import json
from pydub import AudioSegment

from project_telephonic.config import (
    SAMPLE_RATE, SELECTED_WHISPER_MODEL,
    TEMP_OUTPUT_DIR
)
from project_telephonic.utils.file_utils import (
    convert_to_wav, remove_file, dump_temp, write_rttm
)
from project_telephonic.models.asr import ASRModel
from project_telephonic.models.diarization_eend import EENDDiarizationModel
from project_telephonic.models.vad import VADModel
from project_telephonic.processors.eend_segmenter import EENDSegmenter
from project_telephonic.processors.aligner import align_asr_to_diar

class AudioProcessor:
    def __init__(self, file_path: str, mode: str = "combined"):
        self.file_path = file_path
        self.mode = mode
        self.asr_model = ASRModel(SELECTED_WHISPER_MODEL)
        self.eend_model = EENDDiarizationModel()
        self.diar_result = None
        self.transcript_chunks = None

    def process(self):
        base_name = os.path.splitext(self.file_path)[0]
        wav_file = base_name + "_16k.wav"
        convert_to_wav(self.file_path, wav_file, SAMPLE_RATE)

        if self.mode == "diarization":
            segments = self.run_diarization(wav_file)
        elif self.mode == "transcription":
            segments = self.run_asr(wav_file)
        elif self.mode == "combined":
            segments = self.run_combined(wav_file)
        else:
            raise ValueError("Invalid processing mode.")

        remove_file(wav_file)
        remove_file(self.file_path)
        return segments

    def run_diarization(self, wav_file: str):
        # 1) VAD: split on speech/silence to create sub-chunks if desired
        # (Optional) but recommended for very long calls
        # For now, run EEND on entire file:
        diar_seg = EENDSegmenter(self.eend_model)
        diar_segments = diar_seg.segment(wav_file)

        # Save RTTM
        write_rttm(self.eend_model.diarize(wav_file),
                   os.path.join(TEMP_OUTPUT_DIR, "diar.rttm"),
                   file_id=os.path.basename(wav_file))
        return diar_segments

    def run_asr(self, wav_file: str):
        transcript_chunks = self.asr_model.transcribe(
            wav_file,
            english_only=(SELECTED_WHISPER_MODEL=="distil")
        )
        segments = []
        for c in transcript_chunks:
            c_start, c_end = c.get("timestamp", (0.0, 0.0))
            segments.append({
                "type": "speech",
                "start": c_start,
                "end": c_end,
                "speaker": "",
                "text": c.get("text", "").strip()
            })
        return segments

    def run_combined(self, wav_file: str):
        # Threaded approach to do diar & asr in parallel
        diar_seg = EENDSegmenter(self.eend_model)

        def diar_task():
            self.diar_result = diar_seg.segment(wav_file)

        def asr_task():
            self.transcript_chunks = self.asr_model.transcribe(
                wav_file,
                english_only=(SELECTED_WHISPER_MODEL=="distil")
            )

        threads = [threading.Thread(target=diar_task),
                   threading.Thread(target=asr_task)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Save diarization to RTTM
        write_rttm(self.eend_model.diarize(wav_file),
                   os.path.join(TEMP_OUTPUT_DIR, "diar.rttm"),
                   file_id=os.path.basename(wav_file))

        # Align
        aligned = align_asr_to_diar(self.transcript_chunks, self.diar_result)

        # Insert silence segments
        final_segments = self.insert_silences(aligned, wav_file)
        return final_segments

    def insert_silences(self, aligned_chunks, wav_file):
        # Sort by start time
        aligned_chunks.sort(key=lambda x: x.get("start", 0.0))
        final_segments = []
        audio = AudioSegment.from_file(wav_file)
        duration_sec = len(audio) / 1000.0

        # leading silence
        if aligned_chunks and aligned_chunks[0]["start"] > 0:
            final_segments.append({
                "type": "silence",
                "start": 0.0,
                "end": aligned_chunks[0]["start"]
            })
        elif not aligned_chunks:
            # entire file is silence if no chunks
            final_segments.append({
                "type": "silence",
                "start": 0.0,
                "end": duration_sec
            })
            return final_segments

        # speech + gaps
        for i, chunk in enumerate(aligned_chunks):
            final_segments.append({
                "type": "speech",
                "start": chunk["start"],
                "end": chunk["end"],
                "speaker": chunk.get("speaker", "SPEAKER_00"),
                "text": chunk.get("text", "")
            })
            if i < len(aligned_chunks) - 1:
                gap_start = chunk["end"]
                gap_end = aligned_chunks[i+1]["start"]
                if gap_end > gap_start:
                    final_segments.append({
                        "type": "silence",
                        "start": gap_start,
                        "end": gap_end
                    })

        # trailing silence
        if aligned_chunks[-1]["end"] < duration_sec:
            final_segments.append({
                "type": "silence",
                "start": aligned_chunks[-1]["end"],
                "end": duration_sec
            })

        return final_segments

def format_segments(segments):
    formatted = []
    for seg in segments:
        item = {
            "type": seg.get("type"),
            "start": round(seg.get("start", 0.0), 2),
            "end": round(seg.get("end", 0.0), 2)
        }
        if seg["type"] == "speech":
            item["speaker"] = seg.get("speaker", "")
            item["text"] = seg.get("text", "")
        formatted.append(item)
    return formatted
