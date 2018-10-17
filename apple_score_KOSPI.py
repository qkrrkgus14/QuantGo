import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from keras.models import Sequential
from keras.models import load_model
import load_miracle as lm


code, date, name, x = lm.latestdata_get_apple()
p_save = np.empty((1, x.shape[0]))

x = x[:, :441] #데이터축소
x = x.reshape(-1, 1, 21, 21) #모양변형

#model = Sequential()
model = load_model('apple_kospi.h5py')


for d in range(x.shape[0]):
    p = np.array([x[d, :]])
    #p = x[d:]
    p_data = model.predict(p)
    k = np.linspace(30,-30,32)
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

