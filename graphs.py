import plotly.offline as py
import plotly.graph_objs as go
import json
from consts import * 

def graph(file):
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
    playerX = [key["playerY"] for key in data]
    encoder = [key["E"] for key in data]
    encoder_angular = [e * 0.18 for e in encoder]

    plot1 = go.Scatter(x=time, y=S1, mode='lines', name="Sensor 1")
    plot2 = go.Scatter(x=time, y=S2, mode='lines', name="Sensor 2")
    plot3 = go.Scatter(x=time, y=S3, mode='lines', name="Sensor 3")
    plot4 = go.Scatter(x=time, y=S4, mode='lines', name="Sensor 4")
    plot5 = go.Scatter(x=time, y=S5, mode='lines', name="Sensor 5")
    plot6 = go.Scatter(x=time, y=S6, mode='lines', name="Sensor 6")
    # plot7 = go.Scatter(x=time, y=encoder, mode='lines', name="Encoder")
    plot_player = go.Scatter(x=time, y=playerX, mode='lines', name="Player position")
    plot_angular = go.Scatter(x=time, y=encoder_angular, mode='lines', name="Encoder angular")

    graphs = [plot1, plot2, plot3, plot4, plot5, plot6, plot_angular]
    return graphs

# Plot the game object items 
def plot_items(item_path, isWind=False):
    plots = []

    # game objects are in pixel units, graphs need to be in time units
    # conversion obtained experimentally, dividing the initial height by total time (both displayed in hud)
    # also removing the little delay before game starts
    time_conversion = lambda position : position / 146.06 - 1.13

    with open(item_path, 'r') as items:
        file = json.load(items)
        if isWind:
            for item in file:
                start = time_conversion(item["y_start"])
                end = time_conversion(item["y_end"])
                magnitude = item["magnitude"]*100
                # x = central point, width = half width
                plot = go.Bar(x=[(start+end)/2], width=end-start, y=[magnitude])
                plots.append(plot)
        else:
            x_values =  []
            y_values = []
            for item in file:
                x_values.append(item["x"]-320)
                y_values.append(time_conversion(item["y"]))
            plot = go.Scatter(x=y_values, y=x_values, mode='markers')
            plots.append(plot)
    return plots

# edit file name to view the graphs
file = 'sensors-2022-12-8-14h34'
if __name__ == '__main__':
    path = 'results/{}.json'.format(file)
    plot_sensors = graph(path)
    plot_coins = plot_items(COINS_CONFIG)
    plot_winds = plot_items(WIND_CONFIG, True)
    py.offline.plot(plot_coins + plot_winds + plot_sensors)