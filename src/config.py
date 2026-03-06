"""Configuration management"""

import os
from pathlib import Path
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Config:
    """Base configuration"""
    
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = BASE_DIR / "data"
    OUTPUT_DIR = BASE_DIR / "outputs"
    LOG_DIR = BASE_DIR / "logs"
    
    RAW_DATA_DIR = DATA_DIR / "raw"
    PROCESSED_DATA_DIR = DATA_DIR / "processed"
    
    REPORTS_DIR = OUTPUT_DIR / "reports"
    FIGURES_DIR = OUTPUT_DIR / "figures"
    DASHBOARDS_DIR = OUTPUT_DIR / "dashboards"
    
    # Create directories
    for dir_path in [RAW_DATA_DIR, PROCESSED_DATA_DIR, REPORTS_DIR, FIGURES_DIR, DASHBOARDS_DIR, LOG_DIR]:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # API endpoints
    KIJANG_URL = "https://data.kijang.net"
    GOV_MY_URL = "https://data.gov.my"
    PARLIMEN_URL = "https://www.parlimen.gov.my"
    
    # Analysis parameters
    BLOOD_DONOR_COHORT_DAYS = 365
    OUTLIER_ZSCORE_THRESHOLD = 3.0
    OUTLIER_IQR_MULTIPLIER = 1.5
    
    # SARA parameters
    SARA_MONTHLY_ALLOWANCE = 200
    SARA_DAILY_CALORIC_TARGET = 2000
    SARA_DAILY_PROTEIN_TARGET = 50
    
    # Cache
    ENABLE_CACHE = os.getenv("ENABLE_CACHE", "true").lower() == "true"
    CACHE_TIMEOUT = int(os.getenv("CACHE_TIMEOUT", "3600"))
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///bnm_assessment.db")
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Testing
    TESTING = False

class DevelopmentConfig(Config):
    """Development"""
    DEBUG = True
    LOG_LEVEL = "DEBUG"

class ProductionConfig(Config):
    """Production"""
    DEBUG = False
    LOG_LEVEL = "INFO"

class TestingConfig(Config):
    """Testing"""
    TESTING = True
    DATABASE_URL = "sqlite:///:memory:"

env = os.getenv("ENVIRONMENT", "development").lower()
if env == "production":
    config = ProductionConfig()
elif env == "testing":
    config = TestingConfig()
else:
    config = DevelopmentConfig()