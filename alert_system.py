"""
Raise alerts on sensible metrics

Alerts:
- variation of ships count (by type)
- static ships
- (not implemented) rare appearance of a ship (if a droids is detected)
- (not implemented) new areas organization (evol num clusters, shift position)
"""
import settings as stng
from fcts import Detector, load_data

# Load data
data_t0 = load_data(stng.PATH_DATA_TOT, date_max=stng.DATE_MIN)
data_t1 = load_data(stng.PATH_DATA_TOT, date_min=stng.DATE_MIN, date_max=stng.DATE_MAX)
# data_t0 = load_data(stng.PATH_DATA_SNAP_1)
# data_t1 = load_data(stng.PATH_DATA_SNAP_2)

# Init detector
detector = Detector(data_t0, data_t1)

# Run scans
detector.detect_large_variations(threshold=1.7)
detector.detect_static_objects(n_periods_min=1, smooth=5)
detector.detect_static_objects_2_snaps(smooth=3)

# Save alerts to file
detector.export(stng.PATH_ALERTS)
