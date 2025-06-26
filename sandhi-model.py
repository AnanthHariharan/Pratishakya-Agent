from pathlib import Path
import re

# File paths
input_path = Path("texts/rig-plain-samhita.txt")
output_path = Path("output/rig-transformed-padapatha.txt")

# Read input lines
lines = input_path.read_text(encoding="utf-8").splitlines()

vowels = 'aāiīuūeēoōṛṝ'
consonants = ''.join(set('kghṅcjñṭḍṇtdnpbmyrlvśṣsh') - set(vowels))

# Rule 2.10: Pratiloma Sandhi (consonant + vowel)
def apply_pratiloma_sandhi(words):
    replacements = {'k': 'g', 'ṭ': 'ḍ', 't': 't', 'p': 'b'}
    result = []
    for i in range(len(words) - 1):
        word = words[i]
        next_word = words[i + 1]
        if word and next_word and word[-1] in replacements and next_word[0] in vowels:
            word = word[:-1] + replacements[word[-1]]
        result.append(word)
    result.append(words[-1])
    return result

# Rule 2.11: Drop Visarga (ḥ) before a consonant in specific words
def drop_visarga(words):
    exceptions = {'eṣaḥ', 'syaḥ', 'saḥ'}
    result = []
    for i in range(len(words) - 1):
        w = words[i]
        if w in exceptions and words[i + 1][0] in consonants:
            w = w[:-1]  # remove visarga
        result.append(w)
    result.append(words[-1])
    return result

# Rule 2.15–2.19: Vowel-vowel Sandhi
sandhi_map = {
    ('a', 'a'): 'ā', ('a', 'ā'): 'ā', ('ā', 'a'): 'ā', ('ā', 'ā'): 'ā',
    ('i', 'i'): 'ī', ('i', 'ī'): 'ī', ('ī', 'i'): 'ī', ('ī', 'ī'): 'ī',
    ('u', 'u'): 'ū', ('u', 'ū'): 'ū', ('ū', 'u'): 'ū', ('ū', 'ū'): 'ū',
    ('a', 'i'): 'e', ('a', 'ī'): 'e', ('ā', 'i'): 'e', ('ā', 'ī'): 'e',
    ('a', 'u'): 'o', ('a', 'ū'): 'o', ('ā', 'u'): 'o', ('ā', 'ū'): 'o',
    ('a', 'e'): 'ai', ('ā', 'e'): 'ai', ('a', 'ai'): 'ai', ('ā', 'ai'): 'ai',
    ('a', 'o'): 'au', ('ā', 'o'): 'au', ('a', 'au'): 'au', ('ā', 'au'): 'au'
}

def apply_vowel_sandhi(words):
    result = []
    skip_next = False
    for i in range(len(words) - 1):
        if skip_next:
            skip_next = False
            continue
        w1, w2 = words[i], words[i + 1]
        if w1 and w2 and w1[-1] in vowels and w2[0] in vowels:
            combined = sandhi_map.get((w1[-1], w2[0]))
            if combined:
                new_word = w1[:-1] + combined + w2[1:]
                result.append(new_word)
                skip_next = True
                continue
        result.append(w1)
    if not skip_next:
        result.append(words[-1])
    return result

# Transform lines: apply rules in sequence
transformed_lines = []
for line in lines:
    if line.strip():
        words = line.strip().split()
        words = apply_pratiloma_sandhi(words)
        words = drop_visarga(words)
        words = apply_vowel_sandhi(words)
        transformed_lines.append(" | ".join(words) + " |")

# Write the output
output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text("\n".join(transformed_lines), encoding="utf-8")

# Preview the result
print("\n".join(transformed_lines[:6]))
