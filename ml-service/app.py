from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from src.predict import PolicyAnalyzer

app = FastAPI(title="Privacy & Consent Policy Analyzer API", version="1.0")

# Enable CORS for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Analyzer Instance
analyzer = PolicyAnalyzer()

class ClauseRequest(BaseModel):
    clause_text: str

@app.get("/")
def read_root():
    return {"status": "online", "model_loaded": analyzer.model_loaded}

@app.post("/analyze")
def analyze_clause(request: ClauseRequest):
    if not request.clause_text or not request.clause_text.strip():
        raise HTTPException(status_code=400, detail="Clause text cannot be empty.")
    
    try:
        results = analyzer.analyze_clause(request.clause_text)
        return results
    except Exception as e:
        print(f"[!] Error during inference: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Inference Engine Error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)