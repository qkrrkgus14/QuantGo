from sklearn.cross_validation import train_test_split
import pymysql.cursors
import numpy as np
from PIL import Image
import os, glob

def alldata_get_bit():         #모든데이터가져오기함수
    conn = pymysql.connect(host = '183.98.188.74', user = 'lyj', password = 'test1234', db = 'quantgo', charset = 'utf8') #미라클서버연결
    cur = conn.cursor() #커서객체생성
    sql = 'select * from bitgo'
    cur.execute(sql)
    res = cur.fetchall()   #fetchall 실행결과얻기 

    miracle_x = np.array(res) #행렬로 가져오기
    trans_x = miracle_x[:, 3:487] #x만 가져오기
    trans_t = miracle_x[:, -32:] #final, t가져오기
    x_train, x_test, t_train, t_test = train_test_split(trans_x, trans_t, test_size=0.2, random_state=0)
    x_train = trans_x.astype(np.float)
    x_test = trans_x.astype(np.float)
    t_train = trans_t.astype(np.float)
    t_test = trans_t.astype(np.float) 
    return x_train, x_test, t_train, t_test

def latestdata_get_bit():
    conn = pymysql.connect(host = '183.98.188.74', user = 'lyj', password = 'test1234', db = 'quantgo', charset = 'utf8') #미라클서버연결
    cur = conn.cursor() #커서객체생성
    sql = 'select * from bitgolatest'
    cur.execute(sql)
    res = cur.fetchall()   #fetchall 실행결과얻기 
    miracle_x = np.array(res) #행렬로 가져오기
    
    #trans_code = miracle_x[:, 2:3]      #코드번호가져오기
    trans_name = miracle_x[:, 2:3]      #종목명가져오기
    trans_date = miracle_x[0:1, 1:2]    #날짜가져오기
    trans_x = miracle_x[:, 4:-32]        #입력변수 x 가져오기
    #trans_report = miracle_x[:, 31:35]  #리포트가져오기
    date = trans_date[0, 0]             #날짜
    #code = trans_code.T
    name = trans_name.T
    x = trans_x.astype(np.float)
    #report = trans_report.T
    return date, name, x

def latestdata_get_apple():
    conn = pymysql.connect(host = '183.98.188.74', user = 'lyj', password = 'test1234', db = 'quantgo', charset = 'utf8') #미라클서버연결
    cur = conn.cursor() #커서객체생성

    sql = 'select * from apple order by date DESC limit 200'
    cur.execute(sql)
    res = cur.fetchall()   #fetchall 실행결과얻기
    miracle_x = np.array(res) #행렬로 가져오기
  
    trans_code = miracle_x[:, 2:3]      #코드번호가져오기
    trans_name = miracle_x[:, 3:4]      #종목명가져오기
    trans_date = miracle_x[0:1, 1:2]    #날짜가져오기
    trans_x = miracle_x[:, 4:-32]        #입력변수 x 가져오기
    #trans_report = miracle_x[:, 31:35]  #리포트가져오기
    date = trans_date[0, 0]             #날짜
    code = trans_code.T
    name = trans_name.T
    x = trans_x.astype(np.float)
    #report = trans_report.T
    return code, date, name, x

def latestdata_get_apple_kosdaq():
    conn = pymysql.connect(host = '183.98.188.74', user = 'lyj', password = 'test1234', db = 'quantgo', charset = 'utf8') #미라클서버연결
    cur = conn.cursor() #커서객체생성

    sql = 'select * from applek order by date DESC limit 100'
    cur.execute(sql)
    res = cur.fetchall()   #fetchall 실행결과얻기
    miracle_x = np.array(res) #행렬로 가져오기
  
    trans_code = miracle_x[:, 2:3]      #코드번호가져오기
    trans_name = miracle_x[:, 3:4]      #종목명가져오기
    trans_date = miracle_x[0:1, 1:2]    #날짜가져오기
    trans_x = miracle_x[:, 4:-32]        #입력변수 x 가져오기
    #trans_report = miracle_x[:, 31:35]  #리포트가져오기
    date = trans_date[0, 0]             #날짜
    code = trans_code.T
    name = trans_name.T
    x = trans_x.astype(np.float)
    #report = trans_report.T
    return code, date, name, x

def counseldata_get_apple(codenumber):   #특정데이터
    conn = pymysql.connect(host = '183.98.188.74', user = 'lyj', password = 'test1234', db = 'quantgo', charset = 'utf8') #미라클서버연결
    cur = conn.cursor()  # 커서객체생성
    sql = 'select * from apple where code = "A' + codenumber + '" order by date DESC limit 1'
    cur.execute(sql)
    res = cur.fetchall()
    miracle_x = np.array(res)  # 행렬로 가져오기
    final_x = miracle_x[:, 4:-32]
    x_data = final_x
    return x_data
