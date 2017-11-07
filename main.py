import json
import websocket
import numpy as np
import pandas as pd
from randomwalk import randomwalk
import stockplot as sp
import stockstats
import plotly

class CoinCheckTrade:
    def __init__(self):
        # websocketを定義する，ここでheaderにauthorizationを登録することでaccess tokenを使ったwebsocketを設定することができる。
        websocket.enableTrace(True)
        ws = websocket.WebSocketApp("wss://ws-api.coincheck.com/", header=["Content-Type: application/json"], on_open=self.on_open, on_message=self.on_message, on_error=self.on_error, on_close=self.on_close)

        # websocketを起動する。Ctrl+Cで終了するようにする。
        try:
            ws.run_forever()
        except KeyboardInterrupt:
            ws.close()

    # ここで定義したメソッドがwebsocketのコールバック関数になる。
    # messageをうけとったとき
    def on_message(self, ws, message):
        print(json.loads(message))

    # エラーが起こった時
    def on_error(self, ws, error):
        print(error)

    # websocketを閉じた時
    def on_close(self, ws):
        print('disconnected streaming server')

    # websocketを開いた時
    def on_open(self, ws):
        print('connected streaming server')
        req = '{"type": "subscribe","channel": "btc_jpy-trades"}'
        ws.send(req)

    def one_minutes(self, data):
        return

if __name__ == "__main__":
#    coincheck = CoinCheckTrade()
