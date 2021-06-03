"""
Functions for geo challenge alert system
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import georaster as gr
sns.set_theme()

def load_data(path, idx_col='id', date_col='stream_date'):
    """
    Load data

    Args:
        path (string): path to data file

    Returns:
        data (DataFrame)
    """
    data = pd.read_csv(path, index_col=idx_col, parse_dates=[date_col])
    return data
