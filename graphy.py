import pandas as pd
import plotly.express as px

df = pd.read_csv('findings/thresholded100-control-data-flow-split.csv')

files = list(df.columns)[1:]

# TODO: add code to plot the percentages