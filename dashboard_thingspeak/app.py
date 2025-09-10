from flask import Flask, render_template
import requests
import pandas as pd
import plotly.graph_objs as go

app = Flask(__name__)

THINGSPEAK_CHANNEL_ID = '2943258'
THINGSPEAK_API_KEY = 'G3BDQS6I5PRGFEWR'
NUM_RESULTS = 100
THINGSPEAK_URL = f"https://api.thingspeak.com/channels/{THINGSPEAK_CHANNEL_ID}/feeds.json"

def get_thingspeak_data():
    params = {'results': NUM_RESULTS}
    if THINGSPEAK_API_KEY:
        params['api_key'] = THINGSPEAK_API_KEY

    response = requests.get(THINGSPEAK_URL, params=params)
    if response.status_code != 200:
        return None, "Erro ao acessar a API do ThingSpeak"

    data = response.json()['feeds']
    df = pd.DataFrame(data)
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['umidade'] = pd.to_numeric(df['field1'], errors='coerce')
    df['temperatura'] = pd.to_numeric(df['field2'], errors='coerce')
    df.dropna(subset=['umidade', 'temperatura'], inplace=True)
    return df, None

@app.route('/')
def index():
    df, error = get_thingspeak_data()
    if error:
        return f"<h1>{error}</h1>"

    last_temp = df['temperatura'].iloc[-1]
    last_umidade = df['umidade'].iloc[-1]

    # Gráfico de Temperatura
    temp_trace = go.Scatter(
        x=df['created_at'], y=df['temperatura'],
        mode='lines+markers',
        name='Temperatura (°C)',
        line=dict(color='#6f72e7'),
        marker=dict(size=6)
    )
    temp_layout = go.Layout(
        title='Temperatura ao Longo do Tempo',
        xaxis=dict(title='Data'),
        yaxis=dict(title='°C'),
        plot_bgcolor='#f4f7fc',
        paper_bgcolor='#f4f7fc',
        font=dict(color='#4a47a3'),
        hovermode='x unified'
    )
    temp_fig = go.Figure(data=[temp_trace], layout=temp_layout)

    # Gráfico de Umidade
    umidade_trace = go.Scatter(
        x=df['created_at'], y=df['umidade'],
        mode='lines+markers',
        name='Umidade (%)',
        line=dict(color='#9f84e8'),
        marker=dict(size=6)
    )
    umidade_layout = go.Layout(
        title='Umidade ao Longo do Tempo',
        xaxis=dict(title='Data'),
        yaxis=dict(title='%'),
        plot_bgcolor='#f4f7fc',
        paper_bgcolor='#f4f7fc',
        font=dict(color='#4a47a3'),
        hovermode='x unified'
    )
    umidade_fig = go.Figure(data=[umidade_trace], layout=umidade_layout)

    temp_div = temp_fig.to_html(full_html=False)
    umidade_div = umidade_fig.to_html(full_html=False)

    return render_template("index.html",
                           last_temp=round(last_temp, 2),
                           last_umidade=round(last_umidade, 2),
                           temp_plot=temp_div,
                           umidade_plot=umidade_div)

if __name__ == '__main__':
    app.run(debug=True)
