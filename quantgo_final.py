from datetime import datetime, timedelta
import pymysql.cursors
import numpy as np
import time
import pandas as pd
import pymysql.cursors

import win32com.client
import pythoncom
import os, sys
import inspect
import time
import pymysql.cursors
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


def Login(url='hts.etrade.co.kr', port=200001, svrtype=0, id='', pwd='', cert=''):
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
    
    #주식종목코드조회
    
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



def t1471(종목코드='',분구분='00',시간='',자료개수='001'):
    
    #시간대별호가잔량추이
    
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


def t1636(구분="0",금액수량구분="1",정렬기준="",종목코드="",IDXCTS=""):
    
    #종목별프로그램매매동향
    
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

        등락율 = float(query.GetFieldData(OUTBLOCK1, "diff", i).strip())

        lst = [등락율]
        result.append(lst)

    df1 = DataFrame(data=result, columns=["등락율"])

    XAQueryEvents.상태 = False

    return df1


# 관리/불성실/투자유의조회
def t1404(구분='1',종목체크='',종목코드_CTS=""):
    
    #관리/불성실/투자유의조회
    
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
    
    #투자경고/매매정지/정리매매조회
    
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
    
    #초저유동성조회
    
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
        
        
        df_final = DataFrame([])
        
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
        
        
        
        #실제 학습데이터로 돌릴 종목
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
        
        df_final = DataFrame([])
        df_1471 = pd.read_excel("result.xlsx")
        
        #넘파이형식으로 변환
        df_1471 = df_1471.values
        
        df = df_1471
        print(len(df))
        
        #종목 거를꺼 다 거르고 D+1일 실제등락율 데이터 만드는 for문
        for i in range(len(df)):
            print(i)
            time.sleep(1)
            df_8430_code = df[i][1] 
            df_8430_name = df[i][0]
            
            
            df_axis = t1636(종목코드=df_8430_code)
            df_axis = df_axis.ix[:0]
            
            df_axis.insert(0,"일자",b)
            df_axis.insert(1,"단축코드", df_8430_code)
            df_axis.insert(2,"종목명", df_8430_name)
            df_final = df_final.append(df_axis)
            
            print(df_final)
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
                
        print("실제등락율 데이터 수집이 완료되었습니다")
        
        print(df_final)
        print("시작한시간: ", a)        


#df_result = df_result.dropna() #빈값인 데이터 자체 날려버리기
df_final = df_final.fillna(0) #빈값 0으로 채우기(이걸사용함)
df_final.columns = ["date","code","name","diff"]





#전체학습데이터 끌어오는 코드
conn = pymysql.connect(host = '183.98.188.74', user = 'lyj', password = 'test1234', db = 'quantgo', charset = 'utf8') #미라클서버연결
cur = conn.cursor()
sql = 'select * from quantgo_kospi_train'
cur.execute(sql)
res = cur.fetchall()
miracle_date = np.array(res)
#print(miracle_date)
miracle_date = miracle_date.tolist()
#print(miracle_date[0][1])

aaa = []
for i in range(len(miracle_date)):
    #print(miracle_date[i][1])
    aaa.append(miracle_date[i][1])
    

#aaa[-1] = 전일 거래일자
print(aaa[-1])

ddd = ["dummy","date","code","name",
       "d1","d2","d3","d4","d5","d6","d7","d8","d9","d10",
       "d11","d12","d13","d14","d15","d16","d17","d18","d19","d20",
       "d21","d22","d23","d24","d25","d26","d27","d28","d29","d30",
       "d31","d32","d33","d34","d35","d36","d37","d38","d39","d40",
       "d41","d42","d43","d44","d45","d46","d47","d48","d49","d50",
       "d51","d52","d53","d54","d55","d56","d57","d58","d59","d60",
       "d61","d62","d63","d64","d65","d66","d67","d68","d69","d70",
       "d71","d72","d73","d74","d75","d76","d77","d78","d79","d80"]


#전 거래일자의 학습데이터만 끌어오는 코드
sql_1 = "select *from quantgo_kospi_train where date=%s"
cur.execute(sql_1,aaa[-1])
res = cur.fetchall()
mi = np.array(res)
#print(mi)


#전 거래일자 판다스 데이터프레임만들고, 컬럼 매칭
df_result = pd.DataFrame(mi, columns=ddd)
#print(df_result)

#df_final = D+1일 실제등락율 데이터
print(df_final)

#알아서 종목명을 기준으로 매칭시켜서 d81컬럼을 만들고 실제등락율 붙이는 코드
df_result['d81'] = df_result['name'].map(df_final.set_index('name')['diff'])
df_result = df_result.drop(["dummy"], axis=1)
#print(df_result)
print(len(df_result))

df_result = df_result.fillna(0)


#판다스 넘파이 형태로 변경
date = df_result.date.values
date = date.astype(str)
code = df_result.code.values
code = code.astype(str)
name = df_result.name.values

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
d81 = df_result.d81.values


#소수점 형태로 변환
d1 = d1.astype(float)
d2 = d2.astype(float)
d3 = d3.astype(float)
d4 = d4.astype(float)
d5 = d5.astype(float)
d6 = d6.astype(float)
d7 = d7.astype(float)
d8 = d8.astype(float)
d9 = d9.astype(float)
d10 = d10.astype(float)
d11 = d11.astype(float)
d12 = d12.astype(float)
d13 = d13.astype(float)
d14 = d14.astype(float)
d15 = d15.astype(float)
d16 = d16.astype(float)
d17 = d17.astype(float)
d18 = d18.astype(float)
d19 = d19.astype(float)
d20 = d20.astype(float)
d21 = d21.astype(float)
d22 = d22.astype(float)
d23 = d23.astype(float)
d24 = d24.astype(float)
d25 = d25.astype(float)
d26 = d26.astype(float)
d27 = d27.astype(float)
d28 = d28.astype(float)
d29 = d29.astype(float)
d30 = d30.astype(float)
d31 = d31.astype(float)
d32 = d32.astype(float)
d33 = d33.astype(float)
d34 = d34.astype(float)
d35 = d35.astype(float)
d36 = d36.astype(float)
d37 = d37.astype(float)
d38 = d38.astype(float)
d39 = d39.astype(float)
d40 = d40.astype(float)
d41 = d41.astype(float)
d42 = d42.astype(float)
d43 = d43.astype(float)
d44 = d44.astype(float)
d45 = d45.astype(float)
d46 = d46.astype(float)
d47 = d47.astype(float)
d48 = d48.astype(float)
d49 = d49.astype(float)
d50 = d50.astype(float)
d51 = d51.astype(float)
d52 = d52.astype(float)
d53 = d53.astype(float)
d54 = d54.astype(float)
d55 = d55.astype(float)
d56 = d56.astype(float)
d57 = d57.astype(float)
d58 = d58.astype(float)
d59 = d59.astype(float)
d60 = d60.astype(float)
d61 = d61.astype(float)
d62 = d62.astype(float)
d63 = d63.astype(float)
d64 = d64.astype(float)
d65 = d65.astype(float)
d66 = d66.astype(float)
d67 = d67.astype(float)
d68 = d68.astype(float)
d69 = d69.astype(float)
d70 = d70.astype(float)
d71 = d71.astype(float)
d72 = d72.astype(float)
d73 = d73.astype(float)
d74 = d74.astype(float)
d75 = d75.astype(float)
d76 = d76.astype(float)
d77 = d77.astype(float)
d78 = d78.astype(float)
d79 = d79.astype(float)
d80 = d80.astype(float)
d81 = d81.astype(float)


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
d81 = d81.tolist()

print(df_result)
print(len(df_result))


for i in range (len(df_result)):
    print(name[i])
    sql = 'insert into quantgo_kospi_final (date,code,name,d1,d2,d3,d4,d5,d6,d7,d8,d9,d10,d11,d12,d13,d14,d15,d16,d17,d18,d19,d20,d21,d22,d23,d24,d25,d26,d27,d28,d29,d30,d31,d32,d33,d34,d35,d36,d37,d38,d39,d40,d41,d42,d43,d44,d45,d46,d47,d48,d49,d50,d51,d52,d53,d54,d55,d56,d57,d58,d59,d60,d61,d62,d63,d64,d65,d66,d67,d68,d69,d70,d71,d72,d73,d74,d75,d76,d77,d78,d79,d80,d81) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
    cur.execute(sql, (date[i],code[i],name[i],
                      d1[i],d2[i],d3[i],d4[i],d5[i],d6[i],d7[i],d8[i],d9[i],d10[i],
                      d11[i],d12[i],d13[i],d14[i],d15[i],d16[i],d17[i],d18[i],d19[i],d20[i],
                      d21[i],d22[i],d23[i],d24[i],d25[i],d26[i],d27[i],d28[i],d29[i],d30[i],
                      d31[i],d32[i],d33[i],d34[i],d35[i],d36[i],d37[i],d38[i],d39[i],d40[i],
                      d41[i],d42[i],d43[i],d44[i],d45[i],d46[i],d47[i],d48[i],d49[i],d50[i],
                      d51[i],d52[i],d53[i],d54[i],d55[i],d56[i],d57[i],d58[i],d59[i],d60[i],
                      d61[i],d62[i],d63[i],d64[i],d65[i],d66[i],d67[i],d68[i],d69[i],d70[i],
                      d71[i],d72[i],d73[i],d74[i],d75[i],d76[i],d77[i],d78[i],d79[i],d80[i],d81[i]))        
    conn.commit()
    print("실제등락율 붙인 데이터 성공")
print(len(name))







#miracle_date = miracle_date.tolist()
#print(miracle_date[0])

'''
def get_date(x=0):return (datetime.now() + timedelta(days=x)).strftime("%Y%m%d")
#전 거래일 날짜 찾는 구문
count = 0
while True:
    count += -1
    if get_date(count) in miracle_date:
        print(get_date(count))
        break

'''

'''
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
    #sql = 'insert into quantgo_kospi_train (date,code,name,d1,d2,d3) values (%s,%s,%s,%s,%s,%s)'
    #sql = 'insert into quantgo_kospi_train (date) values (%s)'
    #cur.execute(sql, (date[i],code[i],name[i],d1[i],d2[i],d3[i]))
    conn.commit()
    print("성공")
print(len(name))
'''



