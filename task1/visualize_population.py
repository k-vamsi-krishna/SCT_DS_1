import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
# No sys import needed if not redirecting stdout

# --- 1. Load the Datasets ---
# MODIFIED: Using absolute paths provided by the user.
# Please ensure these files are actually inside this folder and have these exact names.
base_path = "C:/Users/bharg/Downloads/API_SP.POP.TOTL_DS2_en_csv_v2_131993 (4)/"

main_data_file = base_path + "API_SP.POP.TOTL_DS2_en_csv_v2_131993.csv"
country_metadata_file = base_path + "Metadata_Country_API_SP.POP.TOTL_DS2_en_csv_v2_131993.csv"
indicator_metadata_file = base_path + "Metadata_Indicator_API_SP.POP.TOTL_DS2_en_csv_v2_131993.csv"


print(f"--- Loading datasets from: {base_path} ---")
try:
    # Main population data - skip first 4 rows as they are metadata/headers
    df_pop = pd.read_csv(main_data_file, skiprows=4)
    print(f"'{main_data_file}' loaded successfully.")

    # Country metadata
    df_country_meta = pd.read_csv(country_metadata_file)
    print(f"'{country_metadata_file}' loaded successfully.")

    # Indicator metadata (less relevant for this task, but good to acknowledge)
    df_indicator_meta = pd.read_csv(indicator_metadata_file)
    print(f"'{indicator_metadata_file}' loaded successfully.")

except FileNotFoundError as e:
    print(f"Error: A file was not found at the specified path. Please double-check the path and filenames: {e}")
    exit() # Exit if the file isn't found
except Exception as e:
    print(f"An error occurred while loading datasets: {e}")
    exit()

print("\n--- Initial Data Inspection (Main Population Data) ---")
print("Head of Population Data:")
print(df_pop.head())
print("\nInfo of Population Data:")
df_pop.info()

print("\n--- Initial Data Inspection (Country Metadata) ---")
print("Head of Country Metadata:")
print(df_country_meta.head())
print("\nInfo of Country Metadata:")
df_country_meta.info()

# --- 2. Data Preprocessing ---
print("\n--- Preprocessing Data ---")

# Drop unnecessary columns from main population data
# 'Indicator Name' and 'Indicator Code' are constant for this dataset (Total Population)
df_pop_processed = df_pop.drop(columns=['Indicator Name', 'Indicator Code'], errors='ignore')

# Melt the DataFrame to transform year columns into rows
# Columns from '1960' to '2023' (or latest year available) are population values
# Identify year columns (assuming they are numeric and after 'Country Name', 'Country Code')
year_cols = [col for col in df_pop_processed.columns if str(col).isdigit()]
id_vars = ['Country Name', 'Country Code']

# Check if year_cols is empty, if so, infer them
if not year_cols:
    print("Warning: No numeric year columns found directly. Attempting to infer.")
    # Assuming years are from 1960 to 2023 based on typical World Bank data
    potential_year_cols = [str(year) for year in range(1960, 2025)]
    year_cols = [col for col in df_pop_processed.columns if col in potential_year_cols]
    if not year_cols:
        print("Error: Could not identify year columns in the population data.")
        exit()

df_pop_melted = df_pop_processed.melt(id_vars=id_vars,
                                      value_vars=year_cols,
                                      var_name='Year',
                                      value_name='Population')

# Convert 'Year' to numeric
df_pop_melted['Year'] = pd.to_numeric(df_pop_melted['Year'], errors='coerce')

# Convert 'Population' to numeric, handling '..' as NaN
# The '..' indicates missing values in World Bank data
df_pop_melted['Population'] = pd.to_numeric(df_pop_melted['Population'], errors='coerce')

# Drop rows with missing population values
df_pop_melted.dropna(subset=['Population', 'Year'], inplace=True)
df_pop_melted['Year'] = df_pop_melted['Year'].astype(int) # Convert Year back to int

print("\nHead of Melted Population Data:")
print(df_pop_melted.head())
print("\nInfo of Melted Population Data:")
df_pop_melted.info()

# Merge with country metadata to get 'Region' for filtering aggregates
df_merged = pd.merge(df_pop_melted, df_country_meta[['Country Code', 'Region']],
                     on='Country Code', how='left')

print("\nHead of Merged Data (with Region):")
print(df_merged.head())

# Filter out aggregates (e.g., 'World', 'EU', 'High income') by checking 'Region'
# Countries usually have a defined region, aggregates often have NaN or specific names
df_countries = df_merged[df_merged['Region'].notna()].copy()

print(f"\nNumber of entries after filtering for countries: {len(df_countries)}")

# --- 3. Data Visualization – Distribution Analysis ---
print("\n--- Generating Visualizations ---")
sns.set_style("whitegrid")

# Get the latest year available in the filtered data
latest_year = df_countries['Year'].max()
print(f"\nAnalyzing population distribution for the latest year: {latest_year}")

# Filter data for the latest year
df_latest_year = df_countries[df_countries['Year'] == latest_year]

# Sort by population and select top N countries
top_n = 20 # Number of top countries to visualize
df_top_countries = df_latest_year.sort_values(by='Population', ascending=False).head(top_n)

# Plotting: Bar chart for top N most populous countries
plt.figure(figsize=(14, 8))
sns.barplot(x='Population', y='Country Name', data=df_top_countries, palette='viridis')
plt.title(f'Top {top_n} Most Populous Countries in {latest_year}')
plt.xlabel('Population') # Initial label, will be adjusted
plt.ylabel('Country')

# Adjust x-axis ticks to show population in billions or millions
max_pop = df_top_countries['Population'].max()
if max_pop >= 1_000_000_000: # If population is in billions
    plt.ticklabel_format(style='plain', axis='x') # Disable scientific notation
    plt.xticks(ticks=np.arange(0, max_pop + 1_000_000_000, 1_000_000_000),
               labels=[f'{x/1_000_000_000:.1f}' for x in np.arange(0, max_pop + 1_000_000_000, 1_000_000_000)])
    plt.xlabel('Population (Billions)')
elif max_pop >= 1_000_000: # If population is in millions
    plt.ticklabel_format(style='plain', axis='x')
    plt.xticks(ticks=np.arange(0, max_pop + 1_000_000, 1_000_000),
               labels=[f'{x/1_000_000:.0f}' for x in np.arange(0, max_pop + 1_000_000, 1_000_000)])
    plt.xlabel('Population (Millions)')

plt.tight_layout()
plt.savefig('top_countries_population_latest_year.png')
plt.show() # Display the plot directly in Thonny
print(f"Bar chart 'top_countries_population_latest_year.png' saved, showing top {top_n} countries.")

print("\n--- Analysis Complete ---")
print("The bar chart visualizes the population distribution for the most recent year across top countries.")
