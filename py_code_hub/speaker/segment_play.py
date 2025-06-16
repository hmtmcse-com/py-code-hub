import pyaudio
from pydub import AudioSegment


def play_audio_segment(audio_segment):
    p = pyaudio.PyAudio()

    # Open stream based on audio segment properties
    stream = p.open(
        format=p.get_format_from_width(audio_segment.sample_width),
        channels=audio_segment.channels,
        rate=audio_segment.frame_rate,
        output=True
    )

    # Play audio
    stream.write(audio_segment.raw_data)

    # Clean up
    stream.stop_stream()
    stream.close()
    p.terminate()


def announce_token(token_prefix, token_numbers, counter_numbers):
    print(f"{token_prefix} {''.join(token_numbers)} {''.join(counter_numbers)}")
    voices = [
        "./audio_file/segment/tn.mp3",
        f"./audio_file/segment/{token_prefix}.mp3",
    ]

    for token in token_numbers:
        voices.append(f"./audio_file/segment/{token}.mp3")

    voices.append( "./audio_file/segment/cn.mp3")

    for counter in counter_numbers:
        voices.append(f"./audio_file/segment/{counter}.mp3")

    audio = AudioSegment.empty()
    for f in voices:
        audio += AudioSegment.from_file(f)
    play_audio_segment(audio)


# Example
announce_token("a", ["0", "0", "1"], ["0", "2"])
announce_token("b", ["1", "0", "1"], ["2", "2"])
announce_token("c", ["1", "9", "1"], ["9", "2"])
