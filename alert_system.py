"""
Raise alerts on sensible ratios

Alerts:
- large variation of ships (by type)
- report static ships
- rare appearance of a ship (if a droids is detected)
- new areas organization (variation num clusters, shift in localisation)
"""
from settings import PATH_DATA_INIT, PATH_DATA_NEW
from fcts import Detector, load_data

# Load data
data_t0 = load_data(PATH_DATA_INIT)
data_t1 = load_data(PATH_DATA_NEW)

# Init detector
detector = Detector(data_t0, data_t1)

# Run scans
detector.detect_large_variations(threshold=1.7)
# static_objects = detector.detect_static_objects()
# rare_objects = detector.detect_rare_objects()
# area_change = detector.detect_area_change()

# Save alerts to file
detector.export()
