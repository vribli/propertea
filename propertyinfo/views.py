import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests
from bs4 import BeautifulSoup
from django.shortcuts import render
from plotly.offline import plot
from plotly.subplots import make_subplots


# Create your views here.
def index(request):
    try:
        name = request.GET['name']
        postal = request.GET['postal']

        # code to get nearest property coordinate begins here
        URL = "https://developers.onemap.sg/commonapi/search?searchVal={} {}&returnGeom=Y&getAddrDetails=Y&pageNum=1".format(
            name, postal)
        info = requests.get(URL).json()
        X = float(info['results'][0]['X'])
        Y = float(info['results'][0]['Y'])
        LAT = float(info['results'][0]['LATITUDE'])
        LONG = float(info['results'][0]['LONGITUDE'])
        # code to get nearest property coordinate ends here

        # code for extracting closest MRT and passenger volume begins here
        MRT_LRT_Station = pd.DataFrame(pd.read_csv("propertea/static/MRT_LRT_Station_Data.csv"))
        MRT_LRT_X_diff = np.subtract(np.array(MRT_LRT_Station['X']), X)
        MRT_LRT_Y_diff = np.subtract(np.array(MRT_LRT_Station['Y']), Y)
        MRT_LRT_Station['DISTANCE'] = np.sqrt(np.square(MRT_LRT_X_diff) + np.square(MRT_LRT_Y_diff))
        MRT_LRT_Station_Name = MRT_LRT_Station.sort_values(by='DISTANCE').iloc[0]['NAME']
        MRT_LRT_Station_Number = MRT_LRT_Station.sort_values(by='DISTANCE').iloc[0]['NUMBER']
        MRT_LRT_Station_Lat, MRT_LRT_Station_Long = MRT_LRT_Station.sort_values(by='DISTANCE').iloc[0]['LATITUDE'], MRT_LRT_Station.sort_values(by='DISTANCE').iloc[0]['LONGITUDE']
        MRT_LRT_Transport_Volume = pd.DataFrame(pd.read_csv("propertea/static/MRT_LRT_Transport_Volume.csv"))
        MRT_LRT_Plotting_Data = MRT_LRT_Transport_Volume[
            MRT_LRT_Transport_Volume['PT_CODE'] == MRT_LRT_Station_Number].sort_values('TIME_PER_HOUR')
        # code for extracting closest MRT and passenger volume ends here

        MRT_LRT_Time = [24 if x == 0 else x for x in MRT_LRT_Plotting_Data['TIME_PER_HOUR'].tolist()]

        # code for MRT plotly begins here
        fig = go.Figure()
        fig.layout = go.Layout(
            title=go.layout.Title(
                text="[Nearest MRT/LRT Station] {}  {}".format(MRT_LRT_Station_Name, MRT_LRT_Station_Number),
            ),

            xaxis=go.layout.XAxis(
                tickmode='array',
                tickvals=MRT_LRT_Time,
                ticktext=[str(i) for i in MRT_LRT_Time],
                title=go.layout.xaxis.Title(text='Time', )
            ),

            yaxis=go.layout.YAxis(
                title=go.layout.yaxis.Title(
                    text='Passenger Volume',
                )
            )
        )
        fig.add_trace(go.Bar(
            x=MRT_LRT_Time,
            y=MRT_LRT_Plotting_Data['TOTAL_TAP_IN_VOLUME'].tolist(),
            name='Total Tap In Volume',
            marker_color='#4287f5', )
        )
        fig.add_trace(go.Bar(
            x=MRT_LRT_Time,
            y=MRT_LRT_Plotting_Data['TOTAL_TAP_OUT_VOLUME'].tolist(),
            name='Total Tap Out Volume',
            marker_color='LightSkyBlue')
        )
        fig.update_layout(barmode='group', xaxis_tickangle=-45, font={"family": "Karla", "size": 16})
        mrt_lrt_plot_div = plot(fig, output_type="div", include_plotlyjs=False)
        # code for MRT plotly ends here

        # code for MRT LRT Services begins here
        MRT_LRT_Route_Data = pd.read_csv("propertea/static/MRT_LRT_Route_Data.csv")
        MRT_LRT_Table_Data = MRT_LRT_Route_Data[MRT_LRT_Route_Data['NUMBER'] == MRT_LRT_Station_Number]
        fig = make_subplots(
            rows=len(list(set(MRT_LRT_Table_Data['LINE'].values))), cols=1,
            shared_xaxes=True,
            vertical_spacing=0,
            specs=list([{"type": "table"}] for i in range(len(list(set(MRT_LRT_Table_Data['LINE'].values)))))
        )

        num = 1 # super super bad coding style below, hope it doesn't crash the website

        for trainline in list(set(MRT_LRT_Table_Data['LINE'].values)):
            subset = MRT_LRT_Table_Data[MRT_LRT_Table_Data['LINE'] == trainline]
            header_values = ["<b>{}</b>".format(trainline)]
            table_values = [['', '<b>Weekday</b>', '<b>Saturday</b>', '<b>Sunday</b>']]
            for index in range(len(subset)):
                header_values.append('<b>{}</b>'.format(subset['TOWARDS'].iloc[index]))
                header_values.append('<b>{}</b>'.format(subset['TOWARDS'].iloc[index]))
                table_values.append(['First Train', str(subset['WD_FIRSTTRAIN'].iloc[index]), str(subset['SAT_FIRSTTRAIN'].iloc[index]), str(subset['SUN_FIRSTTRAIN'].iloc[index])])
                table_values.append(['Last Train', str(subset['WD_LASTTRAIN'].iloc[index]), str(subset['SAT_LASTTRAIN'].iloc[index]), str(subset['SUN_LASTTRAIN'].iloc[index])])

            fig.add_trace(go.Table(
                header=dict(values=header_values,
                            height=30,
                            align=['right','center'],
                            # fill = dict(color = "#9bc3eb"),
                            font=dict(family='Karla, monospace', size=18)                
                            ),
                cells=dict(values=table_values,
                            align=['right','center'],
                            height=30,
                            # fill = dict(color = "#d7e7f7"),
                            font=dict(family='Karla, monospace', size=18)
                            )
                ),
                row = num, col = 1
            )
            num+=1

        fig.update_layout(
            height=400*len(list(set(MRT_LRT_Table_Data['LINE'].values))),
            showlegend=True,
            title_text="MRT SERVICES AT THIS STOP",
        )
        mrt_lrt_table_div = plot(fig, output_type="div", include_plotlyjs=False)
        # code for MRT LRT Services ends here

        # code for extracting closest bus and passenger volume begins here
        Bus_Stop = pd.DataFrame(pd.read_csv("propertea/static/Bus_Stop_Data.csv"))
        Bus_X_diff = np.subtract(np.array(Bus_Stop['X']), X)
        Bus_Y_diff = np.subtract(np.array(Bus_Stop['Y']), Y)
        Bus_Stop['DISTANCE'] = np.sqrt(np.square(Bus_X_diff) + np.square(Bus_Y_diff))
        Bus_Stop_Number = int(Bus_Stop.sort_values(by='DISTANCE').iloc[0]['NUMBER'])
        Bus_Stop_Name = Bus_Stop.sort_values(by='DISTANCE').iloc[0]['NAME']
        Bus_Stop_Lat, Bus_Stop_Long = Bus_Stop.sort_values(by='DISTANCE').iloc[0]['LATITUDE'], Bus_Stop.sort_values(by='DISTANCE').iloc[0]['LONGITUDE']
        Bus_Transport_Volume = pd.DataFrame(pd.read_csv("propertea/static/Bus_Transport_Volume.csv"))
        Bus_Stop_Plotting_Data = Bus_Transport_Volume[Bus_Transport_Volume['PT_CODE'] == Bus_Stop_Number].sort_values('TIME_PER_HOUR')
        # code for extracting closest bus and passenger volume ends here

        Bus_Time = [24 if x == 0 else x for x in Bus_Stop_Plotting_Data['TIME_PER_HOUR'].tolist()]

        # code for Bus plotly begins here
        fig = go.Figure()
        fig.layout = go.Layout(
            title=go.layout.Title(
                text="[Nearest Bus Stop] {}  {}".format(Bus_Stop_Name.upper(), Bus_Stop_Number),
                yanchor='bottom'
            ),

            xaxis=go.layout.XAxis(
                tickmode='array',
                tickvals=Bus_Time,
                ticktext=[str(i) for i in Bus_Time],
                title=go.layout.xaxis.Title(text='Time', )
            ),

            yaxis=go.layout.YAxis(
                title=go.layout.yaxis.Title(
                    text='Passenger Volume',
                )
            )
        )

        fig.add_trace(go.Bar(
            x=Bus_Time,
            y=Bus_Stop_Plotting_Data['TOTAL_TAP_IN_VOLUME'].tolist(),
            name='Total Tap In Volume',
            marker_color='#4287f5', )
        )

        fig.add_trace(go.Bar(
            x=Bus_Time,
            y=Bus_Stop_Plotting_Data['TOTAL_TAP_OUT_VOLUME'].tolist(),
            name='Total Tap Out Volume',
            marker_color='LightSkyBlue')
        )

        fig.update_layout(barmode='group', xaxis_tickangle=-45, font={"family": "Karla", "size": 16})
        bus_plot_div = plot(fig, output_type="div", include_plotlyjs=False)
        # code for Bus plotly ends here

        # code for Bus Services begins here
        Bus_Route_Data = pd.DataFrame(pd.read_csv("propertea/static/Bus_Route_Data.csv"))
        Bus_Table_Data = Bus_Route_Data[Bus_Route_Data['BUSSTOPCODE'] == str(Bus_Stop_Number)]

        fig = make_subplots(
            rows=len(Bus_Table_Data), cols=1,
            shared_xaxes=True,
            vertical_spacing=0,
            specs=list([{"type": "table"}] for i in range(len(Bus_Table_Data)))
        )

        for index in range(len(Bus_Table_Data)):
            FirstBus = [Bus_Table_Data['WD_FIRSTBUS'].iloc[index], Bus_Table_Data['SAT_FIRSTBUS'].iloc[index],
                        Bus_Table_Data['SUN_FIRSTBUS'].iloc[index]]
            for j in range(len(FirstBus)):
                if len(FirstBus[j]) == 2:
                    FirstBus[j] = '00' + FirstBus[j]
                elif len(FirstBus[j]) == 3:
                    FirstBus[j] = '0' + FirstBus[j]

            LastBus = [Bus_Table_Data['WD_LASTBUS'].iloc[index], Bus_Table_Data['SAT_LASTBUS'].iloc[index],
                       Bus_Table_Data['SUN_LASTBUS'].iloc[index]]
            for j in range(len(LastBus)):
                if len(LastBus[j]) == 2:
                    LastBus[j] = '00' + LastBus[j]
                elif len(LastBus[j]) == 3:
                    LastBus[j] = '0' + LastBus[j]

            fig.add_trace(go.Table(
                header=dict(values=['<b>{}</b>'.format(Bus_Table_Data['ROUTENAME'].iloc[index]), '<b>First Bus</b>',
                                    '<b>Last Bus</b>'],
                            align=['right', 'center'],
                            height=30,
                            font=dict(family='Karla, monospace', size=18)
                            ),
                cells=dict(values=[['Weekdays', 'Saturdays', 'Sundays & Public Holidays'],
                                   FirstBus,
                                   LastBus
                                   ],
                           align=['right', 'center'],
                           height=30,
                           font=dict(family='Karla, monospace', size=18)
                           )
            ),
                row=index + 1, col=1
            )

        fig.update_layout(
            height=len(Bus_Table_Data) * 220,
            showlegend=True,
            title_text="BUS SERVICES AT THIS STOP...",
        )
        bus_table_div = plot(fig, output_type="div", include_plotlyjs=False)
        # code for Bus Services ends here

        url = 'https://www.google.no/search?client=opera&hs=cTQ&source=lnms&tbm=isch&sa=X&ved=0ahUKEwig3LOx4PzKAhWGFywKHZyZAAgQ_AUIBygB&biw=1920&bih=982'
        page = requests.get(url, params={'q': name + " singapore property"}).text

        soup = BeautifulSoup(page, 'html.parser')

        links = []

        for raw_img in soup.find_all('img'):
            link = raw_img.get('src')
            if link and 'http://' in link:
                links.append(link)
            if len(links) >= 3:
                break

        context = {
            'name': name,
            'postal': postal,
            'mrt_lrt_plot': mrt_lrt_plot_div,
            'mrt_lrt_table_plot': mrt_lrt_table_div,
            'bus_plot': bus_plot_div,
            'bus_table_plot': bus_table_div,
            'links': links,
            'url': 'https://www.google.no/search?client=opera&hs=cTQ&source=lnms&tbm=isch&sa=X&ved=0ahUKEwig3LOx4PzKAhWGFywKHZyZAAgQ_AUIBygB&biw=1920&bih=982&q=' + name + " singapore property",
            'LAT': LAT,
            'LONG': LONG,
            'nearest_train_lat': MRT_LRT_Station_Lat, 
            'nearest_train_long':MRT_LRT_Station_Long,
            'nearest_bus_lat': Bus_Stop_Lat,
            'nearest_bus_long': Bus_Stop_Long
        }

        return render(request, "propertyinfo/index.html", context)
    except KeyError:
        return HttpResponse("Access through home, please")
