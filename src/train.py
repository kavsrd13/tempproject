import os
import sys
import mlflow
import yaml
from dotenv import load_dotenv
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score
from utils import load_config, load_data, save_model

load_dotenv()

def train():
    print("Starting training pipeline...")
    config = load_config()
    
    # Load data
    data_path = config["data"]["raw_data_path"]
    df = load_data(data_path)
    
    target_col = config["data"]["target_col"]
    X = df.drop(columns=[target_col])
    y = df[target_col]
    
    test_size = config["data"]["test_size"]
    random_state = config["data"]["random_state"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)
    
    # Setup MLflow
    mlflow_uri = os.getenv("MLFLOW_TRACKING_URI", "sqlite:///mlruns.db")
    mlflow.set_tracking_uri(mlflow_uri)
    mlflow.set_experiment(config["mlflow"]["experiment_name"])
    
    with mlflow.start_run():
        # Hyperparameters
        C = config["model"]["C"]
        max_iter = config["model"]["max_iter"]
        
        mlflow.log_param("C", C)
        mlflow.log_param("max_iter", max_iter)
        mlflow.log_param("test_size", test_size)
        
        # Train model
        print("Training model...")
        model = LogisticRegression(C=C, max_iter=max_iter, random_state=random_state)
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, average='weighted')
        rec = recall_score(y_test, y_pred, average='weighted')
        
        print(f"Accuracy: {acc:.4f}, Precision: {prec:.4f}, Recall: {rec:.4f}")
        mlflow.log_metric("accuracy", acc)
        mlflow.log_metric("precision", prec)
        mlflow.log_metric("recall", rec)
        
        # Save and log model
        model_path = config["model"]["model_save_path"]
        save_model(model, model_path)
        
        mlflow.sklearn.log_model(model, "logistic_regression")
        print("Training completed successfully.")

if __name__ == "__main__":
    train()
