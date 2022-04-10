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
import time


directory = 'results_Wed_Apr__6_14:10:42_2022'

# Dictionary to hold data about different thresholds
thresholded_data = collections.defaultdict(lambda: collections.defaultdict(lambda: []))

for filename in os.listdir(directory):
    df = pd.read_csv(os.path.join(directory, filename))
    print("File:", filename)

    graph = nx.DiGraph()

    adj_list = dict()
    marked = set()
    w_history = dict()
    branch_ins = set()

    counter = 0

    #################################################
    #   Build Adjacency List and un-thresholded graph
    #################################################
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
            branch_ins.add(i)
            q = [i]
            while q:
                node = q.pop()
                marked.add(node)
                for v in adj_list[node]:
                    if v not in marked:
                        q.append(v)
            counter += 1

    pos = collections.defaultdict(lambda: 0)

    left_counter = 0
    right_counter = 0

    for i in adj_list:
        if i in marked:
            pos[i] = (1, i)
            right_counter += 1
        else:
            pos[i] = (0, i)
            left_counter += 1
    
    crossovers = 0
    for n in adj_list:
        for e in adj_list[n]:
            if pos[n][0] != pos[e][0]:
                crossovers += 1
    
    # Threshold = 0 => GOLD. No threshold applied
    thresholded_data[filename]['threshold'].append(0)
    thresholded_data[filename]['data-flow'].append(left_counter)
    thresholded_data[filename]['control-flow'].append(right_counter)
    thresholded_data[filename]['data-flow-percentage'].append(left_counter/len(df))
    thresholded_data[filename]['control-flow-percentage'].append(right_counter/len(df))
    thresholded_data[filename]['crossovers'].append(crossovers)

    ###################################################################################################
    
    #################################################
    #   Build thresholded graphs from adjacency list
    #################################################

    
    MAX_THRESHOLD = 100

    print('\nTHRESHOLDING')
    start_time = time.time()
    for t in range(1, MAX_THRESHOLD+1):
        print('Threshold %d' % t, end='')
        temp_marked = set()

        # re-mark nodes that form dependencies for a given branch instruction
        for ins in branch_ins:
            q = [ins]
            while q:
                node = q.pop()
                temp_marked.add(node)
                for v in adj_list[node]:
                    if v not in temp_marked and abs(node - v) <= t:
                        q.append(v)

        left_counter = 0
        right_counter = 0

        pos = collections.defaultdict(lambda: 0)

        # count data-flow and control-flow nodes and crossovers
        for i in adj_list:
            if i in temp_marked:
                pos[i] = (1, i)
                right_counter += 1
            else:
                pos[i] = (0, i)
                left_counter += 1
        
        crossovers = 0
        for n in adj_list:
            for e in adj_list[n]:
                if pos[n][0] != pos[e][0]:
                    crossovers += 1

        thresholded_data[filename]['threshold'].append(t)
        thresholded_data[filename]['data-flow'].append(left_counter)
        thresholded_data[filename]['control-flow'].append(right_counter)
        thresholded_data[filename]['data-flow-percentage'].append(left_counter/len(df))
        thresholded_data[filename]['control-flow-percentage'].append(right_counter/len(df))
        thresholded_data[filename]['crossovers'].append(crossovers)

        print('\r', end='')

    print('\nTook %.2f seconds\n' % (time.time() - start_time))


#################################################
#   Save thresholded data to csv
#################################################

new_df = pd.DataFrame(thresholded_data)
print(new_df)
new_df.to_csv('./findings/thresholded100-control-data-flow-split.csv')