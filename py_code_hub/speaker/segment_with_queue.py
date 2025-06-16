import queue
import threading
import time
import pyaudio
from pydub import AudioSegment

audio_queue = queue.Queue()


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
    time.sleep(1)


def announce_token(token_prefix, token_numbers, counter_numbers):
    print(f"{token_prefix} {''.join(token_numbers)} {''.join(counter_numbers)}")
    voices = [
        "./audio_file/segment/tn.mp3",
        f"./audio_file/segment/{token_prefix}.mp3",
    ]

    for token in token_numbers:
        voices.append(f"./audio_file/segment/{token}.mp3")

    voices.append("./audio_file/segment/cn.mp3")

    for counter in counter_numbers:
        voices.append(f"./audio_file/segment/{counter}.mp3")

    audio = AudioSegment.empty()
    for f in voices:
        audio += AudioSegment.from_file(f)
    return audio


def scan_queue():
    while True:
        audio = audio_queue.get()
        if audio:
            print(f"Got Audio Sample........ {audio}")
            play_audio_segment(audio)


worker = threading.Thread(target=scan_queue)
worker.start()


def add_data_to_queue():
    print("Start Add Data to Queue")
    while True:
        for index in range(9):
            audio = announce_token("a", ["0", "0", f"{index}"], ["0", f"{index + 1}"])
            audio_queue.put(audio)
            time.sleep(index * 4)
            print("Added")
        exit(0)


data_worker = threading.Thread(target=add_data_to_queue)
data_worker.start()
