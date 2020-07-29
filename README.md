# 表达式说明

本表达式用于快速对时间序列进行运算，让不会编程语言的新手也能通过写出公式，验证想法。地址为 https://www.quantinfo.com/Tools/View/3/formula.html
欢迎到 www.fmz.com 进行量化交易。

## 支持数据

目前支持商品期货数据和部分数字货币数据，即quantinfo网站上存在的行情数据。
商品期货支持期货合约，连续合约（后缀888）和指数合约（后缀000），支持周期1分钟、5分钟、15
分钟、30分钟、1小时、4小时、1日等，可获取到open、high、low、close、volume,可选择时间范围。

## 数据调用方式

1. 商品期货：`CTP.MA805.close`,其中CTP代表商品期货，MA805代表甲醇805合约，close代表收盘价。
2. 如果直接使用`CTP.MA805`,其中包含5组数据`open、high、low、close、volume`，在计算中注意保持数据
维度的一致。
3. 数字货币支持交易对：
    BCH_BTC_HUOBI,BCH_BTC_OKEX,BTC_FUTURES_NEXT_WEEK_OKEX,BTC_FUTURES_QUARTER_OKEX   
    BTC_FUTURES_THIS_WEEK_OKEX,BTC_USD_BITFINEX,BTC_USD_OKCOIN,ETC_BTC_HUOBI,ETC_BTC_OKEX               
    ETH_BTC_HUOBI,ETH_BTC_OKEX,LTC_BTC_HUOBI,LTC_BTC_OKEX
    调用方式：HUOBI.BCH_BTC，OKEX.LTC_BTC等。注意数据有缺失。
4. 默认选择商品期货，可以直接输入`MA888.close`代替`CTP.MA888.close`
5. 其它交易所和交易对待支持。

## TA-Lib库支持

可以直接使用talib库中的函数，如`SMA(CTP.MA805,20)`,注意此时`CTP.MA805`不要加`.close`,程序会自行确定使用相应数据，不指定参数使用默认参数，如果要指定参数须按顺序填写，参数只能为数字。
如果函数返回多组数据，如`MACD(CTP.MA805)`返回macd、macdsignal、macdhist三组数据，此时调用`MACD(CTP.MA805).macd`
具体talib库的返回值和参数设置https://mrjbq7.github.io/ta-lib/doc_index.html

## 其它函数支持

以下函数中，输入x代表数据时间序列，输入p代表逻辑时间序列，输出未说明均为与输入格式相同的序列
1. log(x)：
取x的自然对数。
2. shift(x,n):
x平移n，n为正数代表向前平移，负数向后。如`shift(CTP.MA805.close,1)`即计算与上一根
K线收盘价的价差，注意`shift(CTP.MA805,1).close`的效果相同。
delay(x,n)为同一函数。
3. abs(x)： 
x的绝对值。
4. mean(x,n): 
时间序列x的滚动平均值，窗口为n，如`mean(CTP.MA805.close,10)`即为10个周期收盘价均值。
如果不传入n,则返回x的总体平均值。
5. std(x,n): 
窗口为n的滚动标准差。如果不传入n,则返回x的总体标准差。
6. sum(x,n):
窗口为n的滚动和。如果不传入n,则返回x的总体和。
7. rank(x): 
x的排序值，最小为1。
8. min(x,y)：
返回x和y序列中的对应位置较小的组成的新序列，如`min(CTP.MA805.close,CTP.MA809.close)`
如果只传入x,则返回x的最小值。
9. max(x,y):
如上
10. tsrank(x,n):
窗口为n的滚动排序值。
11. tsmin(x,n):
窗口为n的最小值。
12. tsmax(x,n):
窗口为n的最大值。
13. prod(x,n): 
窗口为n的连乘积。
14. delta(x,n):
距离为n的差分，如`CTP.MA805.close.delay(1)/CTP.MA805.close.shift(1)`即为相应周期
的收益率序列。
15. cov(x,y,n):
序列x和y的滚动协方差。
16. corr(x,y,n):
序列x和y的滚动相关系数。如`corr(CTP.MA809.close,CTP.MA805.close,20)`,即为20个周期
甲醇9月份和5月份收盘价的相关系数。
17. sma(x,n,m):
自定义的sma函数。
18. skew(x,n):
窗口为n的偏度。
19. kurt(x,n): 
窗口为n的峰度。
20. wma(x,n): 
自定义的wma函数。
21. highday(x,n):
窗口为n，序列里最大值据当前的距离。
22. lowday(x,n): 
窗口为n，序列里最小值据当前的距离。
23. sequence(n)：
长度为n的等差序列，即[1,2,3,...n]
24. regbeta(x,y,n):
窗口为n内，x对y回归的系数。
25. regresi(x,y,n):
窗口为n内，x对y回归的残差。
26. sumif(x,n,p)：
窗口为n内，满足条件p的x的求和，如：
`sumif(CTP.MA809.volume,30,CTP.MA809.volume>100)`
即MA809合约在30个周期的窗口内，满足交易量大于100的成交量求和。
27. count(p,n): 
窗口为n内，满足条件p的x的个数，如：`count(CTP.MA809.volume>100,30)`
n不传入，默认统计整个时间序列
28. sign(x): 
序列x的符号，正数为1，负数为-1.
29. kdj(x,n=9,k=3,j=3):
KDJ指标，调用`kdj(MA888.close).k`
30. IC(x,r):
x为所求的alpha因子,r为收益率序列.返回一个数字。

## 支持的运算符与常数

注意运算支持时间序列，代表相应位置的运算，返回的仍然是时间序列
1. 支持+, -, *, /,四则运算。
2. \**指数运算。
3. ==, >=, >, <, <=, !=，比较运算符
4. &(与)，||(或)，~(非)，逻辑运算符
6. //,整除;%,取余
7. p?x:y 三目运算，如:
`(CTP.MA809.close-CTP.MA805.close)>20?1:0`
表示如果MA809合约收盘价大于MA805合约20元，值取1，否则为0。也支持：
`(CTP.MA809.close-CTP.MA805.close)>20?CTP.MA809.close:CTP.MA805.close`
8. 自然对数的底数：e;圆周率：pi;黄金分割比：phi

## 语法与绘图

1. 使用逗号和换行分隔不同的句子，支持赋值操作，把最后一句的结果画出,如:
`p = CTP.MA809.close>CTP.MA805.close,a = CTP.MA809.close,b = CTP.MA805.close,p?a:b`
2. 可使用PLOT函数画不同的图和类型，如：
`PLOT(MA888.close,line,0),PLOT(MA888.volume,column,1)`
会画两张共享x轴(时间轴)的图，第一个参数是类型，可选line:线，columns:柱。第二个参数是所属的分组，
同一分组的图将叠加绘制。默认画线，分组为0.注意分组顺序从0开始，依次加1.
注意当语句中出现`PLOT()`函数时，规则1不再使用。
3. 注意标点符号应为英文标点。


## 应用示例

1. 简易计算器功能:
`3\**0.5+2.0/3*(3+4)+pi`

2. 画K线： 
`PLOT(MA888,candlestick,0),PLOT(MA888.volume,column,1)`

3. 计算收益率序列：
`100*delta(MA888.close,1)/delay(MA888.close,1)`

4. 3中的收益率由于主力合约切换，收益率序列产生异常值，可以使用三目运算去异常值：
`100*abs(delta(MA888.close,1)/delay(MA888.close,1))>5?0:100*delta(MA888.close,1)/MA888.close`

5. 在K线上叠加均线：
`PLOT(MA888,candlestick,0),PLOT(mean(MA888.close,10),0)`

6. 使用TA-Lib库的函数：
`PLOT(MA888.close,0),PLOT(MACD(MA888,10),1)`

7. 合约跨期套利，画出合约差价：
`MA809.close-MA805.close`

8. 合约跨期套利，求出平均差价：
`mean(MA809.close-MA805.close)`

9. 合约跨期套利，最大差价：
`max(MA809.close-MA805.close)`

10. 合约跨期套利，求出差价标准差：
`std(MA809.close-MA805.close)`

11. 合约跨期套利，差价大于20的次数：
`count(MA805.close-MA809.close>20)`

12. 跨品种套利，画出两品种相关系数变化：
`corr(j888.close,jm888.close,15)`

13. 跨品种套利，画出两品种线性回归系数的变化：
`regbeta(j888.close,jm888.close,15)`

14. 简单改一下可以套用一些alpha公式
参考：[聚宽](https://www.joinquant.com/data/dict/alpha191#alpha181)
注意链接里的文章错误较多，可参考原始研报[国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系](http://vdisk.weibo.com/s/uEfe2futCdyJ9)

如alpha_001，原始公式为：

`(-1 * CORR(RANK(DELTA(LOG(VOLUME),1)),RANK(((CLOSE-OPEN)/OPEN)),6))`

改为：

`-1 * corr(rank(delta(log(MA888.volume),1)),rank(((MA888.close-MA888.open)/MA888.open)),6)`

如alpha_002, 原始公式为：

`-1 * delta(((close-low)-(high-close))/((high-low)),1)`

改为：

`-1 * delta(((MA888.close-MA888.low)-(MA888.high-MA888.close))/((MA888.high-MA888.low)),1)`

如alpha_003,原始公式为：

`SUM((CLOSE=DELAY(CLOSE,1)?0:CLOSE-(CLOSE>DELAY(CLOSE,1)?MIN(LOW,DELAY(CLOSE,1)):MAX(HIGH,DELAY(CLOSE,1)))),6)`

公式的嵌套比较多，为了方便清晰可以改为：

    CLOSE=MA888.close,LOW=MA888.low,HIGH=MA888.high
    temp1=(CLOSE-(((CLOSE>delay(CLOSE,1)))?min(LOW,delay(CLOSE,1)):max(HIGH,delay(CLOSE,1))))
    temp2=(CLOSE==delay(CLOSE,1))?0:temp1
    sum(temp2,6)

如alpha_005，原始公式为:

`(-1*TSMAX(CORR(TSRANK(VOLUME,5),TSRANK(HIGH,5),5),3))`

改为：

    VOLUME = MA888.volume,HIGH=MA888.high  
    (-1*tsmax(corr(tsmax(VOLUME,5),tsrank(HIGH,5),5),3))

alpha一般的研究框架：判断一个alpha是否有效的方法是求其和收益率序列的相关系数,如：

    CLOSE = MA888.close,VOLUME=MA888.volume,HIGH=MA888.high,LOW=MA888.low,OPEN=MA888.open  
    RET=delta(CLOSE,1)/delay(CLOSE,1)  
    alpha=sma(CLOSE-delay(CLOSE,5),5,1)  
    IC(alpha,delay(RET,-1))
        
返回的结果绝对值越大说明alpha因子与收益率相关系数越强，预测性越好。
