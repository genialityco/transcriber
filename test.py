from faster_whisper import WhisperModel

# Usa 'small', 'base', 'medium', 'large-v2' según tu GPU/RAM
model_size = "small"
model = WhisperModel(model_size, device="cuda", compute_type="float16")

segments, info = model.transcribe("jfk.flac")

print("Lenguaje detectado:", info.language)
for segment in segments:
    print(f"[{segment.start:.2f} - {segment.end:.2f}] {segment.text}")

