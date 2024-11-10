import tkinter as tk
from tkinter import filedialog
import numpy as np
import pandas as pd



def select_file():
    # Set up and hide a Tinker root window
    root = tk.Tk()
    root.withdraw()

    # Open file dialog in project folder to select raw exercise data CSV.
    file_path = filedialog.askopenfilename(initialdir='.', title='Select a CSV file', filetypes=[("CSV files", "*.csv")])
    
    return file_path

def extract_exercise(text):
    start = text.find('.') + 2  # Position after first period and space
    end = text.find('·') - 1    # Position before first bullet
    return text[start:end].strip()

def strip_invalid_values(value):
    value = str(value).strip()
    if len(value) < 4 or value == '' or any(char.isdigit() for char in value):
        return
    return value 

# Assign primary muscle group targeted to each exercise
def assign_muscle_group(unique_items):
    
    muscle_group_lookup = pd.read_csv('muscle_group_lookup.csv', header='Exercise')
    print(muscle_group_lookup)
    merged_df = pd.merge(unique_items, muscle_group_lookup, on='Exercise', how='inner')
    print(merged_df)
    return

def fuzzy_join():     
    from fuzzywuzzy import fuzz
    from fuzzywuzzy import process
    muscle_group_lookup_df = pd.read_csv('muscle_group_lookup.csv')
    unique_workouts_df = pd.read_csv('unique_workouts.csv')

    # Set the columns to be joined
    muscle_col = muscle_group_lookup_df.columns[0]
    workout_col = unique_workouts_df.columns[0]
    print(muscle_group_lookup_df.head())
    print(unique_workouts_df.head())
    matched_data = []
    threshold = 70

    for workout in unique_workouts_df[workout_col].dropna():
        # Find closest match in lookup dataframe's column
        match_info = process.extractOne(workout, muscle_group_lookup_df[muscle_col], scorer=fuzz.token_sort_ratio)
        if match_info is not None:
            match, score = match_info[0], match_info[1]
            # Only add matches above a certain similarity threshold
            if score >= threshold:
                matched_row = muscle_group_lookup_df[muscle_group_lookup_df[muscle_col] == match].iloc[0]
                matched_data.append((workout, matched_row[muscle_col], matched_row[1]))
        #     else:
        #         matched_data.append((workout, None, None))
            else:
                matched_data.append((workout, None, None))
  

    # Create a resulting dataframe
    result_df = pd.DataFrame(matched_data, columns=[workout_col, muscle_col, 'Muscle Group'])
    print(result_df.head())
    return result_df





def main():

    # Select workout export
    workouts_file_path = select_file()

    if not workouts_file_path:
        print("File selection was canceled.")
        exit()
    elif not workouts_file_path.endswith('.csv'):
        print("Selected file is not a CSV file.")
        exit()
    else:
        # Load the CSV file into a dataframe
        raw_data = pd.read_csv(workouts_file_path, header=None)

        # Apply the extract exercise function to each entry in the first column
        extract = raw_data[0].apply(extract_exercise)

        # Strip empty values form array
        extract = extract[extract.str.strip() != '']
        extract_cleaned = extract.apply(strip_invalid_values)
        

        unique_items = pd.DataFrame(extract_cleaned.unique(), columns=['Exercise']).dropna()
    

        unique_items.to_csv('unique_workouts.csv', index = False)
        exercise_and_muscle = fuzzy_join()
        exercise_and_muscle.to_csv('joined.csv', index=False)
    return

main()