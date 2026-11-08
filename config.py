"""
SeniorSite AI - Configuration Settings
"""

import os
from pathlib import Path

# Project Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = BASE_DIR / "seniorsite.duckdb"

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)

# Ollama Configuration
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.1"

# Census API (get free key at https://api.census.gov/data/key_signup.html)
# For demo, we use sample data - add your key here for live data
CENSUS_API_KEY = os.getenv("CENSUS_API_KEY", "")

# Geographic Focus - Texas Triangle Counties
TEXAS_TRIANGLE_COUNTIES = {
    # Houston Metro
    "48201": {"name": "Harris County", "metro": "Houston"},
    "48157": {"name": "Fort Bend County", "metro": "Houston"},
    "48339": {"name": "Montgomery County", "metro": "Houston"},
    "48167": {"name": "Galveston County", "metro": "Houston"},
    
    # Dallas-Fort Worth Metro
    "48113": {"name": "Dallas County", "metro": "DFW"},
    "48439": {"name": "Tarrant County", "metro": "DFW"},
    "48085": {"name": "Collin County", "metro": "DFW"},
    "48121": {"name": "Denton County", "metro": "DFW"},
    
    # San Antonio Metro (for future expansion)
    "48029": {"name": "Bexar County", "metro": "San Antonio"},
}

# Senior Housing Industry Metrics Thresholds
METRICS_CONFIG = {
    "target_age_cohorts": {
        "independent_living": 75,
        "assisted_living": 80,
        "memory_care": 85
    },
    "income_thresholds": {
        "independent_living": 48000,  # Annual household income
        "assisted_living": 60000,
        "memory_care": 72000
    },
    "penetration_benchmarks": {
        "undersupplied": 0.08,  # Below 8%
        "balanced": 0.12,       # 8-12%
        "saturated": 0.15       # Above 15%
    },
    "proximity_standards": {
        "hospital_miles": 10,
        "competitor_miles": 5
    }
}

# Site Scoring Weights (default - user can adjust)
DEFAULT_SCORING_WEIGHTS = {
    "demographic": 0.40,    # Population growth, age distribution
    "market": 0.35,         # Penetration rate, competitor density
    "accessibility": 0.25   # Healthcare proximity, amenities
}
