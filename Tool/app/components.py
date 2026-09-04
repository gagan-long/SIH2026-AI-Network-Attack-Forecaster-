import plotly.express as px
import pandas as pd

def plot_risk_timeline(forecast_output, threshold=0.75):
    chart_df = pd.DataFrame({
        "Window Ahead (+k)": list(range(1, forecast_output["K"] + 1)),
        "Infiltration Probability": forecast_output["risk_timeline"],
        "Projected Stage": forecast_output["tactics"]
    })
    
    fig = px.line(
        chart_df, x="Window Ahead (+k)", y="Infiltration Probability",
        text="Projected Stage", markers=True, color_discrete_sequence=["#D32F2F"]
    )
    fig.add_hline(y=threshold, line_dash="dash", line_color="orange", annotation_text="Critical Escalation Threshold")
    fig.update_traces(textposition="top left", textfont=dict(size=11))
    fig.update_layout(yaxis_range=[0, 1.05], height=400, margin=dict(l=20, r=20, t=40, b=20),
                      xaxis_title="Future Time Windows", yaxis_title="Probability of Infiltration")
    return fig

def plot_feature_attribution(top_features):
    feat_df = pd.DataFrame(list(top_features.items()), columns=["Feature", "Attribution"]).sort_values("Attribution", ascending=True)
    fig = px.bar(feat_df, x="Attribution", y="Feature", orientation="h", color="Attribution", color_continuous_scale="Reds")
    fig.update_layout(height=320, showlegend=False, margin=dict(l=20, r=20, t=20, b=20), xaxis_title="Relative Impact (SHAP value)", yaxis_title="")
    return fig

def format_mitre_progression(tactics):
    distinct_tactics = []
    for t in tactics:
        if not distinct_tactics or distinct_tactics[-1] != t:
            distinct_tactics.append(t)
    return " ➔ ".join([f"**{t}**" for t in distinct_tactics])