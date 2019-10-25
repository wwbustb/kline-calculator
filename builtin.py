#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author:  lightxue
# Email:   bkmgtp@gmail.com
# Version: 0.01
# Website: https://github.com/lightxue/SwissCalc

import math
import re
import pandas as pd
import numpy as np
from scipy.stats import rankdata
import talib
from talib.abstract import Function


funcs = {}
# Numeric

math_funcs = {var : getattr(math, var)
              for var in dir(math) if callable(getattr(math, var))}
funcs.update(math_funcs)

#talib

TA_funcs = {var : talib.abstract.Function(var)
              for var in talib.get_functions()}

def ternary(p,x,y):
    if type(x) != pd.core.series.Series:
        x = pd.Series(index=p.index,data=x)
    if type(y) != pd.core.series.Series:
        y = pd.Series(index=p.index,data=y)
    temp = y.copy()
    temp[p]=x[p]
    return temp

def log(x):
    return np.log(x)

def shift(x,n):
    return x.shift(n)

def delay(x,n):
    return x.shift(n)

def abs(x):
    return x.abs()

def sum(x, n=None):
    if n:
        return x.rolling(n).sum()
    else:
        return x.sum()

def mean(x, n=None):
    if n:
        return x.rolling(n).mean().apply(lambda s:round(s,4))
    else:
        return x.mean()

def std(x,n=None):
    if n:
        return x.rolling(n).std().apply(lambda s:round(s,4))
    else:
        return x.std()

def rank(x):
    return x.rank()

def min(x,y=None):
    if y is not None:
        return np.minimum(x,y)
    else:
        return x.min()

def max(x,y=None):
    if y is not None:
        return np.maximum(x,y)
    else:
        return x.max()

def tsrank(x,n):
    return x.rolling(n).apply(lambda x:rankdata(x)[-1])

def tsmin(x,n):
    return x.rolling(n).min()

def tsmax(x,n):
    return x.rolling(n).max()

def prod(x,n):
    return x.rolling(n).apply(lambda x:np.prod(x))

def delta(x,n=1):
    return x.diff(n)

def cov(x,y,n):
    if n:
        return x.rolling(n).cov(y).apply(lambda s:round(s,4))
    else:
        return np.cov(x,y)[0][1]

def corr(x,y,n):
    return  x.rolling(n).corr(y).apply(lambda s:round(s,4))

def sma(x,n,m):
    x = x.fillna(0)
    res = x.copy()
    for i in range(1,len(x)):
        res.iloc[i] = (x.iloc[i]*m+res.iloc[i-1]*(n-m))/float(n)
    return res.apply(lambda s:round(s,4))

def skew(x,n):
    return x.rolling(n).skew().apply(lambda s:round(s,4))

def kurt(x,n):
    return x.rolling(n).kurt().apply(lambda s:round(s,4))

def sign(x):
    return np.sign(x)

def wma(x,n):
    return x.rolling(n).apply(lambda y:sum(y*np.arange(1,n+1))/np.arange(1,n+1).sum()).apply(lambda s:round(s,4))

def highday(x,n):
    return x.rolling(n).apply(lambda x:n-np.argmax(x))

def lowday(x,n):
    return x.rolling(n).apply(lambda x:n-np.argmin(x))

def sequence(n):
    return np.arange(1,n+1)

def regbeta(x,y,n):
    def calcbeta(a,b):return sum((a-a.mean())*(b-b.mean()))/sum((a-a.mean())**2) if not a.empty else np.nan
    beta = pd.concat([(pd.Series(calcbeta(x[i-n:i],y[i-n:i]), index=[x.index[i]])) for i in range(len(x))])
    return beta.apply(lambda s:round(s,5))

def regresi(x,y,n):
    beta = regbeta(x,y,n)
    res = y-beta*x
    return res.apply(lambda s:round(s,5))

def sumif(x,n,p):
    x[~p]=0
    return x.rolling(n).sum()

def count(p,n=None):
    if n:
        return p.rolling(n).sum()
    else:
        return p.sum()
def kdj(x,n=9, k=3, d=3):
    rsv = 100*(x-x.rolling(n).min())/(x.rolling(n).max()-x.rolling(n).min())
    kv = x.copy()
    kv.name = 'k'
    dv = x.copy()
    dv.name = 'd'
    kv.iloc[0]=50
    dv.iloc[0]=50
    for i in range(1,len(x)):
        if np.isnan(kv.iloc[i-1]):
            kv.iloc[i-1] = 50
            dv.iloc[i-1] = 50
        kv.iloc[i] = ((k-1)*kv.iloc[i-1] + rsv.iloc[i])/float(k)
        dv.iloc[i] = ((d-1)*dv.iloc[i-1] + kv.iloc[i])/float(d)
    jv = 3*kv - 2*dv
    jv.name = 'j'
    return pd.concat([kv,dv,jv],axis=1).applymap(lambda s:round(s,4))

def IC(x,r):
    mask = reduce(np.logical_and,[~np.isnan(x),~np.isinf(x),~np.isnan(r),~np.isinf(r)])
    return round(np.corrcoef(x[mask], r[mask])[0][1], 4)

def test(x=1,y=1,z=1):
    return 'x=',x,' y=',y,' z='



builtin_funcs = {var : globals()[var]
              for var in dir() if callable(globals()[var])}
funcs.update(builtin_funcs)