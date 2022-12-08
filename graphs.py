import plotly.offline as py
import plotly.graph_objs as go
import json
from consts import * 

def graph(file, level=None):
    """
    Generate the graph corresponding to the file
    """
    data = json.load(open(file, 'r'))

    time = [key["T"]/1000 for key in data]
    S1 = [key["S1"] for key in data]
    S2 = [key["S2"] for key in data]
    S3 = [key["S3"] for key in data]
    S4 = [key["S4"] for key in data]
    S5 = [key["S5"]for key in data]
    S6 = [key["S6"] for key in data]
    encoder = [key["E"] for key in data]
    encoder_angular = [e * 0.18 for e in encoder]

    # plot1 = go.Scatter(x=time, y=S1, mode='lines', name="Sensor 1")
    # plot2 = go.Scatter(x=time, y=S2, mode='lines', name="Sensor 2")
    # plot3 = go.Scatter(x=time, y=S3, mode='lines', name="Sensor 3")
    # plot4 = go.Scatter(x=time, y=S4, mode='lines', name="Sensor 4")
    # plot5 = go.Scatter(x=time, y=S5, mode='lines', name="Sensor 5")
    # plot6 = go.Scatter(x=time, y=S6, mode='lines', name="Sensor 6")
    # plot7 = go.Scatter(x=time, y=encoder, mode='lines', name="Encoder")
    plot8 = go.Scatter(x=time, y=encoder_angular, mode='lines', name="Encoder angular")

    plot_winds = []

    if level:

        with open(WIND_CONFIG, 'r') as winds:
            file = json.load(winds)
            for wind in file:
                start = wind["y_start"]
                end = wind["y_end"]
                magnitude = wind["magnitude"]
                plot_winds.append(go.Bar(x=[(start-180)/300], width=((end-start+100)/300), y=[magnitude]))

    graphs = [plot8]
    py.offline.plot(graphs)

# edit file name to view the graphs
file = 'sensors-2022-12-8-14h34'
if __name__ == '__main__':
    path = 'results/{}.json'.format(file)
    graph(path, 'level_2')