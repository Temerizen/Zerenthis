from gtts import gTTS

def generate_voice(script):
    path = "backend/outputs/audio.mp3"
    tts = gTTS(script)
    tts.save(path)
    return path
