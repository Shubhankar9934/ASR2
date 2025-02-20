# project_telephonic/utils/file_utils.py
import os
import logging
from pydub import AudioSegment
from project_telephonic.config import TEMP_OUTPUT_DIR, SAMPLE_RATE

def convert_to_wav(input_file: str, output_wav: str, sample_rate: int = SAMPLE_RATE):
    logging.info("Converting '%s' to WAV at %d Hz...", input_file, sample_rate)
    audio = AudioSegment.from_file(input_file)
    audio = audio.set_frame_rate(sample_rate).set_channels(1)
    audio.export(output_wav, format="wav")
    logging.info("Conversion complete. WAV saved as '%s'.", output_wav)
    return output_wav

def remove_file(file_path: str):
    try:
        os.remove(file_path)
        logging.info("Removed temporary file '%s'.", file_path)
    except Exception as e:
        logging.error("Failed to remove file '%s': %s", file_path, str(e))

def dump_temp(data, filename):
    path = os.path.join(TEMP_OUTPUT_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(str(data))
    logging.info("Dumped temporary output to '%s'.", path)

def write_rttm(diarization_result, output_rttm, file_id="audio"):
    """
    Write diarization result to an RTTM file.
    Format:
      SPEAKER <file-id> 1 <start> <duration> <NA> <speaker_label> <NA> <NA>
    """
    lines = []
    for turn, _, speaker in diarization_result.itertracks(yield_label=True):
        start = turn.start
        duration = turn.end - turn.start
        line = (f"SPEAKER {file_id} 1 {start:.2f} {duration:.2f} "
                f"<NA> {speaker} <NA> <NA>")
        lines.append(line)

    with open(output_rttm, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")
    logging.info("RTTM file written to '%s'.", output_rttm)
