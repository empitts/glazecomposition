import os
import pickle
import numpy 
import pandas as pd

def combine_pickle_files_by_prefix(directory, prefix, output_filename):
    """
    Combines pickle files with a given prefix into a single pickle file.
    Assumes each pickle file contains a Pandas DataFrame.
    """
    combined_data = pd.DataFrame()
    
    for filename in os.listdir(directory):
        if filename.startswith(prefix) and filename.endswith(".pkl"):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'rb') as f:
                try:
                    print(filename)
                    data = pickle.load(f)
                    if isinstance(data, pd.DataFrame):
                        combined_data = pd.concat([combined_data, data], ignore_index=True)
                    else:
                        print(f"Warning: Skipping {filename} as it does not contain a Pandas DataFrame.")
                except Exception as e:
                    print(f"Error loading {filename}: {e}")

    if not combined_data.empty:
        output_filepath = os.path.join(directory, output_filename)
        with open(output_filepath, 'wb') as f:
            pickle.dump(combined_data, f)
        print(f"Combined data saved to {output_filepath}")
    else:
        print("No DataFrames found to combine.")

# Example usage:
# Assuming your pickle files are in the current directory and start with "my_data_"
# combine_pickle_files_by_prefix(".", "my_data_", "combined_data.pkl")

def main():
    combine_pickle_files_by_prefix('.', 'glazy_data_2', 'glazy_data_top_production_plus.pkl')

if __name__ == "__main__":
    main()
