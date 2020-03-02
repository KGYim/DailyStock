# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import traceback
import pandas as pd
import datetime
import talib as tl
import configparser

def ReadInI(Route):
    config = configparser.ConfigParser()
    config.read(Route)

    dictionary = {}
    for section in config.sections():
        dictionary[section] = {}
        for option in config.options(section):
            try:
                dictionary[section][option] = config.get(section,option)
            except:
                pass
    return dictionary

dicRename = {"날짜":'date','종가':'close','전일비':'change_rate','시가':'open','고가':'high','저가':'low','거래량':'vol'}
# code = '035420'  # NAVER

class StockSystem(object):
    def __init__(self):
        self.dicStockInfo = ReadInI("StockInfo.ini")
        

    def parse_page(self,code, page):
        try:
            url = 'http://finance.naver.com/item/sise_day.nhn?code={code}&page={page}'.format(code=code, page=page)
            res = requests.get(url)
            _soap = BeautifulSoup(res.text, 'lxml')
            _df = pd.read_html(str(_soap.find("table")), header=0)[0]
            _df = _df.dropna()
            return _df#.rename(columns = dicRename)
        except Exception as e:
            traceback.print_exc()
        return None

    def parse_date(self,code,str_datefrom):
        pg_last = 100
        df = None
        for page in range(1, pg_last+1):
            _df = self.parse_page(code, page)
            _df_filtered = _df[_df['날짜'] > str_datefrom]
            if df is None:
                df = _df_filtered
            else:
                df = pd.concat([df, _df_filtered])
            if len(_df) > len(_df_filtered):
                break
        return df.reset_index(drop=True)


    def MakeMiddleData(self,code,df):
        PDI = tl.PLUS_DI(df.high, df.low, df.close, timeperiod=14)
        MDI = tl.MINUS_DI(df.high, df.low, df.close, timeperiod=14)
        ADX = tl.ADX(df.high, df.low, df.close, timeperiod=14)
        R = tl.WILLR(df.high, df.low, df.close, timeperiod=14)

        if list(R)[-1] < -80:
            if list(PDI)[-1] > list(MDI)[-1]:
                print("R : ",R[len(df)-1])
                print("Name : ",self.dicStockInfo['info'][code])


    def run(self):
        str_dateto = '2019.05.01'
        for i in self.dicStockInfo['info'].keys():
            df = self.parse_date(i,str_dateto)
            df = self.parse_date(i,str_dateto)
            df = df.rename(columns=dicRename)
            df = df.sort_values(by=['date']).reset_index(drop=True)
            if list(df["vol"])[-1] <10000:
                continue
            
            try:
                self.MakeMiddleData(i,df)
            except Exception as e:
                print("{0}({1})".format(self.dicStockInfo['info'][i],i))
                print("Error : ",e)
                print(df)

        

if __name__ == "__main__":
    try:
        StockSystem().run()
    except KeyboardInterrupt:
        exit()








# str_dateto = datetime.datetime.strftime(datetime.datetime.today(), '%Y.%m.%d')
# str_dateto = '2019.01.01'

# def parse_date(code,str_datefrom):
#     pg_last = 100
#     df = None
#     for page in range(1, pg_last+1):
#         _df = parse_page(code, page)
#         _df_filtered = _df[_df['날짜'] > str_datefrom]
#         if df is None:
#             df = _df_filtered
#         else:
#             df = pd.concat([df, _df_filtered])
#         if len(_df) > len(_df_filtered):
#             break
#     return df.reset_index(drop=True)

# df = parse_date(code,str_dateto)
# print(df)


#     def GetDirectionalMovement(self,dicPreStockData,dicPostStockData):
#         tmpPDM = dicPostStockData['high'] - dicPreStockData['high']
#         tmpMDM = dicPreStockData['low'] - dicPostStockData['low']

#         tmpTop = dicPostStockData['low'] - dicPreStockData['high']
#         tmpLow = dicPreStockData['low'] - dicPostStockData['high']
        
#         if tmpTop > 0:
#             return tmpTop, 0
#         if tmpLow >0:
#             return 0, tmpLow

#         if (tmpPDM > 0) and (tmpMDM <=0):
#             PDM = tmpPDM
#             MDM = 0
#             return PDM, MDM

#         if (tmpPDM <=0) and (tmpMDM >0):
#             PDM = 0
#             MDM = tmpMDM
#             return PDM, MDM

#         if (tmpPDM <= 0) and (tmpMDM <=0):
#             return 0,0

#         if (tmpPDM >0) and (tmpMDM >0):
#             if tmpPDM >= tmpMDM:
#                 return tmpPDM, 0
#             else:
#                 return 0, tmpMDM

#     def getTrueRange(self,dicPreStockData,dicPostStockData):
#         tmp1 = abs(dicPostStockData['high'] - dicPostStockData['low'])
#         tmp2 = abs(dicPostStockData['high'] - dicPreStockData['close'])
#         tmp3 = abs(dicPostStockData['low'] - dicPreStockData['close'])
#         return max(tmp1,tmp2,tmp3)

#     def getDirectionalIndicator(PDM,MDM,TR):
#         PDI = PDM/TR
#         MDI = MDM/TR
#         return PDI,MDI