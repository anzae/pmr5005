import plotly.offline as py
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import json
from consts import * 

# ----------------------------------------------------------
# PLOTLY DOCUMENTATION
# ----------------------------------------------------------
# https://plotly.com/python/reference/
# ----------------------------------------------------------

# Edit file name to see respective graph
file = 'sensors_2023_1_9_13h16m4s'
path = 'results/{}.json'.format(file)

def sensors_graphs(file):
    """
    Generates a dict with the graphs S1, S2, S3, S4, S5, S6, playerPosition and encoder
    """
    data = json.load(open(file, 'r'))

    time = [key["T"]/1000 for key in data]
    S1 = [key["S1"] for key in data]
    S2 = [key["S2"] for key in data]
    S3 = [key["S3"] for key in data]
    S4 = [key["S4"] for key in data]
    S5 = [key["S5"]for key in data]
    S6 = [key["S6"] for key in data]
    playerX = [key["playerX"] for key in data]
    playerY = [key["playerY"] for key in data]
    encoder = [key["E"] * 0.18 for key in data]

    plot1 = go.Scatter(x=playerY, y=S1, mode='lines', name='Sensor 1')
    plot2 = go.Scatter(x=playerY, y=S2, mode='lines', name='Sensor 2')
    plot3 = go.Scatter(x=playerY, y=S3, mode='lines', name='Sensor 3')
    plot4 = go.Scatter(x=playerY, y=S4, mode='lines', name='Sensor 4')
    plot5 = go.Scatter(x=playerY, y=S5, mode='lines', name='Sensor 5')
    plot6 = go.Scatter(x=playerY, y=S6, mode='lines', name='Sensor 6')
    plot_player = go.Scatter(x=playerY, y=playerX, mode='lines', name='Trajetória', line={'width': 4})
    plot_encoder = go.Scatter(x=playerY, y=encoder, mode='lines', name='Posição angular')

    graphs = {
        'sensor1': plot1, 
        'sensor2': plot2,
        'sensor3': plot3,
        'sensor4': plot4, 
        'sensor5': plot5,
        'sensor6': plot6,
        'player': plot_player,
        'encoder': plot_encoder
    }
    return graphs


def level_graphs():
    """
    Generates the plot of the level, wind magnitude 100x bigger 
    """
    data_coins = json.load(open(COINS_CONFIG, 'r'))
    data_wind = json.load(open(WIND_CONFIG, 'r'))
    plots = []

    coins_x = [item['x']-320 for item in data_coins]
    coins_y = [item['y'] for item in data_coins]
    plot_coins = go.Scatter(x=coins_y, y=coins_x, mode='lines+markers', line={'dash':'dash', 'width': 3}, name='Trajetória esperada')
    plots.append(plot_coins)

    for wind in data_wind:
        start = wind['y_start']
        end = wind['y_end']
        magnitude = wind['magnitude'] * 100
        plot = go.Bar(x=[(start+end)/2], width=end-start, y=[magnitude], name="Vento")
        plots.append(plot)

    return(plots)

if __name__ == '__main__':
    sensors = sensors_graphs(path)
    level = level_graphs()

    fig = make_subplots(rows=3, cols=1)

    # plot 1
    # posição atual e posição desejada
    for element in level:
        fig.add_trace(element, row=1, col=1)
    fig.add_trace(sensors['player'], row=1, col=1)

    # plot 2
    # pressão palmar (sensores 1 e 6) e ventos
    for element in level:
        fig.add_trace(element, row=2, col=1)
    fig.append_trace(sensors['sensor1'], row=2, col=1)
    fig.append_trace(sensors['sensor6'], row=2, col=1)

    # plot 3
    # outros sensores
    for element in level:
        fig.add_trace(element, row=3, col=1)
    fig.add_trace(sensors['sensor2'], row=3, col=1)
    fig.add_trace(sensors['sensor3'], row=3, col=1)
    fig.add_trace(sensors['sensor4'], row=3, col=1)
    fig.add_trace(sensors['sensor5'], row=3, col=1)

    py.offline.plot(fig)