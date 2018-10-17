import numpy as np
import pymysql.cursors
import neural_network
from sklearn.cross_validation import train_test_split

from keras.models import Sequential
from keras.layers import Activation, Dropout, Flatten, Dense
from keras.layers.convolutional import Conv2D, MaxPooling2D, ZeroPadding2D
from keras.optimizers import SGD
import matplotlib.pyplot as plt

conn = pymysql.connect(host = '183.98.188.74', user = 'lyj', password = 'test1234', db = 'quantgo', charset = 'utf8') #미라클서버연결
cur = conn.cursor()
sql = 'select * from apple'
cur.execute(sql)
res = cur.fetchall()

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
