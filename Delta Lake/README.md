Delta Lake MERGE Implementation using Databricks

Week 7 Assignment – Delta Lake

Project Overview
This project demonstrates incremental data processing using Delta Lake in Databricks. The objective is to simulate a real-world data engineering workflow where an existing dataset is updated with new incoming records using the MERGE operation.
The assignment covers data ingestion, data cleaning, Delta table creation, generation of incremental data, merge implementation, and result validation.

Objective

Load data into a Delta table.

Perform basic data cleaning.

Generate an incremental dataset.

Apply Delta Lake MERGE operation.

Update existing records.

Insert new records.

Validate the final dataset.

Technologies Used

Databricks Community Edition

Apache Spark (PySpark)

Delta Lake

Python

Git & GitHub

Project Structure

Delta Lake/

│

├── Data/

│   └── Sample - Superstore.csv

│
├── Notebooks/

│   └── delta_scd_assignment.ipynb

│

├──Report/

│   └──Celebal_Week7_Delta_Lake_Assignment_Report.pdf

│

├── Screenshots/

│   ├── Data_cleaning/

│   ├── data_Loading/

│   ├── Final_Output/

│   ├── SCD1/

│   └── Validation/

│

│

└── README.md

Dataset

The original Superstore dataset provided during the internship was used as the master dataset.
To satisfy the assignment requirement of incremental processing, an incremental dataset was generated programmatically by:
Updating existing records
Creating new records with unique Row_ID values
This approach simulates real-world incremental data ingestion.
Workflow
Data Loading
Imported the Superstore dataset into Databricks.
Loaded the CSV file into a Spark DataFrame.
Data Cleaning
Performed basic preprocessing:
Checked for missing values
Checked for duplicate records
Renamed columns to make them Delta Lake compatible
The dataset contained no missing values or duplicate rows.
Delta Table Creation
The cleaned dataset was stored as a Delta table using overwrite mode.
This Delta table acts as the master table for future updates.
Incremental Data Creation
A second dataset was created to simulate incoming data.
The incremental dataset contains:
Updated records (existing Row_ID values)
New records (new Row_ID values)
This demonstrates a practical incremental loading scenario.
MERGE Operation
Delta Lake MERGE was used to:
Update existing records
Insert new records
The unique Row_ID column was used as the merge key to ensure accurate record matching.
Validation
After the MERGE operation, validation was performed by checking:
Final row count
Duplicate Row_ID values
Updated records
Newly inserted records
The final output confirmed that the MERGE operation completed successfully.
Key Concepts Demonstrated
Delta Lake
Delta Tables
Incremental Data Processing
MERGE INTO
Upsert Operations
Data Cleaning
Data Validation
Apache Spark DataFrames
Learning Outcomes
Through this assignment, I gained hands-on experience with:
Working in the Databricks environment
Creating and managing Delta tables
Performing incremental data processing
Understanding MERGE (Upsert) operations
Validating data after ETL processes
Building a structured data engineering workflow
Result
The project successfully demonstrates how Delta Lake performs incremental data processing by updating existing records and inserting new records into a Delta table using the MERGE operation.
This workflow closely represents modern ETL and ELT processes used in data engineering projects.
Acknowledgement
This assignment was completed as part of the Data Engineering Internship Program at Celebal Technologies to gain practical experience with Apache Spark, Databricks, and Delta Lake.

Author

Harsh Meshram

Data Engineer Intern

Celebal Technologies