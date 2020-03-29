import requests
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.offline import plot
from plotly.subplots import make_subplots
from bs4 import BeautifulSoup

class PropertyInfoController():
    def __init__(self, request):
        self.name = request.GET['name']
        self.postal = request.GET['postal']
        self.URL = "https://developers.onemap.sg/commonapi/search?searchVal={} {}&returnGeom=Y&getAddrDetails=Y&pageNum=1".format(self.name, self.postal)
        self.info = requests.get(self.URL).json()
        self.X = float(self.info['results'][0]['X'])
        self.Y = float(self.info['results'][0]['Y'])
        self.LAT = float(self.info['results'][0]['LATITUDE'])
        self.LONG = float(self.info['results'][0]['LONGITUDE'])
        self.MRT_LRT_Data = self.MRTLRTData()
        self.Bus_Data = self.BusData()

    def MRTLRTData(self):
        MRT_LRT_Data = {}
        MRT_LRT_Station = pd.DataFrame(pd.read_csv("propertea/static/MRT_LRT_Station_Data.csv"))
        MRT_LRT_X_diff = np.subtract(np.array(MRT_LRT_Station['X']), self.X)
        MRT_LRT_Y_diff = np.subtract(np.array(MRT_LRT_Station['Y']), self.Y)
        MRT_LRT_Station['DISTANCE'] = np.sqrt(np.square(MRT_LRT_X_diff) + np.square(MRT_LRT_Y_diff))
        MRT_LRT_Data['Name'] = MRT_LRT_Station.sort_values(by='DISTANCE').iloc[0]['NAME']
        MRT_LRT_Data['Number'] = MRT_LRT_Station.sort_values(by='DISTANCE').iloc[0]['NUMBER']
        MRT_LRT_Data['Lat'], MRT_LRT_Data['Long'] = MRT_LRT_Station.sort_values(by='DISTANCE').iloc[0]['LATITUDE'], \
                                                    MRT_LRT_Station.sort_values(by='DISTANCE').iloc[0]['LONGITUDE']
        return MRT_LRT_Data

    def MRTLRTPlot(self):
        MRT_LRT_Transport_Volume = pd.DataFrame(pd.read_csv("propertea/static/MRT_LRT_Transport_Volume.csv"))
        MRT_LRT_Plotting_Data = MRT_LRT_Transport_Volume[MRT_LRT_Transport_Volume['PT_CODE'] == self.MRT_LRT_Data['Number']].sort_values('TIME_PER_HOUR')
        MRT_LRT_Time = [24 if x == 0 else x for x in MRT_LRT_Plotting_Data['TIME_PER_HOUR'].tolist()]
        fig = go.Figure()
        fig.layout = go.Layout(
            title=go.layout.Title(
                text="[Nearest MRT/LRT Station] {}  {}".format(self.MRT_LRT_Data['Name'], self.MRT_LRT_Data['Number']),
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
        return plot(fig, output_type="div", include_plotlyjs=False)

    def MRTLRTTable(self):
        MRT_LRT_Route_Data = pd.read_csv("propertea/static/MRT_LRT_Route_Data.csv")
        MRT_LRT_Table_Data = MRT_LRT_Route_Data[MRT_LRT_Route_Data['NUMBER'] == self.MRT_LRT_Data['Number']]
        fig = make_subplots(
            rows=len(list(set(MRT_LRT_Table_Data['LINE'].values))), cols=1,
            shared_xaxes=True,
            vertical_spacing=0,
            specs=list([{"type": "table"}] for i in range(len(list(set(MRT_LRT_Table_Data['LINE'].values)))))
        )

        num = 1  # super super bad coding style below, hope it doesn't crash the website

        for trainline in list(set(MRT_LRT_Table_Data['LINE'].values)):
            subset = MRT_LRT_Table_Data[MRT_LRT_Table_Data['LINE'] == trainline]
            header_values = ["<b>{}</b>".format(trainline)]
            table_values = [['', '<b>Weekday</b>', '<b>Saturday</b>', '<b>Sunday</b>']]
            for index in range(len(subset)):
                header_values.append('<b>{}</b>'.format(subset['TOWARDS'].iloc[index]))
                header_values.append('<b>{}</b>'.format(subset['TOWARDS'].iloc[index]))
                table_values.append(
                    ['First Train', str(subset['WD_FIRSTTRAIN'].iloc[index]), str(subset['SAT_FIRSTTRAIN'].iloc[index]),
                     str(subset['SUN_FIRSTTRAIN'].iloc[index])])
                table_values.append(
                    ['Last Train', str(subset['WD_LASTTRAIN'].iloc[index]), str(subset['SAT_LASTTRAIN'].iloc[index]),
                     str(subset['SUN_LASTTRAIN'].iloc[index])])

            fig.add_trace(go.Table(
                header=dict(values=header_values,
                            height=30,
                            align=['right', 'center'],
                            # fill = dict(color = "#9bc3eb"),
                            font=dict(family='Karla, monospace', size=18)
                            ),
                cells=dict(values=table_values,
                           align=['right', 'center'],
                           height=30,
                           # fill = dict(color = "#d7e7f7"),
                           font=dict(family='Karla, monospace', size=18)
                           )
            ),
                row=num, col=1
            )
            num += 1

        fig.update_layout(
            height=400 * len(list(set(MRT_LRT_Table_Data['LINE'].values))),
            showlegend=True,
            title_text="MRT/LRT SERVICES AT THIS STOP",
        )
        return plot(fig, output_type="div", include_plotlyjs=False)

    def BusData(self):
        Bus_Data = {}
        Bus_Stop = pd.DataFrame(pd.read_csv("propertea/static/Bus_Stop_Data.csv"))
        Bus_X_diff = np.subtract(np.array(Bus_Stop['X']), self.X)
        Bus_Y_diff = np.subtract(np.array(Bus_Stop['Y']), self.Y)
        Bus_Stop['DISTANCE'] = np.sqrt(np.square(Bus_X_diff) + np.square(Bus_Y_diff))
        Bus_Data['Number'] = int(Bus_Stop.sort_values(by='DISTANCE').iloc[0]['NUMBER'])
        Bus_Data['Name'] = Bus_Stop.sort_values(by='DISTANCE').iloc[0]['NAME']
        Bus_Data['Lat'], Bus_Data['Long'] = Bus_Stop.sort_values(by='DISTANCE').iloc[0]['LATITUDE'], \
                                      Bus_Stop.sort_values(by='DISTANCE').iloc[0]['LONGITUDE']
        return Bus_Data

    def BusPlot(self):
        Bus_Transport_Volume = pd.DataFrame(pd.read_csv("propertea/static/Bus_Transport_Volume.csv"))
        Bus_Stop_Plotting_Data = Bus_Transport_Volume[Bus_Transport_Volume['PT_CODE'] == self.Bus_Data['Number']].sort_values(
            'TIME_PER_HOUR')

        Bus_Time = [24 if x == 0 else x for x in Bus_Stop_Plotting_Data['TIME_PER_HOUR'].tolist()]

        # code for Bus plotly begins here
        fig = go.Figure()
        fig.layout = go.Layout(
            title=go.layout.Title(
                text="[Nearest Bus Stop] {}  {}".format(self.Bus_Data['Name'].upper(), self.Bus_Data['Number']),
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
        return plot(fig, output_type="div", include_plotlyjs=False)

    def BusTable(self):
        Bus_Route_Data = pd.DataFrame(pd.read_csv("propertea/static/Bus_Route_Data.csv"))
        Bus_Table_Data = Bus_Route_Data[Bus_Route_Data['BUSSTOPCODE'] == str(self.Bus_Data['Number'])]

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
        return plot(fig, output_type="div", include_plotlyjs=False)

    def PropertyImages(self):
        url = 'https://www.google.no/search?client=opera&hs=cTQ&source=lnms&tbm=isch&sa=X&ved=0ahUKEwig3LOx4PzKAhWGFywKHZyZAAgQ_AUIBygB&biw=1920&bih=982'
        page = requests.get(url, params={'q': self.name + " singapore property"}).text

        soup = BeautifulSoup(page, 'html.parser')

        links = []

        for raw_img in soup.find_all('img'):
            link = raw_img.get('src')
            if link and 'http://' in link:
                links.append(link)
            if len(links) >= 3:
                break

        return links




