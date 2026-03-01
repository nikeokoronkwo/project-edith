from fastapi import FastAPI

# This creates your backend application
app = FastAPI(title="Project Sentinel API")

# A dummy endpoint returning the exact data format your spec requires
@app.get("/api/sectors")
def get_sectors():
    return [
        {
            "sector_id": "Sector Alpha",
            "current_threat_score": 85,
            "top_risk_resource": "Clean Water",
            "stock_summary": "Critically Low"
        },
        {
            "sector_id": "Sector Bravo",
            "current_threat_score": 42,
            "top_risk_resource": "Medical Kits",
            "stock_summary": "Stable"
        }
    ]

@app.get("/")
def read_root():
    return {"message": "Sentinel Backend is running!"}