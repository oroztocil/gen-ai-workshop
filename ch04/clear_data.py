import pandas as pd
import sys

def remove_newlines_in_quotes(input_file, output_file):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(input_file, dtype=str)

    # Replace newline characters within quoted strings
    df = df.map(lambda x: x.replace('\n', ' ') if isinstance(x, str) else x)

    # Write the modified DataFrame back to a new XLSX file
    df.to_excel(output_file, index=False)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python clear_data.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = input_file.replace('.csv', '_cleared.xlsx')

    remove_newlines_in_quotes(input_file, output_file)
