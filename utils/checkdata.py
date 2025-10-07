import pickle
import pandas as pd
import numpy as np

def main():
    file_path = './glazy_data_top_production_plus.pkl'

    try:

        with open(file_path, 'rb') as file:
            data = pickle.load(file)

            # Set display options to show full content
            pd.set_option('display.max_rows', None)  # Display all rows
            pd.set_option('display.max_columns', None) # Display all columns
            pd.set_option('display.width', 1000) # Adjust display width for better readability

            #print(data)
            print(len(data))
            print(data.columns)
            print(data.loc[data.index[600]])
            #print(data.iloc[15])

            #print(data['Reviews'].apply(lambda x: len(x) == 0).sum())
            print(data['ImageTotal'].sum())

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred while reading the pickle file: {e}")



if __name__ == "__main__":

    main()
