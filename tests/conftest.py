import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

@pytest.fixture
def sample_data():
    import pandas as pd
    return pd.DataFrame({
        'date': pd.date_range('2020-01-01', periods=100),
        'value': range(100),
    })

@pytest.fixture
def temp_dir(tmp_path):
    return tmp_path