# Clinical Data Engineering Pipeline

I built a full-stack ETL data pipeline for ingesting, validating, and analyzing clinical healthcare datasets. The system uses a FastAPI backend for data processing and a Streamlit frontend for interactive exploration and visualization.
Users can upload CSV datasets, automatically clean and validate the data, compute summary statistics, and generate charts to analyze medical conditions and billing patterns.

## Tech Stack
### Backend
- Python
- FastAPI
- Pandas

### Frontend
- Streamlit
- Altair

### Other Tools
- REST APIs
- CSV file processing

## Features
- Upload and preview clinical datasets
- Schema validation for required dataset columns
- Data cleaning and normalization
- Derived Length of Stay metric
- Aggregation endpoints for analytics
- Interactive charts for exploring patient conditions and billing trends

## API Endpoints
- /upload/preview	- Uploads and validates a dataset and returns summary statistics
- /charts/conditions - Returns patient counts grouped by medical condition
- /charts/billing-by-conditions	- Returns average billing amount grouped by medical condition

## Demo Workflow
- Upload a clinical CSV dataset through the Streamlit interface
- The FastAPI backend validates and cleans the dataset
- Summary statistics and dataset preview are generated
- Interactive charts visualize patient conditions and billing trends

## Running the Project
### Install Dependencies
```pip install fastapi uvicorn pandas streamlit altair requests```
### Start the Backend
```uvicorn main:app --reload```

Backend runs at:
http://127.0.0.1:8000

Start the Frontend
```streamlit run app.py```
