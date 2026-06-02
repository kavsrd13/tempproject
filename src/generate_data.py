import os
import pandas as pd
from sklearn.datasets import load_iris
import yaml

def generate_data():
    print("Generating initial dataset...")
    with open("configs/config.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    out_path = config["data"]["raw_data_path"]
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    
    # Load Iris dataset (4 features, easy for UI)
    data = load_iris()
    df = pd.DataFrame(data.data, columns=['sepal_length', 'sepal_width', 'petal_length', 'petal_width'])
    df['target'] = data.target
    
    df.to_csv(out_path, index=False)
    print(f"Dataset generated and saved to {out_path}")

if __name__ == "__main__":
    generate_data()

if __name__ == "__main__":
    generate_data()
