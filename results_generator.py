import json
from datetime import datetime
import random

d = datetime.now()
date_formatted = '{}-{}-{}-{}h{}m{}s'.format(d.year, d.month, d.day, d.hour, d.minute, d.second)
file = "results/sensors-" + date_formatted + ".json"    
data = []

t0 = 0
y0 = 300
x0 = 0
theta0 = 0

# mock time = 20s
# y total = 2700

for i in range(2000):

    xi = x0 + random.randint(-10, 10)
    thetai = theta0 + random.randint(-10, 10)

    data_frame = {
        "T": t0 + i/100,
        "S1": random.randint(0,1000),
        "S2": random.randint(0,1000),
        "S3": random.randint(0,1000),
        "S4": random.randint(0,1000),
        "S5": random.randint(0,1000),
        "S6": random.randint(0,1000),
        "E": thetai,
        "playerX": xi,
        "playerY": y0 + 1.2*i
    }

    x0 = xi
    theta0 = thetai
    data.append(data_frame)

with open(file, 'w') as file:
    json.dump(data, file)