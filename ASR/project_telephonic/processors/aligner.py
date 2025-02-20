# project_telephonic/processors/aligner.py
import logging

def align_asr_to_diar(asr_chunks, diar_segments):
    """
    Map ASR chunks to diarization segments using dynamic programming or
    a simpler "closest match" approach. This is a placeholder for a more
    sophisticated alignment method.
    """
    logging.info("Aligning ASR chunks to diarized segments...")
    # Example approach:
    #  - For each ASR chunk with (start, end), find overlapping diar segment
    #  - If multiple overlaps, pick the one with largest intersection
    aligned = []
    for chunk in asr_chunks:
        c_start, c_end = chunk.get("timestamp", (0.0, 0.0))
        chunk_text = chunk.get("text", "")
        # Find a best speaker region
        best_speaker = "unknown"
        best_overlap = 0.0

        for seg in diar_segments:
            if seg["type"] != "speech":
                continue
            seg_start, seg_end = seg["start"], seg["end"]
            # Overlap
            overlap = min(c_end, seg_end) - max(c_start, seg_start)
            if overlap > best_overlap:
                best_overlap = overlap
                best_speaker = seg["speaker"]
        # Build aligned chunk
        aligned.append({
            "start": c_start,
            "end": c_end,
            "speaker": best_speaker,
            "text": chunk_text
        })

    logging.info("Alignment complete. Produced %d aligned segments.", len(aligned))
    return aligned
