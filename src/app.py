import os
import uuid
import pandas as pd
from fastapi import FastAPI, Request, Form, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
import uvicorn
from src.utils import load_model, load_config, log_production_data, update_ground_truth
from src.monitor import generate_drift_report

app = FastAPI(title="MLOps API")
templates = Jinja2Templates(directory="src/templates")

config = load_config()

def get_model():
    try:
        return load_model(config["model"]["model_save_path"])
    except Exception:
        return None

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/predict")
async def predict(request: Request):
    form_data = await request.form()
    features = {k: float(v) for k, v in form_data.items() if k != 'ground_truth'}
    
    model = get_model()
    if not model:
        return templates.TemplateResponse("index.html", {"request": request, "error_message": "Model not found. Please train it first."})
        
    # Maintain correct order of features for Iris
    feature_names = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width']
    df = pd.DataFrame([[features[f] for f in feature_names]], columns=feature_names)
    
    prediction = int(model.predict(df)[0])
    prediction_id = str(uuid.uuid4())
    
    # Log to production
    log_record = features.copy()
    log_record['prediction_id'] = prediction_id
    log_record['prediction'] = prediction
    log_record['ground_truth'] = ""
    
    log_production_data(config["data"]["production_logs_path"], log_record)
    
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "prediction_result": prediction,
        "prediction_id": prediction_id
    })

@app.post("/feedback")
async def feedback(request: Request, prediction_id: str = Form(...), ground_truth: int = Form(...)):
    try:
        update_ground_truth(config["data"]["production_logs_path"], prediction_id, ground_truth)
        message = "Ground truth updated successfully!"
    except Exception as e:
        message = f"Error: {str(e)}"
        
    return templates.TemplateResponse("index.html", {"request": request, "feedback_message": message})

@app.post("/generate_report")
async def generate_report(background_tasks: BackgroundTasks):
    background_tasks.add_task(generate_drift_report)
    return {"message": "Report generation started."}

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    report_path = "reports/evidently_dashboard.html"
    if os.path.exists(report_path):
        return FileResponse(report_path)
    return HTMLResponse("<h1>Dashboard not generated yet.</h1><p>Submit some data, provide feedback, and click Generate Dashboard.</p>")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
