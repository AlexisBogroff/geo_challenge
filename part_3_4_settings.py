"""
Settings for geo challenge alert system
"""
PATH_ALERTS = 'data/alerts/'
PATH_DATA_TOT = 'data/starships_clean.csv'
PATH_DATA_INIT = 'data/starships_slice_init.csv'
PATH_DATA_NEW_1 = 'data/starships_slice_new_1.csv'
PATH_DATA_NEW_2 = 'data/starships_slice_new_2.csv'
PATH_DATA_SNAP_1 = 'data/starships_snap_1.csv'
PATH_DATA_SNAP_2 = 'data/starships_snap_2.csv'

# Reduct noise by lowering the precision
SMOOTH = 5

# Data range to use [date_min, date_max[
DATE_MIN = '2020-01-01'
DATE_MAX = '2020-10-01'
