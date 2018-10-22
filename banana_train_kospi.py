#-*-coding: utf-8 -*-
import numpy as np
import pandas as pd
from pandas import DataFrame, Series

import pymysql.cursors
#import neural_network
from datetime import datetime, timedelta
from collections import OrderedDict

from sklearn.cross_validation import train_test_split
from keras.models import Sequential
from keras.layers import Activation, Dropout, Flatten, Dense
from keras.layers.convolutional import Conv2D, MaxPooling2D, ZeroPadding2D
from keras.optimizers import SGD
import matplotlib.pyplot as plt



conn = pymysql.connect(host = '183.98.188.74', user = 'lyj', password = 'test1234', db = 'quantgo', charset = 'utf8') #미라클서버연결
cur = conn.cursor()
sql = 'select date from quantgo_kospi_train'
cur.execute(sql)
res = cur.fetchall()
miracle_date = np.array(res)
print(len(miracle_date))

miracle_date = miracle_date.reshape(1,len(miracle_date))
print(miracle_date.shape)


#넘파이를 리스트형식으로 변환
aaaa = []
for i in range(len(miracle_date)):
    aaaa.append(miracle_date[i])
#    print(aaaa)
    
print(len(aaaa[0]))


def get_date(x=0):return (datetime.now() + timedelta(days=x)).strftime("%Y%m%d")


#리스트 안의 리스트로되어있는 것을 리스트로 다시 뽑아옴
kkk = []
for i in range(len(aaaa[0])):
    a = str(aaaa[0][i])
    kkk.append(a)
    
#print(kkk)
print("")
print("")
print("")


#중복된 데이터 제거하고 일자를 순서대로 나열
kkk = list(OrderedDict.fromkeys(kkk))
print(kkk)
print(kkk[-1])#전 거래일
print(kkk[-2])#전전 거래일
print(kkk[-3])#전전전 거래일
#print(kkk[-4])#전전전전 거래일
#print(kkk[-5])#전전전전전 거래일

def make_t(number): #정답값 원핫-인코딩하기
    t = np.zeros(60,dtype=int)
    if number >=29: #상한가
        t[0]=1
    elif number >=28:
        t[1]=1
    elif number >=27:
        t[2]=1
    elif number >=26:
        t[3]=1
    elif number >=25:
        t[4]=1
    elif number >=24:
        t[5]=1
    elif number >=23:
        t[6]=1
    elif number >=22:
        t[7]=1
    elif number >=21:
        t[8]=1
    elif number >=20:
        t[9]=1
    elif number >=19:
        t[10]=1
    elif number >=18:
        t[11]=1
    elif number >=17:
        t[12]=1
    elif number >=16:
        t[13]=1
    elif number >=15:
        t[14]=1
    elif number >=14:
        t[15]=1
    elif number >=13:
        t[16]=1
    elif number >=12:
        t[17]=1
    elif number >=11:
        t[18]=1
    elif number >=10:
        t[19]=1
    elif number >=9:
        t[20]=1
    elif number >=8:
        t[21]=1
    elif number >=7:
        t[22]=1
    elif number >=6:
        t[23]=1
    elif number >=5:
        t[24]=1
    elif number >=4:
        t[25]=1
    elif number >=3:
        t[26]=1
    elif number >=2:
        t[27]=1
    elif number >=1:
        t[28]=1
    elif number >=0:
        t[29]=1
    elif number >=-1:
        t[30]=1
    elif number >=-2:
        t[31]=1
    elif number >=-3:
        t[32]=1
    elif number >=-4:
        t[33]=1
    elif number >=-5:
        t[34]=1
    elif number >=-6:
        t[35]=1
    elif number >=-7:
        t[36]=1
    elif number >=-8:
        t[37]=1
    elif number >=-9:
        t[38]=1
    elif number >=-10:
        t[39]=1
    elif number >=-11:
        t[40]=1
    elif number >=-12:
        t[41]=1
    elif number >=-13:
        t[42]=1
    elif number >=-14:
        t[43]=1
    elif number >=-15:
        t[44]=1
    elif number >=-16:
        t[45]=1
    elif number >=-17:
        t[46]=1
    elif number >=-18:
        t[47]=1
    elif number >=-19:
        t[48]=1
    elif number >=-20:
        t[49]=1
    elif number >=-21:
        t[50]=1
    elif number >=-22:
        t[51]=1
    elif number >=-23:
        t[52]=1
    elif number >=-24:
        t[53]=1
    elif number >=-25:
        t[54]=1
    elif number >=-26:
        t[55]=1
    elif number >=-27:
        t[56]=1
    elif number >=-28:
        t[57]=1
    elif number >=-29:
        t[58]=1
    elif number >=-30:
        t[59]=1
    return t

x1 = np.arange(460) #붙일행렬
sql1 = "select * from quantgo_kospi_train where date=%s"
sql2 = "select * from quantgo_kospi_train where date=%s and name=%s"

for i in range(len(kkk)-5): #전체날짜순회하기
    cur.execute(sql1,(kkk[-(1+i)])) #날짜별 자료받기
    res1 = cur.fetchall()
    raw = np.array(res1)
    name = raw[:,3]    #종목명 얻기
    t = raw[:, 4]*30   #등락율이자 정답값 얻기
    x2 = np.arange(2)  #붙여넣을 행렬
    t = make_t(t)      #정답 원핫인코딩

    for j in range(5): #5거래일 순회
        cur.execute(sql2,(kkk[-(2+j)], name))  #자료받기
        res2 = cur.fetchall()
        data = np.array(res2)
        x2 = np.concatenate([x2, data])        #데이터쌓기

    x2 = x2[:, 2:]
    if (1,400) == x2.shape:
        print("데이터 5거래일 존재")
        x2 = np.concatenate([x2,t]) #정답뒤에 붙이기
        x1 = np.vstack([x1,x2])     #배열쌓기
    else:
        print("데이터 5거래일이 존재하지 않음. 오류")

x1 = x1[1:, :]        #붙일행렬떼기
final_x = x1[:, :-60] #속성
final_t = x1[: -60:]  #정답

print(final_x.shape) #속성값 shape 확인
print(final_t.shape) #정답값 shape 확인




x_train, x_test, t_train, t_test = train_test_split(final_x, final_t, test_size=0.2, random_state=33)

x_train = x_train.reshape(-1,1,20,20) #inputshape
x_test =  x_test.reshape(-1,1,20,20)

#model = neural_network.apple_nn(input_shape = x_train.shape[1:], nb_classes = 32)

model = Sequential()
model.add(ZeroPadding2D((1,1),input_shape=x_train.shape[1:]))
model.add(Conv2D(30, kernel_size=3, padding="same"))
model.add(Activation("relu"))
model.add(MaxPooling2D(pool_size=(2,2)))

#model.add(Conv2D(60,(3,3), padding="same"))
#model.add(Activation("relu"))

model.add(Flatten())
model.add(Dense(512))
model.add(Activation("relu"))

model.add(Dropout(0.25))
model.add(Dense(60))
model.add(Activation('softmax'))


#신경망조립(compile)
optimizer = SGD(lr = 0.001, decay=1e-8, momentum=0.9, nesterov =True)
model.compile(optimizer = optimizer, loss = "categorical_crossentropy", metrics = ['accuracy'])


#학습평가 및 그래프화
history = model.fit(x_train, t_train, batch_size = 32, epochs = 100, verbose = 1, validation_split = 0.2)
score = model.evaluate(x_test, t_test, verbose = 1)

print("오차율= ", score[0])
print("정확도= ", score[1])
plt.plot(history.history["acc"])
plt.plot(history.history["val_acc"])
plt.title("Banana_Acc_KOSPI")
plt.ylabel("Accuracy_Banana_KOSPI")
plt.xlabel("Apochs_Banana_KOSPI")
plt.legend(['train', 'test'], loc='upper left')
plt.show()


#신경망저장
model.save("Banana_kospi.h5py", overwrite=True)
