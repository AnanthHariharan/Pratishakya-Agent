import os

def remove_empty_lines(input_filename, output_filename):
    """
    Reads an input text file, removes all empty lines, and writes the
    cleaned content to an output text file.

    An empty line is defined as a line that contains only whitespace
    or is completely blank.

    Args:
        input_filename (str): The path to the input text file.
        output_filename (str): The path where the cleaned content will be saved.
    """
    try:
        # Open the input file for reading
        with open(input_filename, 'r', encoding='utf-8') as infile:
            # Open the output file for writing
            with open(output_filename, 'w', encoding='utf-8') as outfile:
                # Iterate through each line in the input file
                for line in infile:
                    # Strip leading/trailing whitespace (including newlines)
                    # If the stripped line is not empty, write it to the output file
                    if line.strip():
                        outfile.write(line)
        print(f"Successfully processed '{input_filename}'.")
        print(f"Empty lines removed. Cleaned content saved to '{output_filename}'.")

    except FileNotFoundError:
        print(f"Error: Input file '{input_filename}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Define the input and output filenames as specified
input_file = "samhita.txt"
output_file = "rig-samhita.txt"


# Call the function to remove empty lines
remove_empty_lines(input_file, output_file)
