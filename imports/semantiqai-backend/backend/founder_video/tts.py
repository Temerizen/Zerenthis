import os
import wave
import contextlib

def synthesize_voice(text: str, output_path: str):
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty("rate", 172)
        engine.save_to_file(text, output_path)
        engine.runAndWait()
        return output_path
    except Exception as e:
        raise RuntimeError(f"TTS generation failed: {e}")

def wav_duration(path: str) -> float:
    with contextlib.closing(wave.open(path, "r")) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        return frames / float(rate)
