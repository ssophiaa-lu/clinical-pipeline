# Clinical Data Engineering ETL Pipeline

I built a full-stack ETL data pipeline for ingesting, validating, and analyzing clinical healthcare datasets. The system uses a FastAPI backend for data processing and a Streamlit frontend for interactive exploration and visualization.
Users can upload CSV datasets, automatically clean and validate the data, compute summary statistics, and generate charts to analyze medical conditions and billing patterns.

## DEMO 

<div>
    <a href="https://www.loom.com/share/4a8b0166a58d4d85afb6ba6b4c37ccf9">
      <p>Clinical Data Engineering ETL Pipeline - Watch Video</p>
    </a>
    <a href="https://www.loom.com/share/4a8b0166a58d4d85afb6ba6b4c37ccf9">
      <img style="max-width:300px;" src="https://cdn.loom.com/sessions/thumbnails/4a8b0166a58d4d85afb6ba6b4c37ccf9-ef96d0534aceb8ca-full-play.gif#t=0.1">
    </a>
  </div>

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


## Running the Project (Docker)

### Prerequisites
- Install Docker
- Install Docker Compose (included with Docker Desktop)

### Run the Full Application
```bash
docker compose up --build
```
## Running the Project (without Docker)
### Install Dependencies
```pip install fastapi uvicorn pandas streamlit altair requests```
## Running the Project

This project has two components:

- **FastAPI backend** for data processing
- **Streamlit frontend** for visualization

You will run them in **two separate terminals**.

---

### 1. Start the Backend (FastAPI)

Open a terminal and run:

```
cd clinical-pipeline/backend
uvicorn main:app --reload
```

The API server will run at:

http://127.0.0.1:8000
### 2. Start the Frontend (Streamlit)

Open a new terminal tab and run:
```
cd clinical-pipeline/frontend
streamlit run app.py
```

The Streamlit app will run at:

http://localhost:8501
