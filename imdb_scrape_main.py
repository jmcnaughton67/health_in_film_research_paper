import requests
from bs4 import BeautifulSoup
import pandas as pd
from time import sleep
from random import randint
from fake_useragent import UserAgent
import os

# Function to generate a random user agent header
def random_user_agent_header():
    ua = UserAgent()
    return {
        'Accept-Language': 'en-us,en;q=0.8',
        'User-Agent': str(ua.random)
    }


# Function to fetch summary from IMDB
def fetch_synopsis(url, headers):
    sleep(randint(3, 10))  # Random delay before making a request
    with requests.Session() as session:
        response = session.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to connect to IMDb for ID: {url} - Error Code: {response.status_code}", flush=True)
            return ''

        soup = BeautifulSoup(response.text, 'html.parser')
        plot_data = soup.findAll('div', attrs={'class': 'ipc-html-content-inner-div'})
        descriptions = [div.get_text(strip=True) for div in plot_data]
        return ' '.join(descriptions)



# Function to scrape IMDb data for a specific year
def scrape_imdb(year, num_entries):
    movie_name = []
    year_list = []
    movie_link = []
    synopsis_list = []

    start = 1
    while len(movie_name) < num_entries:
        url = f'https://www.imdb.com/search/title/?title_type=feature&year={year}-01-01,{year}-12-31&start={start}&sort=boxoffice_gross_us,desc'
        headers = random_user_agent_header()  # Use a random user agent for this request too
        page = requests.get(url, headers=headers)  # Pass headers
        sleep(randint(2, 6))  # Random delay before next request
        if page.status_code != 200:
            print('Failed to connect to IMDb - Error Code:', page.status_code, flush=True)
            break

        print(f"Scraping starting from movie {start}", flush=True)
        soup = BeautifulSoup(page.text, 'html.parser')
        movie_data = soup.findAll('div', attrs={'class': 'lister-item mode-advanced'})

        for store in movie_data:
            if len(movie_name) == num_entries:
                break  # Stop once we have enough movies
            print(len(movie_name), flush=True)
            # Movie Name
            name = str(store.h3.a.text)
            movie_name.append(name)
            print(name, flush=True)

            # IMDb ID and Plot Summary Link
            imdb_id = store.h3.a['href'].split('/')[2]
            plot_summary_url = f'https://www.imdb.com/title/{imdb_id}/plotsummary?ref_=tt_stry_pl#synopsis'
            movie_link.append(plot_summary_url)  # appending the URL to movie_link list

            # Movie Release Year
            year_of_release = f'{year}'
            year_list.append(year_of_release)
            print(year_of_release, flush=True)

            # movie Synopsis
            synopsis_header = random_user_agent_header()
            current_synopsis = fetch_synopsis(plot_summary_url, synopsis_header)  # pass plot_summary_url directly
            synopsis_list.append(current_synopsis)  # append the fetched synopsis

        start += 50

    # Store data in a DataFrame
    df = pd.DataFrame({
        'Title': movie_name[:num_entries],
        'Year': year_list[:num_entries],
        'Movie URL': movie_link[:num_entries],
        'Synopsis': synopsis_list[:num_entries]  # uncommented this line to include synopsis
    })
    return df

# Parameter Specifications
years_to_scrape = [1945, 1951]
num_entries_to_scrape = 5
csv_file = f'imdb_top_{num_entries_to_scrape}_movies_combined.csv'
dir_name = 'year_data' # Define the directory where CSV files will be stored

# Create an empty master DataFrame to hold all the results
master_df = pd.DataFrame()

# Create directory if it does not exist
if not os.path.exists(dir_name):
    os.makedirs(dir_name)

# Loop through the years to scrape for movie summaries
for year_to_scrape in years_to_scrape:
    # Use the function to scrape IMDb data for a specified year
    result_df = scrape_imdb(year_to_scrape, num_entries_to_scrape)

    # Define the name of the new CSV file for the current year
    csv_file = os.path.join(dir_name, f'imdb_top_{year_to_scrape}.csv')

    # Save the current year's data to a new CSV file in the specified directory
    result_df.to_csv(csv_file, index=False)

    # Print out a message to indicate the CSV file has been created
    print(f"Data for {year_to_scrape} has been written to {csv_file}", flush=True)

    # Append the current year's results to the master DataFrame (if you still want to keep it in memory)
    master_df = pd.concat([master_df, result_df], ignore_index=True)
