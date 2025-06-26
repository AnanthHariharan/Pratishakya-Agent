import os

def split_rigveda_text_by_start_char(input_filename, samhita_filename, padapatha_filename):
    """
    Reads an input text file and splits its content into two new files
    based on the first character of each line.
    Lines starting with a number go to samhita_filename.
    Lines starting with a letter go to padapatha_filename.

    Args:
        input_filename (str): The name of the input text file (e.g., 'rigveda-combined-deltlef.txt').
        samhita_filename (str): The name of the output file for lines starting with numbers (e.g., 'samhita.txt').
        padapatha_filename (str): The name of the output file for lines starting with letters (e.g., 'padapatha.txt').
    """
    try:
        with open(input_filename, 'r', encoding='utf-8') as infile, \
             open(samhita_filename, 'w', encoding='utf-8') as samhita_file, \
             open(padapatha_filename, 'w', encoding='utf-8') as padapatha_file:

            for line in infile:
                # Strip leading/trailing whitespace to get to the first significant character
                stripped_line = line.strip()

                if not stripped_line:
                    # Skip empty lines
                    continue

                first_char = stripped_line[0]

                if first_char.isdigit():
                    samhita_file.write(line)
                elif first_char.isalpha():
                    padapatha_file.write(line)
                else:
                    # Optional: Handle lines that don't start with a number or a letter
                    # For example, you could print a warning or write them to a separate log.
                    print(f"Skipping line that does not start with a number or letter: {line.strip()}")

        print(f"Successfully split '{input_filename}' into '{samhita_filename}' (lines starting with numbers) "
              f"and '{padapatha_filename}' (lines starting with letters).")

    except FileNotFoundError:
        print(f"Error: The file '{input_filename}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Define the filenames
input_file = 'combined-svara.txt'
samhita_output_file = 'samhita.txt'
padapatha_output_file = 'padapatha.txt'

# Run the splitting function
if __name__ == "__main__":
    # Create a dummy input file for demonstration if it doesn't exist
    if not os.path.exists(input_file):
        print(f"Creating a dummy '{input_file}' for demonstration purposes.")
        with open(input_file, 'w', encoding='utf-8') as f:
            f.write("1. This is the first Samhita line.\n")
            f.write("A. This is the first Padapatha line.\n")
            f.write("2. Another Samhita line.\n")
            f.write("B. Another Padapatha line.\n")
            f.write("3. Third Samhita entry.\n")
            f.write("C. Third Padapatha entry.\n")
            f.write("   Whitespace then starts with a letter.\n") # Line starting with whitespace then letter
            f.write("- A line starting with a symbol.\n") # This line will be skipped
            f.write("4. Final Samhita line.\n")
            f.write("D. Final Padapatha line.\n")
        print(f"Dummy file '{input_file}' created.")

    split_rigveda_text_by_start_char(input_file, samhita_output_file, padapatha_output_file)
