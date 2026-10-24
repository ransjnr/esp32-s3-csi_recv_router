import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

capture_path = Path("captures/movement_test.log")

timestamps = []
amplitudes = []

with capture_path.open(encoding="utf-8", errors="replace") as capture_file:
    for line in capture_file:
        if not line.startswith("CSI_DATA,"):
            continue

        record = next(csv.reader([line]))

        if len(record) != 25:
            continue

        values = np.array(json.loads(record[24]), dtype=float)

        if len(values) != 128:
            continue

        imaginary = values[0::2]
        real = values[1::2]

        amplitude = np.sqrt(real ** 2 + imaginary ** 2)

        if int(record[23]):
            amplitude[:2] = np.nan

        timestamps.append(int(record[18]))
        amplitudes.append(amplitude)

if not amplitudes:
    raise SystemExit("No matching CSI records found.")

time_s = (np.array(timestamps) - timestamps[0]) / 1_000_000
amplitudes = np.array(amplitudes)

plt.figure(figsize=(11, 5))
plt.pcolormesh(
    time_s,
    np.arange(amplitudes.shape[1]),
    amplitudes.T,
    shading="auto",
)
plt.xlabel("Time (seconds)")
plt.ylabel("CSI pair index")
plt.title("CSI amplitude — still / movement / still")
plt.colorbar(label="Amplitude (device units)")
plt.tight_layout()
plt.savefig("captures/movement_amplitude.png", dpi=150)
plt.show()