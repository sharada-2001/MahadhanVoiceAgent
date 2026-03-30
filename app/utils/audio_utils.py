import sounddevice as sd
import numpy as np


def record_audio():

    samplerate = 24000
    duration = 3

    device = None   # default microphone

    print("Recording...")

    audio = sd.rec(
        int(duration * samplerate),
        samplerate=samplerate,
        channels=1,
        dtype="int16",
        device=device
    )

    sd.wait()

    print("Recording finished")

    return audio.tobytes()