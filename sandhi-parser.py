import re
import unicodedata

class ImprovedSandhiReverser:
    """
    Improved Vedic sandhi reverser with better rule organization and accuracy.
    Uses a more systematic approach to handle different types of sandhi.
    """

    def __init__(self, padapatha_lexicon):
        """
        Initialize with lexicon and organized sandhi rules.
        """
        self.lexicon = padapatha_lexicon
        self.memo = {}
        
        # Vowel classifications for sandhi rules
        self.vowels = set('aāiīuūṛṝḷḹeēoōaiāī auāū')
        self.short_vowels = set('aiuṛḷ')
        self.long_vowels = set('āīūṝḹ')
        self.voiced_consonants = set('gghḍddhbβjjhyrlvhṃṅṇnm')
        self.unvoiced_consonants = set('kkhṭttthpphjśṣs')
        
        # Organize rules by priority - more specific first
        self.sandhi_rules = [
            # Avagraha rules (highest priority)
            self._reverse_avagraha_patterns,
            
            # Vowel sandhi rules
            self._reverse_vṛddhi_sandhi,
            self._reverse_guṇa_sandhi,
            self._reverse_dīrgha_sandhi,
            self._reverse_yaṇ_sandhi,
            
            # Visarga sandhi rules
            self._reverse_visarga_before_voiced,
            self._reverse_visarga_before_unvoiced,
            self._reverse_visarga_special,
            
            # Consonant sandhi rules
            self._reverse_consonant_clusters,
            self._reverse_nasal_assimilation,
            
            # Final vowel modifications
            self._reverse_final_vowel_changes,
        ]

    def reverse_sandhi(self, samhita_line):
        """
        Main entry point for sandhi reversal.
        """
        self.memo = {}
        # Remove spaces and normalize text
        text = samhita_line.replace(' ', '').strip()
        if not text:
            return []
            
        results = self._find_splits(text)
        return results[0] if results else None

    def _find_splits(self, text):
        """
        Core recursive splitting function with improved memoization.
        """
        if not text:
            return [[]]
        
        if text in self.memo:
            return self.memo[text]

        all_splits = []

        # Try direct lexicon match first
        if text in self.lexicon:
            all_splits.append([text])

        # Apply sandhi rules in order of priority
        for rule_func in self.sandhi_rules:
            try:
                splits = rule_func(text)
                for first_word, remainder in splits:
                    if first_word in self.lexicon:
                        rest_splits = self._find_splits(remainder)
                        for rest_split in rest_splits:
                            all_splits.append([first_word] + rest_split)
            except Exception:
                continue  # Skip problematic rules

        # Try simple prefix matching as fallback
        for i in range(1, min(len(text), 15)):  # Limit search to reasonable word lengths
            prefix = text[:i]
            if prefix in self.lexicon:
                suffix = text[i:]
                suffix_splits = self._find_splits(suffix)
                for suffix_split in suffix_splits:
                    all_splits.append([prefix] + suffix_split)

        self.memo[text] = all_splits
        return all_splits

    def _reverse_avagraha_patterns(self, text):
        """
        Handle avagraha (elision) patterns more comprehensively.
        """
        splits = []
        
        # Pattern: o' -> aḥ + a (most common)
        if "o'" in text:
            pos = text.find("o'")
            if pos > 0:
                prefix = text[:pos]
                word1 = prefix + 'aḥ'
                remainder = 'a' + text[pos+2:]
                splits.append((word1, remainder))
        
        # Pattern: e' -> e + a (pūrvarūpa)
        if "e'" in text:
            pos = text.find("e'")
            if pos >= 0:
                word1 = text[:pos+1]  # Keep the 'e'
                remainder = 'a' + text[pos+2:]
                splits.append((word1, remainder))
        
        # Pattern: a' -> a + a (rare but possible)
        if "a'" in text:
            pos = text.find("a'")
            if pos >= 0:
                word1 = text[:pos+1]
                remainder = 'a' + text[pos+2:]
                splits.append((word1, remainder))
                
        return splits

    def _reverse_vṛddhi_sandhi(self, text):
        """
        Handle vṛddhi (strengthening) sandhi: ai/au combinations.
        """
        splits = []
        
        # ai -> a + i/e/ai
        if 'ai' in text:
            pos = text.find('ai')
            if pos > 0:
                prefix = text[:pos]
                word1 = prefix + 'a'
                remainder_base = text[pos+2:]
                
                # Try different possibilities
                for start_vowel in ['i', 'e', 'ai']:
                    remainder = start_vowel + remainder_base
                    if self._has_valid_continuation(remainder):
                        splits.append((word1, remainder))
        
        # au -> a + u/o/au
        if 'au' in text:
            pos = text.find('au')
            if pos > 0:
                prefix = text[:pos]
                word1 = prefix + 'a'
                remainder_base = text[pos+2:]
                
                for start_vowel in ['u', 'o', 'au']:
                    remainder = start_vowel + remainder_base
                    if self._has_valid_continuation(remainder):
                        splits.append((word1, remainder))
                        
        return splits

    def _reverse_guṇa_sandhi(self, text):
        """
        Handle guṇa (strengthening) sandhi: e/o combinations.
        """
        splits = []
        
        # e -> a + i
        if 'e' in text:
            pos = text.find('e')
            if pos > 0:
                prefix = text[:pos]
                word1 = prefix + 'a'
                remainder = 'i' + text[pos+1:]
                if self._has_valid_continuation(remainder):
                    splits.append((word1, remainder))
        
        # o -> a + u
        if 'o' in text:
            pos = text.find('o')
            if pos > 0:
                prefix = text[:pos]
                word1 = prefix + 'a'
                remainder = 'u' + text[pos+1:]
                if self._has_valid_continuation(remainder):
                    splits.append((word1, remainder))
                    
        return splits

    def _reverse_dīrgha_sandhi(self, text):
        """
        Handle dīrgha (lengthening) sandhi: similar vowels combine.
        """
        splits = []
        
        # Long vowel mappings
        mappings = {
            'ā': 'a', 'ī': 'i', 'ū': 'u', 'ṝ': 'ṛ', 'ḹ': 'ḷ'
        }
        
        for long_vowel, short_vowel in mappings.items():
            if long_vowel in text:
                pos = text.find(long_vowel)
                if pos > 0:
                    # Try splitting at different positions around the long vowel
                    for split_pos in range(max(0, pos-3), min(len(text), pos+4)):
                        if split_pos > 0 and split_pos < len(text):
                            word1 = text[:split_pos-1] + short_vowel
                            remainder = short_vowel + text[split_pos:]
                            if word1 in self.lexicon:
                                splits.append((word1, remainder))
                                
        return splits

    def _reverse_yaṇ_sandhi(self, text):
        """
        Handle yaṇ sandhi: semivowels from vowels.
        """
        splits = []
        
        # y -> i (before vowels)
        for i, char in enumerate(text):
            if char == 'y' and i > 0 and i < len(text) - 1:
                if text[i+1] in self.vowels:
                    word1 = text[:i] + 'i'
                    remainder = text[i+1:]
                    if word1 in self.lexicon:
                        splits.append((word1, remainder))
        
        # v -> u (before vowels)
        for i, char in enumerate(text):
            if char == 'v' and i > 0 and i < len(text) - 1:
                if text[i+1] in self.vowels:
                    word1 = text[:i] + 'u'
                    remainder = text[i+1:]
                    if word1 in self.lexicon:
                        splits.append((word1, remainder))
                        
        return splits

    def _reverse_visarga_before_voiced(self, text):
        """
        Handle visarga changes before voiced consonants.
        """
        splits = []
        
        # r from visarga before voiced consonants
        for i, char in enumerate(text):
            if char == 'r' and i > 0 and i < len(text) - 1:
                if text[i+1] in self.voiced_consonants:
                    # Check if this could be from visarga
                    if text[i-1] in 'aiuṛ':
                        word1 = text[:i] + 'ḥ'
                        remainder = text[i+1:]
                        if word1 in self.lexicon:
                            splits.append((word1, remainder))
        
        # Deletion of visarga before voiced sounds (with compensation)
        for i in range(len(text)-1):
            if text[i] in self.vowels and text[i+1] in self.voiced_consonants:
                # Try adding visarga
                word1 = text[:i+1] + 'ḥ'
                remainder = text[i+1:]
                if word1 in self.lexicon:
                    splits.append((word1, remainder))
                    
        return splits

    def _reverse_visarga_before_unvoiced(self, text):
        """
        Handle visarga changes before unvoiced consonants.
        """
        splits = []
        
        # s, ś, ṣ from visarga
        for sibilant in ['s', 'ś', 'ṣ']:
            for i, char in enumerate(text):
                if char == sibilant and i > 0:
                    word1 = text[:i] + 'ḥ'
                    remainder = text[i:]
                    if word1 in self.lexicon:
                        splits.append((word1, remainder))
                        
        return splits

    def _reverse_visarga_special(self, text):
        """
        Handle special visarga patterns.
        """
        splits = []
        
        # Common patterns like 'ḥ' -> 'r' in specific contexts
        # This is a simplified version - actual rules are more complex
        
        return splits

    def _reverse_consonant_clusters(self, text):
        """
        Handle consonant cluster simplifications.
        """
        splits = []
        
        # This is a complex area - implementing basic cases
        # Double consonants that might be simplified
        doubles = ['tt', 'kk', 'pp', 'cc', 'ṭṭ']
        
        for double in doubles:
            if double in text:
                pos = text.find(double)
                if pos > 0:
                    # Try splitting with single consonant
                    word1 = text[:pos+1]  # Keep first consonant
                    remainder = text[pos+1:]  # Start with second consonant
                    if word1 in self.lexicon:
                        splits.append((word1, remainder))
                        
        return splits

    def _reverse_nasal_assimilation(self, text):
        """
        Handle nasal assimilation patterns.
        """
        splits = []
        
        # Simplified nasal assimilation rules
        # n -> ṅ before velars, ṇ before cerebrals, etc.
        
        return splits

    def _reverse_final_vowel_changes(self, text):
        """
        Handle final vowel modifications.
        """
        splits = []
        
        # Cases where final vowels are modified in sandhi
        # This is quite complex and context-dependent
        
        return splits

    def _has_valid_continuation(self, remainder):
        """
        Check if remainder can potentially form valid words.
        """
        if not remainder:
            return True
        
        # Check if any word in lexicon starts with the beginning of remainder
        for length in range(1, min(len(remainder) + 1, 10)):
            prefix = remainder[:length]
            if any(word.startswith(prefix) for word in self.lexicon):
                return True
        
        return False


def prepare_data(samhita_text, padapatha_text):
    """
    Improved data preparation with better cleaning.
    """
    # Clean Samhita lines
    cleaned_samhita_lines = []
    for line in samhita_text.strip().split('\n'):
        line = re.sub(r'RV_[\d,]+\.\d+[ac]\s*', '', line)
        line = re.sub(r'\|\|.*', '', line)
        line = line.replace('|', '').strip()
        if line:
            cleaned_samhita_lines.append(line)
    
    # Clean Padapatha with better parsing
    full_padapatha_text = padapatha_text.replace('\n', ' ')
    full_padapatha_text = re.sub(r'-RV_[\d:]+/\d+-', '', full_padapatha_text)
    full_padapatha_text = re.sub(r'\(RV_[\d,]+\)', '', full_padapatha_text)
    full_padapatha_text = re.sub(r'//[^/]+//', 'LINEBREAK', full_padapatha_text)
    
    cleaned_padapatha_lines = []
    padapatha_lexicon = set()
    
    lines = full_padapatha_text.split('LINEBREAK')
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Better word splitting and cleaning
        words = []
        for word in line.split('|'):
            word = word.strip()
            if word and word not in ['', '//', '//1//']:
                # Clean up word formatting
                word = re.sub(r'--+', '-', word)  # Multiple dashes to single
                word = word.replace('=', '')
                words.append(word)
                padapatha_lexicon.add(word)
        
        if words:
            cleaned_padapatha_lines.append(words)
    
    return cleaned_samhita_lines, cleaned_padapatha_lines, padapatha_lexicon


def main():
    """
    Main function with improved testing and output.
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

    # Prepare data
    samhita_lines, padapatha_lines, lexicon = prepare_data(samhita_text, padapatha_text)
    
    print(f"--- Improved Sandhi Reverser ---")
    print(f"Lexicon size: {len(lexicon)} unique words")
    print(f"Sample lexicon words: {list(lexicon)[:10]}...")
    
    # Initialize reverser
    reverser = ImprovedSandhiReverser(lexicon)
    
    # Test processing
    total_lines = min(len(samhita_lines), len(padapatha_lines))
    matches = 0
    partial_matches = 0

    for i in range(total_lines):
        samhita_line = samhita_lines[i]
        expected_split = padapatha_lines[i]
        
        # Process without spaces
        samhita_input = samhita_line.replace(' ', '')
        generated_split = reverser.reverse_sandhi(samhita_input)
        
        print(f"\n{'='*60}")
        print(f"Line {i+1}")
        print(f"SAMHITA:   {samhita_line}")
        print(f"INPUT:     {samhita_input}")
        print(f"EXPECTED:  {' | '.join(expected_split)}")
        
        if generated_split:
            print(f"GENERATED: {' | '.join(generated_split)}")
            
            if generated_split == expected_split:
                print("RESULT:    ✓ EXACT MATCH")
                matches += 1
            else:
                # Check for partial matches
                common_words = set(generated_split) & set(expected_split)
                if common_words:
                    print(f"RESULT:    ~ PARTIAL MATCH ({len(common_words)}/{len(expected_split)} words)")
                    partial_matches += 1
                else:
                    print("RESULT:    ✗ NO MATCH")
        else:
            print("GENERATED: [FAILED - No valid split found]")
            print("RESULT:    ✗ PARSING FAILED")

    print(f"\n{'='*60}")
    print("FINAL RESULTS:")
    print(f"Total lines processed: {total_lines}")
    print(f"Exact matches: {matches} ({matches/total_lines:.1%})")
    print(f"Partial matches: {partial_matches} ({partial_matches/total_lines:.1%})")
    print(f"Overall success rate: {(matches + partial_matches)/total_lines:.1%}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()