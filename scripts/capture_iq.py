#!/usr/bin/env python3
"""Make a finite, receive-only HackRF IQ recording (.cs8)."""
import argparse
import shutil
import subprocess
from pathlib import Path


def positive_number(value: str) -> float:
    try:
        answer = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a number") from exc
    if answer <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return answer


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frequency", type=positive_number, required=True,
                        help="centre frequency in Hz (for example 100e6)")
    parser.add_argument("--sample-rate", type=positive_number, required=True,
                        help="sample rate in samples/s (for example 2e6)")
    parser.add_argument("--duration", type=positive_number, required=True,
                        help="recording length in seconds")
    parser.add_argument("--output", type=Path, required=True, help="output .cs8 file")
    parser.add_argument("--lna-gain", type=int, default=16, choices=range(0, 41, 8))
    parser.add_argument("--vga-gain", type=int, default=20, choices=range(0, 63, 2))
    args = parser.parse_args()

    if shutil.which("hackrf_transfer") is None:
        parser.error("hackrf_transfer is not installed; install the 'hackrf' package")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    sample_count = round(args.duration * args.sample_rate)
    command = [
        "hackrf_transfer", "-r", str(args.output), "-f", str(round(args.frequency)),
        "-s", str(round(args.sample_rate)), "-n", str(sample_count),
        "-l", str(args.lna_gain), "-g", str(args.vga_gain),
    ]
    print("Receive-only capture:", " ".join(command))
    print(f"Expected size: {sample_count * 2 / 1e6:.1f} MB")
    subprocess.run(command, check=True)
    print(f"Saved {args.output} ({args.output.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
