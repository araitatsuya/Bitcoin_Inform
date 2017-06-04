import smtplib
import time
import json
import urllib2
import datetime
import numpy as np
#import matplotlib
#import matplotlib.pyplot as plt
import math

T_BIN5 = 10 * 1
OVER_BOUGHT = 60
OVER_SOLD = 30
OVER_BOUGHT2 = 50
OVER_SOLD2 = 50
RSI_N = 14
MOVING_LENGTH = 27


def ExpMovingAverage(previous_EMA, current_val, window):
    weight = 2.0/(1.0 + window)
    a =  previous_EMA * (1.0 - weight) + current_val * weight
    return a

def rsiFunc(prices, n):
    deltas = np.diff(prices)
    seed = deltas[:n+1]
    up = seed[seed>=0].sum()/n
    down = -seed[seed<0].sum()/n
    rs = up/down
    rsi = np.zeros_like(prices)
    rsi[:n] = 100. - 100./(1.+rs)
    
    for i in range(n, len(prices)):
        delta = deltas[i-1] # cause the diff is 1 shorter
        
        if delta>0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta
        
        up = (up*(n-1) + upval)/n
        down = (down*(n-1) + downval)/n
        
        rs = up/down
        rsi[i] = 100. - 100./(1.+rs)
    
    return rsi



def send_email(msg, sub):
    
    gmail_user = "XXXXXXXXXXX@gmail.com"
    gmail_pwd = "XXXXXXXXX" #Device Specific

    FROM = 'From@gmail.com'
    TO = ['To@gmail.com'] #must be a list
    SUBJECT = sub
    TEXT = msg
    
    # Prepare actual message
    message = """\From: %s\nTo: %s\nSubject: %s\n\n%s""" % (FROM, ", ".join(TO), SUBJECT, TEXT)
    try:
        #server = smtplib.SMTP(SERVER)
        server = smtplib.SMTP("smtp.gmail.com", 587) #or port 465 doesn't seem to work!
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        server.sendmail(FROM, TO, message)
        #server.quit()
        server.close()
        print 'successfully sent the mail'
    except:
        print "failed to send mail"

def btceRead(current_val):
    old_val = current_val
    try:
        btcePrices = urllib2.urlopen('https://btc-e.com/api/2/btc_usd/ticker').read()
        #coinMxPrices = urllib2.urlopen('https://coin.mx/api/v2/exchange/history?platform=BTCUSD&limit=1').read()
        #https://btc-e.com/api/3/depth/btc_usd
        btcejason = json.loads(btcePrices)
        #coinMxjason = json.loads(coinMxPrices)
        btcelastP = btcejason['ticker']['last']
        btcelastT = btcejason['ticker']['updated']
        btcelastV = btcejason['ticker']['vol']
        #print "Hellow World"
        #print btcelastP
        current_val = [btcelastP]
        current_val.append(btcelastV)
        current_val.append(btcelastT)
    
    except Exception, e:
        current_val = old_val
        print 'failed API', str(e)
    
    return current_val

old_val = [0] * 3
timeBin5 = 0
btcDatear = [0] * MOVING_LENGTH
btcPricear = [0] * MOVING_LENGTH
btcPricearMax = [0] * MOVING_LENGTH
btcPricearMin = [0] * MOVING_LENGTH
btcVolumear = [0] * MOVING_LENGTH
crssMACD = [0] * MOVING_LENGTH
btcDatearTemp5 = []
btcPricearTemp5 = []
btcVolumearTemp5 = []
sampleNum  = 0
stance = 'wait'

while True:
    current_val = btceRead(old_val)
    if int(current_val[2]) != int(old_val[2]):
        old_val = current_val
        #print old_val[2]
        if timeBin5 == 0:
            '''
            Initialization
            '''
            timeBin5 = int(old_val[2]) + T_BIN5
            EMAPrices26 = float(old_val[0])
            EMAPrices12 = float(old_val[0])
            EMAPMACD9 = EMAPrices12 - EMAPrices26
        
        if int(old_val[2]) < int(timeBin5):
            
            btcDatearTemp5.append(float(old_val[2]))
            btcPricearTemp5.append(float(old_val[0]))
            btcVolumearTemp5.append(float(current_val[1]) - float(old_val[1]))
            
            #print btcVolumearTemp5[-1], btcPricearTemp5[-1]
        else:


            #priceMean = sum([a*b for a,b in zip(btcPricearTemp5,btcVolumearTemp5)])
            #priceMean = priceMean / sum(btcVolumearTemp5)
            priceMean = sum(btcPricearTemp5)/float(len(btcPricearTemp5))
            btcDatear.reverse()
            btcDatear.pop()
            btcDatear.reverse()
            
            btcPricear.reverse()
            btcPricear.pop()
            btcPricear.reverse()
            btcPricearMax.reverse()
            btcPricearMax.pop()
            btcPricearMax.reverse()
            btcPricearMin.reverse()
            btcPricearMin.pop()
            btcPricearMin.reverse()
            btcVolumear.reverse()
            btcVolumear.pop()
            btcVolumear.reverse()

            btcDatear.append(float(timeBin5))
            btcPricear.append(priceMean)
            btcPricearMax.append(max(btcPricearTemp5))
            btcPricearMin.append(min(btcPricearTemp5))
            btcVolumear.append(sum(btcVolumearTemp5))
                
            timeBin5 = timeBin5 + T_BIN5
            btcDatearTemp5 = []
            btcPricearTemp5 = []
            btcVolumearTemp5 = []
                
            btcDatearTemp5.append(float(old_val[2]))
            btcPricearTemp5.append(float(old_val[0]))
            btcVolumearTemp5.append(float(current_val[1]) - float(old_val[1]))
        
            sampleNum = sampleNum + 1
            
            EMAPrices12 = ExpMovingAverage(EMAPrices12, btcPricear[-1],12.0)
            EMAPrices26 = ExpMovingAverage(EMAPrices26, btcPricear[-1],26.0)
            MACD = EMAPrices12 - EMAPrices26
            EMAPMACD9 = ExpMovingAverage(EMAPMACD9, EMAPrices12 - EMAPrices26,9.0)
                
            crssMACD.reverse()
            crssMACD.pop()
            crssMACD.reverse()
            crssMACD.append(MACD - EMAPMACD9)

            if sampleNum > MOVING_LENGTH:
    
                rsiLine = rsiFunc(btcPricear,RSI_N)
                                
                if stance == 'long'	and (crssMACD[-1] - crssMACD[-2]) + crssMACD[-1] > 0 and crssMACD[-1] <= 0:
                    print 'Buy Signal BTC @', btcPricear[-1]
                    print 'Time', str(datetime.datetime.fromtimestamp(float(time.time())).strftime('%Y-%m-%d %H:%M:%S'))
                    msg_buy = "Buy Signal BTC @" + str(btcPricear[-1]) + " RSI@" + str(rsiLine[-1]) + " MACDcross " + str(crssMACD[-2]) + " -> " + str(crssMACD[-1]) + " Time@" + str(datetime.datetime.fromtimestamp(float(time.time())).strftime('%Y-%m-%d %H:%M:%S'))
                    send_email(msg_buy, "Buy Signal")
                if stance == 'long'	and crssMACD[-2] < 0 and crssMACD[-1] > 0:
                    print 'Buy Signal BTC @', btcPricear[-1]
                    print 'Time', str(datetime.datetime.fromtimestamp(float(time.time())).strftime('%Y-%m-%d %H:%M:%S'))
                    msg_buy = "Buy Signal BTC @" + str(btcPricear[-1]) + " RSI@" + str(rsiLine[-1]) + " MACDcross " + str(crssMACD[-2]) + " -> " + str(crssMACD[-1]) + " Time@" + str(datetime.datetime.fromtimestamp(float(time.time())).strftime('%Y-%m-%d %H:%M:%S'))
                    send_email(msg_buy, "Buy Signal")
                            
                if stance == 'short' and (crssMACD[-1] - crssMACD[-2]) + crssMACD[-1] < 0 and crssMACD[-1] >= 0:
                    print 'Sell Signal BTC @', btcPricear[-1]
                    print 'Time', str(datetime.datetime.fromtimestamp(float(time.time())).strftime('%Y-%m-%d %H:%M:%S'))
                    msg_sell = "Sell Signal BTC @" + str(btcPricear[-1]) + " RSI@" + str(rsiLine[-1]) + " MACDcross " + str(crssMACD[-2]) + " -> " + str(crssMACD[-1]) + " Time@" + str(datetime.datetime.fromtimestamp(float(time.time())).strftime('%Y-%m-%d %H:%M:%S'))
                    send_email(msg_sell, "Sell Signal")
                    
                if stance == 'short' and crssMACD[-2] > 0 and crssMACD[-1] < 0:
                    print 'Sell Signal BTC @', btcPricear[-1]
                    print 'Time', str(datetime.datetime.fromtimestamp(float(time.time())).strftime('%Y-%m-%d %H:%M:%S'))
                    msg_sell = "Sell Signal BTC @" + str(btcPricear[-1]) + " RSI@" + str(rsiLine[-1]) + " MACDcross " + str(crssMACD[-2]) + " -> " + str(crssMACD[-1]) + " Time@" + str(datetime.datetime.fromtimestamp(float(time.time())).strftime('%Y-%m-%d %H:%M:%S'))
                    send_email(msg_sell, "Sell Signal")
                
                if rsiLine[-1] < OVER_SOLD and stance != 'long':
                    print 'Buy Signal BTC @', btcPricear[-1]
                    print 'Time', str(datetime.datetime.fromtimestamp(float(time.time())).strftime('%Y-%m-%d %H:%M:%S'))
                    stance = 'long'
                    msg_buy = "Buy Signal BTC @" + str(btcPricear[-1]) + " RSI@" + str(rsiLine[-1]) + " MACDcross " + str(crssMACD[-2]) + " -> " + str(crssMACD[-1]) + " Time@" + str(datetime.datetime.fromtimestamp(float(time.time())).strftime('%Y-%m-%d %H:%M:%S'))
                    send_email(msg_buy, "Buy Signal")

                if rsiLine[-1] > OVER_BOUGHT and stance != 'short':
                    print 'Sell Signal BTC @', btcPricear[-1]
                    print 'Time', str(datetime.datetime.fromtimestamp(float(time.time())).strftime('%Y-%m-%d %H:%M:%S'))
                    stance = 'short'
                    msg_sell = "Sell Signal BTC @" + str(btcPricear[-1]) + " RSI@" + str(rsiLine[-1]) + " MACDcross " + str(crssMACD[-2]) + " -> " + str(crssMACD[-1]) + " Time@" + str(datetime.datetime.fromtimestamp(float(time.time())).strftime('%Y-%m-%d %H:%M:%S'))
                    send_email(msg_sell, "Sell Signal")
                
                if rsiLine[-1] < OVER_BOUGHT2 and stance == 'short':
                    stance = 'wait'
                if rsiLine[-1] > OVER_SOLD2 and stance == 'long':
                    stance = 'wait'

                    #if rsiLine[-1] < OVER_SOLD and crssMACD[-1] < 0:
                    #print 'Buy Signal BTC @', btcPricear[-1]
                    #print 'Time', str(datetime.datetime.fromtimestamp(float(time.time())).strftime('%Y-%m-%d %H:%M:%S'))
                    #msg_buy = "Buy Signal BTC @" + str(btcPricear[-1]) + " RSI@" + str(rsiLine[-1]) + " MACDcross" + str(crssMACD[-2]) + "->" + str(crssMACD[-1]) + " Time@" + str(datetime.datetime.fromtimestamp(float(time.time())).strftime('%Y-%m-%d %H:%M:%S'))
                    #send_email(msg_buy, "Buy Signal")
                    #if rsiLine[-1] > OVER_BOUGHT and crssMACD[-1] > 0:
                    #print 'Sell Signal BTC @', btcPricear[-1]
                    #print 'Time', str(datetime.datetime.fromtimestamp(float(time.time())).strftime('%Y-%m-%d %H:%M:%S'))
                    #msg_sell = "Sell Signal BTC @" + str(btcPricear[-1]) + " RSI@" + str(rsiLine[-1]) + " MACDcross" + str(crssMACD[-2]) + "->" + str(crssMACD[-1]) + " Time@" + str(datetime.datetime.fromtimestamp(float(time.time())).strftime('%Y-%m-%d %H:%M:%S'))
                    #send_email(msg_sell, "Sell Signal")
    
                print btcPricear[-1], 'RSI: ',rsiLine[-1], 'MACD Cross: ', crssMACD[-1], 'Stance: ', stance
            else:
                print btcPricear[-1], 'Ideling'

    time.sleep(1)