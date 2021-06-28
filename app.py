import dash
import dash_core_components as dcc
import dash_html_components as html
from datetime import datetime as dt
from datetime import date,timedelta
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
from dash.dependencies import Input, Output, State
import model

app = dash.Dash(__name__)
server = app.server

item1 = html.Div(
          [
            html.H1("The Stonks App", className="start"),
            html.Div([
              dcc.Input(id='stockcode', value='aapl', type='text',placeholder = 'input stock code'),html.Button(id='stockcode_submit', type='submit', children='Submit',n_clicks = 0)
            ],className='stockcodeselect'),
            html.Div([
              html.Div([
              dcc.DatePickerRange(
              id='my-date-picker-range',
              #min_date_allowed=date(1995, 8, 5),
              #max_date_allowed=date(2017, 9, 19),
              initial_visible_month=date.today(),
              end_date=date.today()
              ),
              html.Div(id='output-container-date-picker-range')
            ],className='datepicker'),

            html.Div([html.Button(id='stock_price_click', type='button', children='STOCK PRICE',n_clicks = 0,className='dateButton')],className = 'datepickerbutton')  
            

            ],className = 'Date'),# Stock price button
            html.Div([
              #html.Button(id='stock_price_click', type='button', children='STOCK PRICE'),# Stock price button 
              #html.Button(id='indicator_click', type='button', children='INDICATORS'),# Indicators button
              dcc.Input(id='no_days',value=5, type='number',min=1,max=7,placeholder = 'no of days'),# Number of days of forecast input
              html.Button(id='no_days_submit', type='submit', children='FORECAST',n_clicks = 0)# Forecast button
            ],className='forecast'),
          ],
        className="nav")
info = html.Div(
          [
            html.Div(
                  [  html.Img(id = 'company_logo'),# Logo
                    html.H2(id = 'company_name') # Company Name
                  ],
                className="header"),
            html.Div( #Description
              id="description", className="description_ticker")

          ],
        className="content")
plots =  html.Div([
            dcc.Graph(
                # Stock price plot
            id="graphs-content"), 
            #html.Button(id='stock_price_click', type='submit', children='STOCK PRICE'),# Stock price button 
            #html.Div([
                #dcc.Graph(
                # Indicator price plot
            #id="indicator-content"), 
                #html.Button(id='indicator_click', type='submit', children='INDICATORS'),# Indicators button
            #], id="main-content"),
           # html.Div([
                # Forecast plot
             dcc.Graph(
                # Stock price plot
            id="predict-content"),     
            #], id="forecast-content")
            ],className = "plots")
item2 = html.Div(children = [info,plots],className = 'info')

app.layout = html.Div(children = [item1, item2],className = 'container')
def get_more(df):
    df['EWA_20'] = df['Close'].ewm(alpha=0.6).mean()
    fig = px.scatter(df,
                    x= 'Date' ,# Date str,
                    y='EWA' ,# EWA_20 str,
                    title="Exponential Moving Average vs Date")

    fig.update_traces(mode= 'lines')# appropriate mode)
    
    return fig;

def get_stock_price_fig(df):
    #df['EWA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
    df['EWA'] = df['Close'].ewm(alpha=0.5).mean()
    fig = px.line(df,
                  x = 'Date' ,# Date str,
                  y= ['Open','Close','EWA'],# list of 'Open' and 'Close',
                  title="Closing, Opening and Indicator Price vs Date")
    return fig


#Call Backs
@app.callback(
    Output(component_id='company_name', component_property='children'),
    Output('company_logo', 'src'),
    Output(component_id='description', component_property='children'),
    Input('stockcode_submit', 'n_clicks'),
    State(component_id='stockcode', component_property='value')
    
)
def update_company_details(n,val):
  ticker = yf.Ticker(val)
  inf = ticker.info
  df = pd.DataFrame().from_dict(inf, orient="index").T
  return df['shortName'][0],df['logo_url'][0],df['longBusinessSummary'][0] # df's first element of 'longBusinessSummary', df's first element value of 'logo_url', df's first element value of 'shortName'

#Call Backs
@app.callback(
    Output('graphs-content','figure'),
    Input('stock_price_click', 'n_clicks'),
    Input('stockcode_submit', 'n_clicks'),
    State(component_id='stockcode', component_property='value'),
    State('my-date-picker-range','start_date'),
    State('my-date-picker-range','end_date')
    ) 
def update_plots(n,m,val,start_date,end_date):
  ticker = yf.Ticker(val)
  df = ticker.history(start=start_date,end=end_date)
  df.reset_index(inplace=True)
  fig = get_stock_price_fig(df)
  return fig # plot the graph of fig using DCC function


#Call Backs
@app.callback(
    Output('predict-content','figure'),
    Input('no_days_submit', 'n_clicks'),
    State(component_id='no_days', component_property='value'),
    State(component_id='stockcode', component_property='value'),
    State('my-date-picker-range','end_date')
    
) 
def forecast(n,future,val,end_date):
  ticker = yf.Ticker(val)
  df = ticker.history(start=dt.strptime(end_date, '%Y-%m-%d').date()-timedelta(days = 500),end=end_date)
  df.reset_index(inplace=True)
  #print(df)
  prediction = model.predict(df['Close'],60,future)
  fig = px.line(x= [(dt.strptime(end_date, '%Y-%m-%d').date()+timedelta(days = i)).isoformat() for i in range(1,future+1)] ,# Date str,
                    y=prediction ,# EWA_20 str,
                    title="Prediction of Closeing Price for next {} days".format(future))

  fig.update_traces(mode= 'lines')# appropriate mode)
    
    
  return fig # plot the graph of fig using DCC function  


if __name__ == '__main__':
    app.run_server(debug=True)