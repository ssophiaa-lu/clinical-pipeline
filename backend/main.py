from fastapi import UploadFile, File, HTTPException, FastAPI
import pandas as pd
from io import BytesIO

app = FastAPI()

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

async def read_csv_upload(file: UploadFile) -> pd.DataFrame:
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a .csv file")

    raw = await file.read()
    try:
        df = pd.read_csv(BytesIO(raw))
    except Exception:
        raise HTTPException(status_code=400, detail="Could not parse CSV")

    return df


@app.get("/")
def root():
    return {"message": "API is "}



@app.post("/upload/preview")
async def upload_preview(file: UploadFile = File(...)):
    df = await read_csv_upload(file)

    nrows_pre_cleaned = len(df)
    df = clean_df(df)
    nrows_cleaned = len(df)
    dropped_rows = nrows_pre_cleaned - nrows_cleaned



    return {
        "filename": file.filename,
        "rows": int(df.shape[0]),
        "cols": int(df.shape[1]),
        "columns": list(df.columns),
        "head": df.head(5).to_dict(orient="records"),
        "avg_age": float(df["Age"].mean()),
        "avg_stay_length": float(df["Length of Stay"].mean()),
        "rows dropped": int(dropped_rows),

    }


def clean_df(df: pd.DataFrame) -> pd.DataFrame:

    # After reading file, return required columns not present
    missing_cols = []
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            missing_cols.append(col)
    
    if missing_cols: 
        raise HTTPException(
            status_code=400,
            detail={"Missing columns": missing_cols}
        )
    

    df["Discharge Date"] = pd.to_datetime(df["Discharge Date"], errors="coerce")
    df["Date of Admission"] = pd.to_datetime(df["Date of Admission"], errors="coerce")
    df["Length of Stay"] = (df["Discharge Date"] - df["Date of Admission"]).dt.days

    df = df[df["Length of Stay"] >= 0]
    df["Name"] = df["Name"].astype(str).str.lower()
    df["Age"] = pd.to_numeric(df["Age"], errors="coerce")
    df = df.dropna(subset=["Date of Admission", "Discharge Date", "Age", "Length of Stay"])

    return df

@app.post("/charts/conditions")
async def chart_conditions(file: UploadFile = File(...)):
    df = await read_csv_upload(file)
    df = clean_df(df)

    counts = df["Medical Condition"].value_counts().reset_index()
    counts.columns = ["condition", "count"]
    
    #     [
    #   {"condition": "asthma", "count": 3},
    #   {"condition": "diabetes", "count": 2},
    #   {"condition": "flu", "count": 1}
    # ]
    return counts.to_dict(orient="records")

@app.post("/charts/billing-by-conditions")
async def chart_conditions(file: UploadFile = File(...)):

    df = await read_csv_upload(file)
    df = clean_df(df)

    df["Billing Amount"] =  pd.to_numeric(df["Billing Amount"], errors="coerce")
    grouped_df = df.groupby("Medical Condition")["Billing Amount"].mean().reset_index()
    grouped_df.columns = ["Medical Condition", "Mean Billing Amount"]
    return grouped_df.to_dict(orient="records")
 
