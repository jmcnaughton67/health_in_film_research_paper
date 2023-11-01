import openpyxl
import csv
from collections import OrderedDict

# Load the workbook and get active worksheet
workbook = openpyxl.load_workbook('topic_terms.xlsx')
worksheet = workbook.active



# SETTING UP KEY TERMS
print('Setting up key terms...')
# Create an empty dictionary to store the key term groups
key_term_groups = {}

# Loop through each row in the worksheet
for row in worksheet.iter_rows():
    # Get the name of the key term group from the first cell in the row
    group_name = row[0].value
    
    # Create a list to store the key terms for the current group
    key_terms = []
    
    # Loop through each cell in the row (starting from the second cell)
    for cell in row[1:]:
        # If the cell is not empty, add its value to the list of key terms for the current group
        if cell.value:
            key_terms.append(cell.value)
    
    # Add the current group to the dictionary of key term groups
    key_term_groups[group_name] = key_terms
    print(f'Added {group_name} to key term groups')


 # Convert key terms to lowercase
    for group_name, key_terms in key_term_groups.items():
        key_term_groups[group_name] = [key_term.lower() for key_term in key_terms]




# DATASET CLEANING
print('Cleaning the dataset...')
# Create an empty ordered dictionary to store the count of key terms for each year
year_counts = OrderedDict()

# Convert the release year to an integer
def convert_year_to_int(year):
    return int(float(year.rstrip('0').rstrip('.')))


with open('combined_dataset.csv', 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    rows = [row for row in reader]  # Convert the reader to a list to allow multiple iterations

    # Convert the release year to an integer
    for row in rows:
        row['release_year'] = convert_year_to_int(row['release_year'])

    # Now, since you've modified the release years in 'rows' directly, you can just use it to populate the year_counts dictionary:
    for row in rows:
        year = row['release_year']
        year_counts[year] = {}

    print(year_counts)


# COUNTING KEY TERMS
print('Counting key terms...')

# For each year - check every film's plot for key terms and add them to counts
with open('combined_dataset.csv', 'r') as csvfile:
    rows = list(csv.DictReader(csvfile))
    
    for year in year_counts.keys():
        # Filter the rows to only include films from the current year
        sorted_rows = [row for row in rows if int(float(row['release_year'])) == year]
        print('Checking year: '+str(year))
        print('Number of Films in this year: ', len(sorted_rows))

        for row in sorted_rows:
            plot = row['plot']
            words = plot.split()

            # Loop through each key term group
            for group_name, key_terms in key_term_groups.items():
                group_count = 0

                for word in words:
                    # If the word is a key term in the current group, increment the count for the group
                    if word.lower() in key_terms:
                        group_count += 1
                        print(f'Found {word} in {group_name} in the film {row["title"]}')

                # If the current group has at least one key term in the plot text, increment the count for the corresponding year in the dictionary
                if group_count > 0:
                    if group_name not in year_counts[year]:
                        year_counts[year][group_name] = 0

                    # Now update the count
                    year_counts[year][group_name] += group_count


## OUTPUT RESULTS
print('Writing results to csv file...')
# Write the count of key term groups for each year to a csv file
with open('topic_counts.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    # Write the header row
    writer.writerow(['Year'] + list(key_term_groups.keys()))
    # Write the data rows
    for year, group_counts in sorted(year_counts.items()):
        row = [year] + [group_counts.get(group_name, 0) for group_name in key_term_groups.keys()]
        writer.writerow(row)
