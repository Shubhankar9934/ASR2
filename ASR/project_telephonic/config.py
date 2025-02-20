# project_telephonic/config.py
import os

# -------------------------------------------------------------------
# Model configuration
# -------------------------------------------------------------------
DEFAULT_WHISPER_MODEL_ID = "openai/whisper-large"
DISTIL_WHISPER_MODEL_ID = "distil-whisper/distil-large-v3"
EEND_MODEL_ID = "pyannote/speaker-diarization-3.1"  # Overlap-aware, can adapt for SA-EEND

VAD_MODEL_ID = "pyannote/voice-activity-detection"

HF_TOKEN = os.getenv("HF_HUB_TOKEN", "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")

# Use CPU or GPU
DEVICE = "cuda" if os.environ.get("CUDA_VISIBLE_DEVICES") else "cpu"

# Choose an ASR model
SELECTED_WHISPER_MODEL = "distil"  # or "whisper"

# Audio processing configuration
SAMPLE_RATE = 16000

# Processing mode
PROCESSING_MODE = os.getenv("PROCESSING_MODE", "combined").lower()
if PROCESSING_MODE not in ("diarization", "transcription", "combined"):
    raise ValueError("Invalid PROCESSING_MODE (must be diarization, transcription, or combined).")

# Temporary output directory
TEMP_OUTPUT_DIR = os.getenv("TEMP_OUTPUT_DIR", "temp_debug")
if not os.path.exists(TEMP_OUTPUT_DIR):
    os.makedirs(TEMP_OUTPUT_DIR)
