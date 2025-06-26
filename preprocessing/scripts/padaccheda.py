import re

def convert_to_pada_format(text):
    lines = text.strip().split("\n")
    output = []
    
    for line in lines:
        if not line.strip():
            continue

        match = re.search(r'\|\s*(RV_(\d+),(\d+)\.(\d+))', line)
        if match:
            full_ref = match.group(1)
            mandala = int(match.group(2))
            hymn = int(match.group(3))
            verse = int(match.group(4))
            verse_text = re.sub(r'\|\s*RV_\d+,\d+\.\d+', '', line)
        else:
            verse_text = line

        words = [w for w in verse_text.strip().split() if w != '|']
        if match:
            split_line = " | ".join(words) + f" // rv_{mandala},{hymn}.{verse} //"
        else:
            split_line = " | ".join(words)
        output.append(split_line)
    
    return "\n\n".join(output)

if __name__ == "__main__":
    with open("rigveda-original-gretil.txt", "r", encoding="utf-8") as infile:
        text = infile.read()

    formatted = convert_to_pada_format(text)

    with open("rigveda-padaccheda.txt", "w", encoding="utf-8") as outfile:
        outfile.write(formatted)
