import csv
from pathlib import Path
import json

capture_path = Path("captures/baseline_stationary.log") # Change this to the path of your capture file

record_count = 0
first_record = None
last_record = None

previous_id = None
id_discontinuities = 0

invalid_csi_records = 0
csi_lengths = set()

with capture_path.open(
    mode="r",
    encoding="utf-8",
    errors="replace",
) as capture_file:
    for line in capture_file:
        if not line.startswith("CSI_DATA,"):
            continue

        record = next(csv.reader([line]))
        
        if len(record) != 25:
            invalid_csi_records += 1
            continue

        try:
            declared_length = int(record[22])
            csi_values = json.loads(record[24])
        except (ValueError, json.JSONDecodeError):
            invalid_csi_records += 1
            continue

        if not isinstance(csi_values, list):
            invalid_csi_records += 1
            continue

        if len(csi_values) != declared_length:
            invalid_csi_records += 1
            continue

        if not all(type(value) is int for value in csi_values):
            invalid_csi_records += 1
            continue

        csi_lengths.add(declared_length)
        
        record_id = int(record[1])

        if previous_id is not None:
            if record_id != previous_id + 1:
                id_discontinuities += 1

        previous_id = record_id

        record_count += 1

        if first_record is None:
            first_record = record

        last_record = record

print(f"Invalid CSI records: {invalid_csi_records}")
print(f"CSI lengths observed: {sorted(csi_lengths)}")

print(f"CSI records: {record_count}")

if first_record is not None:
    
    first_timestamp_us = int(first_record[18])
    last_timestamp_us = int(last_record[18])

    duration_s = (
        last_timestamp_us - first_timestamp_us
    ) / 1_000_000

    print(f"ID discontinuities: {id_discontinuities}")
    print(f"Capture duration: {duration_s:.6f} seconds")

    if duration_s > 0:
        rate_hz = (record_count - 1) / duration_s
        print(f"Average capture rate: {rate_hz:.2f} records/second")
        
    print(f"Fields in first record: {len(first_record)}")
    print(f"First record ID: {first_record[1]}")
    print(f"Last record ID: {last_record[1]}")
else:
    print("No CSI records found.")