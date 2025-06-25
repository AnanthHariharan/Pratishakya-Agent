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
input_file = "rigveda-mandala-1.txt"
output_file = "rigveda-mandala-1-preprocessed.txt"

# --- Create a dummy input file for demonstration ---
# This part is just for testing the script if the file doesn't exist
# You can remove this block if you already have rigveda-mandala-1.txt
if not os.path.exists(input_file):
    print(f"Creating a dummy '{input_file}' for demonstration purposes...")
    dummy_content = """agnim | īḷe | puraḥ-hitam | yajñasya | devam | ṛtvijam | hotāram | ratna-dhātamam // rv_1,1.1 //

agniḥ | pūrvebhiḥ | ṛṣi-bhiḥ | īḍyaḥ | nūtanaiḥ | uta | saḥ | devān | ā | iha | vakṣati // rv_1,1.2 //

agninā | rayim | aśnavat | poṣam | eva | dive--dive | yaśasam | vīravat-tamam // rv_1,1.3 //

agne | yam | yajñam | adhvaram | viśvataḥ | pari-bhūḥ | asi | saḥ | it | deveṣu | gacchati // rv_1,1.4 //"""
    with open(input_file, 'w', encoding='utf-8') as f:
        f.write(dummy_content)
    print("Dummy file created.")
# --- End of dummy file creation ---


# Call the function to remove empty lines
remove_empty_lines(input_file, output_file)
