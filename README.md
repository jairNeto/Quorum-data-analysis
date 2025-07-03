# Quorum Legislative Data Analysis


## Overview

This project processes legislative data from CSV files and generates two main reports:
1. **Legislators Support/Oppose Count** - Shows how many bills each legislator supported vs opposed
2. **Enhanced Bills Report** - Shows bill details with voting statistics and sponsor information

## Project Structure

```
.
├── src/
│   ├── main.py           # CLI entry point
│   └── data_processor.py # Core data processing with pandas
├── data/                 # Input CSV files
├── output/              # Generated reports
├── requirements.txt     # Python dependencies
├── Dockerfile          # Container definition
├── Makefile           # Build and run commands
└── README.md          # This file
```

## Data Structure

The application expects the following CSV files in the `data/` directory:
- `legislators.csv` - Legislator information (id, name)
- `bills.csv` - Bill information (id, title, sponsor_id)
- `votes.csv` - Vote sessions (id, bill_id)
- `vote_results.csv` - Individual voting records (id, legislator_id, vote_id, vote_type)

**Vote Types:**
- `1` = Support
- `2` = Oppose

## Quick Start

1. **Build and run all reports:**
   ```bash
   make run
   ```

2. **Run tests**
   ```bash
   make test
   ```

## Output Files

Generated in the `output/` directory:

### legislators-support-oppose-count.csv
Contains voting statistics for each legislator:
- `legislator_id` - Unique legislator identifier
- `legislator_name` - Full name with party and district
- `num_supported_bills` - Count of bills supported
- `num_opposed_bills` - Count of bills opposed

### bills.csv
Contains enhanced bill information with voting statistics:
- `id` - Bill identifier
- `title` - Bill title
- `primary_sponsor` - Sponsor's name
- `supporter_count` - Number of supporting votes
- `opposer_count` - Number of opposing votes


## Implementation Write-up

### 1. Discuss your solution's time complexity. What tradeoffs did you make?

The current solution has an overall time complexity of O(n) where n represents the size of the largest dataset. Each step (hash join, hash group-by, vectorised column assignment) is O(N) since the datasets are small.
I chose to use pandas for this implementation because the provided CSV files were relatively small, making it feasible to load entire datasets into memory for fast processing. The main tradeoff was prioritizing code simplicity and development speed over memory efficiency - pandas operations are much more readable and maintainable than manual loops, but they do consume more memory. If we were dealing with significantly larger files (millions of records), I would consider using PySpark instead, which could handle distributed processing and larger-than-memory datasets while maintaining similar operation patterns.

### 2. How would you change your solution to account for future columns that might be requested, such as "Bill Voted On Date" or "Co-Sponsors"?

For reading additional data columns like "Bill Voted On Date" or "Co-Sponsors", I wouldn't need to make any changes to the current data loading functions since pandas automatically reads all columns from CSV files. The modular design with separate loading methods for each data source makes this seamless. However, if we wanted to include these new columns in our output CSV files or create entirely new reports, we would need to either add new functions to the DataProcessor class or modify the existing `generate_legislators_support_oppose_count()` and `generate_bills_csv()` functions. The `_write_output()` method is already flexible enough to handle any DataFrame structure, so the main changes would be in the data processing and column selection logic before writing the files.

### 3. How would you change your solution if instead of receiving CSVs of data, you were given a list of legislators or bills that you should generate a CSV for?

If I received lists of legislators or bills instead of CSV files, I would create a data validation layer using Pydantic model classes for each data type (Legislator, Bill, Vote, VoteResult). These Pydantic models would ensure data integrity and provide clear schemas for the expected data structure. Once the input lists are validated through these models, I would convert them into pandas DataFrames using the validated Pydantic objects, which would allow me to reuse all the existing processing logic without modification. This approach maintains data quality through validation while preserving the efficient pandas operations for analysis and CSV generation that the current solution relies on.

### 4. How long did you spend working on the assignment?

I spent approximately 1 hour working on this assignment.
