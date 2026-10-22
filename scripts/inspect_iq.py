#!/usr/bin/env python3
"""Plot the averaged power spectrum of a HackRF signed-8-bit IQ recording."""
import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def positive(value: str) -> float:
    number = float(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return number


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="interleaved signed-8-bit IQ (.cs8)")
    parser.add_argument("--frequency", type=positive, required=True, help="centre frequency (Hz)")
    parser.add_argument("--sample-rate", type=positive, required=True, help="sample rate (samples/s)")
    parser.add_argument("--fft-size", type=int, default=65536, help="power of two; default: 65536")
    parser.add_argument("--output", type=Path, default=Path("spectrum.png"))
    args = parser.parse_args()
    if args.fft_size < 256 or args.fft_size & (args.fft_size - 1):
        parser.error("--fft-size must be a power of two of at least 256")

    raw = np.fromfile(args.input, dtype=np.int8)
    raw = raw[:len(raw) - len(raw) % 2]
    if len(raw) < args.fft_size * 2:
        parser.error("capture is shorter than one FFT block")
    iq = raw[0::2].astype(np.float32) + 1j * raw[1::2].astype(np.float32)
    blocks = len(iq) // args.fft_size
    iq = iq[:blocks * args.fft_size].reshape(blocks, args.fft_size)
    window = np.hanning(args.fft_size).astype(np.float32)
    power = np.mean(np.abs(np.fft.fftshift(np.fft.fft(iq * window, axis=1), axes=1)) ** 2, axis=0)
    power_db = 10 * np.log10(power + 1e-12)
    frequencies = args.frequency + np.fft.fftshift(np.fft.fftfreq(args.fft_size, 1 / args.sample_rate))

    fig, axis = plt.subplots(figsize=(12, 5))
    axis.plot(frequencies / 1e6, power_db, linewidth=0.7)
    axis.set(title=f"HackRF spectrum: {args.input.name} ({blocks} averaged FFTs)",
             xlabel="Frequency (MHz)", ylabel="Relative power (dB)")
    axis.grid(True, alpha=0.3)
    fig.tight_layout()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=160)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
