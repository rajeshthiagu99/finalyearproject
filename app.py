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

def vo2review(vo2max):
    #vo2max review
    if vo2max>60:
        return 'excellent , keep it up'

    if vo2max>52 and vo2max<60:
        return 'good , slight improvement is needed'
    
    if vo2max>47 and vo2max<52:
        return 'above average ,consistent training will improve your results'

    if vo2max>42 and vo2max<47:
        return 'average need to work hard'

    if vo2max<42:
        return 'below average need to take care of your health'


app = flask.Flask(__name__)


@app.route('/', methods=['POST'])
def home():
    output=[]

    #getting input
    data = request.json

    #converting to dataframes
    df_distances=pd.DataFrame(data['distances'])
    df_heartbeats=pd.DataFrame(data['heartbeats'])
    df_all=df_distances.merge(df_heartbeats,on='time')

    #calculating time for warmup
    df_all['time']=pd.to_datetime(df_all['time'])
    start_time=df_all.sort_values('time')['time'].values[0]
    df_all=df_all[df_all['heartbeat']>df_all['heartbeat'].mean()]
    time_to_reach=df_all.sort_values('time')['time'].values[0]
    warm_up_time=(time_to_reach-start_time).astype('timedelta64[s]')
    output.append({'name':'optimal warm up time','image':False,'data':str(warm_up_time)})




    #calculation of vo2 max
    vo2max=15*(max(df_heartbeats['heartbeat'])/min(df_heartbeats['heartbeat']))
    output.append({'name':'vo2max','image':False,'data':vo2max})

    #analysing of vo2 max
    vo2_review_data=vo2review(vo2max)
    output.append({'name':'vo2max review','image':False,'data':vo2_review_data})

    #max heartrate
    output.append({'name':'max_heartrate','image':False,'data':max(df_heartbeats['heartbeat'])})

    #zone calculation
    df_heartbeats['zones']=df_heartbeats.heartbeat.apply(zone)

    # plotting zone bar graph
    df_heartbeats.zones.plot(kind='bar')
    plt.savefig('zone_bar_chart.png')
    encoded = base64.b64encode(open("zone_bar_chart.png", "rb").read())
    os.remove("zone_bar_chart.png")
    output.append({'name':'zone_bar_chart','image':True,'data':encoded.decode("utf-8")})

    #plotting heatmap
    x=df_heartbeats.zones
    sns.heatmap(np.array(x).reshape(len(x),1), cmap="YlGnBu")
    plt.savefig('heatmap.png')
    encoded = base64.b64encode(open("heatmap.png", "rb").read())
    os.remove("heatmap.png")
    output.append({'name':'heatmap','image':True,'data':encoded.decode("utf-8")})


    return json.dumps(output)

if __name__ == "__main__":
    app.run(debug=True)