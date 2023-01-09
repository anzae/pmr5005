import json
from datetime import datetime
import random

d = datetime.now()
date_formatted = '{}_{}_{}_{}h{}m{}s'.format(d.year, d.month, d.day, d.hour, d.minute, d.second)
file = "results/sensors_" + date_formatted + ".json"    
data = []

t0 = 0
y0 = 300
x0 = 0
theta0 = 0

s10 = 4096
s20 = 0
s30 = 0
s40 = 0
s50 = 0
s60 = 4096

# mock time = 20s
# y total = 2700

for i in range(2000):

    xi = x0 + random.randint(-10, 10)
    thetai = theta0 + random.randint(-10, 10)
    s1 = s10 + random.randint(-50, 50)
    s2 = s20 + random.randint(-50, 50)
    s3 = s30 + random.randint(-50, 50)
    s4 = s40 + random.randint(-50, 50)
    s5 = s50 + random.randint(-50, 50)
    s6 = s60 + random.randint(-50, 50)

    data_frame = {
        "T": t0 + i/100,
        "S1": s1,
        "S2": s2,
        "S3": s3,
        "S4": s4,
        "S5": s5,
        "S6": s6,
        "E": thetai,
        "playerX": xi,
        "playerY": y0 + 1.2*i
    }

    x0 = xi
    theta0 = thetai
    s10 = s1
    s20 = s2
    s30 = s3
    s40 = s4
    s50 = s5
    s60 = s6

    data.append(data_frame)

with open(file, 'w') as file:
    json.dump(data, file)