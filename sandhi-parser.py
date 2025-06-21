import re
import unicodedata

class SandhiReverser:
    """
    Reverses Vedic sandhi to convert a Samhita line into its Padapatha form.
    This class uses a rule-based, lexicon-driven, recursive backtracking approach.
    """

    def __init__(self, padapatha_lexicon):
        """
        Initializes the reverser with a master lexicon of all valid Padapatha words.
        Args:
            padapatha_lexicon (set): A set of all unique words from the Padapatha.
                                     This is crucial for validating splits.
        """
        self.lexicon = padapatha_lexicon
        # A memoization cache to store results for already computed substrings,
        # significantly speeding up the process by avoiding re-computation.
        self.memo = {}
        # The order of rules can matter. More specific rules should come first.
        self.SANDHI_RULES = [
            self._reverse_e_to_a_i,
            self._reverse_o_to_a_u,
            self._reverse_ai_to_a_e_ai,
            self._reverse_au_to_a_o_au,
            self._reverse_a_avagraha,
            self._reverse_e_avagraha,
            self._reverse_dirgha_sandhi,
            self._reverse_yan_sandhi_v,
            self._reverse_yan_sandhi_y,
            self._reverse_r_visarga,
            self._reverse_s_visarga,
        ]

    def reverse_sandhi(self, samhita_line):
        """
        Public method to start the sandhi reversal process for a full line.
        Args:
            samhita_line (str): A single line of Samhita text.
        Returns:
            list: A list of words representing the best Padapatha split, or None if no valid split is found.
        """
        # Clear the memoization cache for each new line.
        self.memo = {}
        result = self._find_splits(samhita_line)
        # The result might be wrapped in a list, so we unwrap it if necessary.
        return result[0] if result else None

    def _find_splits(self, text):
        """
        The core recursive function that finds valid splits for a given text segment.
        Uses memoization to avoid re-calculating results for the same substring.
        Args:
            text (str): The piece of Samhita text to be split.
        Returns:
            list: A list of possible valid splits, where each split is a list of words.
                  Returns an empty list if no valid split is found.
        """
        if not text:
            # Base case: an empty string is a successful parse end.
            return [[]]
        
        # If we have already computed the result for this text, return it from the cache.
        if text in self.memo:
            return self.memo[text]

        all_valid_splits = []

        # === 1. Try a "no-sandhi" split first ===
        # Check if the whole remaining text is a valid word.
        if text in self.lexicon:
            all_valid_splits.append([text])

        # === 2. Try all possible sandhi rules at the current position ===
        for rule in self.SANDHI_RULES:
            # A rule can return multiple potential splits (e.g., 's' could be from visarga or be original).
            possible_splits = rule(text)
            for first_word, rest_of_text in possible_splits:
                # For each valid first word proposed by the rule,
                # recursively find splits for the rest of the text.
                following_splits = self._find_splits(rest_of_text)
                if following_splits:
                    # If the rest of the text can be split successfully,
                    # combine the current first word with the subsequent splits.
                    for split in following_splits:
                        all_valid_splits.append([first_word] + split)

        # === 3. Try a simple prefix split as a fallback ===
        # This handles cases where a word doesn't undergo sandhi at its end.
        for i in range(1, len(text)):
            prefix = text[:i]
            if prefix in self.lexicon:
                suffix = text[i:]
                # Recursively find splits for the suffix.
                following_splits = self._find_splits(suffix)
                if following_splits:
                    # Combine the prefix with the successful suffix splits.
                    for split in following_splits:
                        all_valid_splits.append([prefix] + split)
        
        # Cache the result for the current text before returning.
        self.memo[text] = all_valid_splits
        return all_valid_splits

    # --- Sandhi Rule Implementations ---
    # Each rule function takes the current text and returns a list of possible
    # (first_word, rest_of_text) tuples if the rule applies.
    # Otherwise, it returns an empty list.

    def _reverse_dirgha_sandhi(self, text):
        # Reverse long vowel sandhi (ā -> a+a, ī -> i+i, etc.)
        splits = []
        vowel_map = {'ā': 'a', 'ī': 'i', 'ū': 'u', 'ṝ': 'ṛ'}
        for long_vowel, short_vowel in vowel_map.items():
            if long_vowel in text:
                parts = text.split(long_vowel, 1)
                for i in range(1, len(parts[0]) + 1):
                    prefix = parts[0][:i]
                    word1 = prefix + short_vowel
                    if word1 in self.lexicon:
                        rest = short_vowel + parts[0][i:] + long_vowel + parts[1]
                        splits.append((word1, rest))
        return splits
        
    def _reverse_yan_sandhi_y(self, text):
        # Reverse yaṇ sandhi (y -> i before a vowel)
        # e.g., 'py upa' -> 'pi upa'. 'dhiyā' -> 'dhiā' (which becomes 'dhiyā')
        splits = []
        if 'y' in text and text.index('y') > 0:
            pos = text.index('y')
            word1_stem = text[:pos]
            vowel_after_y = text[pos+1]
            if vowel_after_y in "aeiouāīūṛṝ":
                word1 = word1_stem + 'i'
                if word1 in self.lexicon:
                    rest = text[pos+1:]
                    splits.append((word1, rest))
        return splits

    def _reverse_yan_sandhi_v(self, text):
        # Reverse yaṇ sandhi (v -> u before a vowel)
        # e.g., 'anvaya' -> 'anu aya'
        splits = []
        if text.startswith('v') and len(text) > 1:
             # This simple case is less common for splitting.
             # More complex logic needed for internal splits.
             pass
        elif 'v' in text and text.index('v') > 0:
             pos = text.index('v')
             prefix = text[:pos]
             vowel_after_v = text[pos+1]
             if vowel_after_v in "aeiouāīūṛṝe":
                 word1 = prefix + 'u'
                 if word1 in self.lexicon:
                     rest = text[pos+1:]
                     splits.append((word1, rest))
        return splits

    def _reverse_e_to_a_i(self, text):
        # Reverse guṇa sandhi (e -> a + i)
        splits = []
        if 'e' in text:
            pos = text.find('e')
            prefix = text[:pos]
            
            word1 = prefix + 'a'
            rest = 'i' + text[pos+1:]

            if word1 in self.lexicon and any(rest.startswith(w) for w in self.lexicon if w.startswith('i')):
                 splits.append((word1, rest))
        return splits

    def _reverse_o_to_a_u(self, text):
        # Reverse guṇa sandhi (o -> a + u)
        splits = []
        if 'o' in text:
            pos = text.find('o')
            prefix = text[:pos]
            
            word1 = prefix + 'a'
            rest = 'u' + text[pos+1:]

            if word1 in self.lexicon and any(rest.startswith(w) for w in self.lexicon if w.startswith('u')):
                 splits.append((word1, rest))
        return splits

    def _reverse_ai_to_a_e_ai(self, text):
        # Reverse vṛddhi sandhi (ai -> a + e/ai)
        splits = []
        if 'ai' in text:
            pos = text.find('ai')
            prefix = text[:pos]

            # Try ai -> a + e
            word1_a = prefix + 'a'
            rest_e = 'e' + text[pos+2:]
            if word1_a in self.lexicon and any(rest_e.startswith(w) for w in self.lexicon if w.startswith('e')):
                splits.append((word1_a, rest_e))
            
            # Try ai -> a + ai
            rest_ai = 'ai' + text[pos+2:]
            if word1_a in self.lexicon and any(rest_ai.startswith(w) for w in self.lexicon if w.startswith('ai')):
                splits.append((word1_a, rest_ai))
        return splits

    def _reverse_au_to_a_o_au(self, text):
        # Reverse vṛddhi sandhi (au -> a + o/au)
        splits = []
        if 'au' in text:
            pos = text.find('au')
            prefix = text[:pos]
            
            word1_a = prefix + 'a'
            
            # Try au -> a + o
            rest_o = 'o' + text[pos+2:]
            if word1_a in self.lexicon and any(rest_o.startswith(w) for w in self.lexicon if w.startswith('o')):
                splits.append((word1_a, rest_o))

            # Try au -> a + au
            rest_au = 'au' + text[pos+2:]
            if word1_a in self.lexicon and any(rest_au.startswith(w) for w in self.lexicon if w.startswith('au')):
                splits.append((word1_a, rest_au))
        return splits
        
    def _reverse_a_avagraha(self, text):
        # Reverse o ' -> aḥ a (from visarga sandhi)
        # e.g., 'so 'bravīt' -> 'saḥ abravīt'
        splits = []
        if "o'" in text:
            pos = text.find("o'")
            prefix = text[:pos]
            
            word1 = prefix + 'aḥ'
            rest = 'a' + text[pos+2:]

            if word1 in self.lexicon:
                splits.append((word1, rest))
        return splits

    def _reverse_e_avagraha(self, text):
        # Reverse e ' -> e a (from pūrvarūpa sandhi)
        # e.g., 'te 'bruvan' -> 'te abruvan'
        splits = []
        if "e'" in text:
            pos = text.find("e'")
            word1 = text[:pos+1]
            rest = 'a' + text[pos+2:]
            if word1 in self.lexicon:
                splits.append((word1, rest))
        return splits
    
    def _reverse_r_visarga(self, text):
        # Reverses 'r' that likely came from a visarga
        # e.g., punarapi -> punaḥ api
        splits = []
        if 'r' in text:
            pos = text.find('r')
            if pos > 0 and pos < len(text) -1:
                vowel_before = text[pos-1]
                char_after = text[pos+1]
                # Rule is complex, this is a simplified heuristic:
                # visarga becomes 'r' before voiced sounds, except 'r'
                if vowel_before in 'aiuṛ' and char_after in 'ghjḍdhjbgdāīūṛṝeovyhlṃṅṇnm':
                    prefix = text[:pos]
                    if prefix.endswith('a'): # e.g. punaḥ, not agnir
                         word1 = prefix[:-1] + 'aḥ'
                         if word1 in self.lexicon:
                              splits.append((word1, text[pos+1:]))
        return splits
    
    def _reverse_s_visarga(self, text):
        # Reverses ś, ṣ, s that came from a visarga
        splits = []
        for s_char in ['ś', 'ṣ', 's']:
            if s_char in text:
                pos = text.find(s_char)
                if pos > 0:
                    prefix = text[:pos]
                    word1 = prefix + 'ḥ'
                    if word1 in self.lexicon:
                         # This assumes the sibilant replaces the visarga
                         rest = text[pos:]
                         splits.append((word1, rest))
        return splits


def prepare_data(samhita_text, padapatha_text):
    """
    Cleans and aligns the raw Samhita and Padapatha texts.
    """
    # Clean Samhita lines
    cleaned_samhita_lines = []
    for line in samhita_text.strip().split('\n'):
        line = re.sub(r'RV_[\d,]+\.\d+[ac]\s*', '', line) # Remove verse numbers
        line = re.sub(r'\|\|.*', '', line) # Remove double pipe and anything after
        line = line.replace('|', '').strip() # Remove single pipe
        if line:
            cleaned_samhita_lines.append(line)
            
    # Clean and parse Padapatha lines
    # This is more complex due to the format
    full_padapatha_text = padapatha_text.replace('\n', ' ')
    # Remove metadata
    full_padapatha_text = re.sub(r'-RV_[\d:]+/\d+-', '', full_padapatha_text)
    full_padapatha_text = re.sub(r'\(RV_[\d,]+\)', '', full_padapatha_text)
    full_padapatha_text = re.sub(r'// RV_[\d,]+\.\d+\.\d+ //', 'LINEBREAK', full_padapatha_text)
    full_padapatha_text = re.sub(r'//\d+//.', 'LINEBREAK', full_padapatha_text)

    cleaned_padapatha_lines = []
    padapatha_lexicon = set()
    
    lines = full_padapatha_text.split('LINEBREAK')
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Split words by '|' and clean them up
        words = [w.strip().replace('--', '-').replace('=', '') for w in line.split('|') if w.strip()]
        cleaned_padapatha_lines.append(words)
        for word in words:
            # Normalize accents for the lexicon for broader matching,
            # though a more advanced model would use accents for disambiguation.
            # For now, we keep them to match exactly.
            padapatha_lexicon.add(word)

    return cleaned_samhita_lines, cleaned_padapatha_lines, padapatha_lexicon

def main():
    """
    Main function to run the sandhi reversal and testing process.
    """
    samhita_text = """
    RV_1,001.01a agnim īḷe purohitaṃ yajñasya devam ṛtvijam |
    RV_1,001.01c hotāraṃ ratnadhātamam ||
    RV_1,001.02a agniḥ pūrvebhir ṛṣibhir īḍyo nūtanair uta |
    RV_1,001.02c sa devāṃ eha vakṣati ||
    RV_1,001.03a agninā rayim aśnavat poṣam eva dive-dive |
    RV_1,001.03c yaśasaṃ vīravattamam ||
    RV_1,001.04a agne yaṃ yajñam adhvaraṃ viśvataḥ paribhūr asi |
    RV_1,001.04c sa id deveṣu gacchati ||
    RV_1,001.05a agnir hotā kavikratuḥ satyaś citraśravastamaḥ |
    RV_1,001.05c devo devebhir ā gamat ||
    RV_1,001.06a yad aṅga dāśuṣe tvam agne bhadraṃ kariṣyasi |
    RV_1,001.06c tavet tat satyam aṅgiraḥ ||
    RV_1,001.07a upa tvāgne dive-dive doṣāvastar dhiyā vayam |
    RV_1,001.07c namo bharanta emasi ||
    RV_1,001.08a rājantam adhvarāṇāṃ gopām ṛtasya dīdivim |
    RV_1,001.08c vardhamānaṃ sve dame ||
    RV_1,001.09a sa naḥ piteva sūnave 'gne sūpāyano bhava |
    RV_1,001.09c sacasvā naḥ svastaye ||
    """

    padapatha_text = """
    -RV_1:1/1-
    (RV_1,1)
    agnim | īḷe | puraḥ-hitam | yajñasya | devam | ṛtvijam | hotāram | ratna-dhātamam // RV_1,1.1 //
    agniḥ | pūrvebhiḥ | ṛṣi-bhiḥ | īḍyaḥ | nūtanaiḥ | uta | saḥ | devān | ā | iha | vakṣati // RV_1,1.2 //
    agninā | rayim | aśnavat | poṣam | eva | dive-dive | yaśasam | vīravat-tamam // RV_1,1.3 //
    agne | yam | yajñam | adhvaram | viśvataḥ | pari-bhūḥ | asi | saḥ | it | deveṣu | gacchati // RV_1,1.4 //
    agniḥ | hotā | kavi-kratuḥ | satyaḥ | citraśravaḥ-tamaḥ | devaḥ | devebhiḥ | ā | gamat // RV_1,1.5 //
    //1//.

    -RV_1:1/2-
    yat | aṅga | dāśuṣe | tvam | agne | bhadram | kariṣyasi | tava | it | tat | satyam | aṅgiraḥ // RV_1,1.6 //
    upa | tvā | agne | dive-dive | doṣāvastaḥ | dhiyā | vayam | namaḥ | bharantaḥ | ā | imasi // RV_1,1.7 //
    rājantam | adhvarāṇām | gopām | ṛtasya | dīdivim | vardhamānam | sve | dame // RV_1,1.8 //
    saḥ | naḥ | pitāiva | sūnave | agne | su-upāyanaḥ | bhava | sacasva | naḥ | svastaye // RV_1,1.9 //
    //2//.
    """

    # Prepare the data
    samhita_lines, padapatha_lines, lexicon = prepare_data(samhita_text, padapatha_text)
    
    print(f"--- Lexicon created with {len(lexicon)} unique words. ---")
    
    # Initialize the reverser
    reverser = SandhiReverser(lexicon)

    # Process each line and compare
    total_lines = len(samhita_lines)
    matches = 0

    for i, samhita_line in enumerate(samhita_lines):
        if i >= len(padapatha_lines):
            break
        
        # We need to process the samhita line without spaces
        samhita_input = samhita_line.replace(' ', '')
        generated_split = reverser.reverse_sandhi(samhita_input)
        
        expected_split = padapatha_lines[i]
        
        print("\n" + "="*50)
        print(f"Processing Line {i+1}")
        print(f"SAMHITA:   {samhita_line}")
        print(f"EXPECTED:  {' | '.join(expected_split)}")
        
        if generated_split:
            print(f"GENERATED: {' | '.join(generated_split)}")
            if generated_split == expected_split:
                print("RESULT:    MATCH")
                matches += 1
            else:
                print("RESULT:    MISMATCH")
        else:
            print("GENERATED: FAILED TO FIND A VALID SPLIT")
            print("RESULT:    MISMATCH")

    print("\n" + "="*50)
    print("--- Test Complete ---")
    print(f"Total Lines: {total_lines}")
    print(f"Matches:     {matches}")
    print(f"Accuracy:    {matches/total_lines:.2%}")
    print("="*50)


if __name__ == "__main__":
    main()
