import os

def split_rigveda_text(input_filename, samhita_filename, padapatha_filename):
    """
    Reads an input text file and splits its content into two new files.
    The first two lines go to samhita_filename, the next two to padapatha_filename,
    and this pattern alternates until the end of the input file.

    Args:
        input_filename (str): The name of the input text file (e.g., 'rigveda-combined-deltlef.txt').
        samhita_filename (str): The name of the output file for Samhita lines (e.g., 'samhita.txt').
        padapatha_filename (str): The name of the output file for Padapatha lines (e.g., 'padapatha.txt').
    """
    try:
        with open(input_filename, 'r', encoding='utf-8') as infile, \
             open(samhita_filename, 'w', encoding='utf-8') as samhita_file, \
             open(padapatha_filename, 'w', encoding='utf-8') as padapatha_file:

            line_count = 0
            while True:
                line1 = infile.readline()
                if not line1:  # End of file
                    break
                line2 = infile.readline()
                if not line2:  # End of file, but only one line was read in this pair
                    # Handle case where file ends on an odd line count for the pair
                    if line_count % 4 == 0: # If we were expecting samhita lines
                        samhita_file.write(line1)
                    else: # If we were expecting padapatha lines
                        padapatha_file.write(line1)
                    break

                if line_count % 4 == 0 or line_count % 4 == 1:
                    # Lines 0 and 1 (and 4, 5 etc.) go to samhita.txt
                    samhita_file.write(line1)
                    samhita_file.write(line2)
                else:
                    # Lines 2 and 3 (and 6, 7 etc.) go to padapatha.txt
                    padapatha_file.write(line1)
                    padapatha_file.write(line2)

                line_count += 2 # Increment by 2 as we process lines in pairs

        print(f"Successfully split '{input_filename}' into '{samhita_filename}' and '{padapatha_filename}'.")

    except FileNotFoundError:
        print(f"Error: The file '{input_filename}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Define the filenames
input_file = 'rigveda-combined-deltlef-preprocessed.txt'
samhita_output_file = 'samhita.txt'
padapatha_output_file = 'padapatha.txt'

# Run the splitting function
if __name__ == "__main__":
    # Create a dummy input file for demonstration if it doesn't exist
    if not os.path.exists(input_file):
        print(f"Creating a dummy '{input_file}' for demonstration purposes.")
        with open(input_file, 'w', encoding='utf-8') as f:
            for i in range(1, 11): # Create 10 lines of dummy data
                f.write(f"This is line {i} of the Rigveda document.\n")
        print(f"Dummy file '{input_file}' created.")

    split_rigveda_text(input_file, samhita_output_file, padapatha_output_file)
