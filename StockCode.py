import configparser
import sys
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QAxContainer import *
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QLineEdit
import time

from pandas import Series, DataFrame
import pandas as pd
import numpy as np

def ReadInI(Route):
    config = configparser.ConfigParser()
    config.read(Route)

    dictionary = {}
    for section in config.sections():
        dictionary[section] = {}
        for option in config.options(section):
            dictionary[section][option] = config.get(section,option)
    return dictionary

dicInitialInfo = ReadInI("Info.ini")

class IndiWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.StockCode = {}
        self.count= 0
        self.list = None

        self.IndiTR = QAxWidget("GIEXPERTCONTROL.GiExpertControlCtrl.1")
        # self.login()

        rqid = self.IndiTR.dynamicCall("RequestData()") # 데이터 요청

        # Indi API event
        self.IndiTR.ReceiveData.connect(self.ReceiveData)
        self.IndiTR.ReceiveSysMsg.connect(self.ReceiveSysMsg)
        self.rqidD = {} # TR 관리를 위해 사전 변수를 하나 생성합니다.
        
        self.GetStockCode()


    def login(self):
        # 신한i Indi 자동로그인
        login = self.IndiTR.StartIndi('{}'.format(dicInitialInfo["info"]["id"]), '{}'.format(dicInitialInfo["info"]["pw"]), '', 'C:/SHINHAN-i/indi/giexpertstarter.exe')
        if login == True :
            print("Success Login")
        else:
            print("Check Info.ini or Internet Connect")

        time.sleep(30)

    # 생성한 버튼을 눌렀을 때 전 종목코드 조회가 나가도록 설정해줍니다.
    def GetStockCode(self):
        # stock_mst : 주식 종목코드 조회를 요청할 TR입니다.
        # 해당 TR의 필드입력형식에 맞춰서 TR을 날리면 됩니다.
        # 데이터 요청 형식은 다음과 같습니다.
        ret = self.IndiTR.dynamicCall("SetQueryName(QString)","stock_mst")
        rqid = self.IndiTR.dynamicCall("RequestData()") # 데이터 요청
        self.rqidD[rqid] =  "stock_mst"
        

    def btn_Search(self,MainSymbol):
        # self.MainSymbol = list(self.StockCode.keys())[0]
        # print(self.MainSymbol,':',self.StockCode[self.MainSymbol])

        self.MainSymbol = MainSymbol
    
        # 차트조회 : 과거주가는 차트조회를 통해 받아올 수 있습니다.
        # TR_SCHART : 과거주가를 요청할 TR입니다.
        # 해당 TR의 필드입력형식에 맞춰서 TR을 날리면 됩니다.
        # 데이터 요청 형식
        ret = self.IndiTR.dynamicCall("SetQueryName(QString)", "TR_SCHART")
        ret = self.IndiTR.dynamicCall("SetSingleData(int, QString)", 0, self.MainSymbol) # 단축코드
        ret = self.IndiTR.dynamicCall("SetSingleData(int, QString)", 1, "D") # 1:분봉, D:일봉, W:주봉, M:월봉
        ret = self.IndiTR.dynamicCall("SetSingleData(int, QString)", 2, "1") # 분봉: 1~30, 일/주/월 : 1
        ret = self.IndiTR.dynamicCall("SetSingleData(int, QString)", 3, "00000000") # 시작일(YYYYMMDD)
        ret = self.IndiTR.dynamicCall("SetSingleData(int, QString)", 4, "99999999") # 종료일(YYYYMMDD)
        ret = self.IndiTR.dynamicCall("SetSingleData(int, QString)", 5, "9999") # 조회갯수(1~9999)
        rqid = self.IndiTR.dynamicCall("RequestData()") # 데이터 요청
        self.rqidD[rqid] =  "TR_SCHART"
        # self.IndiTR.ReceiveData.connect(self.ReceiveData)


     # 요청한 TR로 부터 데이터를 받는 함수입니다.
    def ReceiveData(self, rqid):
        # TR을 날릴때 ID를 통해 TR이름을 가져옵니다.
        TRName = self.rqidD[rqid]

        # 과거주가를 알아보기위한 TR인 stock_mst를 요청했었습니다.
        if TRName == "stock_mst" :
            # GetMultiRowCount()는 TR 결과값의 multi row 개수를 리턴합니다.
            nCnt = self.IndiTR.dynamicCall("GetMultiRowCount()")

            # 받을 열만큼 가거 데이터를 받도록 합니다.
            # for i in range(0, 10):
            for i in range(0, nCnt):
                # 데이터 양식

                DATA = {}

                # 데이터 받기
                DATA['ISIN_CODE'] = self.IndiTR.dynamicCall("GetMultiData(int, int)", i, 0)  # 표준코드
                DATA['CODE'] = self.IndiTR.dynamicCall("GetMultiData(int, int)", i, 1)  # 단축코드
                DATA['MARKET'] = self.IndiTR.dynamicCall("GetMultiData(int, int)", i, 2   )  # 장구분
                DATA['NAME'] = self.IndiTR.dynamicCall("GetMultiData(int, int)", i, 3)  # 종목명
                DATA['SECTOR'] = self.IndiTR.dynamicCall("GetMultiData(int, int)", i, 4)  # KOSPI200 세부업종
                DATA['SETTLEMENT'] = self.IndiTR.dynamicCall("GetMultiData(int, int)", i, 5)  # 결산연월
                DATA['SEC'] = self.IndiTR.dynamicCall("GetMultiData(int, int)", i, 6)  # 거래정지구분
                DATA['MANAGEMENT'] = self.IndiTR.dynamicCall("GetMultiData(int, int)", i, 7)  # 관리구분
                DATA['ALERT'] = self.IndiTR.dynamicCall("GetMultiData(int, int)", i, 8)  # 시장경보구분코드
                DATA['ROCK'] = self.IndiTR.dynamicCall("GetMultiData(int, int)", i, 9)  # 락구분
                DATA['INVALID'] = self.IndiTR.dynamicCall("GetMultiData(int, int)", i, 10)  # 불성실공시지정여부
                DATA['MARGIN'] = self.IndiTR.dynamicCall("GetMultiData(int, int)", i, 11)  # 증거금 구분
                DATA['CREDIT'] = self.IndiTR.dynamicCall("GetMultiData(int, int)", i, 12)  # 신용증거금 구분
                DATA['ETF'] = self.IndiTR.dynamicCall("GetMultiData(int, int)", i, 13)  # ETF 구분
                DATA['PART'] = self.IndiTR.dynamicCall("GetMultiData(int, int)", i, 14)  # 소속구분

                if DATA['SEC'] == "1":
                    continue
                self.StockCode[DATA['CODE']] = DATA['NAME']
                # print(DATA)
            
            self.list = list(self.StockCode.keys())
            # print(self.StockCode)
            # print(self.list)
            self.btn_Search(self.list[self.count])

        if TRName == "TR_SCHART" :
            # GetMultiRowCount()는 TR 결과값의 multi row 개수를 리턴합니다.
            nCnt = self.IndiTR.dynamicCall("GetMultiRowCount()")
            # 받을 열만큼 가거 데이터를 받도록 합니다.
            columns = ['DATE', 'TIME', 'OPEN', 'HIGH', 'Low', 'Close', 'Price_ADJ', 'Vol_ADJ', 'Rock', 'Vol', 'Trading_Value']
            body = []
            for i in range(0, 14):
                row = []
                # 데이터 양식
                DATA = {}

                # 데이터 받기
                row.append(self.IndiTR.dynamicCall("GetMultiData(int, int)", i, 0))  # 일자
                row.append(self.IndiTR.dynamicCall("GetMultiData(int, int)", i, 1))  # 시간
                row.append(self.IndiTR.dynamicCall("GetMultiData(int, int)", i, 2)) # 시가
                row.append(self.IndiTR.dynamicCall("GetMultiData(int, int)", i, 3))  # 고가
                row.append(self.IndiTR.dynamicCall("GetMultiData(int, int)", i, 4))  # 저가
                row.append(self.IndiTR.dynamicCall("GetMultiData(int, int)", i, 5))  # 종가
                row.append(self.IndiTR.dynamicCall("GetMultiData(int, int)", i, 6))  # 주가수정계수
                row.append(self.IndiTR.dynamicCall("GetMultiData(int, int)", i, 7))  # 거래량 수정계수
                row.append(self.IndiTR.dynamicCall("GetMultiData(int, int)", i, 8))  # 락구분
                row.append(self.IndiTR.dynamicCall("GetMultiData(int, int)", i, 9))  # 단위거래량
                row.append(self.IndiTR.dynamicCall("GetMultiData(int, int)", i, 10))  # 단위거래대금
                body.append(row)

            

            if self.count % 100 ==0:
                print("count : ",self.count)

            pdData = pd.DataFrame(body,columns=columns)
            # print(self.list[self.count],self.StockCode[self.list[self.count]])
            # print(pdData)
            try:
                MaxHigh = int(max(pdData["HIGH"]))
                MinLOW = int(min(pdData["Low"]))
                tmpData = pdData.loc[pdData["DATE"]==sorted(pdData["DATE"],reverse=True)[0],["Close","Vol"]]
                LastClose = int(tmpData["Close"][0])
                R = ((MaxHigh-LastClose)/(MaxHigh-MinLOW))*(-100)
                # print("MaxHigh : ",MaxHigh)
                # print("MinLOW : ",MinLOW)
                # print("LastClose : ",LastClose)
                # print("R : ",R)

                # print(self.list[self.count],self.StockCode[self.list[self.count]])
                # print("R : ",R)
                if R < -80:
                    print(self.list[self.count],self.StockCode[self.list[self.count]])
                    print("R : ",R)
                    print("거래량 : ",tmpData["Vol"][0])

            except Exception as ex:
                print(print(self.list[self.count],self.StockCode[self.list[self.count]]))
                print("count : ",self.count)
            #     print("MaxHigh : ",MaxHigh)
            #     print("MinLOW : ",MinLOW)
            #     print("LastClose : ",LastClose)

            self.count +=1
            if self.count == len(self.list):
                
                self.rqidD.__delitem__(rqid)
                return 0

            self.btn_Search(self.list[self.count])

        self.rqidD.__delitem__(rqid)


    # 시스템 메시지를 받은 경우 출력합니다.
    def ReceiveSysMsg(self, MsgID):
        print("System Message Received = ", MsgID)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    IndiWindow = IndiWindow()
    app.exec_()
