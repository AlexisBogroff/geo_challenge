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
        self.static_ships = None
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
            print('\n\nOuliters count:\n')
            print(self.count_outliers)


    def detect_static_objects(self, n_periods_min=1, smooth=None, verbose=True):
        """
        Detect static objects on the given period

        Args:
            n_periods: number of inter periods. For example:
                       - n_periods_min=1: detects all static ships (static
                                          over any duration).
                       - n_periods_min=2: detects ships that were static for
                                          at least 2 periods, i.e. 3 dates.
            smooth (int): precision to round the latitude and longitude
            verbose (bool): display results

        Returns:
            Static objects ordered by duration

        Note:
            Be careful as a low precision might consider different ships as
            a unique ship. Thus, it might consider that a ship has been static
            over multiple periods, althought the comparison is made btw 2 snaps.
            To keep information on the date, use the more restrictive function
            detect_static_objects_2_snaps.
        """
        AGG_COLS = ['lon', 'lat', 'ship_type']

        # Merge data
        data = pd.concat([self.data_t0, self.data_t1], ignore_index=True)

        if smooth:
            data = smooth_positions(data, smooth)

        # Mask static rows
        ma_duplicated_pos = data[AGG_COLS].duplicated()

        # Count number of static periods by static ship
        static = data[ma_duplicated_pos][AGG_COLS].value_counts()

        # Filter on duration
        ma_duration = static >= n_periods_min
        static = static[ma_duration]

        # Set to attribute
        self.static_ships = static

        if verbose:
            print(f'\n\nStatic ships over at least {n_periods_min} periods:\n')
            print(static)


    def detect_static_objects_2_snaps(self, smooth=None, verbose=True):
        """
        Detect static objects between two snapshots

        Args:
            smooth (int): precision to round the latitude and longitude
            verbose (bool): display results

        Returns:
            Static objects ordered by duration

        Note:
            Do not use on more than two snapshots at a time, as results
            might not be as expected. Idem when using low precision (smooth).
        """
        data_t0 = self.data_t0.copy()
        data_t1 = self.data_t1.copy()

        if smooth:
            data_t0 = smooth_positions(data_t0, threshold=smooth)
            data_t1 = smooth_positions(data_t1, threshold=smooth)

        # Get static ships
        static = pd.merge(data_t0, data_t1, how='inner', on=['lon', 'lat'])
        self.static_ships = static

        if verbose:
            print('\n\nStatic ships between 2 periods:\n')
            print(static)


    def export(self, path, ext='csv', outliers=True, static=True):
        """
        Save data to csv file

        Args:
            data (DataFrame): Tabular data (2D)
            f_name: file name
            ext: file extension

        Note:
            Only export count_outliers for now. Others not yet implemented.
        """
        f_name = path + datetime.now().strftime("%Y%m%d_%H%M%S")

        if outliers:
            # Export outliers
            f_name_outliers = f_name + '_outliers'
            self.count_outliers.sort_values('date', ascending=False, inplace=True)
            self.count_outliers.to_csv(f_name_outliers + '.' + ext)

        if static:
            # Export static ships:
            f_name_static = f_name + '_static'
            self.static_ships.to_csv(f_name_static + '.' + ext)



def filter_on_date(data, date_col, date_min=None, date_max=None):
    """
    Extract data corresponding to specified date range

    Args:
        data (DataFrame)
        date_col: name of column with dates
        date_min (str or datetime): min date included
        date_max (str or datetime): max date excluded

    Returns:
        data filtered
    """
    if date_min:
        ma_min = data[date_col] >= date_min
        data = data[ma_min]
    if date_max:
        ma_max = data[date_col] < date_max
        data = data[ma_max]
    return data


def load_data(path, idx_col='id', date_col='date', verbose=True, **kwargs):
    """
    Load data

    Args:
        path (str): path to data file
        idx_col (str): column to use as index
        date_col (str): column to cast as datetime
        verbose (bool): activate verbosity
        kwargs: date parameters of filter_on_date

    Returns:
        data (DataFrame)
    """
    data = pd.read_csv(path, index_col=idx_col, parse_dates=[date_col])
    data = filter_on_date(data, date_col, **kwargs)
    return data


def smooth_positions(data, threshold):
    smooth = data.copy()
    smooth['lon'] = round(smooth['lon'], threshold)
    smooth['lat'] = round(smooth['lat'], threshold)
    return smooth
