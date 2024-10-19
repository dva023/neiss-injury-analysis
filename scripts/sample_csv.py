import csv
import os
import random
import sys


def sample_csv(input_file, num_samples):

    # Generate output filename
    base, ext = os.path.splitext(input_file)
    output_file = f"{base}_{num_samples}_samples{ext}"

    if os.path.exists(output_file):
        os.remove(output_file)
        print(f"Removed existing file: {output_file}")

    # Count the total number of lines
    with open(input_file, "r") as f:
        total_lines = sum(1 for _ in f) - 1  # exclude header

    # Generate random line numbers to sample
    sample_lines = sorted(
        random.sample(range(2, total_lines + 2), min(num_samples, total_lines))
    )

    with open(input_file, "r", newline="") as infile, open(
        output_file, "w", newline=""
    ) as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        # Write the header
        header = next(reader)
        writer.writerow(header)

        # Write sampled lines
        for i, row in enumerate(reader, start=2):
            if i in sample_lines:
                writer.writerow(row)
                sample_lines.remove(i)
            if not sample_lines:
                break


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python sample_csv.py <input_file> <number_of_lines>")
        sys.exit(1)

    input_file = sys.argv[1]
    num_samples = int(sys.argv[2])

    sample_csv(input_file, num_samples)
    print(
        f"Randomly selected {num_samples} lines have been extracted from {input_file}"
    )
