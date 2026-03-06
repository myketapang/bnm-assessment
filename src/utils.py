"""Utility functions"""

import logging
import time
from pathlib import Path
from functools import wraps
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class Timer:
    """Context manager for timing"""
    
    def __init__(self, name="Operation"):
        self.name = name
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        logger.info(f"Starting: {self.name}")
        return self
    
    def __exit__(self, *args):
        self.end_time = time.time()
        elapsed = self.end_time - self.start_time
        logger.info(f"Completed {self.name} in {elapsed:.2f}s")
    
    @property
    def elapsed(self):
        if self.end_time:
            return self.end_time - self.start_time
        return None

def timing(func):
    """Decorator to time execution"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        logger.info(f"{func.__name__} completed in {elapsed:.2f}s")
        return result
    return wrapper

def load_data(filepath, **kwargs):
    """Load data from file"""
    path = Path(filepath)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    logger.info(f"Loading data from {filepath}")
    
    if path.suffix == '.parquet':
        return pd.read_parquet(filepath, **kwargs)
    elif path.suffix == '.csv':
        return pd.read_csv(filepath, **kwargs)
    elif path.suffix in ['.xlsx', '.xls']:
        return pd.read_excel(filepath, **kwargs)
    else:
        raise ValueError(f"Unsupported format: {path.suffix}")

def save_data(df, filepath, **kwargs):
    """Save data to file"""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Saving data to {filepath}")
    
    if path.suffix == '.parquet':
        df.to_parquet(filepath, **kwargs)
    elif path.suffix == '.csv':
        df.to_csv(filepath, index=False, **kwargs)
    elif path.suffix in ['.xlsx', '.xls']:
        df.to_excel(filepath, index=False, **kwargs)

def validate_data(df, required_columns=None, min_rows=1):
    """Validate dataframe"""
    
    if len(df) < min_rows:
        raise ValueError(f"Expected >= {min_rows} rows, got {len(df)}")
    
    if required_columns:
        missing = set(required_columns) - set(df.columns)
        if missing:
            raise ValueError(f"Missing columns: {missing}")
    
    logger.info(f"Validation passed: {len(df)} rows")
    return True

def ensure_dir(dirpath):
    """Ensure directory exists"""
    Path(dirpath).mkdir(parents=True, exist_ok=True)
    return Path(dirpath)

def calculate_metrics(actual, predicted):
    """Calculate error metrics"""
    
    actual = np.array(actual)
    predicted = np.array(predicted)
    
    mae = np.mean(np.abs(actual - predicted))
    rmse = np.sqrt(np.mean((actual - predicted) ** 2))
    
    ss_res = np.sum((actual - predicted) ** 2)
    ss_tot = np.sum((actual - np.mean(actual)) ** 2)
    r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
    
    return {
        'mae': mae,
        'rmse': rmse,
        'r2': r2
    }