import plotly.offline as py
import plotly.graph_objs as go
import json

def graph(file):
    """
    Generate the graph corresponding to the file
    """
    data = json.load(open(file, 'r'))

    time = [key["T"]/1000000 for key in data]
    S1 = [key["S1"] for key in data]
    S2 = [key["S2"] for key in data]
    S3 = [key["S3"] for key in data]
    S4 = [key["S4"] for key in data]
    S5 = [key["S5"]for key in data]
    S6 = [key["S6"] for key in data]
    encoder = [-key["E"] for key in data]

    plot1 = go.Scatter(x=time, y=S1, mode='lines', name="Sensor 1")
    plot2 = go.Scatter(x=time, y=S2, mode='lines', name="Sensor 2")
    plot3 = go.Scatter(x=time, y=S3, mode='lines', name="Sensor 3")
    plot4 = go.Scatter(x=time, y=S4, mode='lines', name="Sensor 4")
    plot5 = go.Scatter(x=time, y=S5, mode='lines', name="Sensor 5")
    plot6 = go.Scatter(x=time, y=S6, mode='lines', name="Sensor 6")
    plot7 = go.Scatter(x=time, y=encoder, mode='lines', name="Encoder")

    graphs = [plot1, plot2, plot3, plot4, plot5, plot6, plot7]
    py.offline.plot(graphs)

# edit file name to view the graphs
file = 'sensors-2022-10-21-10h48.json'
if __name__ == '__main__':
    path = 'results/{}'.format(file)
    graph(path)