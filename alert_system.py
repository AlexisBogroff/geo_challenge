"""
Raise alerts on sensible ratios

Alerts:
- large variation of ships (by type)
- report static ships
- rare appearance of a ship (if a droids is detected)
- new areas organization (variation num clusters, shift in localisation)
"""
from settings import PATH_DATA_INIT, PATH_DATA_NEW
import fcts

# Load data
data_t0 = fcts.load_data(PATH_DATA_INIT)
data_t1 = fcts.load_data(PATH_DATA_NEW)

# Run detectors
fluctuant_objects = fcts.detect_large_variations(data_t0, data_t1)
print('debug', fluctuant_objects)
# static_objects = fcts.detect_static_objects(data_t0, data_t1)
# rare_objects = fcts.detect_rare_objects(data_t0, data_t1)
# area_change = fcts.detect_area_change(data_t0, data_t1)

# Save alerts to file
# fcts.save_to_file(fluctuant_objects, 'alert_large_variations')
# fcts.save_to_file(static_objects)
# fcts.save_to_file(rare_objects)
# fcts.save_to_file(area_change)
