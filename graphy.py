import pandas as pd
import plotly.express as px
import collections

df = pd.read_csv('findings/thresholded100-control-data-flow-split.csv')

THRESHOLD = 0
DATA_FLOW = 1
CONTROL_FLOW = 2
DATA_FLOW_PERCENTAGE = 3
CONTROL_FLOW_PERCENTAGE = 4
CROSSOVERS = 5


files = list(df.columns)[1:]
# print(df)
# print(files)

data = collections.defaultdict(lambda: [])

for f in files:
    # print(df[f])
    threshold = [int(i) for i in df[f][THRESHOLD].strip().replace(' ', '').replace('[', '').replace(']', '').split(',')[1:]]
    data_flow = [int(i) for i in df[f][DATA_FLOW].strip().replace(' ', '').replace('[', '').replace(']', '').split(',')[1:]]
    control_flow = [int(i) for i in df[f][CONTROL_FLOW].strip().replace(' ', '').replace('[', '').replace(']', '').split(',')[1:]]
    data_flow_percentage = [float(i)*100 for i in df[f][DATA_FLOW_PERCENTAGE].strip().replace(' ', '').replace('[', '').replace(']', '').split(',')[1:]]
    control_flow_percentage = [float(i)*100 for i in df[f][CONTROL_FLOW_PERCENTAGE].strip().replace(' ', '').replace('[', '').replace(']', '').split(',')[1:]]
    crossovers = [int(i) for i in df[f][CROSSOVERS].strip().replace(' ', '').replace('[', '').replace(']', '').split(',')[1:]]
    cross_div_control = []
    for i in range(len(control_flow)):
        cross_div_control.append(crossovers[i]/control_flow[i]*100)
    filenames = [f] * len(threshold)


    data['filename'].extend(filenames)
    data['threshold'].extend(threshold)
    data['data-flow'].extend(data_flow)
    data['control-flow'].extend(control_flow)
    data['data-flow-percentage'].extend(data_flow_percentage)
    data['control-flow-percentage'].extend(control_flow_percentage)
    data['crossovers'].extend(crossovers)
    data['crossovers/control-flow'].extend(cross_div_control)

    # for i in range(len(df[f][THRESHOLD])):
    #     data['filename'].append(f)
    #     data['threshold'].append(int(df[f][THRESHOLD][i]))
    #     data['data-flow'].append(int(df[f][DATA_FLOW][i]))
    #     data['control-flow'].append(int(df[f][CONTROL_FLOW][i]))
    #     data['data-flow-percentage'].append(float(df[f][DATA_FLOW_PERCENTAGE][i]))
    #     data['control-flow-percentage'].append(float(df[f][CONTROL_FLOW_PERCENTAGE][i]))
    #     data['crossovers'].append(int(df[f][CROSSOVERS][i]))
    #     data['crossovers/control-flow'].append(int(df[f][CROSSOVERS][i])/int(df[f][CONTROL_FLOW][i]))

data_frame = pd.DataFrame.from_dict(data)
print(data_frame)
data_frame.to_csv('findings/threshold-cleaned.csv')

# fig = px.line(data_frame, x='threshold', y='control-flow-percentage', 
#         color='filename', markers=True, symbol='filename'
#     )
# fig.show()
# fig.write_image('findings/control-flow-vs-threshold.svg')

# fig = px.line(data_frame, x='threshold', y='crossovers/control-flow', 
#         color='filename', markers=True, symbol='filename'
#     )
# fig.show()
# fig.write_image('findings/crossover-percentage-vs-threshold.svg')

# fig = px.line(data_frame, x='threshold', y='crossovers', 
#         color='filename', markers=True, symbol='filename'
#     )
# fig.show()
# fig.write_image('findings/crossovers-vs-threshold.svg')

    
