#!/usr/bin/env python3
"""Educational mono broadcast-FM demodulator for a centred HackRF .cs8 capture."""
import argparse
import wave
from pathlib import Path

import numpy as np


def positive(value: str) -> float:
    number = float(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return number


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="centred signed-8-bit IQ capture")
    parser.add_argument("--sample-rate", type=positive, required=True, help="IQ rate; use 2.4e6")
    parser.add_argument("--audio-rate", type=int, default=48_000, help="output rate (default: 48000)")
    parser.add_argument("--output", type=Path, default=Path("fm.wav"))
    args = parser.parse_args()
    ratio = round(args.sample_rate / args.audio_rate)
    if ratio < 2 or abs(args.sample_rate / ratio - args.audio_rate) > 1:
        parser.error("sample rate must be an integer multiple of --audio-rate (e.g. 2.4e6 and 48k)")

    raw = np.fromfile(args.input, dtype=np.int8)
    raw = raw[:len(raw) - len(raw) % 2]
    iq = raw[0::2].astype(np.float32) + 1j * raw[1::2].astype(np.float32)
    if len(iq) < ratio * 10:
        parser.error("capture is too short")

    # Phase change between adjacent IQ samples is proportional to FM deviation.
    phase = np.angle(iq[1:] * np.conj(iq[:-1]))
    # Simple moving-average anti-alias filter, then decimate to audio rate.
    usable = len(phase) // ratio * ratio
    audio = phase[:usable].reshape(-1, ratio).mean(axis=1)
    audio -= audio.mean()
    peak = np.max(np.abs(audio))
    if peak > 0:
        audio /= peak
    pcm = np.asarray(np.clip(audio * 0.85, -1, 1) * 32767, dtype="<i2")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(args.output), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(args.audio_rate)
        wav.writeframes(pcm.tobytes())
    print(f"Wrote {args.output} ({len(audio) / args.audio_rate:.1f} seconds, mono {args.audio_rate} Hz)")


if __name__ == "__main__":
    main()
