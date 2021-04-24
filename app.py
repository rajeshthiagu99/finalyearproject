import flask
from flask import request, render_template
from datetime import datetime as dt
import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import base64
import os

def zone(hr):
    m=189
    if hr<(0.75*m):
        return 0
    if hr>(0.75*m) and hr<(0.85*m):
        return 1
    if hr>(0.85*m) and hr<(0.90*m):
        return 2
    if hr>(0.90*m) and hr<(0.92*m):
        return 3
    if hr>(0.92*m):
        return 4


app = flask.Flask(__name__)


@app.route('/', methods=['POST'])
def home():
    output=[]
    #getting input
    data = request.json
    #converting to dataframes
    df_distances=pd.DataFrame(data['distances'])
    df_heartbeats=pd.DataFrame(data['heartbeats'])
    #calculation of vo2 max
    vo2max=15*(max(df_heartbeats['heartbeat'])/min(df_heartbeats['heartbeat']))
    # results={
    #     'vo2max':vo2max,
    #     'max_heartrate':max(df_heartbeats['heartbeat'])
    # }
    output.append({'name':'vo2max','image':False,'data':vo2max})
    output.append({'name':'max_heartrate','image':False,'data':max(df_heartbeats['heartbeat'])})

    #zone calculation
    df_heartbeats['zones']=df_heartbeats.heartbeat.apply(zone)
    # results['zones']=json.dumps(list(df_heartbeats['zones']))



    # plotting zone bar graph
    df_heartbeats.zones.plot(kind='bar')
    plt.savefig('zone_bar_chart.png')
    encoded = base64.b64encode(open("zone_bar_chart.png", "rb").read())
    os.remove("zone_bar_chart.png")
    # results['zone_bar_chart']=encoded.decode("utf-8")
    output.append({'name':'zone_bar_chart','image':True,'data':encoded.decode("utf-8")})


    #plotting heatmap
    x=df_heartbeats.zones
    sns.heatmap(np.array(x).reshape(len(x),1), cmap="YlGnBu")
    plt.savefig('heatmap.png')
    encoded = base64.b64encode(open("heatmap.png", "rb").read())
    os.remove("heatmap.png")
    # results['heatmap']= encoded.decode("utf-8")
    output.append({'name':'heatmap','image':True,'data':encoded.decode("utf-8")})

    
    
    return json.dumps(output)

if __name__ == "__main__":
    app.run(debug=True)