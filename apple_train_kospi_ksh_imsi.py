#-*-coding: utf-8 -*-
import numpy as np
import pandas as pd
from pandas import DataFrame, Series, Pane

import pymysql.cursors
import neural_network
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
    print(aaaa)
    
print(len(aaaa[0]))


def get_date(x=0):return (datetime.now() + timedelta(days=x)).strftime("%Y%m%d")


#리스트 안의 리스트로되어있는 것을 리스트로 다시 뽑아옴
kkk = []
for i in range(len(aaaa[0])):
    a = str(aaaa[0][i])
    kkk.append(a)
    
print(kkk)
print("")
print("")
print("")


#중복된 데이터 제거하고 일자를 순서대로 나열
kkk = list(OrderedDict.fromkeys(kkk))
print(kkk)
print(kkk[-1])#전 거래일
print(kkk[-2])#전전 거래일
print(kkk[-3])#전전전 거래일
print(kkk[-4])#전전전전 거래일
print(kkk[-5])#전전전전전 거래일


# 최근 5거래일 데이터 뽑아오는 코드
sql_1 = "select * from quantgo_kospi_train where date=%s or date=%s or date=%s or date=%s or date=%s"
cur.execute(sql_1,(kkk[-5],kkk[-4],kkk[-3],kkk[-2],kkk[-1]))
res_1 = cur.fetchall()
miracle_x = np.array(res_1)
print(miracle_x)






miracle_x = np.array(res)
final_x = miracle_x[:, 4:-32] #x만 가져오기
final_t = miracle_x[:, -32:] #final, t가져오기

print(final_x.shape) #속성값 shape 확인
print(final_t.shape) #정답값 shape 확인





x_train, x_test, t_train, t_test = train_test_split(final_x, final_t, test_size=0.2, random_state=33)

x_train = x_train.reshape(-1,1,21,21) #inputshape
x_test =  x_test.reshape(-1,1,21,21)

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
model.add(Dense(32))
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
plt.title("Apple_Acc_KOSPI")
plt.ylabel("Accuracy_Apple_KOSPI")
plt.xlabel("Apochs_Apple_KOSPI")
plt.legend(['train', 'test'], loc='upper left')
plt.show()


#신경망저장
model.save("apple_kospi.h5py", overwrite=True)
