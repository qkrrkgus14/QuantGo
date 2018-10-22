import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from keras.models import Sequential
from keras.models import load_model

from time import strftime, localtime
import pymysql.cursors


weekdays = ["월","화","수","목","금","토","일"]
tm = localtime()
print(tm)

week = weekdays[tm.tm_wday] #요일구하기 (고쳐야함)
print(week)

today = strftime("%Y%m%d", localtime()) #오늘날짜구하기 (고쳐야함)
print(today)

conn = pymysql.connect(host = '183.98.188.74', user = 'lyj', password = 'test1234', db = 'quantgo', charset = 'utf8') #서버 MYSQL연결
cur = conn.cursor() #객체 커서 만들기
sql1 = "select * from quantgo_kospi_train where date=%s"
sql2 = "select * from quantgo_kospi_train "
cur.execute(sql1, (today)) #금일의 자료 받기
res = cur.fetchall() #가져오기
data = np.array(res)
if np.any(data == today): #만약 오늘 데이터가 없으면
    print('금일' + today + "데이터가 존재하여 예측이 가능합니다.")
elif int(strftime('%H', localtime())) < 16:
    print("금일" + today + "는" + week + "요일이고" + strftime("%H", localtime()) + '시라서 데이터가 없어 지난데이터로 예측합니다')
    cur.execute(sql2)
    res = cur.fetchall()
    data = np.array(res)
    date = data[-1][1] #가장 최신날짜가져오기
    cur.execute(sql1,(date)) #가상 최신데이터로 예측
    res = cur.fetchall()
    data = np.array(res)
x = data[:,4:]
print("")
print("")
print("x.shape :",x.shape)
print("")
print("")

p_save = np.empty((1, x.shape[0]))

x = x.reshape(-1, 1, 20, 20) #모양변형




#model = Sequential()
model = load_model('banana_kospi.h5py')


for d in range(x.shape[0]):
    p = np.array([x[d, :]])
    #p = x[d:]
    p_data = model.predict(p)
    k = np.linspace(30,-30,60)
    multi = np.multiply(k, p_data)
    predict_score = multi.sum()
    p_save[0, d] = predict_score

indexer = p_save.argsort()
for e in range(11):
    score_chart = str(e+1)+":"+str(name[0][indexer[0][-(1+e)]])+" : 점수:"+str(round(p_save[0][indexer[0][-(1+e)]],3))+"코드 : "+str(code[0][indexer[0][-(1+e)]])+"."
    #score_chart = str(e+1)+":"+str(name[0][indexer[0][-(1+e)]])+" : 점수:"+str(p_save[0][indexer[0][-(1+e)]])+"."
    print(score_chart) #데이터기준시각


print("")
print("")
print("반대종목 리스트")
for i in range(11):
    score_chart2 = str(i+1)+":" + str(name[0][indexer[0][i]])+" : 점수:"+str(round(p_save[0][indexer[0][i]],3))+","
    print(score_chart2)
    
print("")
print("")
print("")

#code0 = code[0]
name0 = name[0]
p_save0 = p_save[0]

df = pd.DataFrame({'종목명':name0, '퀀트고점수':p_save0})


print(df.sort_values(by='퀀트고점수',ascending=False))


