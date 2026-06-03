# End-to-End MLOps Pipeline

Welcome to the **End-to-End MLOps Pipeline**! This project demonstrates a production-ready machine learning lifecycle, completely automated from data versioning to cloud deployment.

## 🌍 Live Production Environment
The application is fully deployed and accessible at: 
**👉 [Live API & Dashboard](https://mlops-api.orangecoast-8f02d54b.centralus.azurecontainerapps.io)**

---

## 🏗️ Architecture & Tech Stack

This project integrates several industry-standard tools to create a robust MLOps workflow:

1. **Data Versioning (DVC + Azure Blob Storage):** Large datasets and models are tracked by Data Version Control (DVC) and securely stored in Azure Blob Storage. Git only tracks the tiny `.dvc` metadata pointers.
2. **Experiment Tracking (MLflow):** All model parameters, hyperparameters, and accuracy metrics are logged locally using MLflow for easy comparison across training runs.
3. **Model Serving & UI (FastAPI):** The trained model is served via a high-performance FastAPI backend. A custom HTML/CSS frontend is provided to make predictions, capture user feedback (ground truth), and trigger monitoring reports.
4. **Data & Model Drift Monitoring (Evidently AI):** As production data rolls in, Evidently AI automatically compares it against the baseline training data to generate interactive HTML reports highlighting data drift.
5. **CI/CD Automation (GitHub Actions):** Pushing new data triggers a fully automated GitHub Actions workflow.
6. **Cloud Deployment (Docker + Azure Container Apps):** The GitHub Action builds a Docker image, pushes it to Azure Container Registry (ACR), and instantly deploys it as a serverless Azure Container App.

---

## 🚀 How the Automation Works (CI/CD)

The true magic of this project is the CI/CD pipeline. Here is how you can trigger a full retraining and deployment cycle without ever leaving your terminal:

1. **Modify the Data:** Change some rows in your local `data/raw/dataset.csv`.
2. **Push Data to Azure (DVC):**
   ```bash
   dvc add data/raw/dataset.csv
   dvc push
   ```
   *(This uploads the heavy data to Azure Blob Storage and updates the `dataset.csv.dvc` file)*
3. **Trigger the Pipeline (Git):**
   ```bash
   git add data/raw/dataset.csv.dvc
   git commit -m "Updated dataset for retraining"
   git push origin main
   ```
   
**What happens next?** 
GitHub Actions automatically wakes up, pulls your newly uploaded data from Azure, runs `src/train.py` to train a fresh model, packages the new model into a Docker container, and deploys it live to Azure!

---

## 💻 Local Development Setup

If you want to run the project locally on your machine:

**1. Clone and Setup Environment**
```bash
git clone https://github.com/your-username/your-repo-name.git
cd mlops_project
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

**2. Pull Data from Azure**
Make sure your `.env` file contains your `AZURE_STORAGE_CONNECTION_STRING`, then run:
```bash
dvc pull data/raw/dataset.csv.dvc
```

**3. Train the Model locally**
```bash
python src/train.py
```

**4. Start the Application**
```bash
uvicorn src.app:app --host 0.0.0.0 --port 8000 --reload
```
Open `http://localhost:8000` in your browser. This will automatically start the MLflow server in the background, which you can access via the button on the UI!

---

## 📈 Monitoring Features

The deployed application features a built-in monitoring loop:
1. **Predict:** Users submit feature data and receive a prediction.
2. **Feedback:** Users can submit the actual correct answer ("ground truth") for their specific Prediction ID.
3. **Monitor:** Clicking "Generate Dashboard" calculates the drift between the new production data and the original training data using **Evidently AI**.

*Author: Krishna Dwivedi & Antigravity AI*