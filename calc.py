#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, "../..")

if sys.version_info[0] >= 3:
    raw_input = input

# Make a calculator function
import pandas as pd
import numpy as np
import ply.lex as lex
import ply.yacc as yacc
from ply.lex import TOKEN
import os
import re
import math
import operator
import builtin
import StringIO
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import mpl_finance as mpf
import datetime
plt.style.use('ggplot')

class Parser(object):
    """
    Base class for a lexer/parser that has the rules defined as methods
    """
    tokens = ()
    precedence = ()

    def __init__(self):

        # Build the lexer and parser
        self.names = {}
        self.funcs = {}
        self.lineno = 0
        self.lexer = lex.lex(module=self)
        self.parser = yacc.yacc(module=self)
        
    def execute(self, s):
        result = self.parser.parse(s)
        return result

    def run(self):
        while 1:
            try:
                s = raw_input('calc > ')
            except Exception:
                pass
            if s== 'exit':
                break
            val = self.execute(s)
            print 'result: \n',str(val)

class Calc(Parser):


    # ------- Internal calculator state
      # Dictionary of stored variablesc

    # ------- Calculator tokenizing rules

    tokens = (
        'ident',
        'newline',
        'integer',
        'pointfloat', 'exponentfloat',
        'add', 'subtract', 'multiply', 'divide', 'floordiv',
        'modulo', 'power', 'factorial',
        'lshift', 'rshift', 'and', 'not', 'or', 'xor',
        'lessthan','lessequel','equal','notequal','greaterthan','greaterequal',
        'assign',
        'addassign', 'subassign', 'mulassign', 'divassign',
        'modassign', 'powassign',
        'lsftassign', 'rsftassign',
        'andassign', 'orassign', 'xorassign',
        'lparen', 'rparen', 'comma', 'question', 'colon', 'dot'
    )

    # Tokens

    #t_keyword = r''
    t_ignore = ' \t'
    t_ident = r'[a-zA-Z_][a-zA-Z0-9_]*'

    # numeric operator
    t_add        = r'\+'
    t_subtract   = r'-'
    t_multiply   = r'\*'
    t_floordiv   = r'//'
    t_divide     = r'/'
    t_modulo     = r'%'
    t_power      = r'\*\*'
    t_factorial  = r'!'

    # bit operator
    t_lshift     = r'<<'
    t_rshift     = r'>>'
    t_and        = r'&'
    t_not        = r'~'
    t_or         = r'\|\|'
    t_xor        = r'\^'
    t_lessthan   = r'<'
    t_lessequel  = r'<='
    t_equal      = r'=='
    t_notequal   = r'!='
    t_greaterthan= r'>'
    t_greaterequal=r'>='

    # delimiter
    t_assign     = r'='
    t_addassign  = r'\+='
    t_subassign  = r'-='
    t_mulassign  = r'\*='
    t_divassign  = r'/='
    t_modassign  = r'%='
    t_powassign  = r'\*\*='

    t_lsftassign = r'<<='
    t_rsftassign = r'>>='
    t_andassign  = r'&='
    t_orassign   = r'\|='
    t_xorassign  = r'\^='

    t_lparen     = r'\('
    t_rparen     = r'\)'
    t_comma      = r','
    t_question   = r'\?'
    t_colon      = r'\:'
    t_dot        = r'\.'



    def t_newline(self,t):
        r'\n+'
        return t
    def t_exponentfloat(self, t):
        r'[0-9]+(\.[0-9]+)?[eE][+-]?[0-9]+'
        t.value = float(t.value)
        return t

    def t_pointfloat(self, t):
        r'[0-9]+\.[0-9]+'
        t.value = float(t.value)
        return t
    
    def t_integer(self, t):
        r'\d+'
        t.value = int(t.value)
        return t

    def t_error(self, t):
        t.lexer.skip(1)
        raise SyntaxError("illegal character '%s'" % (t.value[0]))

    ## Parsing rules

    precedence = (
        ('left', 'assign', 'addassign', 'subassign', 'mulassign',
         'divassign', 'modassign', 'powassign', 'lsftassign',
         'rsftassign', 'andassign', 'orassign', 'xorassign'),
        ('left', 'and', 'or', 'xor'),
        ('left', 'lessthan', 'lessequel', 'equal', 'notequal', 'greaterthan', 'greaterequal'),
        ('left', 'question', 'colon'),
        ('left', 'lshift', 'rshift'),
        ('left', 'add', 'subtract'),
        ('left', 'multiply', 'divide', 'modulo', 'floordiv'),
        ('right','usub', 'uadd', 'not'),
        ('left', 'factorial'),
        ('left', 'power'),
        ('left', 'dot'),
        )



    common_binops = {
        '+'   : operator.add,
        '-'   : operator.sub,
        '*'   : operator.mul,
        '/'   : operator.div,
        '//'  : operator.floordiv,
        '%'   : operator.mod,
        '**'  : operator.pow,
        '+='  : operator.iadd,
        '-='  : operator.isub,
        '*='  : operator.imul,
        '/='  : operator.idiv,
        '%='  : operator.imod,
        '**=' : operator.ipow,
        '<'   : operator.lt,
        '<='  : operator.le,
        '>'   : operator.gt,
        '>='  : operator.ge,
        '=='  : operator.eq,
        '!='  : operator.ne,
    }

    int_binops = {
        '<<'  : operator.lshift,
        '>>'  : operator.rshift,
        '&'   : operator.and_,
        '~'   : operator.inv,
        '||'  : operator.or_,
        '^'   : operator.xor,
        '<<=' : operator.ilshift,
        '>>=' : operator.irshift,
        '&='  : operator.and_,
        '|='  : operator.or_,
        '^='  : operator.xor,
    }

    def p_expression_assign(self, p):
        '''
        expression : ident assign     expression
                   | ident addassign  expression
                   | ident subassign  expression
                   | ident mulassign  expression
                   | ident divassign  expression
                   | ident modassign  expression
                   | ident powassign  expression
                   | ident lsftassign expression
                   | ident rsftassign expression
                   | ident andassign  expression
                   | ident orassign   expression
                   | ident xorassign  expression
        '''
        var = self.names.get(p[1], 0)
        if p[2] == '=':
            if p[3] is None: p[3] = 0
            p[0] = p[3]

        elif p[2] == '/=':
            p[0] = self.common_binops[p[2]](var, float(p[3]))

        elif p[2] in self.common_binops:
            p[0] = self.common_binops[p[2]](var, p[3])

        else:
            p[0] = self.int_binops[p[2]](var, p[3])

        self.names[p[1]] = p[0]

    def p_expression_binop(self, p):
        '''
        expression : expression add expression
                   | expression subtract expression
                   | expression multiply expression
                   | expression divide expression
                   | expression floordiv expression
                   | expression or expression
                   | expression xor expression
                   | expression and expression
                   | expression lessthan expression
                   | expression lessequel expression
                   | expression equal expression
                   | expression notequal expression
                   | expression greaterthan expression
                   | expression greaterequal expression
                   | expression lshift expression
                   | expression rshift expression
                   | expression modulo expression
                   | expression power expression
        '''
        if p[2] == '/':
            p[3] = p[3]

        if p[2] in self.common_binops:
            p[0] = self.common_binops[p[2]](p[1], p[3])
        else:
            p[0] = self.int_binops[p[2]](p[1], p[3])

    def p_expression_unary(self, p):
        '''expression : subtract expression %prec usub
                      | add expression %prec uadd
                      | not expression
        '''
        if    p[1] == '-' :
            p[0] = -p[2]
        elif  p[1] == '+' : p[0] =  p[2]
        elif  p[1] == '~' : p[0] = ~p[2]

    
    
    def p_expression_factorial(self, p):
        '''expression : expression factorial
        '''
        p[0] = math.factorial(p[1])

    def p_expression_func(self, p):
        'expression : function'
        p[0] = p[1]

    def p_func_with_args(self, p):
        'function : ident lparen arguments rparen'
        if p[1] in self.TA_funcs:
            if type(p[3][0]) == pd.core.series.Series:
                inputs = {'open': p[3][0].values,'high': p[3][0].values,
                        'low': p[3][0].values,'close': p[3][0].values,
                        'volume': p[3][0].values}
                p[3][0] = pd.DataFrame(inputs,index = p[3][0].index)
                p[0] = self.TA_funcs[p[1]](*p[3])
            elif type(p[3][0]) == pd.core.frame.DataFrame:
                p[0] = self.TA_funcs[p[1]](*p[3])
        elif p[1] in self.funcs:
            p[0] = self.funcs[p[1]](*p[3])
        else:
            raise SyntaxError('function: %s not found' % p[1])
            

    def p_func_without_args(self, p):
        'function : ident lparen rparen'
        if p[1] in self.funcs:
            p[0] = self.funcs[p[1]]()
        else:
            raise SyntaxError('function: %s not found' % p[1])

    def p_arguments_plural(self, p):
        '''
        arguments : expression comma arguments
        '''
        p[0] = p[3][:]
        p[0].insert(0, p[1])

    def p_arguments_single(self, p):
        '''
        arguments : expression
        '''
        p[0] = [p[1]]

    def p_expression_group(self, p):
        'expression : lparen expression rparen'
        p[0] = p[2]

    def p_expression_number(self, p):
        '''
        expression : integer
                   | float
        '''
        p[0] = p[1]
    
        
    def p_float(self, p):
        '''float : pointfloat
                 | exponentfloat
        '''
        p[0] = p[1]

    def p_expression_ident(self, p):
        'expression : ident'
        if p[1] in self.names.keys():
            p[0] = self.names[p[1]]
        else:
            if any(i.isdigit() for i in p[1]) and any(i.isalpha() for i in p[1]):
                try:
                    p[0] =  getattr(self.names['CTP'], p[1])
                except:
                    self.error += 'No contract named %s \n'%p[1]
            else:
                self.error += '%s is not a defined variable or contract \n'% p[1]
                print self.error

    def p_expression_attr(self, p):
        'expression : expression dot ident'
        if hasattr(p[1],p[3]):
            p[0] = getattr(p[1], p[3])
        else:
            self.error += 'has no attribute of %s \n'%p[3]
            print self.error

    def p_expression_ternary(self, p):
        'expression : ternary'
        p[0] = p[1]

    def p_expression_question(self, p):
        'ternary : expression question expression colon expression'
        p[0] = self.funcs['ternary'](p[1],p[3],p[5])

    def p_ternary_group(self, p):
        'expression : lparen ternary rparen'
        p[0] = p[2]

    def p_expression_nextline(self,p):
        '''
        expression : expression comma expression
                   | expression newline expression
        '''
        p[0] = p[3]

    def p_error(self, p):
        if p:
            self.error = "syntax error at '%s'" % (p.value)
        else:
            self.error = "unkown syntax error"

    def __init__(self):
        super(Calc, self).__init__()
        self.names = {}
        self.funcs = {}
        self.funcs.update(builtin.funcs)
        self.TA_funcs = builtin.TA_funcs
        self.funcs['PLOT'] = self.PLOT
        self.names['e'] = math.e
        self.names['pi'] = math.pi
        self.names['phi'] = 1.6180339887498948482
        self.names['column'] = 'column'
        self.names['line'] = 'line'
        self.names['candlestick'] = 'candlestick'
        self.json_result = []
        self.data = []
        self.df = pd.DataFrame()
        self.error = ''

    def set_args(self, period, ts, te, figsize=(12,4.5)):
        self.period = period
        self.ts = ts
        self.te = te
        self.figsize = figsize
        self.names['CTP'] = Exchange('CTP', self.period, self.ts, self.te)
        self.names['BITFINEX'] = Exchange('BITFINEX', self.period, self.ts, self.te)
        self.names['OKEX'] = Exchange('OKEX', self.period, self.ts, self.te)
        self.names['OKCOIN'] = Exchange('OKCOIN', self.period, self.ts, self.te)
        self.names['HUOBI'] = Exchange('HUOBI', self.period, self.ts, self.te)

    def get_result(self,s):
        try:
            response = self.execute(s)
            ret_json = []
            #without plot       
            if self.data == [] and type(response) != np.float64 and type(response) != np.int64 and type(response) != int and type(response) != float and type(response.index[0]) == np.int64:
                if type(response) == pd.Series:
                    response = response.to_frame()
                if set(['open','high','high','close','volume']).issubset(set(response.columns)):
                    ret_json.append({'name':'Time', 'type':'time', 'group':-1, 'data':list(response.index)})
                    ret_json += [{'name':'ohlc','type':'candlestick','data':response[['open','high','low','close']].values.tolist(),'group':0}]
                    ret_json += [{'name':'volume','type':'column','data':response['volume'].values.tolist(),'group':1}]
                else:
                    response['Time'] = response.index.astype(int)
                    ret_json = [{'name':c,'type':'line','group':0,'data':list(response[c].values)} for c in response.columns]
                for r in ret_json:
                    if r['name'] == 'Time':
                        r['group'] = -1

            #with plot
            elif len(self.data)>=1:
                for d in self.data:
                    self.df = pd.concat([self.df,d['data']], axis=1)
                index = self.df.index
                ret_json += [{'name':'Time', 'data':list(index), 'type':'time', 'group':-1}]
                for d in self.data:
                    if type(d['data']) == pd.Series:
                        ret_json += [{'name':d['name'], 'data':d['data'].reindex(index).tolist(), 'type':d['type'], 'group':d['group']}]
                    else:
                        if d['type'] == 'candlestick':
                            ret_json += [{'name':'Kline', 'type':d['type'], 'group':d['group'], 'data':d['data'][['open','high','low','close']].reindex(index).values.tolist()}]
                        else:
                            ret_json += [{'name':c, 'type':d['type'], 'group':d['group'], 'data':d['data'][c].reindex(index).values.tolist()} for c in d['data'].columns]

            #return a num
            else:
                if type(response) == np.float64:
                    ret_json += [{'name':'value','type':'number','data':[response]}]
                if type(response) == pd.Series:
                    response = response.apply(lambda x:round(x,3))
                    ret_json += [{'name':'value', 'type':'number', 'data':list(response.values)}]
                else:
                    ret_json += [{'name':'value','type':'number','data':[response]}]
            return ret_json, self.error
        except:
            return [0], self.error

    def get_plot_result(self,s):
        data = self.get_result(s)[0]
        if data[0]['type'] == 'number':
            return None
        groups = len(set([d['group'] for d in data]))-1
        fig, axarr = plt.subplots(groups, sharex=True, figsize=(self.figsize[0], self.figsize[1]*groups))
        if type(axarr) != np.ndarray:
            axarr=[axarr]
        for d in data:
            if d['type'] == 'number':
                return
            if d['name'] == 'Time':
                timestamp = d['data']
                date = pd.to_datetime(d['data'], unit='s') + pd.Timedelta('8 h')
                x_length = len(d['data'])
                break
        for d in data:
            if d['name'] == 'Time':
                continue
            if d['type'] == 'line':
                axarr[d['group']].plot(range(x_length), d['data'])
            elif d['type'] == 'column':
                axarr[d['group']].bar(range(x_length), d['data'], width=0.97)
            elif d['type'] == 'candlestick':
                data = pd.DataFrame(data=d['data'], columns=['open', 'high', 'low', 'close'])
                data['time'] = range(x_length)
                data = data[['time', 'open', 'high', 'low', 'close']]
                quotes = data.dropna().values.tolist()
                mpf.candlestick_ohlc(axarr[d['group']], quotes, width=0.9, colorup='r', colordown='green')
            if x_length<10:
                axarr[0].set_xticks(range(x_length))
                axarr[0].set_xticklabels(date.map(lambda x:x.strftime('%Y-%m-%d')))
            else:
                axarr[0].set_xticks(range(x_length)[::x_length/8])
                axarr[0].set_xticklabels(date.map(lambda x:x.strftime('%Y-%m-%d'))[::x_length/8])
            fig.subplots_adjust(hspace=0.05)
            
        #plt.tight_layout()
        period = self.period
        period_str = 'period='+str(period/60)+'hour' if period>=60 else 'period='+str(period)+'min'
        
        fig = plt.gcf()
        fig.text(0.5, 0.5, 'QUANT.LA', fontsize=40, color='gray', ha='center', va='center', alpha=0.5)
        fig.suptitle(s+' '+period_str, y=0.98)
        canvas = FigureCanvas(fig)
        output = StringIO.StringIO()
        canvas.print_png(output)
        fig.clear()

        return output

        
    def PLOT(self,x,group=0,plot_type='line'):
        if type(group) == str and type(plot_type) == int:
            group, plot_type = plot_type, group
        if type(group) == str and type(plot_type) == str:
            plot_type = group
            group = 0
        self.data += [{'group':group, 'type':plot_type, 'data':x, 'name':x.name if hasattr(x, 'name') else 'series'}]

class Exchange:
    def Kline(self,ins):
        if self.exchange.upper() == 'CTP':
            contract = ins
        if self.exchange.upper() == 'BITFINEX':
            contract = ins + '_BITFINEX'
        if self.exchange.upper() == 'OKCOIN':
            contract = ins + '_OKCOIN'
        if self.exchange.upper() == 'OKEX':
            contract = ins + '_OKEX'
        if self.exchange.upper() == 'HUOBI':
            contract = ins + '_HUOBI'
        data = pd.read_json('http://q.fmz.com/chart/history?symbol=%s&resolution=%s&from=%s&to=%s'%(contract,self.period,self.ts,self.te))
        data.columns=['time','open','high','low','close','volume']
        data.index = data['time']
        return data[['open','high','low','close','volume']].astype(float)

    def __init__(self,e,period=24*60, ts=1014344857, te=2614344857):
        self.exchange = e
        self.period = period
        self.ts = ts
        self.te = te
    def __getattr__(self, attr):
        res = self.Kline(attr)
        setattr(self,attr,res)
        return res
    def __str__(self):
        return 'Exchange %s'%self.exchange
    def __repr__(self):
        return 'Exchange %s'%self.exchange

if __name__ == '__main__':

    calc = Calc()
    calc.set_args(24*60, 1519142400, 1521734399)
    calc.run()