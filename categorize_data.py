import networkx as nx
import pandas as pd
import os
import matplotlib.pyplot as plt
import math
import plotly.express as px
import plotly.graph_objects as go
from pylab import rcParams
import numpy as np
import collections
import json


directory = '/Users/pratyushavi/Developer/CSE/CSE 420/Project/results_Wed_Apr__6_14:10:42_2022'

for filename in os.listdir(directory):
    df = pd.read_csv(os.path.join(directory, filename))
    print("File:", filename)

    graph = nx.DiGraph()

    adj_list = dict()
    marked = set()
    w_history = dict()

    counter = 0

    for i, ins in df.iterrows():
        print('Counter:', i, '/',  len(df), 'Branches', counter,end='\r')
        writeRegs = [int(val) for val in ins['Write_Registers'].replace('W[', '').replace(']', '').split(' ') if val]
        readRegs = [int(val) for val in ins['Read_Regsiters'].replace('R[', '').replace(']', '').split(' ') if val]

        adj_list[i] = set()

        for r in readRegs:
            if r in w_history:
                max_val = -1
                for w in w_history[r]:
                    if w < i:
                        max_val = max(max_val, w)
                if max_val != -1:
                    adj_list[i].add(max_val)
                    w_history[r] = set([max_val])

        for w in writeRegs:
            if w not in w_history:
                w_history[w] = set()
            w_history[w].add(i)

        if ins['isBranch']:
            q = [i]
            while q:
                node = q.pop()
                marked.add(node)
                for v in adj_list[node]:
                    if v not in marked:
                        q.append(v)
            counter += 1
            # if counter > 3:
            # break  
    print("\nDone")

    pos = collections.defaultdict(lambda: 0)

    left_counter = 0
    right_counter = 0

    for i in adj_list:
        # if i > 1000:
        #     continue
        if i in marked:
            pos[i] = (1, i)
            right_counter += 1
        else:
            pos[i] = (0, i)
            left_counter += 1
    print('total instructions: ', len(df))
    print('left:', left_counter, '=>',100 * left_counter/len(df), '%')
    print('right:', right_counter, '=>', 100 * right_counter/len(df), '%')
    # print(x,y)
    # fig = px.scatter(x=x, y=y, text=y)
    # fig.show()

    x = []
    y = []
    e_x = []
    e_y = []
    regs = []
    counter = 0
    for n in adj_list:
        # if n <= 1000:
        regs.append(n)
        x.append(pos[n][0])
        y.append(pos[n][1])
        for e in adj_list[n]:
            e_x.append(pos[n][0])       # x0
            e_x.append(pos[e][0])       # x1
            e_x.append(None)

            e_y.append(pos[n][1])      # y0
            e_y.append(pos[e][1])  # y1
            e_y.append(None)

            if pos[n][0] != pos[e][0]:
                counter += 1
    print('crossovers:', counter)
    # edge_trace = go.Scatter(
    #     x=e_x, y=e_y,
    #     line=dict(width=0.5, color='#888'),
    #     hoverinfo='none',
    #     mode='lines'
    # )

    # node_trace = go.Scatter(
    #     x=x, y=y,mode='markers',
    #     hoverinfo='text',
    #     textposition="top center",
    #     text = regs
    # )

    # fig = go.Figure(data=[edge_trace, node_trace])
    # fig.show()
    print("\n=============================\n")