from pathlib import Path

# Define paths
generated_path = Path("output/rig-transformed-padapatha.txt")
reference_path = Path("texts/rig-plain-padapatha.txt")

# Load both files
generated_lines = generated_path.read_text(encoding="utf-8").splitlines()
reference_lines = reference_path.read_text(encoding="utf-8").splitlines()

# Sanity check: trim to same length
min_len = min(len(generated_lines), len(reference_lines))
generated_lines = generated_lines[:min_len]
reference_lines = reference_lines[:min_len]

# Comparison metrics
total_words = 0
matched_words = 0
mismatched_lines = []

for i, (gen_line, ref_line) in enumerate(zip(generated_lines, reference_lines), 1):
    gen_words = [w.strip() for w in gen_line.strip('| ').split('|') if w.strip()]
    ref_words = [w.strip() for w in ref_line.strip('| ').split('|') if w.strip()]
    
    total_words += max(len(gen_words), len(ref_words))
    matched_words += sum(g == r for g, r in zip(gen_words, ref_words))

    if gen_words != ref_words:
        mismatched_lines.append((i, gen_words, ref_words))

# Output results
accuracy = (matched_words / total_words) * 100 if total_words > 0 else 0
print(f"Matched words: {matched_words}/{total_words} ({accuracy:.2f}%)")
print(f"Mismatched lines: {len(mismatched_lines)} out of {min_len}")

# Show a few mismatches
print("\nExamples of mismatched lines:")
for line_num, gen, ref in mismatched_lines[:5]:
    print(f"\nLine {line_num}:")
    print(f"  Generated: {' '.join(gen)}")
    print(f"  Reference: {' '.join(ref)}")
