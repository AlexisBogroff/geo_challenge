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


class Detector:
    """
    Detect outliers and significant change in behavior
    """
    def __init__(self, data_t0, data_t1):
        self.data_t0 = data_t0
        self.data_t1 = data_t1


    def _extract_breach(self, outliers, counts, stats, ship, bound_type='bound_min'):
        """
        Extract counts that breached min or max boundaries
        """
        if bound_type == 'bound_min':
            ma_breach = counts.loc[ship] < stats[bound_type].loc[ship]
        elif bound_type == 'bound_max':
            ma_breach = counts.loc[ship] > stats[bound_type].loc[ship]
        else:
            raise ValueError

        rec = counts[ship][ma_breach]

        if len(rec) > 0:
            for date, count in rec.items():
                breach_pct = round(100 * (count - stats[bound_type].loc[ship]) / stats[bound_type].loc[ship], 2)
                d = {'ship_type': ship,
                    'date': date,
                    'count': count,
                    'bound_type': bound_type,
                    'breach_pct': breach_pct}
                outliers = outliers.append(d, ignore_index=True)

        return outliers


    def detect_large_variations(self, threshold=2, verbose=True):
        """
        Detect large variations

        Args:
            threshold: number of standard deviations allowed
            verbose (bool): activate verbosity

        Returns:
            Objects experiencing large variations
        """
        # Compute ships counts over time on reference data
        counts = self.data_t0.groupby(['ship_type', 'date']).count()['lon']
        stats = counts.groupby('ship_type').describe()
        # Compute boundaries
        stats['bound_max'] = stats['mean'] + threshold * stats['std']
        stats['bound_min'] = stats['mean'] - threshold * stats['std']

        # Compute counts from new data
        counts_new = self.data_t1.groupby(['ship_type', 'date']).count()['lon']
        # Record boundaries breaches
        outliers = pd.DataFrame(columns=['date', 'ship_type', 'count', 'breach_pct', 'bound_type'])

        for ship in stats.index:
            outliers = self._extract_breach(outliers, counts_new, stats, ship, 'bound_min')
            outliers = self._extract_breach(outliers, counts_new, stats, ship, 'bound_max')

        # ==== Return alerts ====
        if verbose:
            print(outliers)
        return outliers


    def detect_static_objects(self, verbose=True):
        """
        Detect static objects

        Args:
            verbose (bool): activate verbosity

        Returns:
            Static objects ordered by duration
        """
        raise NotImplementedError


    def detect_rare_objects(self, threshold=10, verbose=True):
        """
        Detect rare objects

        Args:
            threshold: number of periods allowed
            verbose (bool): activate verbosity

        Returns:
            Rare objects ordered by duration
        """
        raise NotImplementedError



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


def save_to_file(data, f_name):
    """
    Save data to csv file

    Args:
        data (DataFrame): Tabular data (2D)
        f_name: file name
    """
    f_name += str(datetime.now())
    extension = '.csv'
    data.to_csv(f_name + extension)
