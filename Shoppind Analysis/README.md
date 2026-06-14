\#Basic Data Exploration and Cleaning using Pandas



\-Objective



The objective of this project is to perform basic data exploration and data cleaning using the Pandas library in Python. The project demonstrates loading a dataset, understanding its structure, handling missing values, removing duplicate records, performing basic data operations, creating derived features, generating visualizations, and exporting a cleaned dataset for further analysis.



\-Dataset Used



File: Combined\_dataset.csv



The dataset contains product-level information including pricing, ratings, brand details, discounts, category, and other attributes related to an e-commerce shopping platform.





\-Libraries Used



pandas — Data loading, cleaning, and manipulation

numpy — Numerical operations

matplotlib — Plotting and visualization

seaborn — Statistical data visualization



Project Workflow



1\. Load Dataset



The CSV file was loaded into a Pandas DataFrame using pd.read\_csv().



pythondf = pd.read\_csv(file\_path)



Column names were standardized by converting them to lowercase and removing extra whitespace.



2\. Data Exploration



The following exploratory operations were performed:



Displayed first five rows using head()

Displayed last five rows using tail()

Checked dataset dimensions using shape

Listed all column names

Inspected data types using dtypes

Generated dataset information using info()

Produced descriptive statistics using describe(include='all')



These steps helped in understanding the structure, data types, and overall quality of the data.





3\. Missing Value Analysis



Missing values were identified using:



pythondf.isnull().sum()



Actions performed:



Removed completely empty rows using dropna(how='all')

Filled missing numeric values with the column median

Filled missing text or categorical values with "Unknown"



This ensured data consistency without losing excessive information.





4\. Duplicate Removal



Duplicate records were identified using:



pythondf.duplicated().sum()



All duplicates were removed using:



pythondf.drop\_duplicates(inplace=True)



This improved data quality and prevented redundant records from skewing analysis results.





5\. Convert Columns to Numeric



Price-related and rating columns were explicitly converted to numeric format to handle any string formatting or special characters present in the raw data:



pythondf\[col] = pd.to\_numeric(df\[col].astype(str).str.replace(r'\[^0-9.\\-]', '', regex=True), errors='coerce')



Columns converted: initial\_price, discount, final\_price, rating, ratings\_count





6\. Basic Data Operations



Row Filtering



Products with a final price greater than 1000 were filtered:



pythonexpensive\_products = df\[df\['final\_price'] > 1000]



Column Selection



Relevant columns were selected for focused analysis:



pythonselected\_cols = \['title', 'category', 'initial\_price', 'final\_price', 'rating', 'ratings\_count']





7\. Feature Engineering



Three new derived columns were created.



a. Price Difference



Represents the discount amount saved by the customer:



pythondf\['price\_difference'] = df\['initial\_price'] - df\['final\_price']



b. Popularity Score



A metric combining rating and number of ratings to measure overall product popularity:



pythondf\['popularity'] = df\['rating'] \* df\['ratings\_count']



c. Total Amount



Represents total value of a product order calculated as price multiplied by quantity:



pythondf\['total\_amount'] = df\['final\_price'] \* df\['quantity']



Note: If the dataset does not contain a quantity column, total\_amount defaults to final\_price as a fallback.





8\. Analysis



Univariate Analysis



Individual column statistics were computed for final\_price and rating using .describe() to understand distribution, mean, and spread of each variable.



Bivariate Analysis



Correlation between final\_price and rating was calculated using .corr() to understand whether higher-priced products tend to receive better or worse ratings.



Category-Level Analysis



Average final price was computed per category and sorted in descending order to identify high-value product segments:



pythondf.groupby('category')\['final\_price'].mean().sort\_values(ascending=False)





9\. Visualizations



The following plots were created to represent trends and patterns in the data:





Histogram of final\_price to show the distribution of product prices

Boxplot of final\_price to detect price outliers

Bar Chart of average final\_price per category to compare categories by price

Scatter Plot of final\_price vs rating to visualize the relationship between price and rating







10\. Key Insights





Top 10 categories by product count were identified

Average and maximum final price were computed across all products

Average rating across all products was computed

Total revenue was estimated using the total\_amount column

Average saving per product was computed using price\_difference





11\. Business Implications



Pricing Strategy — High-priced categories should be prioritized for seasonal discount campaigns to drive volume without heavy margin loss.

Product Recommendations — Products with high popularity scores are strong candidates for homepage featuring and search ranking boosts.

Discount Management — Large price differences between initial and final price indicate aggressive discounting. These SKUs should be monitored for profit margin erosion over time.

Quality Control — Categories or products with consistently low ratings need supplier review, quality checks, or should be delisted to protect brand trust.

Inventory Planning — The total\_amount column reveals which products drive the most revenue. High total amount products should maintain strong stock availability.

Premium Segment Targeting — Categories with few products but high average price represent premium segments. These need targeted marketing rather than broad discount offers.





12\. Export Cleaned Dataset



The final cleaned and enriched dataset was exported using:



pythondf.to\_csv(output\_path, index=False)



Output file: Cleaned\_Combined\_dataset.csv





Output Files





Data\_CLEANING AND Exploration.ipynb — Complete Jupyter Notebook with all code and outputs

Cleaned\_Combined\_dataset.csv — Final cleaned and feature-engineered dataset

README.md — Project documentation





Final Dataset Summary



Missing values remaining: 0

Duplicate rows remaining: 0

New columns added: price\_difference, popularity, total\_amount





Conclusion



The project successfully demonstrates fundamental Pandas operations including data loading, exploration, type conversion, missing value handling, duplicate removal, row filtering, column selection, feature engineering, statistical analysis, visualization, and data export. Business implications were derived from the cleaned data to demonstrate real-world applicability. The final cleaned dataset is ready for further analysis, modelling, or dashboard integration.

Share

