"""
Reusable chart components using Plotly
"""
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import List, Dict, Any, Optional
import pandas as pd

from dashboard.config import COLORS, CHART_THEME


def create_loss_chart(
    history: Dict[str, List[float]],
    title: str = "Unlearning Loss Curves"
) -> go.Figure:
    """Create loss curve visualization"""
    fig = go.Figure()
    
    epochs = list(range(1, len(history.get("forget_loss", [])) + 1))
    
    # Add traces for each loss type
    if "forget_loss" in history:
        fig.add_trace(go.Scatter(
            x=epochs,
            y=history["forget_loss"],
            name="Forget Loss",
            line=dict(color=COLORS["danger"], width=2),
            mode="lines"
        ))
    
    if "retain_loss" in history:
        fig.add_trace(go.Scatter(
            x=epochs,
            y=history["retain_loss"],
            name="Retain Loss",
            line=dict(color=COLORS["success"], width=2),
            mode="lines"
        ))
    
    if "fisher_loss" in history:
        fig.add_trace(go.Scatter(
            x=epochs,
            y=history["fisher_loss"],
            name="Fisher Loss",
            line=dict(color=COLORS["warning"], width=2),
            mode="lines"
        ))
    
    if "total_loss" in history:
        fig.add_trace(go.Scatter(
            x=epochs,
            y=history["total_loss"],
            name="Total Loss",
            line=dict(color=COLORS["primary"], width=3),
            mode="lines"
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Epoch",
        yaxis_title="Loss",
        template=CHART_THEME["template"],
        paper_bgcolor=CHART_THEME["paper_bgcolor"],
        plot_bgcolor=CHART_THEME["plot_bgcolor"],
        font=dict(color=CHART_THEME["font_color"]),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode="x unified",
    )
    
    return fig


def create_confidence_gauge(
    confidence: float,
    threshold: float = 0.6,
    title: str = "Model Confidence"
) -> go.Figure:
    """Create confidence gauge visualization"""
    # Determine color based on confidence vs threshold
    if confidence < threshold:
        bar_color = COLORS["success"]
        status = "✅ Erased"
    else:
        bar_color = COLORS["danger"]
        status = "⚠️ Not Erased"
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=confidence * 100,
        number={"suffix": "%", "font": {"size": 40}},
        delta={"reference": threshold * 100, "relative": False},
        gauge={
            "axis": {"range": [0, 100], "ticksuffix": "%"},
            "bar": {"color": bar_color},
            "steps": [
                {"range": [0, threshold * 100], "color": "rgba(16, 185, 129, 0.2)"},
                {"range": [threshold * 100, 100], "color": "rgba(239, 68, 68, 0.2)"},
            ],
            "threshold": {
                "line": {"color": COLORS["warning"], "width": 4},
                "thickness": 0.75,
                "value": threshold * 100,
            },
        },
        title={"text": f"{title}<br><span style='font-size:0.8em;color:{bar_color}'>{status}</span>"},
    ))
    
    fig.update_layout(
        template=CHART_THEME["template"],
        paper_bgcolor=CHART_THEME["paper_bgcolor"],
        font=dict(color=CHART_THEME["font_color"]),
        height=300,
    )
    
    return fig


def create_shard_overview(
    shards: List[Dict[str, Any]],
    title: str = "SISA Shard Overview"
) -> go.Figure:
    """Create shard status overview"""
    if not shards:
        shards = [
            {"id": i, "status": "ready", "samples": 1000, "accuracy": 0.95 - i * 0.02}
            for i in range(4)
        ]
    
    df = pd.DataFrame(shards)
    
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{"type": "bar"}, {"type": "pie"}]],
        subplot_titles=("Samples per Shard", "Shard Distribution")
    )
    
    # Bar chart for samples
    fig.add_trace(
        go.Bar(
            x=[f"Shard {s['id']}" for s in shards],
            y=[s.get("samples", 1000) for s in shards],
            marker_color=COLORS["primary"],
            name="Samples",
        ),
        row=1, col=1
    )
    
    # Pie chart for distribution
    fig.add_trace(
        go.Pie(
            labels=[f"Shard {s['id']}" for s in shards],
            values=[s.get("samples", 1000) for s in shards],
            hole=0.4,
            marker_colors=[COLORS["primary"], COLORS["success"], COLORS["warning"], COLORS["info"]],
        ),
        row=1, col=2
    )
    
    fig.update_layout(
        title=title,
        template=CHART_THEME["template"],
        paper_bgcolor=CHART_THEME["paper_bgcolor"],
        plot_bgcolor=CHART_THEME["plot_bgcolor"],
        font=dict(color=CHART_THEME["font_color"]),
        showlegend=False,
        height=350,
    )
    
    return fig


def create_metrics_cards(metrics: Dict[str, Any]) -> Dict[str, go.Figure]:
    """Create mini metric indicator figures"""
    cards = {}
    
    for key, value in metrics.items():
        fig = go.Figure(go.Indicator(
            mode="number",
            value=value if isinstance(value, (int, float)) else 0,
            number={"font": {"size": 36, "color": COLORS["primary"]}},
        ))
        
        fig.update_layout(
            template=CHART_THEME["template"],
            paper_bgcolor=CHART_THEME["paper_bgcolor"],
            height=100,
            margin=dict(l=10, r=10, t=10, b=10),
        )
        
        cards[key] = fig
    
    return cards
