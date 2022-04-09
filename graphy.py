import plotly.express as px
import pandas as pd
import os

directory = '/Users/pratyushavi/Developer/CSE/CSE 420/Project/results_Wed_Apr__6_10:43:11_2022'

for filename in os.listdir(directory):
    df = pd.read_csv(os.path.join(directory, filename))
    data = []
    branch_counter = 0
    for i in df['isBranch']:
        if (i):
            branch_counter += 1
        data.append(branch_counter)
    fig = px.line(data)
    fig.show()
    print(branch_counter/len(data))