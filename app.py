import plotly.graph_objects as go
import pandas as pd
import json
from flask import Flask, render_template

def import_covid19_data():
    '''Import covid19 data from 2019 Novel Coronavirus COVID-19 (2019-nCoV) 
    Data Repository by Johns Hopkins CSSE and output confirmed cases, deaths,
    and recovered cases into three pandas dataframes.
    '''
    
    url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master'\
    +'/csse_covid_19_data/csse_covid_19_time_series/'
    conf = 'time_series_19-covid-Confirmed.csv'
    death = 'time_series_19-covid-Deaths.csv'
    recov = 'time_series_19-covid-Recovered.csv'
    
    confirmed = pd.read_csv(url + conf)
    deaths = pd.read_csv(url + death)
    recov = pd.read_csv(url + recov)
    
    return confirmed, deaths, recov

confirmed, deaths, recovered = import_covid19_data()

confirmed['Province/State'].fillna(confirmed['Country/Region'], inplace=True)
df = pd.DataFrame([confirmed['Province/State'], 
                   confirmed.iloc[:,-1], 
                   confirmed['Lat'], 
                   confirmed['Long']]).T
df.rename(columns={df.columns[0]: "name",
                   df.columns[1]: "pop",
                   df.columns[2]: "lat",
                   df.columns[3]: "lon"}, inplace = True)

df.sort_values(by=['pop'], ascending=False, inplace=True)
df = df[df['pop']!=0]
df = df.astype({'name': 'string',
           'pop': 'int32',
           'lat': 'float32',
           'lon': 'float32'})
df['text'] = df['name'] + '<br>Confirmed ' + (df['pop']).astype(str)
limits = [(0,10),(11,50),(51,100),(101,150),(151,len(df)-1)]
colors = ["royalblue","crimson","lightseagreen","orange","lightgrey"]
cities = []
scale = [100, 10, 5, 1, 0.5]

fig = go.Figure()

for i in range(len(limits)):
    lim = limits[i]
    df_sub = df[lim[0]:lim[1]]
    fig.add_trace(go.Scattergeo(
        lon = df_sub['lon'],
        lat = df_sub['lat'],
        text = df_sub['text'],
        marker = dict(
            size = df_sub['pop']/scale[i],
            color = colors[i],
            line_color='rgb(40,40,40)',
            line_width=0.5,
            sizemode = 'area'
        ),
        name = '{0} - {1}'.format(lim[0],lim[1])))

fig.update_layout(
        title_text = 'Covid-19',
        showlegend = True,
        geo = dict(
            scope = 'world',
            landcolor = 'rgb(217, 217, 217)',
            showcountries=True,
        )
    )

app = Flask(__name__)


@app.route('/')
def index():
    data = json.loads(fig.to_json())['data']
    layout = json.loads(fig.to_json())['layout']
    return render_template('index.html', data=data, layout=layout)


if __name__ == '__main__':
    app.run()