import csv
import os
import random
import sys


def sample_csv(input_file, output_file, num_samples):

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
    if len(sys.argv) != 4:
        print("Usage: python script.py <input_file> <output_file> <number_of_lines>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    num_samples = int(sys.argv[3])

    sample_csv(input_file, output_file, num_samples)
    print(
        f"Randomly selected {num_samples} lines have been written to {output_file} while preserving original order"
    )
