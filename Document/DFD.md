flowchart TD

subgraph group_ingestion["Telemetry ingestion"]
  node_pcap["PCAP extraction<br/>[pcap_extractor.py]"]
  node_csv["Flow CSV ingestion<br/>[extract_flows.py]"]
  node_schema["Canonical schema"]
  node_capture["Synthetic capture generation"]
  node_dataset["CIC dataset preparation<br/>[prepare_dataset.py]"]
end

subgraph group_sequences["Temporal sequences"]
  node_sequences["Windowed sequences<br/>[build_sequences.py]"]
end

subgraph group_forecasting["Forecasting"]
  node_model["CNN-BiLSTM model<br/>[world_model.py]"]
  node_inference["Autoregressive forecast<br/>[inference.py]"]
  node_forecast["Risk and tactic results<br/>[inference.py]"]
  node_checkpoint[("Saved checkpoint")]
  node_knowledge["MITRE threat context<br/>[kb_mapper.py]"]
end

subgraph group_dashboard["Analyst dashboard"]
  node_dashboard["Streamlit dashboard<br/>[app.py]"]
  node_views["Forecast visualizations<br/>[components.py]"]
end

subgraph group_development["Model development"]
  node_pipeline["Pipeline launcher<br/>[run_pipeline.py]"]
  node_baseline["Logistic regression baseline"]
  node_trainer["World-model training<br/>[train.py]"]
end

node_analyst(("Analyst"))
node_telemetry["PCAP or flow CSV"]

node_analyst -->|"uploads telemetry"| node_dashboard
node_telemetry -->|"provides input"| node_dashboard
node_dashboard -->|"parses PCAP"| node_pcap
node_dashboard -->|"loads CSV"| node_csv
node_dashboard -->|"normalizes PCAP"| node_schema
node_csv -->|"normalizes flows"| node_schema
node_dashboard -->|"builds windows"| node_sequences
node_pipeline -->|"generates capture"| node_capture
node_pipeline -->|"extracts features"| node_pcap
node_pipeline -->|"builds sequences"| node_sequences
node_pipeline -->|"builds model"| node_model
node_pipeline -->|"trains model"| node_trainer
node_trainer -->|"saves weights"| node_checkpoint
node_pipeline -->|"runs evaluation"| node_baseline
node_baseline -->|"extracts features"| node_pcap
node_baseline -->|"standardizes flows"| node_schema
node_dashboard -->|"loads weights"| node_checkpoint
node_dashboard -->|"requests forecast"| node_inference
node_inference -->|"predicts states"| node_model
node_inference -->|"produces forecast"| node_forecast
node_dashboard -->|"renders results"| node_forecast
node_dashboard -->|"renders charts"| node_views
node_dataset -.->|"prepares CSV"| node_telemetry

click node_pipeline "https://github.com/gagan-long/sih2026-ai-network-attack-forecaster-/blob/main/Tool/run_pipeline.py"
click node_dashboard "https://github.com/gagan-long/sih2026-ai-network-attack-forecaster-/blob/main/Tool/app/app.py"
click node_pcap "https://github.com/gagan-long/sih2026-ai-network-attack-forecaster-/blob/main/Tool/features/pcap_extractor.py"
click node_csv "https://github.com/gagan-long/sih2026-ai-network-attack-forecaster-/blob/main/Tool/features/extract_flows.py"
click node_schema "https://github.com/gagan-long/sih2026-ai-network-attack-forecaster-/blob/main/Tool/features/canonical_schema.py"
click node_capture "https://github.com/gagan-long/sih2026-ai-network-attack-forecaster-/blob/main/Tool/scripts/generate_synthetic_pcap.py"
click node_dataset "https://github.com/gagan-long/sih2026-ai-network-attack-forecaster-/blob/main/Tool/scripts/prepare_dataset.py"
click node_sequences "https://github.com/gagan-long/sih2026-ai-network-attack-forecaster-/blob/main/Tool/features/build_sequences.py"
click node_model "https://github.com/gagan-long/sih2026-ai-network-attack-forecaster-/blob/main/Tool/models/world_model.py"
click node_inference "https://github.com/gagan-long/sih2026-ai-network-attack-forecaster-/blob/main/Tool/models/inference.py"
click node_forecast "https://github.com/gagan-long/sih2026-ai-network-attack-forecaster-/blob/main/Tool/models/inference.py"
click node_checkpoint "https://github.com/gagan-long/sih2026-ai-network-attack-forecaster-/blob/main/Tool/models/saved/best_world_model.keras"
click node_baseline "https://github.com/gagan-long/sih2026-ai-network-attack-forecaster-/blob/main/Tool/baseline/logistic_regression.py"
click node_trainer "https://github.com/gagan-long/sih2026-ai-network-attack-forecaster-/blob/main/Tool/models/train.py"
click node_knowledge "https://github.com/gagan-long/sih2026-ai-network-attack-forecaster-/blob/main/Tool/intelligence/kb_mapper.py"
click node_views "https://github.com/gagan-long/sih2026-ai-network-attack-forecaster-/blob/main/Tool/app/components.py"

classDef toneNeutral fill:#f8fafc,stroke:#334155,stroke-width:1.5px,color:#0f172a
classDef toneBlue fill:#dbeafe,stroke:#2563eb,stroke-width:1.5px,color:#172554
classDef toneAmber fill:#fef3c7,stroke:#d97706,stroke-width:1.5px,color:#78350f
classDef toneMint fill:#dcfce7,stroke:#16a34a,stroke-width:1.5px,color:#14532d
classDef toneRose fill:#ffe4e6,stroke:#e11d48,stroke-width:1.5px,color:#881337
classDef toneIndigo fill:#e0e7ff,stroke:#4f46e5,stroke-width:1.5px,color:#312e81
classDef toneTeal fill:#ccfbf1,stroke:#0f766e,stroke-width:1.5px,color:#134e4a
class node_pcap,node_csv,node_schema,node_capture,node_dataset toneBlue
class node_sequences toneAmber
class node_model,node_inference,node_forecast,node_checkpoint,node_knowledge toneMint
class node_dashboard,node_views toneRose
class node_pipeline,node_baseline,node_trainer,node_analyst,node_telemetry toneIndigo