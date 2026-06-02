import pandas as pd
import pickle
import os
import yaml

def load_config(config_path="configs/config.yaml"):
    # Resolve relative paths from the project root (parent of this file's directory)
    if not os.path.isabs(config_path):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(project_root, config_path)
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def load_data(data_path):
    if not os.path.isabs(data_path):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_path = os.path.join(project_root, data_path)
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Data file {data_path} not found.")
    return pd.read_csv(data_path)

def save_model(model, model_path):
    if not os.path.isabs(model_path):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        model_path = os.path.join(project_root, model_path)
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    with open(model_path, "wb") as f:
        pickle.dump(model, f)
    print(f"Model saved to {model_path}")

def load_model(model_path):
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file {model_path} not found.")
    with open(model_path, "rb") as f:
        return pickle.load(f)

def log_production_data(log_path, record):
    """
    Append a dictionary record to the production logs CSV.
    """
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    df = pd.DataFrame([record])
    
    if not os.path.exists(log_path):
        df.to_csv(log_path, index=False)
    else:
        df.to_csv(log_path, mode='a', header=False, index=False)
        
def update_ground_truth(log_path, prediction_id, ground_truth):
    """
    Update the production log with the actual ground truth for a given prediction_id.
    """
    if not os.path.exists(log_path):
        raise FileNotFoundError("Production log not found.")
    
    df = pd.read_csv(log_path)
    if 'prediction_id' not in df.columns:
        raise ValueError("prediction_id column missing in logs.")
        
    mask = df['prediction_id'] == prediction_id
    if not mask.any():
        raise ValueError(f"prediction_id {prediction_id} not found in logs.")
        
    df.loc[mask, 'ground_truth'] = ground_truth
    df.to_csv(log_path, index=False)
