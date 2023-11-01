import os
import pandas as pd

# Set directory path to folder containing csv files
dir_path = 'year_data'

# List to store each dataframe
dataframes = []

# Loop through each csv file in directory
for file in os.listdir(dir_path):
    if file.endswith('.csv'):
        # Read csv file into dataframe
        data = pd.read_csv(os.path.join(dir_path, file))
        # Add dataframe to list
        dataframes.append(data)

# Combine all dataframes using concat (more efficient than append in a loop)
combined_data = pd.concat(dataframes, ignore_index=True)

# Write combined data dataframe to new csv file in the current directory (or specify another directory)
combined_data.to_csv('combined_data.csv', index=False)
print('Data copied to file')
combined_data.info()
