from pathlib import Path
import math, struct, wave
out = Path(__file__).resolve().parents[1] / "App/Resources/siren.wav"
rate, duration, phase = 44100, 1.8, 0.0
samples = bytearray()
for i in range(round(rate * duration)):
    t = i / rate
    frequency = 950 + 330 * math.sin(2 * math.pi * 2.2 * t)
    phase += 2 * math.pi * frequency / rate
    envelope = min(1, t / .012, (duration - t) / .035)
    signal = (math.sin(phase) + .22 * math.sin(3 * phase)) / 1.22
    samples.extend(struct.pack("<h", round(signal * envelope * .85 * 32767)))
with wave.open(str(out), "wb") as f:
    f.setnchannels(1); f.setsampwidth(2); f.setframerate(rate); f.writeframes(samples)
