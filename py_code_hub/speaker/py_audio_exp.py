import pyaudio
import wave

# Path to your WAV file
filename = "audio_file/token_100.wav"

# Open the WAV file
wf = wave.open(filename, 'rb')

# Create a PyAudio instance
p = pyaudio.PyAudio()

# Open a stream with the same format as the WAV file
stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True)

# Read data in chunks
chunk = 1024
data = wf.readframes(chunk)

# Play the sound by writing data to the stream
while data:
    stream.write(data)
    data = wf.readframes(chunk)

# Cleanup
stream.stop_stream()
stream.close()
p.terminate()
wf.close()
