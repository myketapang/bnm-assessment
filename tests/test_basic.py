import pytest
import pandas as pd
import numpy as np

def test_sample_data(sample_data):
    assert len(sample_data) == 100
    assert 'date' in sample_data.columns

def test_dataframe_operations():
    df = pd.DataFrame({'col': [1, 2, 3]})
    assert len(df) == 3
    assert df['col'].sum() == 6

def test_numpy_operations():
    arr = np.array([1, 2, 3, 4, 5])
    assert arr.mean() == 3.0
    assert arr.sum() == 15

if __name__ == '__main__':
    pytest.main([__file__])