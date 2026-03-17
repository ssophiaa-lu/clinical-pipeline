# Imports
from fastapi import UploadFile, File, HTTPException, FastAPI
import pandas as pd

# read uploaded file bytes as a file-like object for pandas
from io import BytesIO

# Initialize FastAPI application
app = FastAPI()

# Define schema requirements for uploaded datasets
# This acts as basic validation to ensure the dataset contains expected fields
REQUIRED_COLUMNS = [
    "Name",
    "Age",
    "Gender",
    "Medical Condition",
    "Date of Admission",
    "Discharge Date",
    "Billing Amount",
    "Admission Type",
]

# utility function to read and parse uploaded CSV files
# separating this logic improves code reuse across multiple API endpoints
async def read_csv_upload(file: UploadFile) -> pd.DataFrame:

    # validate file type before attempting to parse
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a .csv file")

    # read uploaded file as raw bytes
    raw = await file.read()

    # convert raw bytes into a Pandas df
    try:
        df = pd.read_csv(BytesIO(raw))
    except Exception:
        # if parsing fails -> return a client error
        raise HTTPException(status_code=400, detail="Could not parse CSV")

    return df


# verify API is running
@app.get("/")
def root():
    return {"message": "API is running"}


# endpoint for uploading and previewing dataset stats
@app.post("/upload/preview")
async def upload_preview(file: UploadFile = File(...)):

    # extract: read uploaded CSV file
    df = await read_csv_upload(file)
    nrows_pre_cleaned = len(df)

    # transform: clean and normalize dataset
    df = clean_df(df)
    nrows_cleaned = len(df)

    # calc num invalid rows removed
    dropped_rows = nrows_pre_cleaned - nrows_cleaned

    # return dataset preview and summary statistics
    return {
        "filename": file.filename,
        "rows": int(df.shape[0]),
        "cols": int(df.shape[1]),
        "columns": list(df.columns),

        # return first 5 rows so frontend can preview dataset
        "head": df.head(5).to_dict(orient="records"),

        "avg_age": float(df["Age"].mean()),
        "avg_stay_length": float(df["Length of Stay"].mean()),

        "rows dropped": int(dropped_rows),
    }


# transform + clean data
def clean_df(df: pd.DataFrame) -> pd.DataFrame:

    # Validate schema: ensure required columns exist
    missing_cols = []
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            missing_cols.append(col)

    if missing_cols:
        raise HTTPException(
            status_code=400,
            detail={"Missing columns": missing_cols}
        )

    # convert date columns into datetime objects
    df["Discharge Date"] = pd.to_datetime(df["Discharge Date"], errors="coerce")
    df["Date of Admission"] = pd.to_datetime(df["Date of Admission"], errors="coerce")

    # compute patient length of hospital stay
    df["Length of Stay"] = (df["Discharge Date"] - df["Date of Admission"]).dt.days

    df = df[df["Length of Stay"] >= 0]
    df["Name"] = df["Name"].astype(str).str.lower()

    # convert numeric fields 
    df["Age"] = pd.to_numeric(df["Age"], errors="coerce")

    # drop rows with missing critical values
    df = df.dropna(subset=["Date of Admission", "Discharge Date", "Age", "Length of Stay"])

    return df


# endpoint returning counts of patients per medical condition
@app.post("/charts/conditions")
async def chart_conditions(file: UploadFile = File(...)):

    # extract dataset
    df = await read_csv_upload(file)

    # transform dataset
    df = clean_df(df)

    # aggregate: count number of patients by condition
    counts = df["Medical Condition"].value_counts().reset_index()
    counts.columns = ["condition", "count"]

    # return JSON format for frontend 
    return counts.to_dict(orient="records")


# endpoint returning average billing per condition
@app.post("/charts/billing-by-conditions")
async def chart_conditions(file: UploadFile = File(...)):

    # extract 
    df = await read_csv_upload(file)

    # transform dataset
    df = clean_df(df)

    # convert billing to numeric for aggregation
    df["Billing Amount"] = pd.to_numeric(df["Billing Amount"], errors="coerce")

    # aggregate: compute mean billing per medical condition
    grouped_df = df.groupby("Medical Condition")["Billing Amount"].mean().reset_index()

    grouped_df.columns = ["Medical Condition", "Mean Billing Amount"]

    # return JSON response for visualization layer
    return grouped_df.to_dict(orient="records")