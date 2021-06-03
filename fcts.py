"""
Functions for geo challenge alert system
"""
from datetime import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import georaster as gr
sns.set_theme()

def load_data(path, idx_col='id', date_col='date', verbose=True):
    """
    Load data

    Args:
        path (str): path to data file
        idx_col (str): column to use as index
        date_col (str): column to cast as datetime
        verbose (bool): activate verbosity

    Returns:
        data (DataFrame)
    """
    data = pd.read_csv(path, index_col=idx_col, parse_dates=[date_col])
    return data


def detect_large_variations(data_t0, data_t1, threshold=2, verbose=True):
    """
    Detect large variations

    Args:
        data_t0: initial data
        data_t1: new data
        threshold: number of standard deviations allowed
        verbose (bool): activate verbosity

    Returns:
        Objects experiencing large variations
    """
    # ==== Fit model on init data ====

    # Compute ships counts over time
    counts = data_t0.groupby(['ship_type', 'date']).count()['lon']
    stats = counts.groupby('ship_type').describe()

    # Compute boundaries
    stats['bound_max'] = stats['mean'] + threshold * stats['std']
    stats['bound_min'] = stats['mean'] - threshold * stats['std']

    # ==== Evaluate new data ====

    # Compute new counts
    counts_new = data_t1.groupby(['ship_type', 'date']).count()['lon']

    # Record boundaries breaches
    outliers = pd.DataFrame(columns=['date', 'ship_type', 'count', 'breach_pct', 'bound_type'])

    for ship in stats.index:
        # Record counts above max boundary
        ma_above_max = counts_new.loc[ship] > stats['bound_max'].loc[ship]
        rec = counts_new[ship][ma_above_max]
        if len(rec) > 0:
            for date, count in rec.items():
                breach_pct = round(100 * (count - stats['bound_max'].loc[ship]) / stats['bound_max'].loc[ship], 2)
                d = {'ship_type': ship,
                    'date': date,
                    'count': count,
                    'bound_type': 'max',
                    'breach_pct': breach_pct}
                outliers = outliers.append(d, ignore_index=True)

        # Record counts below min boundary
        ma_below_max = counts_new.loc[ship] < stats['bound_min'].loc[ship]
        rec = counts_new[ship][ma_below_max]
        if len(rec) > 0:
            for date, count in rec.items():
                breach_pct = round(100 * (count - stats['bound_min'].loc[ship]) / stats['bound_min'].loc[ship], 2)
                d = {'ship_type': ship,
                    'date': date,
                    'count': count,
                    'bound_type': 'min',
                    'breach_pct': breach_pct}
                outliers = outliers.append(d, ignore_index=True)

    # ==== Return alerts ====

    return outliers


def detect_static_objects(data_t0, data_t1, verbose=True):
    """
    Detect static objects

    Args:
        data_t0: initial data
        data_t1: new data
        verbose (bool): activate verbosity

    Returns:
        Static objects ordered by duration
    """
    raise NotImplementedError


def detect_rare_objects(data_t0, data_t1, threshold=10, verbose=True):
    """
    Detect rare objects

    Args:
        data_t0: initial data
        data_t1: new data
        threshold: number of periods allowed
        verbose (bool): activate verbosity

    Returns:
        Rare objects ordered by duration
    """
    raise NotImplementedError


def save_to_file(data, f_name):
    """
    Save data to csv file

    Args:
        data (DataFrame): Tabular data (2D)
    """
    f_name += str(datetime.now())
    extension = '.csv'
    data.to_csv(f_name + extension)
