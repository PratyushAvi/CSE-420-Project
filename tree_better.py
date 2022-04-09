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

df = pd.read_csv('results_Wed_Apr__6_14:10:42_2022/blackscholes___1___in_4K.txt___Black-Scholes_binary_output.txt.csv')

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
        #     break   
print("\nDone")

# cleaning adj_list
for n in list(adj_list.keys()):
    if n not in marked:
        adj_list.pop(n)

def topologicalSortUtil(n, visited, stack, adj_list, cur_level, levels):
    visited.add(n)

    for v in adj_list[n]:
        levels[n] = max(levels[n], cur_level)
        if v not in visited:
            topologicalSortUtil(v, visited, stack, adj_list, cur_level+1, levels)

    stack.insert(0,n)

def topologicalSort(adj_list):
    visited = set()
    stack = []
    levels = collections.defaultdict(lambda: 0)
    cur_level = 0

    for n in adj_list:
        levels[n] = cur_level
        cur_level += 1
        if n not in visited:
            topologicalSortUtil(n, visited, stack, adj_list, cur_level, levels)
    return stack, levels

topological_nodes, levels = topologicalSort(adj_list)
# print(topological_nodes)
# print(levels)

pos = collections.defaultdict(lambda: 0)
maxmax = max(topological_nodes)

for node in topological_nodes:
    # print(node)
    graph.add_node(node)
    pos[node] = ((maxmax - node) * 2, levels[node])

for node in topological_nodes:
    for e in adj_list[node]:
        graph.add_edge(node, e)

x = []
y = []
e_x = []
e_y = []
regs = []
nodes = list(graph.nodes)
for n in nodes:
    if n > 9999 and n < 11001:
        regs.append(n)
        x.append(pos[n][0])
        y.append(pos[n][1])
        for e in graph.edges(n):
            e_x.append(pos[e[0]][0])       # x0
            e_x.append(pos[e[1]][0])       # x1
            e_x.append(None)

            e_y.append(pos[e[0]][1])      # y0
            e_y.append(pos[e[1]][1])  # y1
            e_y.append(None)

edge_trace = go.Scatter(
    x=e_x, y=e_y,
    line=dict(width=0.5, color='#888'),
    hoverinfo='none',
    mode='lines'
)

node_trace = go.Scatter(
    x=x, y=y,mode='markers+text',
    hoverinfo='text',
    textposition="top center",
    text = regs
)

fig = go.Figure(data=[edge_trace, node_trace])
fig.show()
fig.write_image("fig10k-11k.svg")

# with open("sample.json", "w") as outfile:
#     json.dump(nx.node_link_data(graph), outfile)

# nx.draw(graph, pos, with_labels=True)
# plt.show()