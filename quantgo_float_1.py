#-*-coding: utf-8 -*-
from sklearn.preprocessing import MinMaxScaler
import numpy as np


import win32com.client
import pythoncom
import os, sys
import inspect
import time

import pandas as pd
from pandas import DataFrame, Series, Panel
import datetime as d
a = d.datetime.now()
b = a.strftime('%Y%m%d')
c = d.datetime.now()
print(a)


def safe_cast(val, to_type, default=None):
    try:
        return to_type(val)
    except (ValueError, TypeError):
        return default

class XASessionEvents:
    상태 = False

    def OnLogin(self, code, msg):
        print("OnLogin : ", code, msg)
        XASessionEvents.상태 = True

    def OnLogout(self):
        pass

    def OnDisconnect(self):
        pass

class XAQueryEvents:
    상태 = False

    def OnReceiveData(self, szTrCode):
        #print("OnReceiveData : %s" % szTrCode)
        XAQueryEvents.상태 = True

    #def OnReceiveMessage(self, systemError, messageCode, message):
    #    print("OnReceiveMessage : ", systemError, messageCode, message)


def Login(url='hts.etrade.co.kr', port=20001, svrtype=0, id='qkrrkgus', pwd='test2535', cert='1104qq11!!'):
    session = win32com.client.DispatchWithEvents("XA_Session.XASession", XASessionEvents)
    session.SetMode("_XINGAPI7_","TRUE")
    result = session.ConnectServer(url, port)

    if not result:
        nErrCode = session.GetLastError()
        strErrMsg = session.GetErrorMessage(nErrCode)
        return (False, nErrCode, strErrMsg, None, session)

    session.Login(id, pwd, cert, svrtype, 0)

    while XASessionEvents.상태 == False:
        pythoncom.PumpWaitingMessages()

    계좌 = []
    계좌수 = session.GetAccountListCount()

    for i in range(계좌수):
        계좌.append(session.GetAccountList(i))

    return (True, 0, "OK", 계좌, session)
    
def t8430(구분='1'):   #구분에 따른 상장된 전 종목=0, 코스피=1, 코스닥=2
    '''
    주식종목코드조회
    '''
    query = win32com.client.DispatchWithEvents("XA_DataSet.XAQuery", XAQueryEvents)
    pathname = os.path.dirname(sys.argv[0])
    RESDIR = os.path.abspath(pathname)


    MYNAME = inspect.currentframe().f_code.co_name
    #print(MYNAME)
    INBLOCK = "%sInBlock" % MYNAME
    OUTBLOCK = "%sOutBlock" % MYNAME
    OUTBLOCK1 = "%sOutBlock1" % MYNAME
    RESFILE = "%s\\Res\\%s.res" % (RESDIR, MYNAME)
    

    query.LoadFromResFile(RESFILE)
    query.SetFieldData(INBLOCK, "gubun", 0, 구분)
    query.Request(0)

    while XAQueryEvents.상태 == False:
        pythoncom.PumpWaitingMessages()

    result = []
    nCount = query.GetBlockCount(OUTBLOCK)
    for i in range(nCount):
        종목명 = query.GetFieldData(OUTBLOCK, "hname", i).strip()
        단축코드 = query.GetFieldData(OUTBLOCK, "shcode", i).strip()
        ETF구분 = int(query.GetFieldData(OUTBLOCK, "etfgubun", i).strip())

        lst = [종목명,단축코드,ETF구분]
        result.append(lst)

    XAQueryEvents.상태 = False

    columns=['종목명','단축코드','ETF구분']
    df = DataFrame(data=result, columns=columns)
    return df



def t1471(종목코드='',분구분='500',시간='',자료개수='001'):
    '''
    시간대별호가잔량추이
    '''
    query = win32com.client.DispatchWithEvents("XA_DataSet.XAQuery", XAQueryEvents)
    pathname = os.path.dirname(sys.argv[0])
    RESDIR = os.path.abspath(pathname)

    MYNAME = inspect.currentframe().f_code.co_name
    #print(MYNAME)
    INBLOCK = "%sInBlock" % MYNAME
    OUTBLOCK = "%sOutBlock" % MYNAME
    OUTBLOCK1 = "%sOutBlock1" % MYNAME
    RESFILE = "%s\\Res\\%s.res" % (RESDIR, MYNAME)

    query.LoadFromResFile(RESFILE)
    query.SetFieldData(INBLOCK, "shcode", 0, 종목코드)
    query.SetFieldData(INBLOCK, "gubun", 0, 분구분)
    query.SetFieldData(INBLOCK, "time", 0, 시간)
    query.SetFieldData(INBLOCK, "cnt", 0, 자료개수)
    query.Request(0)

    while XAQueryEvents.상태 == False:
        pythoncom.PumpWaitingMessages()

    result = []
    nCount = query.GetBlockCount(OUTBLOCK1)
    for i in range(nCount):#string=문자, long = int, float="float"
        종가 = int(query.GetFieldData(OUTBLOCK1, "close", i).strip())
        종가 = safe_cast(종가,float)
        
        등락율 = float(query.GetFieldData(OUTBLOCK, "diff", i).strip()) / 30
        등락율 = safe_cast(등락율,float)
        
        누적거래량 = int(query.GetFieldData(OUTBLOCK, "volume", i).strip())
        누적거래량 = safe_cast(누적거래량,float)
        
        누적거래량_1 = int(query.GetFieldData(OUTBLOCK, "volume", i).strip())
        누적거래량_1 = safe_cast(누적거래량_1,float)
        
        매도우선잔량 = int(query.GetFieldData(OUTBLOCK1, "offerrem1", i).strip())
        매도우선잔량 = safe_cast(매도우선잔량,float)
        
        매도우선호가 = int(query.GetFieldData(OUTBLOCK1, "offerho1", i).strip())
        매도우선호가 = safe_cast(매도우선호가,float)
        매도우선호가 = (매도우선호가-종가) / 종가
        
        매수우선호가 = int(query.GetFieldData(OUTBLOCK1, "bidho1", i).strip())
        매수우선호가 = safe_cast(매수우선호가,float)
        매수우선호가 = (매수우선호가-종가) / 종가
        
        매수우선잔량 = int(query.GetFieldData(OUTBLOCK1, "bidrem1", i).strip())
        매수우선잔량 = safe_cast(매수우선잔량,float)
        
        
        총매도 = int(query.GetFieldData(OUTBLOCK1, "totofferrem", i).strip())
        총매도 = safe_cast(총매도,float)
        
        총매수 = int(query.GetFieldData(OUTBLOCK1, "totbidrem", i).strip())
        총매수 = safe_cast(총매수,float)
        
        순매수 = int(query.GetFieldData(OUTBLOCK1, "totsun", i).strip())
        순매수 = safe_cast(순매수,float)
        
        매수비율 = float(query.GetFieldData(OUTBLOCK1, "msrate", i).strip()) / 10000
        등락율_1 = float(query.GetFieldData(OUTBLOCK, "diff", i).strip()) / 30

        
        lst = [종가,등락율,누적거래량,누적거래량_1,매도우선잔량,매도우선호가,매수우선호가,매수우선잔량,총매도,총매수,순매수,매수비율,등락율_1]
        result.append(lst)

    df1 = DataFrame(data=result, columns=['종가','등락율','누적거래량','누적거래량_1','매도우선잔량','매도우선호가','매수우선호가','매수우선잔량','총매도','총매수','순매수','매수비율','등락율_1'])

    XAQueryEvents.상태 = False

    return df1



def t1475(종목코드='',상승하락='1',데이터개수='1',기준일자='',기준시간='',랭크카운터='',조회구분='1'):
    '''
    체결강도
    '''
    query = win32com.client.DispatchWithEvents("XA_DataSet.XAQuery", XAQueryEvents)
    pathname = os.path.dirname(sys.argv[0])
    RESDIR = os.path.abspath(pathname)

    MYNAME = inspect.currentframe().f_code.co_name
    #print(MYNAME)
    INBLOCK = "%sInBlock" % MYNAME
    OUTBLOCK = "%sOutBlock" % MYNAME
    OUTBLOCK1 = "%sOutBlock1" % MYNAME
    RESFILE = "%s\\Res\\%s.res" % (RESDIR, MYNAME)

    query.LoadFromResFile(RESFILE)
    query.SetFieldData(INBLOCK, "shcode", 0, 종목코드)
    query.SetFieldData(INBLOCK, "vptype", 0, 상승하락)
    query.SetFieldData(INBLOCK, "datacnt", 0, 데이터개수)
    query.SetFieldData(INBLOCK, "date", 0, 기준일자)
    query.SetFieldData(INBLOCK, "time", 0, 기준시간)
    query.SetFieldData(INBLOCK, "rankcnt", 0, 랭크카운터)
    query.SetFieldData(INBLOCK, "gubun", 0, 조회구분)
    query.Request(0)

    while XAQueryEvents.상태 == False:
        pythoncom.PumpWaitingMessages()

    result = []
    nCount = query.GetBlockCount(OUTBLOCK1)
    for i in range(nCount):  #string=문자, long = int, float="float"
        거래량 = int(query.GetFieldData(OUTBLOCK1, "volume", i).strip())
        거래량 = safe_cast(거래량,float)
        당일VP = float(query.GetFieldData(OUTBLOCK1, "todayvp", i).strip()) / 1000
        MAVP5일 = float(query.GetFieldData(OUTBLOCK1, "ma5vp", i).strip()) / 1000
        MAVP20일 = float(query.GetFieldData(OUTBLOCK1, "ma20vp", i).strip()) / 1000
        MAVP60일 = float(query.GetFieldData(OUTBLOCK1, "ma60vp", i).strip()) / 1000
        
        lst = [거래량, 당일VP,MAVP5일,MAVP20일,MAVP60일]
        result.append(lst)

    df1 = DataFrame(data=result, columns=["거래량","당일VP","MAVP5일","MAVP20일","MAVP60일"])
    

    XAQueryEvents.상태 = False

    return df1


def t1636(구분="0",금액수량구분="1",정렬기준="",종목코드="",IDXCTS=""):
    '''
    종목별프로그램매매동향
    '''
    query = win32com.client.DispatchWithEvents("XA_DataSet.XAQuery", XAQueryEvents)
    pathname = os.path.dirname(sys.argv[0])
    RESDIR = os.path.abspath(pathname)

    MYNAME = inspect.currentframe().f_code.co_name
    #print(MYNAME)
    INBLOCK = "%sInBlock" % MYNAME
    OUTBLOCK = "%sOutBlock" % MYNAME
    OUTBLOCK1 = "%sOutBlock1" % MYNAME
    RESFILE = "%s\\Res\\%s.res" % (RESDIR, MYNAME)

    query.LoadFromResFile(RESFILE)
    query.SetFieldData(INBLOCK, "gubun", 0, 구분)
    query.SetFieldData(INBLOCK, "gubun1", 0, 금액수량구분)
    query.SetFieldData(INBLOCK, "gubun2", 0, 정렬기준)
    query.SetFieldData(INBLOCK, "shcode", 0, 종목코드)
    query.SetFieldData(INBLOCK, "cts_idx", 0, IDXCTS)
    query.Request(0)

    while XAQueryEvents.상태 == False:
        pythoncom.PumpWaitingMessages()

    result = []
    nCount = query.GetBlockCount(OUTBLOCK1)
    for i in range(nCount):   #string=문자, long = int, float="float"

        순위 = int(query.GetFieldData(OUTBLOCK1, "rank", i).strip()) / 2000
        순위 = safe_cast(순위,float)
        시가총액 = int(query.GetFieldData(OUTBLOCK1, "sgta", i).strip())
        시가총액 = safe_cast(시가총액,float)
        
        거래량_1 = int(query.GetFieldData(OUTBLOCK1, "volume", i).strip())
        거래량_1 = safe_cast(거래량_1,float)
        순매수금액 = int(query.GetFieldData(OUTBLOCK1, "svalue", i).strip()) / 시가총액
        순매수금액 = safe_cast(순매수금액,float)
        
        매도금액 = int(query.GetFieldData(OUTBLOCK1, "offervalue", i).strip()) / 시가총액
        매도금액 = safe_cast(매도금액,float)
        매수금액 = int(query.GetFieldData(OUTBLOCK1, "stksvalue", i).strip()) / 시가총액
        매수금액 = safe_cast(매수금액,float)
        비중 = float(query.GetFieldData(OUTBLOCK1, "rate", i).strip())
        순매수금액_1 = int(query.GetFieldData(OUTBLOCK1, "svalue", i).strip()) / 시가총액
        순매수금액_1 = safe_cast(순매수금액_1,float)

        lst = [순위,시가총액,거래량_1,순매수금액,매도금액,매수금액,비중,순매수금액_1]
        result.append(lst)

    df1 = DataFrame(data=result, columns=["순위","시가총액","거래량_1","순매수금액","매도금액","매수금액","비중","순매수금액_1"])

    XAQueryEvents.상태 = False

    return df1


def t1701(종목코드="",구분="0",시작일자=b,종료일자=b,PR적용="",PR적용구분="1",기관적용="1",외인적용="1"):
    '''
    외인기관종목별동향
    '''
    query = win32com.client.DispatchWithEvents("XA_DataSet.XAQuery", XAQueryEvents)
    pathname = os.path.dirname(sys.argv[0])
    RESDIR = os.path.abspath(pathname)

    MYNAME = inspect.currentframe().f_code.co_name
    INBLOCK = "%sInBlock" % MYNAME
    OUTBLOCK = "%sOutBlock" % MYNAME
    OUTBLOCK1 = "%sOutBlock1" % MYNAME
    RESFILE = "%s\\Res\\%s.res" % (RESDIR, MYNAME)

    query.LoadFromResFile(RESFILE)
    query.SetFieldData(INBLOCK, "shcode", 0, 종목코드)
    query.SetFieldData(INBLOCK, "gubun", 0, 구분)
    query.SetFieldData(INBLOCK, "fromdt", 0, 시작일자)
    query.SetFieldData(INBLOCK, "todt", 0, 종료일자)
    query.SetFieldData(INBLOCK, "prapp", 0, PR적용)
    query.SetFieldData(INBLOCK, "prgubun", 0, PR적용구분)
    query.SetFieldData(INBLOCK, "orggubun", 0, 기관적용)
    query.SetFieldData(INBLOCK, "frggubun", 0, 외인적용)
    query.Request(0)

    while XAQueryEvents.상태 == False:
        pythoncom.PumpWaitingMessages()

    result = []
    nCount = query.GetBlockCount(OUTBLOCK)
    for i in range(nCount):   #string=문자, long = int, float="float"
        누적거래량_2 = int(query.GetFieldData(OUTBLOCK, "volume", i).strip())
        누적거래량_2 = safe_cast(누적거래량_2,float)
        개인_2 = int(query.GetFieldData(OUTBLOCK, "psnvolume", i).strip())
        개인_2 = safe_cast(개인_2,float)
        기관_2 = int(query.GetFieldData(OUTBLOCK, "orgvolume", i).strip())
        기관_2 = safe_cast(기관_2,float)
        외국인 = int(query.GetFieldData(OUTBLOCK, "frgvolume", i).strip())
        외국인 = safe_cast(외국인,float)
        외국계 = int(query.GetFieldData(OUTBLOCK, "frgvolumesum", i).strip())
        외국계 = safe_cast(외국계,float)
        프로그램 = int(query.GetFieldData(OUTBLOCK, "pgmvolume", i).strip())
        프로그램 = safe_cast(프로그램,float)
        보유주식수 = int(query.GetFieldData(OUTBLOCK, "listing", i).strip())
        보유주식수 = safe_cast(보유주식수,float)
        소진율 = float(query.GetFieldData(OUTBLOCK, "sjrate", i).strip()) / 100

        lst = [누적거래량_2,개인_2,기관_2,외국인,외국계,프로그램,보유주식수,소진율]
        result.append(lst)

    df1 = DataFrame(data=result, columns=["누적거래량_2","개인_2","기관_2","외국인","외국계","프로그램","보유주식수","소진율"])
    XAQueryEvents.상태 = False

    return df1


def t1702(종목코드="", 종료일자="", 금액수량구분="0", 매수매도구분="0", 누적구분="0", CTSDATE="", CTSIDX=""):
    '''
    외인기관종목별동향
    '''
    query = win32com.client.DispatchWithEvents("XA_DataSet.XAQuery", XAQueryEvents)
    pathname = os.path.dirname(sys.argv[0])
    RESDIR = os.path.abspath(pathname)

    MYNAME = inspect.currentframe().f_code.co_name
    #print(MYNAME)
    INBLOCK = "%sInBlock" % MYNAME
    OUTBLOCK = "%sOutBlock" % MYNAME
    OUTBLOCK1 = "%sOutBlock1" % MYNAME
    RESFILE = "%s\\Res\\%s.res" % (RESDIR, MYNAME)

    query.LoadFromResFile(RESFILE)
    query.SetFieldData(INBLOCK, "shcode", 0, 종목코드)
    query.SetFieldData(INBLOCK, "todt", 0, 종료일자)
    query.SetFieldData(INBLOCK, "volvalgb", 0, 금액수량구분)
    query.SetFieldData(INBLOCK, "msmdgb", 0, 매수매도구분)
    query.SetFieldData(INBLOCK, "cumulgb", 0, 누적구분)
    query.SetFieldData(INBLOCK, "cts_date", 0, CTSDATE)
    query.SetFieldData(INBLOCK, "cts_idx", 0, CTSIDX)
    query.Request(0)

    while XAQueryEvents.상태 == False:
        pythoncom.PumpWaitingMessages()

    result = []
    nCount = query.GetBlockCount(OUTBLOCK1)
    for i in range(nCount):   #string=문자, long = int, float="float"
        전일대비구분 = query.GetFieldData(OUTBLOCK1, "sign", i).strip()
        전일대비구분 = safe_cast(전일대비구분,float)
        전일대비구분 = 전일대비구분 / 10
        
        사모펀드 = query.GetFieldData(OUTBLOCK1, "amt0000", i).strip()
        사모펀드 = safe_cast(사모펀드,float)
        증권 = query.GetFieldData(OUTBLOCK1, "amt0001", i).strip()
        증권 = safe_cast(증권,float)
        보험 = query.GetFieldData(OUTBLOCK1, "amt0002", i).strip()
        보험 = safe_cast(보험,float)
        투신 = query.GetFieldData(OUTBLOCK1, "amt0003", i).strip()
        투신 = safe_cast(투신,float)
        은행 = query.GetFieldData(OUTBLOCK1, "amt0004", i).strip()
        은행 = safe_cast(은행,float)
        종금 = query.GetFieldData(OUTBLOCK1, "amt0005", i).strip()
        종금 = safe_cast(종금,float)
        기금 = query.GetFieldData(OUTBLOCK1, "amt0006", i).strip()
        기금 = safe_cast(기금,float)
        기타법인 = query.GetFieldData(OUTBLOCK1, "amt0007", i).strip()
        기타법인 = safe_cast(기타법인,float)
        개인 = query.GetFieldData(OUTBLOCK1, "amt0008", i).strip()
        개인 = safe_cast(개인,float)
        등록외국인 = query.GetFieldData(OUTBLOCK1, "amt0009", i).strip()
        등록외국인 = safe_cast(등록외국인,float)
        미등록외국인 = query.GetFieldData(OUTBLOCK1, "amt0010", i).strip()
        미등록외국인 = safe_cast(미등록외국인,float)
        국가외 = query.GetFieldData(OUTBLOCK1, "amt0011", i).strip()
        국가외 = safe_cast(국가외,float)
        기관 = query.GetFieldData(OUTBLOCK1, "amt0018", i).strip()
        기관 = safe_cast(기관,float)
        외인계 = query.GetFieldData(OUTBLOCK1, "amt0088", i).strip()
        외인계 = safe_cast(외인계,float)
        기타계 = query.GetFieldData(OUTBLOCK1, "amt0099", i).strip()
        기타계 = safe_cast(기타계,float)

        lst = [전일대비구분,사모펀드,증권,보험,투신,은행,
               종금,기금,기타법인,개인,등록외국인,미등록외국인,국가외,기관,외인계,기타계]
        result.append(lst)

    df1 = DataFrame(data=result, columns=["전일대비구분","사모펀드","증권","보험","투신","은행",
                                          "종금","기금","기타법인","개인","등록외국인","미등록외국인","국가외","기관","외인계","기타계"])
    XAQueryEvents.상태 = False

    return df1


# 외인기관종목별동향
def t1717(종목코드='',구분='0',시작일자='',종료일자=''):
    '''
    외인기관종목별동향
    '''
    query = win32com.client.DispatchWithEvents("XA_DataSet.XAQuery", XAQueryEvents)
    pathname = os.path.dirname(sys.argv[0])
    RESDIR = os.path.abspath(pathname)

    MYNAME = inspect.currentframe().f_code.co_name
    #print(MYNAME)
    INBLOCK = "%sInBlock" % MYNAME
    OUTBLOCK = "%sOutBlock" % MYNAME
    OUTBLOCK1 = "%sOutBlock1" % MYNAME
    RESFILE = "%s\\Res\\%s.res" % (RESDIR, MYNAME)

    query.LoadFromResFile(RESFILE)
    query.SetFieldData(INBLOCK, "shcode", 0, 종목코드)
    query.SetFieldData(INBLOCK, "gubun", 0, 구분)
    query.SetFieldData(INBLOCK, "fromdt", 0, 시작일자)
    query.SetFieldData(INBLOCK, "todt", 0, 종료일자)
    query.Request(0)

    while XAQueryEvents.상태 == False:
        pythoncom.PumpWaitingMessages()

    result = []
    nCount = query.GetBlockCount(OUTBLOCK)
    for i in range(nCount):
        종가_1 = int(query.GetFieldData(OUTBLOCK, "close", i).strip())
        종가_1 = safe_cast(종가_1,float)
        사모펀드_순매수 = int(query.GetFieldData(OUTBLOCK, "tjj0000_vol", i).strip())
        사모펀드_순매수 = safe_cast(사모펀드_순매수,float)
        
        증권_순매수 = int(query.GetFieldData(OUTBLOCK, "tjj0001_vol", i).strip())
        증권_순매수 = safe_cast(증권_순매수,float)
        보험_순매수 = int(query.GetFieldData(OUTBLOCK, "tjj0002_vol", i).strip())
        보험_순매수 = safe_cast(보험_순매수,float)
        
        투신_순매수 = int(query.GetFieldData(OUTBLOCK, "tjj0003_vol", i).strip())
        투신_순매수 = safe_cast(투신_순매수,float)
        은행_순매수 = int(query.GetFieldData(OUTBLOCK, "tjj0004_vol", i).strip())
        은행_순매수 = safe_cast(은행_순매수,float)
        
        종금_순매수 = int(query.GetFieldData(OUTBLOCK, "tjj0005_vol", i).strip())
        종금_순매수 = safe_cast(종금_순매수,float)
        기금_순매수 = int(query.GetFieldData(OUTBLOCK, "tjj0006_vol", i).strip())
        기금_순매수 = safe_cast(기금_순매수,float)
        
        기타법인_순매수 = int(query.GetFieldData(OUTBLOCK, "tjj0007_vol", i).strip())
        기타법인_순매수 = safe_cast(기타법인_순매수,float)
                   
        개인_순매수 = int(query.GetFieldData(OUTBLOCK, "tjj0008_vol", i).strip())
        개인_순매수 = safe_cast(개인_순매수,float)
        등록외국인_순매수 = int(query.GetFieldData(OUTBLOCK, "tjj0009_vol", i).strip())
        등록외국인_순매수 = safe_cast(등록외국인_순매수,float)
        
        미등록외국인_순매수 = int(query.GetFieldData(OUTBLOCK, "tjj0010_vol", i).strip())
        미등록외국인_순매수 = safe_cast(미등록외국인_순매수,float)
        국가외_순매수 = int(query.GetFieldData(OUTBLOCK, "tjj0011_vol", i).strip())
        국가외_순매수 = safe_cast(국가외_순매수,float)
        
        기관_순매수 = int(query.GetFieldData(OUTBLOCK, "tjj0018_vol", i).strip())
        기관_순매수 = safe_cast(기관_순매수,float)
        외인계_순매수 = int(query.GetFieldData(OUTBLOCK, "tjj0016_vol", i).strip())
        외인계_순매수 = safe_cast(외인계_순매수,float)
        
        기타계_순매수 = int(query.GetFieldData(OUTBLOCK, "tjj0017_vol", i).strip())
        기타계_순매수 = safe_cast(기타계_순매수,float)

        
        사모펀드_단가 = int(query.GetFieldData(OUTBLOCK, "tjj0000_dan", i).strip())
        사모펀드_단가 = safe_cast(사모펀드_단가,float)
        사모펀드_단가 = (사모펀드_단가 - 종가_1) / 종가_1
        
        증권_단가 = int(query.GetFieldData(OUTBLOCK, "tjj0001_dan", i).strip())
        증권_단가 = safe_cast(증권_단가,float)
        증권_단가 = (증권_단가 - 종가_1) / 종가_1
        
        보험_단가 = int(query.GetFieldData(OUTBLOCK, "tjj0002_dan", i).strip())
        보험_단가 = safe_cast(보험_단가,float)
        보험_단가 = (보험_단가 - 종가_1) / 종가_1
        
        투신_단가 = int(query.GetFieldData(OUTBLOCK, "tjj0003_dan", i).strip())
        투신_단가 = safe_cast(투신_단가,float)
        투신_단가 = (투신_단가 - 종가_1) / 종가_1
        
        은행_단가 = int(query.GetFieldData(OUTBLOCK, "tjj0004_dan", i).strip())
        은행_단가 = safe_cast(은행_단가,float)
        은행_단가 = (은행_단가 - 종가_1) / 종가_1
        
        종금_단가 = int(query.GetFieldData(OUTBLOCK, "tjj0005_dan", i).strip())
        종금_단가 = safe_cast(종금_단가,float)
        종금_단가 = (종금_단가 - 종가_1) / 종가_1
        
        기금_단가 = int(query.GetFieldData(OUTBLOCK, "tjj0006_dan", i).strip())
        기금_단가 = safe_cast(기금_단가,float)
        기금_단가 = (기금_단가 - 종가_1) / 종가_1
        
        기타법인_단가 = int(query.GetFieldData(OUTBLOCK, "tjj0007_dan", i).strip())
        기타법인_단가 = safe_cast(기타법인_단가,float)
        기타법인_단가 = (기타법인_단가 - 종가_1) / 종가_1
        
        개인_단가 = int(query.GetFieldData(OUTBLOCK, "tjj0008_dan", i).strip())
        개인_단가 = safe_cast(개인_단가,float)
        개인_단가 = (개인_단가 - 종가_1) / 종가_1
        
        등록외국인_단가 = int(query.GetFieldData(OUTBLOCK, "tjj0009_dan", i).strip())
        등록외국인_단가 = safe_cast(등록외국인_단가,float)
        등록외국인_단가 = (등록외국인_단가 - 종가_1) / 종가_1
        
        미등록외국인_단가 = int(query.GetFieldData(OUTBLOCK, "tjj0010_dan", i).strip())
        미등록외국인_단가 = safe_cast(미등록외국인_단가,float)
        미등록외국인_단가 = (미등록외국인_단가 - 종가_1) / 종가_1
        
        국가외_단가 = int(query.GetFieldData(OUTBLOCK, "tjj0011_dan", i).strip())
        국가외_단가 = safe_cast(국가외_단가,float)
        국가외_단가 = (국가외_단가 - 종가_1) / 종가_1
        
        기관_단가 = int(query.GetFieldData(OUTBLOCK, "tjj0018_dan", i).strip())
        기관_단가 = safe_cast(기관_단가,float)
        기관_단가 = (기관_단가 - 종가_1) / 종가_1
        
        외인계_단가 = int(query.GetFieldData(OUTBLOCK, "tjj0016_dan", i).strip())
        외인계_단가 = safe_cast(외인계_단가,float)
        외인계_단가 = (외인계_단가 - 종가_1) / 종가_1
        
        기타계_단가 = int(query.GetFieldData(OUTBLOCK, "tjj0017_dan", i).strip())
        기타계_단가 = safe_cast(기타계_단가,float)
        기타계_단가 = (기타계_단가 - 종가_1) / 종가_1
        
        개인_순매수_1 = int(query.GetFieldData(OUTBLOCK, "tjj0008_vol", i).strip())
        개인_순매수_1 = safe_cast(개인_순매수_1,float)
        
        lst = [종가_1,사모펀드_순매수,증권_순매수,보험_순매수,투신_순매수,은행_순매수,종금_순매수,기금_순매수,기타법인_순매수,개인_순매수,등록외국인_순매수,미등록외국인_순매수,국가외_순매수,기관_순매수,외인계_순매수,기타계_순매수,
               사모펀드_단가,증권_단가,보험_단가,투신_단가,은행_단가,종금_단가,기금_단가,기타법인_단가,개인_단가,등록외국인_단가,미등록외국인_단가,국가외_단가,기관_단가,외인계_단가,기타계_단가,개인_순매수_1]

        result.append(lst)

    columns=['종가_1','사모펀드_순매수','증권_순매수','보험_순매수','투신_순매수','은행_순매수','종금_순매수','기금_순매수','기타법인_순매수','개인_순매수',
             '등록외국인_순매수','미등록외국인_순매수','국가외_순매수','기관_순매수','외인계_순매수','기타계_순매수','사모펀드_단가','증권_단가',
             '보험_단가','투신_단가','은행_단가','종금_단가','기금_단가','기타법인_단가','개인_단가','등록외국인_단가','미등록외국인_단가',
             '국가외_단가','기관_단가','외인계_단가','기타계_단가','개인_순매수_1']
    df = DataFrame(data=result, columns=columns)

    XAQueryEvents.상태 = False

    return df

def t4201(단축코드="",주기구분="2",틱개수="",건수="1",당일구분="1",시작일자="",종료일자="",연속일자="",연속시간="",연속당일구분="1"):  
    '''
    주식종목코드조회
    '''
    query = win32com.client.DispatchWithEvents("XA_DataSet.XAQuery", XAQueryEvents)
    pathname = os.path.dirname(sys.argv[0])
    RESDIR = os.path.abspath(pathname)


    MYNAME = inspect.currentframe().f_code.co_name
    #print(MYNAME)
    INBLOCK = "%sInBlock" % MYNAME
    OUTBLOCK = "%sOutBlock" % MYNAME
    OUTBLOCK1 = "%sOutBlock1" % MYNAME
    RESFILE = "%s\\Res\\%s.res" % (RESDIR, MYNAME)
    

    query.LoadFromResFile(RESFILE)
    query.SetFieldData(INBLOCK, "shcode", 0, 단축코드)
    query.SetFieldData(INBLOCK, "gubun", 0, 주기구분)
    query.SetFieldData(INBLOCK, "ncnt", 0, 틱개수)
    query.SetFieldData(INBLOCK, "qrycnt", 0, 건수)
    query.SetFieldData(INBLOCK, "tdgb", 0, 당일구분)
    query.SetFieldData(INBLOCK, "sdate", 0, 시작일자)
    query.SetFieldData(INBLOCK, "edate", 0, 종료일자)
    query.SetFieldData(INBLOCK, "cts_date", 0, 연속일자)
    query.SetFieldData(INBLOCK, "cts_time", 0, 연속시간)
    query.SetFieldData(INBLOCK, "cts_daygb", 0, 연속당일구분)
    query.Request(0)

    while XAQueryEvents.상태 == False:
        pythoncom.PumpWaitingMessages()

    result = []
    nCount = query.GetBlockCount(OUTBLOCK1)
    for i in range(nCount):
        종가_2 = int(query.GetFieldData(OUTBLOCK1, "close", i).strip())
        종가_2 = safe_cast(종가_2,float)
        
        전일시가 = int(query.GetFieldData(OUTBLOCK, "jisiga", i).strip())
        전일시가 = safe_cast(전일시가,float)
        전일시가 = (전일시가 - 종가_2) / 종가_2
        
        전일고가 = int(query.GetFieldData(OUTBLOCK, "jihigh", i).strip())
        전일고가 = safe_cast(전일고가,float)
        전일고가 = (전일고가 - 종가_2) / 종가_2

 
        lst = [종가_2,전일시가,전일고가]
        result.append(lst)

    XAQueryEvents.상태 = False

    columns=["종가_2","전일시가","전일고가"]
    df = DataFrame(data=result, columns=columns)
    return df


# 관리/불성실/투자유의조회
def t1404(구분='1',종목체크='',종목코드_CTS=""):
    '''
    관리/불성실/투자유의조회
    '''
    query = win32com.client.DispatchWithEvents("XA_DataSet.XAQuery", XAQueryEvents)
    pathname = os.path.dirname(sys.argv[0])
    RESDIR = os.path.abspath(pathname)

    MYNAME = inspect.currentframe().f_code.co_name
    #print(MYNAME)
    INBLOCK = "%sInBlock" % MYNAME
    OUTBLOCK = "%sOutBlock" % MYNAME
    OUTBLOCK1 = "%sOutBlock1" % MYNAME
    RESFILE = "%s\\Res\\%s.res" % (RESDIR, MYNAME)

    query.LoadFromResFile(RESFILE)
    query.SetFieldData(INBLOCK, "gubun", 0, 구분)
    query.SetFieldData(INBLOCK, "jongchk", 0, 종목체크)
    query.SetFieldData(INBLOCK, "cts_shcode", 0, 종목코드_CTS)
    query.Request(0)

    while XAQueryEvents.상태 == False:
        pythoncom.PumpWaitingMessages()

    result = []
    nCount = query.GetBlockCount(OUTBLOCK1)
    for i in range(nCount):
        한글명 = query.GetFieldData(OUTBLOCK1, "hname", i).strip()
        종목코드 = query.GetFieldData(OUTBLOCK1, "shcode", i).strip()
        
        
        lst = [한글명,종목코드]
        result.append(lst)

    columns=["한글명","종목코드"]
    df = DataFrame(data=result, columns=columns)

    XAQueryEvents.상태 = False

    return df


    
# 투자경고/매매정지/정리매매조회
def t1405(구분='1',종목체크='',종목코드_CTS=""):
    '''
    투자경고/매매정지/정리매매조회
    '''
    query = win32com.client.DispatchWithEvents("XA_DataSet.XAQuery", XAQueryEvents)
    pathname = os.path.dirname(sys.argv[0])
    RESDIR = os.path.abspath(pathname)

    MYNAME = inspect.currentframe().f_code.co_name
    #print(MYNAME)
    INBLOCK = "%sInBlock" % MYNAME
    OUTBLOCK = "%sOutBlock" % MYNAME
    OUTBLOCK1 = "%sOutBlock1" % MYNAME
    RESFILE = "%s\\Res\\%s.res" % (RESDIR, MYNAME)

    query.LoadFromResFile(RESFILE)
    query.SetFieldData(INBLOCK, "gubun", 0, 구분)
    query.SetFieldData(INBLOCK, "jongchk", 0, 종목체크)
    query.SetFieldData(INBLOCK, "cts_shcode", 0, 종목코드_CTS)
    query.Request(0)

    while XAQueryEvents.상태 == False:
        pythoncom.PumpWaitingMessages()

    result = []
    nCount = query.GetBlockCount(OUTBLOCK1)
    for i in range(nCount):
        한글명 = query.GetFieldData(OUTBLOCK1, "hname", i).strip()
        종목코드 = query.GetFieldData(OUTBLOCK1, "shcode", i).strip()
        
        
        lst = [한글명,종목코드]
        result.append(lst)

    columns=["한글명","종목코드"]
    df = DataFrame(data=result, columns=columns)

    XAQueryEvents.상태 = False

    return df


# 초저유동성조회
def t1410(구분='1',종목코드_CTS=""):
    '''
    초저유동성조회
    '''
    query = win32com.client.DispatchWithEvents("XA_DataSet.XAQuery", XAQueryEvents)
    pathname = os.path.dirname(sys.argv[0])
    RESDIR = os.path.abspath(pathname)

    MYNAME = inspect.currentframe().f_code.co_name
    #print(MYNAME)
    INBLOCK = "%sInBlock" % MYNAME
    OUTBLOCK = "%sOutBlock" % MYNAME
    OUTBLOCK1 = "%sOutBlock1" % MYNAME
    RESFILE = "%s\\Res\\%s.res" % (RESDIR, MYNAME)

    query.LoadFromResFile(RESFILE)
    query.SetFieldData(INBLOCK, "gubun", 0, 구분)
    query.SetFieldData(INBLOCK, "cts_shcode", 0, 종목코드_CTS)
    query.Request(0)

    while XAQueryEvents.상태 == False:
        pythoncom.PumpWaitingMessages()

    result = []
    nCount = query.GetBlockCount(OUTBLOCK1)
    for i in range(nCount):
        한글명 = query.GetFieldData(OUTBLOCK1, "hname", i).strip()
        종목코드 = query.GetFieldData(OUTBLOCK1, "shcode", i).strip()
        
        
        lst = [한글명,종목코드]
        result.append(lst)

    columns=["한글명","종목코드"]
    df = DataFrame(data=result, columns=columns)

    XAQueryEvents.상태 = False

    return df

if __name__ == "__main__":
    계좌정보 = pd.read_csv("secret/passwords.csv", converters={'계좌번호': str, '거래비밀번호': str}, encoding="euc-kr")
    주식계좌정보 = 계좌정보.query("구분 == '거래'")
    if len(주식계좌정보) == 0:
        print("secret디렉토리의 passwords.csv 파일에서 거래 계좌를 지정해 주세요")
    else:
        계좌번호 = 주식계좌정보['계좌번호'].values[0].strip()
        id = 주식계좌정보['사용자ID'].values[0].strip()
        pwd = 주식계좌정보['비밀번호'].values[0].strip()
        cert = 주식계좌정보['공인인증비밀번호'][0].strip()
        거래비밀번호 = 주식계좌정보['거래비밀번호'].values[0].strip()
        url = 주식계좌정보['url'][0].strip()

        result, code, msg, 계좌, session = Login(url=url, port=20001, svrtype=0,id=id, pwd=pwd,cert=cert)
        if result == False:
            sys.exit(0)

        #기준이 되는 종목명, 종목코드 끌어오는 [t8430]    
        df = t8430() #코스피
        df = df[df.ETF구분 == 0]
        #df = df[['종목명','단축코드']]
        

        df_result = DataFrame([])

        #t1404 관리/불성실/투자유의종목 뽑아내는 코드
        time.sleep(1.1)
        df111 = t1404(종목체크="1")
        time.sleep(1.1)
        df112 = t1404(종목체크="2")
        time.sleep(1.1)
        df113 = t1404(종목체크="3")
        time.sleep(1.1)
        df114 = t1404(종목체크="4")

        #t1405 투자경고/매매정리/정리매매조회 뽑아내는 코드
        time.sleep(1.1)
        df11 = t1405(종목체크="1")
        time.sleep(1.1)
        df22 = t1405(종목체크='2')
        time.sleep(1.1)
        df33 = t1405(종목체크='3')
        time.sleep(1.1)
        df44 = t1405(종목체크="4")
        time.sleep(1.1)
        df55 = t1405(종목체크="5")

        #t1410 초저유동성조회 뽑아내는 코드
        df66 = t1410()

        
        #제거해야할 종목 전부 pandas_frame으로 합치기
        time.sleep(1.1)
        df_delete = pd.concat([df111,df112,df113,df114,
                             df11,df22,df33,df44,df55,df66],axis=0)
        
        print(df_delete)
        print("len(df_delete) : ",len(df_delete))
        
        #제거해야할 종목들 pandas dataframe을 사전작업으로 numpy로 바구기
        df_delete = df_delete.values

        
        # df(전체종목)에서 빼야할 종목 제거 하는 코드 (종목코드 기준)
        time.sleep(1.1)
        for i in range(len(df_delete)):
            print(df_delete[i][1])
            df = df[df.단축코드 != df_delete[i][1]]



        #제외시킬 종목 제거하는 코드
        #df = df[df.단축코드 != "002600"]
        #print(df)
        
        #종목 다 거르고 난 이후 마지막 작업으로 for문으로 데이터 수집을 위해 numpy로 바꾸기
        df = df.values


        print(df)
        #print(df[0][0]) #종목명
        #print(df[0][1]) #단축코드
        #print(df[0][2]) #ETF구분
        print("종목개수 :", len(df))
        

        #t1471 누적거래량이 0인 종목 뽑아내는 코드
        df_1471 = DataFrame([])

        for i in range(180):
            time.sleep(1.1)
            df_14 = t1471(종목코드=df[i][1])
            df_14.insert(0,"종목명",df[i][0])
            df_14.insert(1,"종목코드",df[i][1])
            df_14.insert(2,"ETF구분", df[i][2])
            df_1471 = df_1471.append(df_14)
            print(df_1471)

            if i == 179:
                print("타임슬립걸렸습니다")
                print("약12분뒤에 다시 수집 시작합니다") 
                time.sleep(720) 
   
        for i in range(180,360):
            time.sleep(1.1)
            df_14 = t1471(종목코드=df[i][1])
            df_14.insert(0,"종목명",df[i][0])
            df_14.insert(1,"종목코드",df[i][1])
            df_14.insert(2,"ETF구분", df[i][2])
            df_1471 = df_1471.append(df_14)
            print(df_1471)
            if i == 359:
                print("타임슬립걸렸습니다")
                print("약12분뒤에 다시 수집 시작합니다") 
                time.sleep(720)

        for i in range(360,540):
            time.sleep(1.1)
            df_14 = t1471(종목코드=df[i][1])
            df_14.insert(0,"종목명",df[i][0])
            df_14.insert(1,"종목코드",df[i][1])
            df_14.insert(2,"ETF구분", df[i][2])
            df_1471 = df_1471.append(df_14)
            print(df_1471)
            if i == 539:
                print("타임슬립걸렸습니다")
                print("약12분뒤에 다시 수집 시작합니다") 
                time.sleep(720)
                
        for i in range(540,720):
            time.sleep(1.1)
            df_14 = t1471(종목코드=df[i][1])
            df_14.insert(0,"종목명",df[i][0])
            df_14.insert(1,"종목코드",df[i][1])
            df_14.insert(2,"ETF구분", df[i][2])
            df_1471 = df_1471.append(df_14)
            print(df_1471)
            if i == 719:
                print("타임슬립걸렸습니다")
                print("약12분뒤에 다시 수집 시작합니다") 
                time.sleep(720)
                
        for i in range(720,len(df)):
            time.sleep(1.1)
            df_14 = t1471(종목코드=df[i][1])
            df_14.insert(0,"종목명",df[i][0])
            df_14.insert(1,"종목코드",df[i][1])
            df_14.insert(2,"ETF구분", df[i][2])
            df_1471 = df_1471.append(df_14)
            print(df_1471)
            #if i == 899:
            #    print("타임슬립걸렸습니다")
            #    print("약12분뒤에 다시 수집 시작합니다") 
            #    time.sleep(720)

writer = pd.ExcelWriter("result.xlsx", engine="xlsxwriter")
df_result.to_excel(writer, sheet_name="Sheet1")
writer.close()
'''
        for i in range(900,1080):
            time.sleep(1.1)
            df_14 = t1471(종목코드=df[i][1])
            df_14.insert(0,"종목명",df[i][0])
            df_14.insert(1,"종목코드",df[i][1])
            df_14.insert(2,"ETF구분", df[i][2])
            df_1471 = df_1471.append(df_14)
            print(df_1471)
            if i == 1079:
                print("타임슬립걸렸습니다")
                print("약12분뒤에 다시 수집 시작합니다") 
                time.sleep(720)
                
        for i in range(1080,1260):
            time.sleep(1.1)
            df_14 = t1471(종목코드=df[i][1])
            df_14.insert(0,"종목명",df[i][0])
            df_14.insert(1,"종목코드",df[i][1])
            df_14.insert(2,"ETF구분", df[i][2])
            df_1471 = df_1471.append(df_14)
            print(df_1471)
            if i == 1259:
                print("타임슬립걸렸습니다")
                print("약12분뒤에 다시 수집 시작합니다") 
                time.sleep(720)

        print("df[1269]:",df[1269][0])
        print("df[1270]:",df[1270][0])
        
        for i in range(1260,1440):
            time.sleep(1.1)
            df_14 = t1471(종목코드=df[i][1])
            df_14.insert(0,"종목명",df[i][0])
            df_14.insert(1,"종목코드",df[i][1])
            df_14.insert(2,"ETF구분", df[i][2])
            df_1471 = df_1471.append(df_14)
            print(df_1471)
            if i == 1439:
                print("타임슬립걸렸습니다")
                print("약12분뒤에 다시 수집 시작합니다") 
                time.sleep(720)
                
        for i in range(1440,len(df)):
            time.sleep(1.1)
            df_14 = t1471(종목코드=df[i][1])
            df_14.insert(0,"종목명",df[i][0])
            df_14.insert(1,"종목코드",df[i][1])
            df_14.insert(2,"ETF구분", df[i][2])
            df_1471 = df_1471.append(df_14)
            print(df_1471)

        #누적거래량 0인 종목 사전에 제거하는 코드
        df_1471 = df_1471[df_1471.누적거래량 != 0]
        
        df_1471 = df_1471.values

        df = df_1471
        
        for i in range(180):
            print(i)
            time.sleep(0.5)
            df_8430_code = df[i][1] 
            df_8430_name = df[i][0]
            df_8430_etf =  df[i][2]
            
            df1 = t1471(종목코드=df_8430_code)
            df2 = t1475(종목코드=df_8430_code)
            df2 = df2.ix[:0]
            df3 = t1636(종목코드=df_8430_code)
            df3 = df3.ix[:0]
            df5 = t1701(종목코드=df_8430_code)
            df6 = t1702(종목코드=df_8430_code)
            df6 = df6.ix[:0]
            df7 = t1717(종목코드=df_8430_code)
            df8 = t4201(단축코드=df_8430_code)
            
            df_axis = pd.concat([df1,df2,df3,df5,df6,df7,df8],axis=1)
            df_axis.insert(0,"일자",b)
            df_axis.insert(1,"단축코드", df_8430_code)
            df_axis.insert(2,"종목명", df_8430_name)
            df_axis.insert(3,"ETF구분",df_8430_etf)
            df_result = df_result.append(df_axis)
            print(df_result)
            if i == 179:
                print("타임슬립걸렸습니다")
                print("약12분뒤에 다시 수집 시작합니다") 
                time.sleep(720) 
                

        for i in range(180,360):
            time.sleep(0.5)
            df_8430_code = df[i][1] 
            df_8430_name = df[i][0]
            df_8430_etf =  df[i][2]
            
            df1 = t1471(종목코드=df_8430_code)
            df2 = t1475(종목코드=df_8430_code)
            df2 = df2.ix[:0]
            df3 = t1636(종목코드=df_8430_code)
            df3 = df3.ix[:0]
            df5 = t1701(종목코드=df_8430_code)
            df6 = t1702(종목코드=df_8430_code)
            df6 = df6.ix[:0]
            df7 = t1717(종목코드=df_8430_code)
            df8 = t4201(단축코드=df_8430_code)
            
            df_axis = pd.concat([df1,df2,df3,df5,df6,df7,df8],axis=1)
            df_axis.insert(0,"일자",b)
            df_axis.insert(1,"단축코드", df_8430_code)
            df_axis.insert(2,"종목명", df_8430_name)
            df_axis.insert(3,"ETF구분",df_8430_etf)
            df_result = df_result.append(df_axis)
            print(df_result)
            if i == 359:
                print("타임슬립걸렸습니다")
                print("약12분뒤에 다시 수집 시작합니다") 
                time.sleep(720)
                

        for i in range(360,540):
            print(i)
            time.sleep(0.5)
            df_8430_code = df[i][1] 
            df_8430_name = df[i][0]
            df_8430_etf =  df[i][2]
            df1 = t1471(종목코드=df_8430_code)
            df2 = t1475(종목코드=df_8430_code)
            df2 = df2.ix[:0]
            df3 = t1636(종목코드=df_8430_code)
            df3 = df3.ix[:0]
            df5 = t1701(종목코드=df_8430_code)
            df6 = t1702(종목코드=df_8430_code)
            df6 = df6.ix[:0]
            df7 = t1717(종목코드=df_8430_code)
            df8 = t4201(단축코드=df_8430_code)
            
            df_axis = pd.concat([df1,df2,df3,df5,df6,df7,df8],axis=1)
            df_axis.insert(0,"일자",b)
            df_axis.insert(1,"단축코드", df_8430_code)
            df_axis.insert(2,"종목명", df_8430_name)
            df_axis.insert(3,"ETF구분",df_8430_etf)
            df_result = df_result.append(df_axis)
            print(df_result)
            if i == 539:
                print("타임슬립걸렸습니다")
                print("약12분뒤에 다시 수집 시작합니다")
                time.sleep(720)
                 

        for i in range(540,720):
            print(i)
            time.sleep(0.5)
            df_8430_code = df[i][1] 
            df_8430_name = df[i][0]
            df_8430_etf =  df[i][2]
            df1 = t1471(종목코드=df_8430_code)
            df2 = t1475(종목코드=df_8430_code)
            df2 = df2.ix[:0]
            df3 = t1636(종목코드=df_8430_code)
            df3 = df3.ix[:0]
            df5 = t1701(종목코드=df_8430_code)
            df6 = t1702(종목코드=df_8430_code)
            df6 = df6.ix[:0]
            df7 = t1717(종목코드=df_8430_code)
            df8 = t4201(단축코드=df_8430_code)
            
            df_axis = pd.concat([df1,df2,df3,df5,df6,df7,df8],axis=1)
            df_axis.insert(0,"일자",b)
            df_axis.insert(1,"단축코드", df_8430_code)
            df_axis.insert(2,"종목명", df_8430_name)
            df_axis.insert(3,"ETF구분",df_8430_etf)
            df_result = df_result.append(df_axis)
            print(df_result)
            if i == 719:
                print("타임슬립걸렸습니다")
                print("약12분뒤에 다시 수집 시작합니다")
                time.sleep(720) 

                
        for i in range(720,900):
            print(i)
            time.sleep(0.5)
            df_8430_code = df[i][1] 
            df_8430_name = df[i][0]
            df_8430_etf =  df[i][2]
            df1 = t1471(종목코드=df_8430_code)
            df2 = t1475(종목코드=df_8430_code)
            df2 = df2.ix[:0]
            df3 = t1636(종목코드=df_8430_code)
            df3 = df3.ix[:0]
            df5 = t1701(종목코드=df_8430_code)
            df6 = t1702(종목코드=df_8430_code)
            df6 = df6.ix[:0]
            df7 = t1717(종목코드=df_8430_code)
            df8 = t4201(단축코드=df_8430_code)
            
            df_axis = pd.concat([df1,df2,df3,df5,df6,df7,df8],axis=1)
            df_axis.insert(0,"일자",b)
            df_axis.insert(1,"단축코드", df_8430_code)
            df_axis.insert(2,"종목명", df_8430_name)
            df_axis.insert(3,"ETF구분",df_8430_etf)
            df_result = df_result.append(df_axis)
            print(df_result)
            if i == 899:
                print("타임슬립걸렸습니다")
                print("약12분뒤에 다시 수집 시작합니다")
                time.sleep(720) 

                
        for i in range(900,1080):
            print(i)
            time.sleep(0.5)
            df_8430_code = df[i][1] 
            df_8430_name = df[i][0]
            df_8430_etf =  df[i][2]
            df1 = t1471(종목코드=df_8430_code)
            df2 = t1475(종목코드=df_8430_code)
            df2 = df2.ix[:0]
            df3 = t1636(종목코드=df_8430_code)
            df3 = df3.ix[:0]
            df5 = t1701(종목코드=df_8430_code)
            df6 = t1702(종목코드=df_8430_code)
            df6 = df6.ix[:0]
            df7 = t1717(종목코드=df_8430_code)
            df8 = t4201(단축코드=df_8430_code)
            
            df_axis = pd.concat([df1,df2,df3,df5,df6,df7,df8],axis=1)
            df_axis.insert(0,"일자",b)
            df_axis.insert(1,"단축코드", df_8430_code)
            df_axis.insert(2,"종목명", df_8430_name)
            df_axis.insert(3,"ETF구분",df_8430_etf)
            df_result = df_result.append(df_axis)
            print(df_result)
            if i == 1079:
                print("타임슬립걸렸습니다")
                print("약12분뒤에 다시 수집 시작합니다")
                time.sleep(720) 

                
        for i in range(1080,1260):
            print(i)
            time.sleep(0.5)
            df_8430_code = df[i][1] 
            df_8430_name = df[i][0]
            df_8430_etf =  df[i][2]
            df1 = t1471(종목코드=df_8430_code)
            df2 = t1475(종목코드=df_8430_code)
            df2 = df2.ix[:0]
            df3 = t1636(종목코드=df_8430_code)
            df3 = df3.ix[:0]
            df5 = t1701(종목코드=df_8430_code)
            df6 = t1702(종목코드=df_8430_code)
            df6 = df6.ix[:0]
            df7 = t1717(종목코드=df_8430_code)
            df8 = t4201(단축코드=df_8430_code)
            
            df_axis = pd.concat([df1,df2,df3,df5,df6,df7,df8],axis=1)
            df_axis.insert(0,"일자",b)
            df_axis.insert(1,"단축코드", df_8430_code)
            df_axis.insert(2,"종목명", df_8430_name)
            df_axis.insert(3,"ETF구분",df_8430_etf)
            df_result = df_result.append(df_axis)
            print(df_result)
            if i == 1259:
                print("타임슬립걸렸습니다")
                print("약12분뒤에 다시 수집 시작합니다")
                time.sleep(720) 

                
        for i in range(1260,1440):
            print(i)
            time.sleep(0.5)
            df_8430_code = df[i][1] 
            df_8430_name = df[i][0]
            df_8430_etf =  df[i][2]
            df1 = t1471(종목코드=df_8430_code)
            df2 = t1475(종목코드=df_8430_code)
            df2 = df2.ix[:0]
            df3 = t1636(종목코드=df_8430_code)
            df3 = df3.ix[:0]
            df5 = t1701(종목코드=df_8430_code)
            df6 = t1702(종목코드=df_8430_code)
            df6 = df6.ix[:0]
            df7 = t1717(종목코드=df_8430_code)
            df8 = t4201(단축코드=df_8430_code)
            
            df_axis = pd.concat([df1,df2,df3,df5,df6,df7,df8],axis=1)
            df_axis.insert(0,"일자",b)
            df_axis.insert(1,"단축코드", df_8430_code)
            df_axis.insert(2,"종목명", df_8430_name)
            df_axis.insert(3,"ETF구분",df_8430_etf)
            df_result = df_result.append(df_axis)
            print(df_result)
            if i == 1439:
                print("타임슬립걸렸습니다")
                print("약12분뒤에 다시 수집 시작합니다")
                time.sleep(720) 


        for i in range(1440,len(df)):
            print(i)
            time.sleep(0.5)
            df_8430_code = df[i][1] 
            df_8430_name = df[i][0]
            df_8430_etf =  df[i][2]
            
            df1 = t1471(종목코드=df_8430_code)
            df2 = t1475(종목코드=df_8430_code)
            df2 = df2.ix[:0]
            df3 = t1636(종목코드=df_8430_code)
            df3 = df3.ix[:0]
            df5 = t1701(종목코드=df_8430_code)
            df6 = t1702(종목코드=df_8430_code)
            df6 = df6.ix[:0]
            df7 = t1717(종목코드=df_8430_code)
            df8 = t4201(단축코드=df_8430_code)
            
        
            df_axis = pd.concat([df1,df2,df3,df5,df6,df7,df8],axis=1)
            
            df_axis.insert(0,"일자",b)
            df_axis.insert(1,"단축코드", df_8430_code)
            df_axis.insert(2,"종목명", df_8430_name)
            df_axis.insert(3,"ETF구분",df_8430_etf)
            df_result = df_result.append(df_axis)
            print(df_result)


        df_result["누적거래량"] = df_result["누적거래량"] * df_result["종가"] / df_result["시가총액"]
        df_result["매도우선잔량"] = df_result["매도우선잔량"] / df_result["누적거래량_1"]
        df_result["매수우선잔량"] = df_result["매수우선잔량"] / df_result["누적거래량_1"]
        df_result["총매도"] = df_result["총매도"] / df_result["누적거래량_1"]
        df_result["총매수"] = df_result["총매수"] / df_result["누적거래량_1"]
        df_result["순매수"] = df_result["순매수"] / df_result["누적거래량_1"]

        df_result["거래량"] = df_result["거래량"] * df_result["종가"] / df_result["시가총액"]
        df_result["거래량_1"] = df_result["거래량_1"] * df_result["종가"] / df_result["시가총액"]
        
        df_result["누적거래량_2"] = df_result["누적거래량_2"] * df_result["종가"] / df_result["시가총액"]
        df_result["개인"] = df_result["개인"] * df_result["종가"] / df_result["시가총액"]
        df_result["기관"] = df_result["기관"] * df_result["종가"] / df_result["시가총액"]
        df_result["외국인"] = df_result["외국인"] * df_result["종가"] / df_result["시가총액"]
        df_result["외국계"] = df_result["외국계"] * df_result["종가"] / df_result["시가총액"]
        df_result["프로그램"] = df_result["프로그램"] * df_result["종가"] / df_result["시가총액"]
        df_result["보유주식수"] = df_result["보유주식수"] * df_result["종가"] / df_result["시가총액"]

        df_result["사모펀드"] = df_result["사모펀드"] * df_result["종가"] / df_result["시가총액"]
        df_result["증권"] = df_result["증권"] * df_result["종가"] / df_result["시가총액"]
        df_result["보험"] = df_result["보험"] * df_result["종가"] / df_result["시가총액"]
        df_result["투신"] = df_result["투신"] * df_result["종가"] / df_result["시가총액"]
        df_result["은행"] = df_result["은행"] * df_result["종가"] / df_result["시가총액"]
        df_result["종금"] = df_result["종금"] * df_result["종가"] / df_result["시가총액"]
        df_result["기금"] = df_result["기금"] * df_result["종가"] / df_result["시가총액"]
        df_result["기타법인"] = df_result["기타법인"] * df_result["종가"] / df_result["시가총액"]
        df_result["개인"] = df_result["개인"] * df_result["종가"] / df_result["시가총액"]
        df_result["등록외국인"] = df_result["등록외국인"] * df_result["종가"] / df_result["시가총액"]
        df_result["미등록외국인"] = df_result["미등록외국인"] * df_result["종가"] / df_result["시가총액"]
        df_result["국가외"] = df_result["국가외"] * df_result["종가"] / df_result["시가총액"]
        df_result["기관"] = df_result["기관"] * df_result["종가"] / df_result["시가총액"]
        df_result["외인계"] = df_result["외인계"] * df_result["종가"] / df_result["시가총액"]
        df_result["기타계"] = df_result["기타계"] * df_result["종가"] / df_result["시가총액"]
        
        df_result["사모펀드_순매수"] = df_result["사모펀드_순매수"] * df_result["종가"] / df_result["시가총액"]
        df_result["증권_순매수"] = df_result["증권_순매수"] * df_result["종가"] / df_result["시가총액"]
        df_result["보험_순매수"] = df_result["보험_순매수"] * df_result["종가"] / df_result["시가총액"]
        df_result["투신_순매수"] = df_result["투신_순매수"] * df_result["종가"] / df_result["시가총액"]
        df_result["은행_순매수"] = df_result["은행_순매수"] * df_result["종가"] / df_result["시가총액"]
        df_result["종금_순매수"] = df_result["종금_순매수"] * df_result["종가"] / df_result["시가총액"]
        df_result["기금_순매수"] = df_result["기금_순매수"] * df_result["종가"] / df_result["시가총액"]
        df_result["기타법인_순매수"] = df_result["기타법인_순매수"] * df_result["종가"] / df_result["시가총액"]
        df_result["개인_순매수"] = df_result["개인_순매수"] * df_result["종가"] / df_result["시가총액"]
        df_result["등록외국인_순매수"] = df_result["등록외국인_순매수"] * df_result["종가"] / df_result["시가총액"]
        df_result["미등록외국인_순매수"] = df_result["미등록외국인_순매수"] * df_result["종가"] / df_result["시가총액"]
        df_result["국가외_순매수"] = df_result["국가외_순매수"] * df_result["종가"] / df_result["시가총액"]
        df_result["기관_순매수"] = df_result["기관_순매수"] * df_result["종가"] / df_result["시가총액"]
        df_result["외인계_순매수"] = df_result["외인계_순매수"] * df_result["종가"] / df_result["시가총액"]
        df_result["기타계_순매수"] = df_result["기타계_순매수"] * df_result["종가"] / df_result["시가총액"]

        df_result["개인_순매수_1"] = df_result["개인_순매수_1"] * df_result["종가"] / df_result["시가총액"]
        
            
        df_result = df_result[df_result.ETF구분 == "0"]
        df_result = df_result.drop(["ETF구분"],axis=1)
        df_result = df_result.drop(["누적거래량_1"],axis=1)
        df_result = df_result.drop(["시가총액"],axis=1)
        df_result = df_result.drop(["종가"],axis=1)
        df_result = df_result.drop(["종가_1"],axis=1)
        df_result = df_result.drop(["종가_2"],axis=1)
        
        print("수집이 완료되었습니다")
        print("최종 데이터 수집입니다")
        print(df_result)
        print("시작한시간: ", a)            



writer = pd.ExcelWriter("Train_Normalization.xlsx", engine="xlsxwriter")
df_result.to_excel(writer, sheet_name="Sheet1")
writer.close()
'''
