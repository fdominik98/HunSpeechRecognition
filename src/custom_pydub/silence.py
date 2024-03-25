import itertools
from typing import Optional
from custom_pydub.custom_audio_segment import AudioSegment
from pydub.silence import detect_nonsilent
from models.settings import Settings


def split_on_silence(settings: Settings, audio: AudioSegment) -> tuple[AudioSegment, Optional[int], Optional[int]]:
    keep_silence = 350

    def pairwise(iterable):
        "s -> (s0,s1), (s1,s2), (s2, s3), ..."
        a, b = itertools.tee(iterable)
        next(b, None)
        return zip(a, b)

    if settings.trim_dbfs_auto:
        threshold = audio.dBFS - 5
    else:
        threshold = settings.noise_threshold

    output_ranges = [
        [start - keep_silence, end + keep_silence]
        for (start, end)
        in detect_nonsilent(audio, settings.silence_dur, threshold, 50)
    ]

    for range_i, range_ii in pairwise(output_ranges):
        last_end = range_i[1]
        next_start = range_ii[0]
        if next_start < last_end:
            range_i[1] = (last_end+next_start)//2
            range_ii[0] = range_i[1]

    processed_audio = AudioSegment.empty()

    first_start = None
    last_end = None

    for start, end in output_ranges:
        if first_start is None:
            first_start = start  # Save the first start timestamp
        last_end = end  # Update the last end timestamp with every iteration

        # Append chunks together
        chunk = audio[max(start, 0):min(end, len(audio))]
        processed_audio += chunk

    return (processed_audio, first_start, last_end)
