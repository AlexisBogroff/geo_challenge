"""
Functions for geo challenge alert system
"""
from datetime import datetime
import numpy as np
import pandas as pd


class Detector:
    """
    Detect outliers and significant change in behavior
    """
    def __init__(self, data_t0, data_t1):
        self.data_t0 = data_t0
        self.data_t1 = data_t1
        self.count_outliers = pd.DataFrame(columns=['date',
                                                    'ship_type',
                                                    'count',
                                                    'breach_pct',
                                                    'bound_type'])


    def _extract_breach(self, counts, stats, ship, bound_type='bound_min'):
        """
        Extract counts that breached min or max boundaries

        Args:
            counts:
            stats (DataFrame): statistics (mean, std) of counts over time
            ship (str): ship type to filter data
            bound_type (str): should be one of bound_min or bound_max
        """
        # Build mask to filter outliers
        if bound_type == 'bound_min':
            ma_breach = counts.loc[ship] < stats[bound_type].loc[ship]
        elif bound_type == 'bound_max':
            ma_breach = counts.loc[ship] > stats[bound_type].loc[ship]
        else:
            raise ValueError

        # Get records that breached the boundary
        records = counts[ship][ma_breach]

        if len(records) > 0:
            # Append to previous records (and add breach percentage)
            for date, count in records.items():

                bound = stats[bound_type].loc[ship]
                breach_pct = (count - bound) / bound  * 100
                breach_pct_rounded = round(breach_pct, 2)

                rec = {'ship_type': ship,
                       'date': date,
                       'count': count,
                       'bound_type': bound_type,
                       'breach_pct': breach_pct_rounded}

                self.count_outliers = self.count_outliers.append(rec, ignore_index=True)


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
        for ship in stats.index:
            self._extract_breach(counts_new, stats, ship, 'bound_min')
            self._extract_breach(counts_new, stats, ship, 'bound_max')

        if verbose:
            print(self.count_outliers)


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


    def export(self, f_name='alerts', ext='csv'):
        """
        Save data to csv file

        Args:
            data (DataFrame): Tabular data (2D)
            f_name: file name
            ext: file extension

        Note:
            Only export count_outliers for now. Others not yet implemented.
        """
        f_name += '_' + datetime.now().strftime("%Y%m%d_%H%M%S")
        self.count_outliers.to_csv(f_name + '.' + ext)



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
