#we will start with some defining some constant like 
import  requests 
import numpy as np 
import talib #talib library for various calculation related to financial and technical indicators
from binance.client  import Client  #importing client 
from config import api_key , api_secret


client = Client(api_key, api_secret) #it takes two parameter, first one api_key and second api_secret_key, i will define that in configuration file 



SYMBOL = "BTCUSDT" #taking this as a example 
TIME_PERIOD= "15m" #taking 15 minute time period 
LIMIT = "200" # taking 200 candles as limit 
QNTY = 0.006 # we will define quantity over here 

#Now we will write function to get data from binance to work with 
# for that we will need to import requests library to fetch data 


def place_order(order_type):
    #order type could be buy or sell 
    # before that , we have to initialize the binance client 
    if(order_type == "buy"):
        # we will place buy order
        order = client.create_order(symbol=SYMBOL, side="buy",quantity=QNTY,type="MARKET") # for type i am going with market order, so whatever price at market. it will place order 
    else:
        order = client.create_order(symbol=SYMBOL, side="sell", quantity=QNTY,type="MARKET") # same thing but changed side 

    print("order placed successfully!") 
    print(order)
    return

#now , you will need to define api_key and api-secret in the config file like this 


#function to get data from binance 
def get_data():
    url = "https://api.binance.com/api/v3/klines?symbol={}&interval={}&limit={}".format(SYMBOL, TIME_PERIOD, LIMIT)
    res = requests.get(url) 
    #now we can either save the response or convert it to numpy array , converting is more reasonable 
    return_data = []
    for each in res.json():
        return_data.append(float(each[4]))
    return np.array(return_data)


#now we have function to get data from binance, now we need to calculate ema. for calculating ema, we are going to use 
# talib library, to install it do this 


#define main entry point for the script 
def main():
    buy = False #it means we are yet to buy and have not bought
    sell = True #we have not sold , but if you want to buy first then set it to True
    ema_8 = None #starting with None 
    ema_21 = None #starting with None 

    #we also need to store the last variables that was the value for the ema_8 and ema_21, so we can compare
    last_ema_8 = None 
    last_ema_21 = None 

    print("started running..")
    #the script will run continously and fetch latest data from binance 
    while True:
        closing_data = get_data() #get latest closing data for the candles 
        #now feed the data to the Ema function of talib
        # i am using ema crossover strategy, in which i am using timeframe 8,21
        # 8 for smaller ema line and 21 for larger 
        ema_8 = talib.EMA(closing_data,8)[-1] #data and timeperiod are the two parameters that the function takes 
        ema_21 = talib.EMA(closing_data, 21)[-1] #same as the last one 
        #now, let's see if values are correct or not 
        #print("ema 8", ema_8[-1])
        #print("ema_21",ema_21[-1]) #ema_21 returns whole array, but we are only interested in last value 
        #now we will check it against real values,

        #now , the last thing we need to do is get the order going. we will create function to place 
        #order

        #logic for buy and sell 
        # also one thing
        if(ema_8 > ema_21 and last_ema_8): #we have to check if the value of ema_8 crossed ema_21 or not 
            if(last_ema_8 < last_ema_21 and not buy): # to check if previously, it was below of ema_21 and we haven't already bought it 
                print("buy logic goes here")
                buy = True 
                sell = False #switch the values for next order

        if(ema_21 > ema_8 and last_ema_21):  #to check if ema_8 got down from top to bottom 
            if(last_ema_21 < last_ema_8 and not sell): # to check if previously it was above ema_21
                print("sell logic goes here")
                sell = True 
                buy = False #switching values for next order 

        #at last we are setting the current values as last one 
        last_ema_8 = ema_8 
        last_ema_21 = ema_21
        #return
        
if __name__ == "__main__":
    main()
