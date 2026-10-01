#!/usr/bin/env python3
"""Measure serial line arrival intervals for LoRa PTT field tests."""

from __future__ import annotations

import argparse
import statistics
import sys
import time

try:
    import serial
except ImportError:
    print("Install pyserial: pip install pyserial", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="PTT serial latency sampler")
    parser.add_argument("--port", default="/dev/ttyUSB0")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--seconds", type=int, default=30)
    args = parser.parse_args()

    deltas: list[float] = []
    last = time.monotonic()

    with serial.Serial(args.port, args.baud, timeout=1) as ser:
        end = time.monotonic() + args.seconds
        print(f"Listening on {args.port} for {args.seconds}s …")
        while time.monotonic() < end:
            line = ser.readline()
            if not line:
                continue
            now = time.monotonic()
            deltas.append(now - last)
            last = now
            print(line.decode(errors="replace").rstrip())

    if len(deltas) < 2:
        print("Not enough packets captured.")
        raise SystemExit(2)

    print("\n--- Inter-arrival stats (seconds) ---")
    print(f"count={len(deltas)} min={min(deltas):.3f} max={max(deltas):.3f} avg={statistics.mean(deltas):.3f}")


if __name__ == "__main__":
    main()
