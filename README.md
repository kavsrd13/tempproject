# MLOps End-to-End Project

This project demonstrates a complete end-to-end MLOps pipeline using DVC, MLflow, FastAPI, Evidently AI, and Azure Container Apps.

## Features
- **Data Versioning**: Uses DVC to track `data/raw/dataset.csv` and push to Azure Blob Storage.
- **Experiment Tracking**: Uses MLflow to track parameters, metrics, and models.
- **Model Deployment**: Uses FastAPI to serve the trained model.
- **Containerization & Deployment**: Dockerized and deployed to Azure Container Apps via a shell script and GitHub Actions.
- **Monitoring**: Uses Evidently AI to track data drift and model drift. The UI includes a dashboard generator.
- **Continuous Integration/Deployment (CI/CD)**: A GitHub Actions workflow automatically trains and deploys the model whenever new data (`dataset.csv.dvc`) is pushed.

## Setup Instructions

### 1. Local Environment
Install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Update the `.env` file with your Azure and MLflow details:
```ini
AZURE_STORAGE_CONNECTION_STRING="your_azure_blob_connection_string_here"
MLFLOW_TRACKING_URI="sqlite:///mlruns.db"
API_TOKEN="Partner@123"
```

### 3. Generate Initial Data
Generate the initial Iris dataset:
```bash
python src/generate_data.py
```

### 4. Setup DVC
Initialize DVC and add your remote:
```bash
dvc init
dvc remote add -d azure_remote azure://your-container-name/dvcstore
dvc remote modify azure_remote connection_string "your_azure_blob_connection_string_here"
```

Track the data:
```bash
dvc add data/raw/dataset.csv
dvc push
```

### 5. Train Model Locally
Run the DVC pipeline:
```bash
dvc repro
```
Or run directly:
```bash
python src/train.py
```

### 6. Run the Application
Start the FastAPI server:
```bash
uvicorn src.app:app --host 0.0.0.0 --port 8000 --reload
```
Open `http://localhost:8000` in your browser. You can:
1. Make predictions
2. Provide ground truth feedback (which logs to `data/production/production_logs.csv`)
3. Generate and view the Evidently AI drift dashboard.

### 7. Deployment
The repository includes a GitHub Action `.github/workflows/train_and_deploy.yml` that will automatically train and deploy to Azure Container Apps whenever a new `dataset.csv.dvc` file is pushed to the `main` branch.

You can also run the deployment manually (make sure you are logged into Azure CLI via `az login`):
```bash
bash deploy_to_azure.sh
```
