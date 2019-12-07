
import pandas as pd
import requests 
import json
from pyti.smoothed_moving_average import smoothed_moving_average as sma
from plotly.offline import plot
import plotly.graph_objs as go 

class TradingModel:

    def __init__(self, symbol):
        self.symbol = symbol
        self.df = self.requestData()

    def requestData(self):
        #define the URL
        base = 'https://api.binance.com'
        endpoint = '/api/v1/klines'
        params = '?&symbol=' + self.symbol + '&interval=1h'

        url = base + endpoint + params
        
        #download the data
        data = requests.get(url)
        dictionnary = json.loads(data.text)

        #put in dataframe and clean 
        df = pd.DataFrame.from_dict(dictionnary)
        df = df.drop(range(6,12), axis=1)

        #rename columns
        col_names = ['time', 'open', 'high', 'low', 'close', 'volume']
        df.columns = col_names

        #values in float please
        for col in col_names:
            df[col] = df[col].astype(float)
        
        #moving averages
        df['fast_ma'] = sma(df['close'].tolist(), 10)
        df['slow_ma'] = sma(df['close'].tolist(), 30)

        return df
    #buy_strategy Buying    
    def strategy(self):
        df = self.df

        buy_signals = []
        sell_signals = []

        for i in range(1, len(df['close'])):

            if df['slow_ma'][i] > df['low'][i] and (df['slow_ma'][i] - df['low'][i]) > 0.035 * df['low'][i]:
                buy_signals.append([df['time'][i], df['low'][i]])

            elif df['fast_ma'][i] > df['high'][i] and (df['fast_ma'][i] - df['high'][i]) < 0.035 * df['high'][i]:
                sell_signals.append([df['time'][i], df['high'][i]])
        
        self.plotData(buy_signals = buy_signals, sell_signals = sell_signals)
    


    def plotData(self, buy_signals = False, sell_signals = False):
        df = self.df

        #plot candlestick chart
        candle = go.Candlestick(
            x = df['time'],
            open = df['open'],
            close = df['close'],
            high = df['high'],
            low = df['low'],
            name = 'Candlesticks chart'
        )

        #plot Fast Moving Averrage
        fsma = go.Scatter(
            x = df['time'],
            y = df['fast_ma'],
            name = 'Fast MA',
            line = dict(color = ('rgba(102,207, 255, 50)'))
        )
        #plot Slow Moving Averrage
        ssma = go.Scatter(
            x = df['time'],
            y = df['slow_ma'],
            name = 'Slow MA',
            line = dict(color = ('rgba(255 ,207, 102, 50)'))
        )

        if buy_signals:
            buy = go.Scatter(
                x = [item[0] for item in buy_signals ],
                y = [item[1] for item in buy_signals ],
                name = 'BUY SIGNALS',
                mode ='markers',
                line = dict(color='rgba(255,0,255,50)')
            )
        
        if sell_signals:
            sell = go.Scatter(
                x = [item[0] for item in sell_signals ],
                y = [item[1] * 1.02 for item in sell_signals ],
                name = 'SELL SIGNALS',
                mode ='markers',
                line = dict(color='rgba(255,255,0,50)')
            )

        #display 
        data = [candle, ssma, fsma, buy, sell]
        layout = go.Layout(title = self.symbol)
        fig = go.Figure(data = data, layout = layout)

        plot(fig, filename=self.symbol)

def Main():
    symbol = "BTCUSDT"
    model = TradingModel(symbol)
    model.requestData()
    model.strategy()

if __name__ == '__main__':
    Main()