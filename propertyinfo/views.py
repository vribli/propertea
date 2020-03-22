from django.shortcuts import render
import pandas as pd
import plotly.graph_objects as go
from plotly.offline import plot
import numpy as np
import requests
from bs4 import BeautifulSoup 

# Create your views here.
def index(request):
    try:
        name = request.GET['name']
        postal = request.GET['postal']
        
        #code to get nearest property coordinate begins here
        URL = "https://developers.onemap.sg/commonapi/search?searchVal={} {}&returnGeom=Y&getAddrDetails=Y&pageNum=1".format(name, postal)
        info = requests.get(URL).json()
        print(URL)
        print(info)
        X = float(info['results'][0]['X'])
        Y = float(info['results'][0]['Y'])
        #code to get nearest property coordinate ends here

        #code for extracting closest MRT and passenger volume begins here
        MRT_LRT_Station = pd.DataFrame(pd.read_csv("propertea/static/MRT_LRT_Station_Data.csv"))
        MRT_LRT_X_diff = np.subtract(np.array(MRT_LRT_Station['X']), X)
        MRT_LRT_Y_diff = np.subtract(np.array(MRT_LRT_Station['Y']), Y)
        MRT_LRT_Station['Distance'] = np.sqrt(np.square(MRT_LRT_X_diff)+np.square(MRT_LRT_Y_diff))
        MRT_LRT_Transport_Volume = pd.DataFrame(pd.read_csv("propertea/static/MRT_LRT_Passenger_Volume.csv"))
        # // add in the correct PT CODE after dataset is fixed
        MRT_LRT_Plotting_Data = MRT_LRT_Transport_Volume[MRT_LRT_Transport_Volume['PT_CODE']=='BP1'][MRT_LRT_Transport_Volume['DAY_TYPE']=='WEEKDAY'].sort_values('TIME_PER_HOUR')
        #code for extracting closest MRT and passenger volume ends here

        MRT_LRT_Time = [24 if x == 0 else x for x in MRT_LRT_Plotting_Data['TIME_PER_HOUR'].tolist()]
        
        # code for MRT plotly begins here
        fig = go.Figure()
        fig.layout = go.Layout(
            title = go.layout.Title(
                text = "[Nearest MRT Station] {}".format(MRT_LRT_Station.sort_values(by='Distance').iloc[0]['Name']),        
            ),

            xaxis = go.layout.XAxis(
                tickmode = 'array',
                tickvals = MRT_LRT_Time,
                ticktext = [str(i) for i in MRT_LRT_Time],
                title = go.layout.xaxis.Title(text='Time',) 
            ),

            yaxis = go.layout.YAxis(
                title = go.layout.yaxis.Title(
                text = 'Passenger Volume',
                )
            )
        )
        fig.add_trace(go.Bar(
            x = MRT_LRT_Time,
            y = MRT_LRT_Plotting_Data['TOTAL_TAP_IN_VOLUME'].tolist(),
            name = 'Total Tap In Volume',
            marker_color = '#4287f5',)
        )
        fig.add_trace(go.Bar(
            x = MRT_LRT_Time,
            y = MRT_LRT_Plotting_Data['TOTAL_TAP_OUT_VOLUME'].tolist(),
            name = 'Total Tap Out Volume',
            marker_color = 'LightSkyBlue')
        )
        fig.update_layout(barmode='group', xaxis_tickangle=-45)
        mrt_lrt_plot_div = plot(fig, output_type="div", include_plotlyjs=False)
        # code for MRT plotly ends here

        #code for extracting closest bus and passenger volume begins here
        Bus_Stop = pd.DataFrame(pd.read_csv("propertea/static/Bus_Stop_Data.csv"))
        Bus_X_diff = np.subtract(np.array(Bus_Stop['X']), X)
        Bus_Y_diff = np.subtract(np.array(Bus_Stop['Y']), Y)
        Bus_Stop['Distance'] = np.sqrt(np.square(Bus_X_diff)+np.square(Bus_Y_diff))
        Bus_Stop_Number = int(Bus_Stop.sort_values(by='Distance').iloc[0]['NUMBER'])
        Bus_Transport_Volume = pd.DataFrame(pd.read_csv("propertea/static/Bus_Transport_Volume.csv"))
        Bus_Stop_Data = Bus_Transport_Volume[Bus_Transport_Volume['PT_CODE']==Bus_Stop_Number][Bus_Transport_Volume['DAY_TYPE']=='WEEKDAY'].sort_values('TIME_PER_HOUR')
        URL = "http://businterchange.net/sgbus/stops/busstop.php?stop={}".format(Bus_Stop_Number)
        r = requests.get(URL)
        Bus_Stop_Name = BeautifulSoup(r.content).find('table').get_text(separator=' ') 
        #code for extracting closest bus and passenger volume ends here

        Bus_Time = [24 if x == 0 else x for x in Bus_Stop_Data['TIME_PER_HOUR'].tolist()]

        # code for Bus plotly begins here
        fig = go.Figure()
        fig.layout = go.Layout(
            title=go.layout.Title(
                text = "[Nearest Bus Stop] {}  {}".format(Bus_Stop_Name.upper(), Bus_Stop_Number),
                yanchor = 'bottom'
            ),

            xaxis = go.layout.XAxis(
                tickmode = 'array',
                tickvals = Bus_Time,
                ticktext = [str(i) for i in Bus_Time],
                title = go.layout.xaxis.Title(text='Time',) 
            ),

            yaxis = go.layout.YAxis(
                title = go.layout.yaxis.Title(
                text = 'Passenger Volume',
                )
            )
        )

        fig.add_trace(go.Bar(
            x = Bus_Time,
            y = Bus_Stop_Data['TOTAL_TAP_IN_VOLUME'].tolist(),
            name = 'Total Tap In Volume',
            marker_color = '#4287f5',)
        )

        fig.add_trace(go.Bar(
            x = Bus_Time,
            y = Bus_Stop_Data['TOTAL_TAP_OUT_VOLUME'].tolist(),
            name = 'Total Tap Out Volume',
            marker_color = 'LightSkyBlue')
        )

        fig.update_layout(barmode = 'group', xaxis_tickangle = -45)
        bus_plot_div = plot(fig, output_type = "div", include_plotlyjs = False)
        # code for MRT plotly ends here

        context = {
            'name' : name,
            'postal' : postal,
            'mrt_lrt_plot' : mrt_lrt_plot_div,
            'bus_plot' : bus_plot_div
        }

        return render(request, "propertyinfo/index.html", context)
    except KeyError:
        return HttpResponse("Access through home, please")
