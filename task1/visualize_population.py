import pandas as pd
import matplotlib.pyplot as plt

# 1. Load the Excel file (skip the first 3 header rows as per World Bank format)
file_path = r"API_SP.POP.TOTL.FE.IN_DS2_en_excel_v2_88529.xlsx"
df = pd.read_excel(file_path, sheet_name='Data', skiprows=3)

# 2. Filter for India
india_female = df[df['Country Name'] == 'India']

# 3. Extract years and population data
years = [str(year) for year in range(1960, 2025) if str(year) in india_female.columns]
population = india_female[years].values.flatten()

# 4. Plot the bar chart
plt.figure(figsize=(14, 6))
plt.bar(years, population, color='skyblue')
plt.xlabel('Year')
plt.ylabel('Female Population')
plt.title("India's Female Population Over Years (1960-2024)")
plt.xticks(rotation=45, fontsize=8)
plt.tight_layout()
plt.show()
