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

returnData = collections.defaultdict(lambda: [])

def categorize(directory):
    print(directory)
    for filename in os.listdir(directory):
        df = pd.read_csv(os.path.join(directory, filename))
        print("File:", filename)

        graph = nx.DiGraph()

        adj_list = dict()
        marked = set()
        w_history = dict()

        counter = 0
        right_counter = 0

        for i, ins in df.iterrows():
            print('Counter:', i, '/',  len(df), 'Branches', counter,end='\r')
            writeRegs = [val for val in ins['Write_Registers'].replace('W[', '').replace(']', '').split(' ') if val]
            readRegs = [val for val in ins['Read_Regsiters'].replace('R[', '').replace(']', '').split(' ') if val]

            adj_list[i] = set()

            # for r in readRegs:
            #     if r in w_history:
            #         max_val = -1
            #         for w in w_history[r]:
            #             if w < i:
            #                 max_val = max(max_val, w)
            #         if max_val != -1:
            #             adj_list[i].add(max_val)
            #             w_history[r] = set([max_val])

            # for w in writeRegs:
            #     if w not in w_history:
            #         w_history[w] = set()
            #     w_history[w].add(i)

            for r in readRegs:
                if r in w_history:
                    adj_list[i].add(w_history[r])


            for w in writeRegs:
                w_history[w] = i

            if ins['isBranch']:
                q = [i]
                while q:
                    node = q.pop()
                    if node not in marked:
                        marked.add(node)
                        right_counter += 1
                    for v in adj_list[node]:
                        if v not in marked:
                            q.append(v)
                counter += 1
                # if counter > 3:
                # break  
        print('data-flow:', len(df) - right_counter, '=>',100 * (len(df) - right_counter)/len(df), '%')
        print('control-flow:', right_counter, '=>', 100 * right_counter/len(df), '%')
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
        print('\n\ntotal instructions: ', len(df))
        print('data-flow:', left_counter, '=>',100 * left_counter/len(df), '%')
        print('control-flow:', right_counter, '=>', 100 * right_counter/len(df), '%')
        # print(x,y)
        # fig = px.scatter(x=x, y=y, text=y)
        # fig.show()

        x = []
        y = []
        e_x = []
        e_y = []
        regs = []
        crossovers = 0
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
                    crossovers += 1
        print('crossovers:', crossovers)
        print('crossovers/control-flow:', crossovers/right_counter*100, '%')
        print("\n=============================\n")
        
        returnData['dir'].append(directory)
        returnData['filename'].append(filename.split('_')[0])
        returnData['control-flow-percentage'].append(right_counter/len(df) * 100)


categorize('results-no-mem')
# categorize('results-with-mem')

# df = pd.DataFrame(returnData)

# print(df)

# fig = px.line(df, x='filename', y='control-flow-percentage', color='dir')
# fig.show()
