#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urlparse
from flask import Flask, request, make_response, Response, send_file
import TA
from calc import Calc
import pandas as pd
import numpy as np
import time
import datetime
from werkzeug.contrib.cache import SimpleCache
import simplejson
from flask_compress import Compress
import os
import logging


app = Flask(__name__)
Compress(app)
cache = SimpleCache()

@app.route('/q/plot/')
def plot():
    '''
    DataFrame.plot(x=None, y=None, kind='line', ax=None, subplots=False, sharex=None, sharey=False, 
    layout=None, figsize=None, use_index=True, title=None, grid=None, legend=True, style=None, 
    logx=False, logy=False, loglog=False, xticks=None, yticks=None, xlim=None, ylim=None, rot=None, 
    fontsize=None, colormap=None, table=False, yerr=None, xerr=None, secondary_y=False, sort_columns=False, **kwds)
    '''
    url = request.url
    app.logger.debug(url)
    query = urlparse.parse_qs(urlparse.urlparse(url).query)
    query = {k: v[0] for k, v in query.items()}
    period = int(query['period'])
    period_str = 'period='+str(period/60)+'hour' if period>=60 else 'period='+str(period)+'min'
    ts = 1505471244
    te = 1515480244
    if '-' in query['start']:
        ts = time.mktime(datetime.datetime.strptime(query['start'], "%Y-%m-%d").timetuple())
        te = time.mktime(datetime.datetime.strptime(query['end'], "%Y-%m-%d").timetuple())
    else:
        ts = int(query['start'])
        te = int(query['end'])
    formula = query['formula']
    figsize = (10,4)
    if 'figsize' in query.keys():
        figsize = (int(query['figsize'].split(',')[0][1:]), int(query['figsize'].split(',')[1][:-1]))
    cache_items = 'plot' + str(period) + str(ts) + str(te) + str(figsize) + str(formula)
    rv = cache.get(cache_items)
    if rv is not None:
        app.logger.debug('use cache')
        return rv
    calc_func = Calc()
    calc_func.set_args(period, int(ts), int(te),figsize)
    plot = calc_func.get_plot_result(formula.strip(' \n'))
    if plot is None:
        return simplejson.dumps({'err':'No images to plot'}, ignore_nan=True),200,[('Content-Type','application/json;charset=utf-8')]
    app.logger.info(formula.strip(' \n'))
    response = make_response(plot.getvalue())
    response.mimetype = 'image/png'
    cache.set(cache_items,response,timeout=3600)
    return response


@app.route('/q/calc/')
def calc():
    url = request.url
    app.logger.debug(url)
    query = urlparse.parse_qs(urlparse.urlparse(url).query)
    query = {k: v[0] for k, v in query.items()}
    period = int(query['period'])
    period_str = 'period='+str(period/60)+'hour' if period>=60 else 'period='+str(period)+'min'
    ts = 1505471244
    te = 1515480244
    if '-' in query['start']:
        ts = time.mktime(datetime.datetime.strptime(query['start'], "%Y-%m-%d").timetuple())
        te = time.mktime(datetime.datetime.strptime(query['end'], "%Y-%m-%d").timetuple())
    else:
        ts = int(query['start'])
        te = int(query['end'])
    formula = query['formula']
    figsize = (10,5)
    if 'figsize' in query.keys():
        figsize = (int(query['figsize'].split(',')[0][1:]), int(query['figsize'].split(',')[1][:-1]))
    cache_items = 'calc' + str(period) + str(ts) + str(te) + str(figsize) + str(formula)
    rv = cache.get(cache_items)
    if rv is not None:
        app.logger.debug('use cache')
        return simplejson.dumps(rv, ignore_nan=True),200,[('Content-Type','application/json;charset=utf-8')]
    calc_func = Calc()
    calc_func.set_args(period, int(ts), int(te))
    ret_json = {}
    calc_result = calc_func.get_result(formula.strip(' \n'))
    app.logger.info(formula.strip(' \n'))
    error = calc_result[1]
    if not error:
        ret_json['code'] = 0
        ret_json['series'] = calc_result[0]
    else:
        ret_json['code'] = 1
        ret_json['series'] = []
        ret_json['msg'] = error
        app.logger.error(error)
    ret_json['formula'] = formula
    ret_json['period'] = period
    ret_json['ts'] = ts
    ret_json['te'] = te
    if len(ret_json['series']) > 0:
        cache.set(cache_items,ret_json,timeout=3600)
    return simplejson.dumps(ret_json, ignore_nan=True),200,[('Content-Type','application/json;charset=utf-8')]

@app.route('/q/ta/')
def ta():
    url = request.url
    query = urlparse.parse_qs(urlparse.urlparse(url).query)
    query = {k: v[0] for k, v in query.items()}
    contract = query['symbol']
    func = query['func']
    args = func.parameters
    period = int(query['period'])
    ts = int(query['ts'])
    te = int(query['te'])
    params = query['params'].split(',')
    for i,p in enumerate(params):
        if p : args[args.keys()[i]]=int(p)
    max_period = max([args[i] for i in filter(lambda x:'period' in x,args)])
    max_period += max(50,0.5*max_period)
    data = pd.read_json('http://q.fmz.com/chart/history?symbol=%s&resolution=%s&from=%s&to=%s'%(contract,period,ts,te)).astype(float)
    data.columns=['time','open','high','low','close','volume']
    data.index = data['time']
    ret = TA.calc(func, data.dropna(), ts, te, **args)
    return ret.to_json()

if __name__ == '__main__':

    app.debug = True
    handler = logging.FileHandler('flask.log', encoding='UTF-8')
    handler.setLevel(logging.DEBUG)
    logging_format = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s')
    handler.setFormatter(logging_format)
    app.logger.addHandler(handler)

    app.run(host='0.0.0.0',port=82,threaded=True)