import pandas as pd
import yaml
import os
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset

def load_config(config_path="configs/config.yaml"):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def generate_drift_report():
    print("Generating drift report...")
    config = load_config()
    
    reference_data_path = config["data"]["raw_data_path"]
    production_logs_path = config["data"]["production_logs_path"]
    
    if not os.path.exists(reference_data_path):
        print("Reference data not found. Cannot generate report.")
        return
        
    if not os.path.exists(production_logs_path):
        print("Production logs not found. Cannot generate report.")
        return
        
    ref_df = pd.read_csv(reference_data_path)
    prod_df = pd.read_csv(production_logs_path)
    
    # For Data Drift, we only want to compare the features, not target or metadata.
    # We will strip out 'target' from reference, and metadata from production.
    target_col = config.get("data", {}).get("target_col", "target")
    if target_col in ref_df.columns:
        ref_df = ref_df.drop(columns=[target_col])
        
    # Keep only the matching features in production data
    features = ref_df.columns.tolist()
    
    # Check if all features exist in production logs (in case of empty or malformed logs)
    missing = [f for f in features if f not in prod_df.columns]
    if missing:
        print(f"Production logs are missing features: {missing}")
        return
        
    prod_df = prod_df[features]
    
    # Simple Data Drift report
    report = Report(metrics=[DataDriftPreset()])
    report.run(reference_data=ref_df, current_data=prod_df, column_mapping=None)
    
    # Save report
    report_path = "reports/evidently_dashboard.html"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    report.save_html(report_path)
    print(f"Report saved to {report_path}")

if __name__ == "__main__":
    generate_drift_report()
