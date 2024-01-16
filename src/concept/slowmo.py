from pydub import AudioSegment
from pydub.playback import play

def slow_down_audio(input_file, output_file, speed_factor):
    # Load the audio file
    audio = AudioSegment.from_file(input_file)

    # Slow down the audio by the speed factor
    # A speed factor of 2.0 will make the audio play at half speed
    slowed_audio = audio._spawn(audio.raw_data, overrides={
        "frame_rate": int(audio.frame_rate / speed_factor)
    }).set_frame_rate(audio.frame_rate)

    # Export the slowed down audio
    slowed_audio.export(output_file, format="mp3")

# Example usage
slow_down_audio('chunk1.mp3', 'chunk1_slow.mp3', 1.15)