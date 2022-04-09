import networkx as nx
import pandas as pd
import os
import matplotlib.pyplot as plt
import math
import plotly.express as px
import plotly.graph_objects as go

# def get_dependency_graph(branch_index, df):
#     print("Making dependency graph")
#     graph = nx.DiGraph()
#     levels = dict()
#     q = [(branch_index, 0)]
#     while len(q):
#         node = q.pop()
#         i = node[0]
#         readRegs = [int(val) if val != '' else None for val in df['Read_Regsiters'][i].replace('R[', '').replace(']', '').strip().split(' ')]
#         # print(readRegs)
#         dep = set()

#         for j in range(i-1, -1, -1):
#             writeRegs = [int(val) if val != '' else None for val in df['Write_Registers'][j].replace('W[', '').replace(']', '').strip().split(' ')]
#             found = False
#             for r_reg in readRegs:
#                 if r_reg != None and r_reg in writeRegs and r_reg not in dep:
#                     graph.add_node(i, name=r_reg)
#                     graph.add_node(j, name=r_reg)
#                     graph.add_edge(i, j)
#                     dep.add(r_reg)
#                     found = True

#             if found:
#                 q.append((j, node[1]+1))
#         levels[i] = max(node[1], levels[i] if i in levels else 0)
                    
#     return graph, levels

df = pd.read_csv('results_Wed_Apr__6_14:10:42_2022/blackscholes___1___in_4K.txt___Black-Scholes_binary_output.txt.csv')

graph = nx.DiGraph()
levels = dict()
for index in range(len(df)-1, -1, -1):
# for index,row in df.iterrows():
    print('Counter: ', index, '/', len(df), end='\r')
    if df['isBranch'][index]:
        # tree = get_dependencies(i, df)
        # for key in tree:
        #     graph.add_node(key)
        #     graph.add_nodes_from(tree[key])
        #     for neighbor in tree[key]:
        #         graph.add_edge(key, neighbor)

        # graph, levels = get_dependency_graph(i, df)

        # print(levels)

        q = [(index, 0)]
        while len(q):
            node = q.pop()
            i = node[0]
            readRegs = [int(val) if val != '' else None for val in df['Read_Regsiters'][i].replace('R[', '').replace(']', '').strip().split(' ')]
            # print(readRegs)
            dep = set()

            for j in range(i-1, -1, -1):
                writeRegs = [int(val) if val != '' else None for val in df['Write_Registers'][j].replace('W[', '').replace(']', '').strip().split(' ')]
                found = False
                for r_reg in readRegs:
                    if r_reg != None and r_reg in writeRegs and r_reg not in dep:
                        graph.add_node(i, name=r_reg)
                        graph.add_node(j, name=r_reg)
                        graph.add_edge(i, j)
                        dep.add(r_reg)
                        found = True

                if found:
                    q.append((j, node[1]+1))
            levels[i] = max(node[1], levels[i] if i in levels else 0)

print("\nDone")

options = {
    "font_size": 36,
    "node_size": 3000,
    "node_color": "white",
    "edgecolors": "black",
    "linewidths": 5,
    "width": 5,
}

x = []
y = []
e_x = []
e_y = []
regs = []
nodes = list(graph.nodes)
for n in nodes:
    x.append(len(nodes) - n)
    y.append(max(levels) - levels[n])
    for e in graph.edges(n):
        e_x.append(len(nodes) - e[0])       # x0
        e_x.append(len(nodes) - e[1])       # x1
        e_x.append(None)

        e_y.append(max(levels) - levels[e[0]])  # y0
        e_y.append(max(levels) - levels[e[1]])  # y1
        e_y.append(None)
    regs.append(graph.nodes[n]['name'])

edge_trace = go.Scatter(
    x=e_x, y=e_y,
    line=dict(width=0.5, color='#888'),
    hoverinfo='none',
    mode='lines'
)

node_trace = go.Scatter(
    x=x, y=y,mode='markers',
    hoverinfo='text',
    text=regs,
    textposition="top center",
)

fig = go.Figure(data=[edge_trace, node_trace])
fig.show()

pos = dict()
for i,n in enumerate(nodes):
    pos[n] = (len(nodes) - n, max(levels) - levels[n])


nx.draw(graph, pos, with_labels=True)
plt.savefig("filename.png")