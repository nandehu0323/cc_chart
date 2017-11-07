import pandas as pd
from pandas.core import common as com
import stockstats as ss
from plotly.tools import FigureFactory as FF
import plotly.offline as pyo
pyo.init_notebook_mode(connected=True)


def set_span(start=None, end=None, periods=None, freq='D'):
    """ 引数のstart, end, periodsに対して
    startとendの時間を返す。

    * start, end, periods合わせて2つの引数が指定されていなければエラー
    * start, endが指定されていたらそのまま返す
    * start, periodsが指定されていたら、endを計算する
    * end, periodsが指定されていたら、startを計算する
    """
    if com._count_not_none(start, end, periods) != 2:  # Like a pd.date_range Error
        raise ValueError('Must specify two of start, end, or periods')
    start = start if start else (pd.Period(end, freq) - periods).start_time
    end = end if end else (pd.Period(start, freq) + periods).start_time
    return start, end


def to_unix_time(*dt: pd.datetime):
    """datetimeをunix秒に変換
    引数: datetime(複数指定可能)
    戻り値: unix秒に直されたリスト"""
    epoch = pd.datetime.utcfromtimestamp(0)
    return ((i - epoch).total_seconds() * 1000 for i in dt)


class StockPlot:
    """Plot candle chart using Plotly & StockDataFrame
    # USAGE

    ```
    # Convert StockDataFrame as StockPlot
    fx = StockPlot(sdf)

    # Add indicator
    fx.append('close_25_sma')

    # Remove indicator
    fx.append('close_25_sma')

    # Plot candle chart
    fx.plot()
    fx.show()
    ```
    """

    def __init__(self, df: pd.core.frame.DataFrame):
        # Arg Check
        co = ['open', 'high', 'low', 'close']
        assert all(i in df.columns for i in co), 'arg\'s columns must have {}, but it has {}'\
            .format(co, df.columns)
        if not type(df.index) == pd.tseries.index.DatetimeIndex:
            raise TypeError(df.index)
        self._init_stock_dataframe = ss.StockDataFrame(df)  # スパン変更前のデータフレーム
        self.stock_dataframe = None  # スパン変更後、インジケータ追加後のデータフレーム
        self.freq = None  # 足の時間幅
        self._fig = None  # <-- plotly.graph_objs

    def resample(self, freq: str):
        """Convert ohlc time span

        USAGE: `fx.resample('D')  # 日足に変換`

        * Args:  変更したい期間 M(onth) | W(eek) | D(ay) | H(our) | T(Minute) | S(econd)
        * Return: スパン変更後のデータフレーム
        """
        self.freq = freq
        self.stock_dataframe = self._init_stock_dataframe.ix[:, ['open', 'high', 'low', 'close']]\
            .resample(freq).agg({'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last'})\
            .dropna()
        return self.stock_dataframe

    def plot(self, start_view=None, end_view=None, periods_view=None, shift=None,
             start_plot=None, end_plot=None, periods_plot=None,
             showgrid=True, validate=False, **kwargs):
        """Retrun plotly candle chart graph

        USAGE: `fx.plot()`

        * Args:
            * start, end: 最初と最後のdatetime, 'first'でindexの最初、'last'でindexの最後
            * periods: 足の本数
            > **start, end, periods合わせて2つの引数が必要**
            * shift: shiftの本数の足だけ右側に空白
        * Return: グラフデータとレイアウト(plotly.graph_objs.graph_objs.Figure)
        """
        # ---------Set "plot_dataframe"----------
        # Default Args
        if com._count_not_none(start_plot,
                               end_plot, periods_plot) == 0:
            end_plot = 'last'
            periods_plot = 300
        # first/last
        start_plot = self.stock_dataframe.index[0] if start_plot == 'first' else start_plot
        end_plot = self.stock_dataframe.index[-1] if end_plot == 'last' else end_plot
        # Set "plot_dataframe"
        start_plot, end_plot = set_span(start_plot, end_plot, periods_plot, self.freq)
        plot_dataframe = self.stock_dataframe.loc[start_plot:end_plot]
        self._fig = FF.create_candlestick(plot_dataframe.open,
                                          plot_dataframe.high,
                                          plot_dataframe.low,
                                          plot_dataframe.close,
                                          dates=plot_dataframe.index)
        # ---------Set "view"----------
        # Default Args
        if com._count_not_none(start_view,
                               end_view, periods_view) == 0:
            end_view = 'last'
            periods_view = 50
        # first/last
        start_view = plot_dataframe.index[0] if start_view == 'first' else start_view
        end_view = plot_dataframe.index[-1] if end_view == 'last' else end_view
        # Set "view"
        start_view, end_view = set_span(start_view, end_view, periods_view, self.freq)
        end_view = set_span(start=end_view, periods=shift,
                            freq=self.freq)[-1] if shift else end_view
        view = list(to_unix_time(start_view, end_view))
        # ---------Plot graph----------
        self._fig['layout'].update(xaxis={'showgrid': showgrid, 'range': view},
                                   yaxis={"autorange": True})
        return self._fig

    def show(self, how='html', filebasename='candlestick_and_trace'):
        """Export file type"""
        if how == 'html':
            ax = pyo.plot(self._fig, filename=filebasename + '.html',
                          validate=False)  # for HTML
        elif how == 'jupyter':
            ax = pyo.iplot(self._fig, filename=filebasename + '.html',
                           validate=False)  # for Jupyter Notebook
        elif how in ('png', 'jpeg', 'webp', 'svg'):
            ax = pyo.plot(self._fig, image=how, image_filename=filebasename,
                          validate=False)  # for file exporting
        else:
            raise KeyError(how)
        return ax
