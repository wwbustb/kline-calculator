#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import StringIO
import talib
from talib.abstract import Function
import matplotlib as mpl
mpl.use('Agg')
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure



def getData(contract,conn,p=15,s=1014344857,e=3614344857):
    if not conn.is_connected:
        try:
            conn = connect(**mysql_info)
        except:
            return None
    contract = contract.split('-')
    if len(contract)==2:
        try:
            sql = "select * from _FUTURES_%s where p = %s and t >= %d and t <= %d"%(contract[0], p*60, s, e)
            data1 = pd.read_sql(sql,conn)
            data1.index = data1['t']
            sql = "select * from _FUTURES_%s where p = %s and t >= %d and t <= %d"%(contract[1], p*60, s, e)
            data2 = pd.read_sql(sql,conn)
            data2.index = data2['t']
            data = data1 - data2
            data['v'] = data1['v'] + data2['v']
            data.columns = ['time', 'perid', 'open', 'high', 'low', 'close', 'volume']
            data.loc[data['open'] >= data['close'], ['high', 'low']] = data[['open', 'close']].rename(columns={'open':'high', 'close':'low'})
            data.loc[data['open'] < data['close'], ['high', 'low']] = data[['close', 'open']].rename(columns={'open':'low', 'close':'high'})
            data = data[['open', 'high', 'low', 'close', 'volume']]
        except:
            print 'contract not found'
    else:
        try:
            sql = "select * from _FUTURES_%s where p = %s and t >= %d and t <= %d"%(contract[0],p*60,s,e)
            data = pd.read_sql(sql,conn)
            data.index =data['t']
            data.columns = ['time','perid','open','high','low','close','volume']
            data = data[['open','high','low','close','volume']]
        except:
            print 'contract not found'
    return data

def calc(func,data,ts,te,**args):
    func = Function(func)
    ret = func(data,**args)
    ret = ret[np.logical_and(ret.index>=ts,ret.index<=te)]
    return ret

def plot(data,**args):
    #axis = fig.add_subplot(1, 1, 1)
    data.index = pd.to_datetime(data.index, unit='s') + pd.Timedelta('8 h')
    ax = data.plot(**args)
    fig = ax.get_figure()
    canvas = FigureCanvas(fig)
    output = StringIO.StringIO()
    canvas.print_png(output)
    fig.clear()

    return output
