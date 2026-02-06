"""
Dashboard Configuration
"""
import os

# API Settings
API_BASE_URL = os.getenv("AMNESIA_API_URL", "http://localhost:8000")
API_V1_PREFIX = "/api/v1"

# Dashboard Settings
DASHBOARD_TITLE = "🧠 Amnesia VMUaaS"
DASHBOARD_ICON = "🧠"
PAGE_TITLE = "Amnesia Dashboard"

# Polling intervals (seconds)
REFRESH_INTERVAL = 5
JOB_POLL_INTERVAL = 2

# Chart colors
COLORS = {
    "primary": "#6366f1",
    "success": "#10b981", 
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "info": "#3b82f6",
    "background": "#0f172a",
    "surface": "#1e293b",
    "text": "#f1f5f9",
    "muted": "#94a3b8",
}

# Chart theme
CHART_THEME = {
    "template": "plotly_dark",
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font_color": COLORS["text"],
}
