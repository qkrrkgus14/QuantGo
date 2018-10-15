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
        print("전체 코스피 종목 수 :", len(df))
        print("제거해야할 종목 갯수: ",len(df_delete))
        print(len(df)-len(df_delete))
        
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
        print("5초뒤 데이터 수집 시작합니다")
        time.sleep(5)
        
        

        
        df_1471 = DataFrame([])

        
        for i in range(len(df)):
            time.sleep(1.1)
            df_14 = t1471(종목코드=df[i][1])
            df_14.insert(0,"종목명",df[i][0])
            df_14.insert(1,"종목코드",df[i][1])
            df_14.insert(2,"ETF구분", df[i][2])
            df_1471 = df_1471.append(df_14)
            print(df_1471)
        
            if i == 180:
                print("타임슬립걸렸습니다")
                print("약12분뒤에 다시 수집 시작합니다") 
                time.sleep(720)
            elif i == 360:
                print("타임슬립걸렸습니다")
                print("약12분뒤에 다시 수집 시작합니다") 
                time.sleep(720)
            elif i == 540:
                print("타임슬립걸렸습니다")
                print("약12분뒤에 다시 수집 시작합니다") 
                time.sleep(720)
            elif i == 720:
                print("타임슬립걸렸습니다")
                print("약12분뒤에 다시 수집 시작합니다") 
                time.sleep(720)
            elif i == 800:
                print("타임슬립걸렸습니다")
                print("약12분뒤에 다시 수집 시작합니다") 
                time.sleep(720)
                
        print("데이터 수집 전 사전에 제거 해야하는 코드 전부 제거하였습니다")
        print("10분 뒤 학습데이터 수집 시작합니다.")
        time.sleep(600)


        writer = pd.ExcelWriter("result.xlsx", engine="xlsxwriter")
        df_1471.to_excel(writer, sheet_name="Sheet1")
        writer.close()
 

        #누적거래량 0인 종목 사전에 제거하는 코드
        df_1471 = df_1471[df_1471.누적거래량 != 0]

        #넘파이형식으로 변환
        df_1471 = df_1471.values
        
        df = df_1471
        print(len(df))
        
        for i in range(len(df)):
            print(i)
            time.sleep(1)
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
            if i == 180:
                print("타임슬립걸렸습니다")
                print("약12분뒤에 다시 수집 시작합니다") 
                time.sleep(720) 

            if i == 360:
                print("타임슬립걸렸습니다")
                print("약12분뒤에 다시 수집 시작합니다") 
                time.sleep(720)
                
            if i == 540:
                print("타임슬립걸렸습니다")
                print("약12분뒤에 다시 수집 시작합니다")
                time.sleep(720)
                 
            if i == 720:
                print("타임슬립걸렸습니다")
                print("약12분뒤에 다시 수집 시작합니다")
                time.sleep(720) 

            if i == 800:
                print("타임슬립걸렸습니다")
                print("약12분뒤에 다시 수집 시작합니다")
                time.sleep(720)


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

        df_result.columns = ["date","code","name",
                                     "d1","d2","d3","d4","d5","d6","d7","d8","d9","d10",
                                     "d11","d12","d13","d14","d15","d16","d17","d18","d19","d20",
                                     "d21","d22","d23","d24","d25","d26","d27","d28","d29","d30",
                                     "d31","d32","d33","d34","d35","d36","d37","d38","d39","d40",
                                     "d41","d42","d43","d44","d45","d46","d47","d48","d49","d50",
                                     "d51","d52","d53","d54","d55","d56","d57","d58","d59","d60",
                                     "d61","d62","d63","d64","d65","d66","d67","d68","d69","d70",
                                     "d71","d72","d73","d74","d75","d76","d77","d78","d79","d80"]
        
        #판다스를 넘파이 형태로 변경
        date = df_result.date.values
        date = date.astype(str)
        code = df_result.code.values
        code = code.astype(str)
        name = df_result.name.values

        d1 = df_result.d1.values
        d1 = df_result.d1.values    
        d2 = df_result.d2.values
        d3 = df_result.d3.values
        d4 = df_result.d4.values
        d5 = df_result.d5.values
        d6 = df_result.d6.values
        d7 = df_result.d7.values
        d8 = df_result.d8.values
        d9 = df_result.d9.values
        d10 = df_result.d10.values
        d11 = df_result.d11.values
        d12 = df_result.d12.values
        d13 = df_result.d13.values
        d14 = df_result.d14.values
        d15 = df_result.d15.values
        d16 = df_result.d16.values
        d17 = df_result.d17.values
        d18 = df_result.d18.values
        d19 = df_result.d19.values
        d20 = df_result.d20.values
        d21 = df_result.d21.values
        d22 = df_result.d22.values
        d23 = df_result.d23.values
        d24 = df_result.d24.values
        d25 = df_result.d25.values
        d26 = df_result.d26.values
        d27 = df_result.d27.values
        d28 = df_result.d28.values
        d29 = df_result.d29.values
        d30 = df_result.d30.values
        d31 = df_result.d31.values
        d32 = df_result.d32.values
        d33 = df_result.d33.values
        d34 = df_result.d34.values
        d35 = df_result.d35.values
        d36 = df_result.d36.values
        d37 = df_result.d37.values
        d38 = df_result.d38.values
        d39 = df_result.d39.values
        d40 = df_result.d40.values
        d41 = df_result.d41.values
        d42 = df_result.d42.values
        d43 = df_result.d43.values
        d44 = df_result.d44.values
        d45 = df_result.d45.values
        d46 = df_result.d46.values
        d47 = df_result.d47.values
        d48 = df_result.d48.values
        d49 = df_result.d49.values
        d50 = df_result.d50.values
        d51 = df_result.d51.values
        d52 = df_result.d52.values
        d53 = df_result.d53.values
        d54 = df_result.d54.values
        d55 = df_result.d55.values
        d56 = df_result.d56.values
        d57 = df_result.d57.values
        d58 = df_result.d58.values
        d59 = df_result.d59.values
        d60 = df_result.d60.values
        d61 = df_result.d61.values
        d62 = df_result.d62.values
        d63 = df_result.d63.values
        d64 = df_result.d64.values
        d65 = df_result.d65.values
        d66 = df_result.d66.values
        d67 = df_result.d67.values
        d68 = df_result.d68.values
        d69 = df_result.d69.values
        d70 = df_result.d70.values
        d71 = df_result.d71.values
        d72 = df_result.d72.values
        d73 = df_result.d73.values
        d74 = df_result.d74.values
        d75 = df_result.d75.values
        d76 = df_result.d76.values
        d77 = df_result.d77.values
        d78 = df_result.d78.values
        d79 = df_result.d79.values
        d80 = df_result.d80.values

        #넘파이형로는 MYSQL 테이블에 넣지 못하기에 리스트형태로 변경
        d1 = d1.tolist()
        d2 = d2.tolist()
        d3 = d3.tolist()
        d4 = d4.tolist()
        d5 = d5.tolist()
        d6 = d6.tolist()
        d7 = d7.tolist()
        d8 = d8.tolist()
        d9 = d9.tolist()
        d10 = d10.tolist()
        d11 = d11.tolist()
        d12 = d12.tolist()
        d13 = d13.tolist()
        d14 = d14.tolist()
        d15 = d15.tolist()
        d16 = d16.tolist()
        d17 = d17.tolist()
        d18 = d18.tolist()
        d19 = d19.tolist()
        d20 = d20.tolist()
        d21 = d21.tolist()
        d22 = d22.tolist()
        d23 = d23.tolist()
        d24 = d24.tolist()
        d25 = d25.tolist()
        d26 = d26.tolist()
        d27 = d27.tolist()
        d28 = d28.tolist()
        d29 = d29.tolist()
        d30 = d30.tolist()
        d31 = d31.tolist()
        d32 = d32.tolist()
        d33 = d33.tolist()
        d34 = d34.tolist()
        d35 = d35.tolist()
        d36 = d36.tolist()
        d37 = d37.tolist()
        d38 = d38.tolist()
        d39 = d39.tolist()
        d40 = d40.tolist()
        d41 = d41.tolist()
        d42 = d42.tolist()
        d43 = d43.tolist()
        d44 = d44.tolist()
        d45 = d45.tolist()
        d46 = d46.tolist()
        d47 = d47.tolist()
        d48 = d48.tolist()
        d49 = d49.tolist()
        d50 = d50.tolist()
        d51 = d51.tolist()
        d52 = d52.tolist()
        d53 = d53.tolist()
        d54 = d54.tolist()
        d55 = d55.tolist()
        d56 = d56.tolist()
        d57 = d57.tolist()
        d58 = d58.tolist()
        d59 = d59.tolist()
        d60 = d60.tolist()
        d61 = d61.tolist()
        d62 = d62.tolist()
        d63 = d63.tolist()
        d64 = d64.tolist()
        d65 = d65.tolist()
        d66 = d66.tolist()
        d67 = d67.tolist()
        d68 = d68.tolist()
        d69 = d69.tolist()
        d70 = d70.tolist()
        d71 = d71.tolist()
        d72 = d72.tolist()
        d73 = d73.tolist()
        d74 = d74.tolist()
        d75 = d75.tolist()
        d76 = d76.tolist()
        d77 = d77.tolist()
        d78 = d78.tolist()
        d79 = d79.tolist()
        d80 = d80.tolist()

        
        #MYSQL / quantgo_kospi_train 테이블에 학습데이터 집어넣기
        for i in range (len(df_result)):
            print(name[i])
            sql = 'insert into quantgo_kospi_train (date,code,name,d1,d2,d3,d4,d5,d6,d7,d8,d9,d10,d11,d12,d13,d14,d15,d16,d17,d18,d19,d20,d21,d22,d23,d24,d25,d26,d27,d28,d29,d30,d31,d32,d33,d34,d35,d36,d37,d38,d39,d40,d41,d42,d43,d44,d45,d46,d47,d48,d49,d50,d51,d52,d53,d54,d55,d56,d57,d58,d59,d60,d61,d62,d63,d64,d65,d66,d67,d68,d69,d70,d71,d72,d73,d74,d75,d76,d77,d78,d79,d80) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
            cur.execute(sql, (date[i],code[i],name[i],
                            d1[i],d2[i],d3[i],d4[i],d5[i],d6[i],d7[i],d8[i],d9[i],d10[i],
                            d11[i],d12[i],d13[i],d14[i],d15[i],d16[i],d17[i],d18[i],d19[i],d20[i],
                            d21[i],d22[i],d23[i],d24[i],d25[i],d26[i],d27[i],d28[i],d29[i],d30[i],
                            d31[i],d32[i],d33[i],d34[i],d35[i],d36[i],d37[i],d38[i],d39[i],d40[i],
                            d41[i],d42[i],d43[i],d44[i],d45[i],d46[i],d47[i],d48[i],d49[i],d50[i],
                            d51[i],d52[i],d53[i],d54[i],d55[i],d56[i],d57[i],d58[i],d59[i],d60[i],
                            d61[i],d62[i],d63[i],d64[i],d65[i],d66[i],d67[i],d68[i],d69[i],d70[i],
                            d71[i],d72[i],d73[i],d74[i],d75[i],d76[i],d77[i],d78[i],d79[i],d80[i]))
            conn.commit()
            print("학습데이터 집어 넣기 성공")
        print(len(name))

        

writer = pd.ExcelWriter("Train_Normalization.xlsx", engine="xlsxwriter")
df_result.to_excel(writer, sheet_name="Sheet1")
writer.close()

