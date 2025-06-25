

from itertools import zip_longest

# Paths to the files
file1_path = "rigveda-comp-padas.txt"
file2_path = "rigveda-padapatha-gretil.txt"

# Read both files
with open(file1_path, "r", encoding="utf-8") as f1:
    lines1 = [line.strip() for line in f1.readlines()]

with open(file2_path, "r", encoding="utf-8") as f2:
    lines2 = [line.strip() for line in f2.readlines()]

# Compare line by line and write differences to a file
with open("comparison_diff.txt", "w", encoding="utf-8") as diff_file:
    for i, (line1, line2) in enumerate(zip_longest(lines1, lines2), start=1):
        if line1 != line2:
            diff_file.write(f"Line {i}:\n")
            diff_file.write(f"  File 1: {line1}\n")
            diff_file.write(f"  File 2: {line2}\n\n")