"""
Report alerts on sensible metrics

Alerts:
- variation of ships count (by type)
- static ships between two snaps, or on the given period
"""
import part_3_4_settings as stng
from part_3_4_fcts import Detector, load_data

# Load data
data_t0 = load_data(stng.PATH_DATA_TOT, date_max=stng.DATE_MIN)
data_t1 = load_data(stng.PATH_DATA_TOT, date_min=stng.DATE_MIN,
                                        date_max=stng.DATE_MAX)

# Init detector
detector = Detector(data_t0, data_t1)

# Run scans
detector.detect_large_variations(threshold=1.7)
detector.detect_static_objects(n_periods_min=1, smooth=5)

# Save alerts to file
detector.export(stng.PATH_ALERTS)
