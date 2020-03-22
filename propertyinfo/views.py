from django.shortcuts import render
import pandas as pd
import plotly.graph_objects as go
from plotly.offline import plot

# Create your views here.
def index(request):
    try:
        name = request.GET['name']
        postal = request.GET['postal']
        
        #code for extracting closest MRT and passenger volume begins here
        MRT_DataFrame = pd.DataFrame(pd.read_csv("propertea/static/MRT_Passenger_Volume.csv"))
        Final_Data = MRT_DataFrame[MRT_DataFrame['PT_CODE']=='BP1'][MRT_DataFrame['DAY_TYPE']=='WEEKDAY'].sort_values('TIME_PER_HOUR')
        #code for extracting closest MRT and passenger volume ends here

        time = [24 if x == 0 else x for x in Final_Data['TIME_PER_HOUR'].tolist()]
        
        # code for plotly begins here
        fig = go.Figure()
        fig.layout = go.Layout(
            title=go.layout.Title(
                text = "{}".format("MRT_LRT_Station.sort_values(by='Distance').iloc[0]['Name']"),        
                x = 0.4,
                yanchor = 'bottom'
            ),

            xaxis=go.layout.XAxis(
                tickmode = 'array',
                tickvals = time,
                ticktext = [str(i) for i in time],
                title = go.layout.xaxis.Title(text='Time',) 
            ),

            yaxis=go.layout.YAxis(
                title=go.layout.yaxis.Title(
                text='Passenger Volume',
                )
            )
        )
        fig.add_trace(go.Bar(
            x=time,
            y=Final_Data['TOTAL_TAP_IN_VOLUME'].tolist(),
            name='Total Tap In Volume',
            marker_color='red',)
        )
        fig.add_trace(go.Bar(
            x=time,
            y=Final_Data['TOTAL_TAP_OUT_VOLUME'].tolist(),
            name='Total Tap Out Volume',
            marker_color='orange')
        )
        fig.update_layout(barmode='group', xaxis_tickangle=-45)
        plot_div = plot(fig, output_type="div", include_plotlyjs=False)
        # code for plotly ends here

        context = {
            'name' : name,
            'postal' : postal,
            'plot' : plot_div
        }

        return render(request, "propertyinfo/index.html", context)
    except KeyError:
        return HttpResponse("Access through home, please")
