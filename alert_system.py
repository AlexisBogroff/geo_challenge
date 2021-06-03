import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import georaster as gr
sns.set_theme()

# Load data
path_data = 'data/starships_clean.csv'
data = pd.read_csv(path_data, index_col='id', parse_dates=['stream_date'])

